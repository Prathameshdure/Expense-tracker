from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, close_db_connection
import mysql.connector

app = Flask(__name__)
app.secret_key = 'smart_spend_key_2026' # Secure session key

# Helper to check login status
def is_logged_in():
    return 'user_id' in session

# --- ROUTES ---

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        
        db = get_db_connection()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                               (username, email, password))
                db.commit()
                flash("Registration successful! Please login.", "success")
                return redirect(url_for('login'))
            except mysql.connector.Error:
                flash("Email already registered.", "danger")
            finally:
                close_db_connection(db, cursor)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        close_db_connection(db, cursor)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login'))
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    uid = session['user_id']
    
    cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s", (uid,))
    total = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY expense_date DESC LIMIT 5", (uid,))
    expenses = cursor.fetchall()
    
    close_db_connection(db, cursor)
    return render_template('dashboard.html', total=total, expenses=expenses)

@app.route('/reports')
def reports():
    if not is_logged_in(): return redirect(url_for('login'))
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT category, SUM(amount) as total FROM expenses WHERE user_id = %s GROUP BY category", (session['user_id'],))
    data = cursor.fetchall()
    
    labels = [row['category'] for row in data]
    values = [float(row['total']) for row in data]
    
    close_db_connection(db, cursor)
    return render_template('reports.html', labels=labels, values=values)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if not is_logged_in(): return redirect(url_for('login'))
    
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO expenses (user_id, amount, category, expense_date, description) VALUES (%s, %s, %s, %s, %s)",
                   (session['user_id'], request.form['amount'], request.form['category'], request.form['date'], request.form['description']))
    db.commit()
    close_db_connection(db, cursor)
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:id>')
def delete_expense(id):
    if not is_logged_in(): return redirect(url_for('login'))
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (id, session['user_id']))
    db.commit()
    close_db_connection(db, cursor)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- CRITICAL FIX FOR PYTHON 3.13 ---
if __name__ == '__main__':
    # use_reloader=False prevents the signal-handling crash in restricted environments
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
