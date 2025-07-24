import bcrypt
from ldap3 import Server, Connection, ALL
from db import get_db_connection

def register_user(username, password, email, fname, lname, dept_id, div_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return 'username_taken'

    cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return 'email_taken'

    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, is_ldap, Fname, Lname, Email, Dept_ID, Div_ID) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (username, hashed_pw, 0, fname, lname, email, dept_id, div_id)
        )
        conn.commit()
        result = 'success'
    except Exception as e:
        print(f"Error registering user: {e}")
        result = 'error'
    finally:
        cursor.close()
        conn.close()
    return result

def register_or_update_ldap_user(username, fname, lname, email, dept_id, div_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    try:
        if user:
            cursor.execute(
                "UPDATE users SET Fname = %s, Lname = %s, Email = %s, Dept_ID = %s, Div_ID = %s, is_ldap = %s "
                "WHERE username = %s",
                (fname, lname, email, dept_id, div_id, 1, username)
            )
        else:
            cursor.execute(
                "INSERT INTO users (username, password, is_ldap, Fname, Lname, Email, Dept_ID, Div_ID) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (username, None, 1, fname, lname, email, dept_id, div_id)
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error registering/updating LDAP user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def validate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password, is_ldap FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and not user['is_ldap'] and user['password'] and bcrypt.checkpw(password.encode(), user['password'].encode()):
        return True
    return False

def ldap_auth(username, password):
    try:
        server = Server('localhost', port=389, get_info=ALL)
        dn = f'uid={username},ou=users,dc=mycompany,dc=com'
        conn = Connection(server, dn, password, auto_bind=True)

        if conn.search(dn, '(objectClass=inetOrgPerson)', attributes=['givenName', 'sn', 'mail', 'departmentNumber']):
            attrs = conn.entries[0]
            fname = attrs.givenName.value if 'givenName' in attrs else 'Unknown'
            lname = attrs.sn.value if 'sn' in attrs else 'Unknown'
            email = attrs.mail.value if 'mail' in attrs else f"{username}@company.com"
            department = attrs.departmentNumber.value if 'departmentNumber' in attrs else 'Unknown'
        else:
            fname, lname, email, department = 'Unknown', 'Unknown', f"{username}@company.com", 'Unknown'

        from utils import map_ldap_department_to_ids
        dept_div_ids = map_ldap_department_to_ids(department)
        dept_id = dept_div_ids['Dept_ID']
        div_id = dept_div_ids['Div_ID']

        register_or_update_ldap_user(username, fname, lname, email, dept_id, div_id)
        return True
    except Exception as e:
        print(f"LDAP auth error: {e}")
        return False