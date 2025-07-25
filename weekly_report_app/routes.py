from flask import render_template, request, redirect, url_for, session, flash, send_from_directory
from functools import wraps
from db import get_db_connection, read_all_entries, update_entry, init_db, init_excel, save_to_excel, Config, get_department_name, get_division_name
from auth import validate_user, ldap_auth, register_user
import pandas as pd
import os
import logging
import re
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_logged_in'):
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            login_type = request.form.get('login_type', 'user')

            if '@' in username:
                username = username.split('@')[0]

            if login_type == 'admin':
                if username == 'admin' and password == 'adminpass123':
                    session['is_admin'] = True
                    session['user_logged_in'] = True
                    session['username'] = username
                    return redirect(url_for('submissions'))
                else:
                    flash('Invalid admin credentials', 'danger')
            else:
                if validate_user(username, password):
                    session['user_logged_in'] = True
                    session['username'] = username
                    session['is_admin'] = False
                    return redirect(url_for('form_page'))
                elif ldap_auth(username, password):
                    session['user_logged_in'] = True
                    session['username'] = username
                    session['is_admin'] = False
                    return redirect(url_for('form_page'))
                else:
                    flash('Invalid username or password', 'error')
        return render_template('login.html')

    @app.route('/user_login', methods=['GET', 'POST'])
    def user_login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if '@' in username:
                username = username.split('@')[0]

            if validate_user(username, password):
                session['user_logged_in'] = True
                session['username'] = username
                session['is_admin'] = False
                return redirect(url_for('form_page'))
            elif ldap_auth(username, password):
                session['user_logged_in'] = True
                session['username'] = username
                session['is_admin'] = False
                return redirect(url_for('form_page'))
            else:
                flash('Invalid username or password', 'error')
        return render_template('user_login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Dept_ID, Name FROM Department")
        departments = cursor.fetchall()
        cursor.execute("SELECT Div_ID, Dept_ID, Name FROM Division")
        divisions = cursor.fetchall()
        cursor.close()
        conn.close()

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            confirm = request.form['confirm_password']
            email = request.form['email']
            fname = request.form['fname']
            lname = request.form['lname']
            dept_id = request.form['dept_id']
            div_id = request.form['div_id']

            valid_div = any(div['Div_ID'] == int(div_id) and div['Dept_ID'] == int(dept_id) for div in divisions)
            if not valid_div:
                flash('Invalid division for selected department.', 'error')
                return render_template('signup.html', departments=departments, divisions=divisions)

            if password != confirm:
                flash('Passwords do not match.', 'error')
                return render_template('signup.html', departments=departments, divisions=divisions)
            if len(password) <= 4 or not re.search(r'\d', password):
                flash('Password must be more than 4 characters and contain at least one number.', 'error')
                return render_template('signup.html', departments=departments, divisions=divisions)

            result = register_user(username, password, email, fname, lname, dept_id, div_id)
            if result == 'success':
                flash('Account created. Please log in.', 'success')
                return redirect(url_for('login'))
            elif result == 'username_taken':
                flash('Username already taken. Try using your full name.', 'error')
            elif result == 'email_taken':
                flash('Email already used.', 'error')
        return render_template('signup.html', departments=departments, divisions=divisions)

    @app.route('/form', methods=['GET', 'POST'])
    @login_required
    def form_page():
        init_excel()
        username = session['username']
        
        # Fetch user details for pre-filling the form
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT CONCAT(u.Fname, ' ', u.Lname) AS full_name, 
                   d.Name AS dept_name, dv.Name AS div_name
            FROM users u
            JOIN Department d ON u.Dept_ID = d.Dept_ID
            JOIN Division dv ON u.Div_ID = dv.Div_ID
            WHERE u.username = %s
        """, (username,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user_data:
            flash('User data not found. Please contact an administrator.', 'error')
            return redirect(url_for('login'))

        if request.method == 'POST':
            name = request.form['name']
            department = request.form['department']
            division = request.form['division']
            comment = request.form['comment']
            work_done_list = request.form.getlist('work_done[]')
            date_list = request.form.getlist('date[]')
            status_list = request.form.getlist('status[]')
            activity_list = request.form.getlist('Activity[]')
            recommendation_list = request.form.getlist('recommendation[]')

            conn = get_db_connection()
            cursor = conn.cursor()
            current_week = get_current_week_sheet_name()

            for i in range(len(work_done_list)):
                entry = {
                    'Username': username,
                    'Name': name,
                    'Department': department,
                    'Division': division,
                    'Work Done': work_done_list[i],
                    'Start Date': date_list[i],
                    'Status': status_list[i],
                    'Activity': activity_list[i],
                    'Recommendation': recommendation_list[i],
                    'Approval from ECOP (if any)': comment
                }
                cursor.execute('''INSERT INTO Feedback 
                    (user_ID, Dept_ID, Div_ID, activity, work_done, start_date, status, 
                     recommendation, ecop_approval, week, last_update) 
                    VALUES ((SELECT id FROM users WHERE username = %s), 
                            (SELECT Dept_ID FROM Department WHERE Name = %s), 
                            (SELECT Div_ID FROM Division WHERE Name = %s), 
                            %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (entry['Username'], entry['Department'], entry['Division'], entry['Activity'],
                     entry['Work Done'], entry['Start Date'], entry['Status'], entry['Recommendation'],
                     entry['Approval from ECOP (if any)'], current_week, None))
                entry['ID'] = cursor.lastrowid
                save_to_excel(entry)

            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('submissions'))
        
        return render_template('form_multi.html', 
                             full_name=user_data['full_name'], 
                             department=user_data['dept_name'], 
                             division=user_data['div_name'])

    @app.route('/submissions')
    @login_required
    def submissions():
        q = request.args.get('q', '').lower()
        is_admin = session.get('is_admin', False)
        username = session.get('username')
        entries = read_all_entries(username=None if is_admin else username)
        df = pd.DataFrame(entries)
        if q:
            df = df[df.apply(lambda row: q in str(row).lower(), axis=1)]
        return render_template('submissions.html', data=df.to_dict(orient='records'), is_admin=is_admin)

    @app.route('/download')
    @admin_required
    def download():
        if not session.get('is_admin', False):
            return "Unauthorized", 403
        if not os.path.exists(Config.EXCEL_FILE):
            return "Report file not found. Please submit some data first.", 404
        directory = os.path.abspath(os.path.dirname(Config.EXCEL_FILE))
        filename = os.path.basename(Config.EXCEL_FILE)
        current_sheet = get_current_week_sheet_name()
        return send_from_directory(
            directory=directory,
            path=filename,
            as_attachment=True,
            download_name=f"DRMD_Weekly_Report_{current_sheet}.xlsx"
        )

    @app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
    @login_required
    def edit(entry_id):
        username = session.get('username')
        is_admin = session.get('is_admin', False)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f.*, u.username, CONCAT(u.Fname, ' ', u.Lname) AS name 
            FROM Feedback f 
            JOIN users u ON f.user_ID = u.id 
            WHERE f.id = %s
        ''', (entry_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            flash('Entry not found.', 'danger')
            return redirect(url_for('submissions'))

        if not is_admin and row['username'] != username:
            flash('Access denied: You can only edit your own entries.', 'danger')
            return redirect(url_for('submissions'))

        entry = {
            'ID': row['id'], 'Username': row['username'], 'Name': row['name'],
            'Department': row['Dept_ID'], 'Division': row['Div_ID'],
            'Activity': row['activity'], 'Work Done': row['work_done'],
            'Start Date': row['start_date'], 'Last Update': row['last_update'],
            'Status': row['status'], 'Recommendation': row['recommendation'],
            'Approval from ECOP (if any)': row['ecop_approval'], 'Week': row['week']
        }

        if request.method == 'POST':
            updated_data = {
                'Activity': request.form['Activity'],
                'Start Date': request.form['date'],
                'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Work Done': request.form['work_done'],
                'Status': request.form['status'],
                'Recommendation': request.form['recommendation'],
                'Approval from ECOP (if any)': request.form['comment']
            }
            if update_entry(entry_id, updated_data):
                flash('Entry updated successfully.', 'success')
                return redirect(url_for('submissions'))
            else:
                flash('Failed to update entry.', 'danger')
            return render_template('edit.html', entry=entry)
        return render_template('edit.html', entry=entry)

    @app.route('/reset_password', methods=['GET', 'POST'])
    @login_required
    def reset_password():
        username = session.get('username')
        if request.method == 'POST':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return render_template('reset_password.html')

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password, is_ldap FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user:
                if user['is_ldap']:
                    flash('LDAP users cannot change passwords from this app.', 'warning')
                    return redirect(url_for('form_page'))
                if bcrypt.checkpw(current_password.encode(), user['password'].encode()):
                    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                    cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed, username))
                    conn.commit()
                    flash('Password updated successfully.', 'success')
                else:
                    flash('Current password is incorrect.', 'error')
            else:
                flash('User not found.', 'error')
            cursor.close()
            conn.close()
        return render_template('reset_password.html', username=username)

    @app.route('/admin/reset_password/<username>', methods=['GET', 'POST'])
    @admin_required
    def admin_reset_password(username):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password, is_ldap FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user:
                flash("Company directory user passwords can't be changed on this app.", 'danger')
                logger.warning(f"Attempt to reset password for non-existent user: {username}")
                return redirect(url_for('submissions'))

            if user.get('is_ldap', 0) == 1:
                flash('LDAP user passwords cannot be changed from this application.', 'warning')
                logger.info(f"Blocked password reset attempt for LDAP user: {username}")
                return redirect(url_for('submissions'))

            if request.method == 'POST':
                new_password = request.form['new_password']
                confirm_password = request.form['confirm_password']

                if new_password != confirm_password:
                    flash('Passwords do not match.', 'error')
                    return render_template('admin_reset_password.html', username=username)

                if len(new_password) <= 4 or not re.search(r'\d', new_password):
                    flash('New password must be more than 4 characters and contain at least one number.', 'error')
                    return render_template('admin_reset_password.html', username=username)

                hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed, username))
                conn.commit()
                flash(f"Password for {username} reset successfully.", 'success')
                logger.info(f"Password reset successful for user: {username}")
                return redirect(url_for('submissions'))

            return render_template('admin_reset_password.html', username=username)
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            logger.error(f"Error in admin_reset_password for {username}: {str(e)}")
            return redirect(url_for('submissions'))
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully.', 'info')
        return redirect(url_for('login'))
