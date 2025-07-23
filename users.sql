MariaDB [(none)]> CREATE DATABASE user_db;
Query OK, 1 row affected (0.001 sec)

MariaDB [(none)]> USE user_db;
Database changed

MariaDB [user_db]> CREATE TABLE Department (
    ->     Dept_ID INT PRIMARY KEY,
    ->     Name VARCHAR(100) NOT NULL,
    ->     HOD_ID INT
    -> );
Query OK, 0 rows affected (0.010 sec)

MariaDB [user_db]> CREATE TABLE Division (
    ->     Div_ID INT PRIMARY KEY,
    ->     Dept_ID INT,
    ->     Name VARCHAR(100) NOT NULL,
    ->     DH_ID INT,
    ->     FOREIGN KEY (Dept_ID) REFERENCES Department(Dept_ID)
    -> );
Query OK, 0 rows affected (0.031 sec)

MariaDB [user_db]> CREATE TABLE User (
    ->     user_ID INT PRIMARY KEY,
    ->     password VARCHAR(255) DEFAULT NULL,
    ->     is_ldap TINYINT(1) NOT NULL CHECK (is_ldap IN (0, 1)),
    ->     Fname VARCHAR(100) NOT NULL,
    ->     Lname VARCHAR(100) NOT NULL,
    ->     Email VARCHAR(150) NOT NULL UNIQUE,
    ->     Dept_ID INT,
    ->     Div_ID INT,
    ->     FOREIGN KEY (Dept_ID) REFERENCES Department(Dept_ID),
    ->     FOREIGN KEY (Div_ID) REFERENCES Division(Div_ID)
    -> );
Query OK, 0 rows affected (0.025 sec)

MariaDB [user_db]> CREATE TABLE Feedback (
    ->  id INT AUTO_INCREMENT PRIMARY KEY,
    ->     username VARCHAR(255) NOT NULL,
    ->     name TEXT,
    ->     Dept_ID INT,
    ->     Div_ID INT,
    ->     activity TEXT,
    ->     work_done TEXT,
    ->     start_date DATE,
    ->     status TEXT,
    ->     recommendation TEXT,
    ->     ecop_approval TEXT,
    ->     week VARCHAR(50),
    ->     last_update DATETIME,
    ->     FOREIGN KEY (Dept_ID) REFERENCES Department(Dept_ID),
    ->     FOREIGN KEY (Div_ID) REFERENCES Division(Div_ID)
    -> );
Query OK, 0 rows affected (0.035 sec)

MariaDB [user_db]> show tables
    -> ;
+-------------------+
| Tables_in_user_db |
+-------------------+
| department        |
| division          |
| feedback          |
| user              |
+-------------------+
4 rows in set (0.001 sec)

MariaDB [user_db]> DESC user;
+----------+--------------+------+-----+---------+-------+
| Field    | Type         | Null | Key | Default | Extra |
+----------+--------------+------+-----+---------+-------+
| user_ID  | int(11)      | NO   | PRI | NULL    |       |
| password | varchar(255) | YES  |     | NULL    |       |
| is_ldap  | tinyint(1)   | NO   |     | NULL    |       |
| Fname    | varchar(100) | NO   |     | NULL    |       |
| Lname    | varchar(100) | NO   |     | NULL    |       |
| Email    | varchar(150) | NO   | UNI | NULL    |       |
| Dept_ID  | int(11)      | YES  | MUL | NULL    |       |
| Div_ID   | int(11)      | YES  | MUL | NULL    |       |
+----------+--------------+------+-----+---------+-------+
8 rows in set (0.022 sec)

MariaDB [user_db]>

