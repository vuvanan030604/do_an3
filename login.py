from flask import Flask, request, render_template, redirect, url_for, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection(db_name, user, password, host, port):
    conn = psycopg2.connect(
        dbname=db_name,
        user=user,
        password=password,
        host=host,
        port=port
    )
    return conn

def get_all_students():
    if 'db_name' in session:
        conn = get_db_connection(
            session['db_name'],
            session['user'],
            session['password'],
            session['host'],
            session['port']
        )
        cur = conn.cursor()
        cur.execute('SELECT hoten, mssv FROM sinhvien')
        students = cur.fetchall()
        conn.close()
        return students
    return []

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    db_name = request.form['db_name']
    user = request.form['user']
    password = request.form['password']
    host = request.form['host']
    port = request.form['port']
    try:
        conn = get_db_connection(db_name, user, password, host, port)
        session['db_name'] = db_name
        session['user'] = user
        session['password'] = password
        session['host'] = host
        session['port'] = port
        return redirect(url_for('students'))
    except Exception as e:
        return f"Error: {e}"

@app.route('/students')
def students():
    if 'db_name' in session:
        students = get_all_students()
        return render_template('students.html', students=students)
    else:
        return redirect(url_for('index'))

@app.route('/add_student', methods=['POST'])
def add_student():
    if 'db_name' in session:
        hoten = request.form['hoten']
        mssv = request.form['mssv']
        try:
            conn = get_db_connection(
                session['db_name'],
                session['user'],
                session['password'],
                session['host'],
                session['port']
            )
            cur = conn.cursor()
            cur.execute('SELECT mssv FROM sinhvien WHERE mssv = %s', (mssv,))
            existing_student = cur.fetchone()
            if existing_student:
                error_message = "MSSV này đã có. Vui lòng nhập MSSV khác."
                students = get_all_students()
                return render_template('students.html', students=students, error_message=error_message)
            cur.execute('INSERT INTO sinhvien (hoten, mssv) VALUES (%s, %s)', (hoten, mssv))
            conn.commit()
            conn.close()
            return redirect(url_for('students'))
        except Exception as e:
            return f"Error: {e}"
    else:
        return redirect(url_for('index'))

@app.route('/search_student', methods=['POST'])
def search_student():
    if 'db_name' in session:
        mssv_filter = request.form.get('mssv_filter', '')
        try:
            conn = get_db_connection(
                session['db_name'],
                session['user'],
                session['password'],
                session['host'],
                session['port']
            )
            cur = conn.cursor()
            cur.execute('SELECT hoten, mssv FROM sinhvien WHERE mssv = %s', (mssv_filter,))
            filtered_student = cur.fetchone()
            conn.close()
            students = get_all_students()
            return render_template('students.html', students=students, filtered_student=filtered_student)
        except Exception as e:
            return f"Error: {e}"
    else:
        return redirect(url_for('index'))

@app.route('/delete_student', methods=['POST'])
def delete_student():
    if 'db_name' in session:
        mssv = request.form.get('mssv', '')
        try:
            conn = get_db_connection(
                session['db_name'],
                session['user'],
                session['password'],
                session['host'],
                session['port']
            )
            cur = conn.cursor()
            cur.execute('DELETE FROM sinhvien WHERE mssv = %s', (mssv,))
            conn.commit()
            conn.close()
            return redirect(url_for('students'))
        except Exception as e:
            return f"Error: {e}"
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
