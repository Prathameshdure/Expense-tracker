from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, close_db_connection
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secure_random_secret_key' # Keep this secret!

# --- Middleware: Check if user is logged in ---
def is_logged_in():
    return 'user_id' in session

# --- ROUTES ---

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# 1. Registration Logic
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
            except mysql.connector.IntegrityError:
                flash("Email already registered.", "danger")
            finally:
                close_db_connection(db, cursor)
        else:
            flash("Database connection error.", "danger")
            
    return render_template('register.html')

# 2. Login Logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        db = get_db_connection()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            close_db_connection(db, cursor)
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid email or password.", "danger")
        else:
            flash("Database connection error.", "danger")
            
    return render_template('login.html')

# 3. Main Dashboard
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    user_id = session['user_id']
    
    # Get Total Sum
    cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s", (user_id,))
    total = cursor.fetchone()['total'] or 0
    
    # Get Category Breakdown (for potential charts)
    cursor.execute("SELECT category, SUM(amount) as amt FROM expenses WHERE user_id = %s GROUP BY category", (user_id,))
    summary = cursor.fetchall()
    
    # Get Top 5 Recent Expenses
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY expense_date DESC LIMIT 5", (user_id,))
    expenses = cursor.fetchall()
    
    close_db_connection(db, cursor)
    return render_template('dashboard.html', total=total, summary=summary, expenses=expenses)

# 4. View All Expenses Page
@app.route('/expenses')
def all_expenses():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s ORDER BY expense_date DESC", (session['user_id'],))
    expenses = cursor.fetchall()
    close_db_connection(db, cursor)
    
    return render_template('expenses.html', expenses=expenses)

# 5. Add Expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']
    description = request.form['description']
    
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO expenses (user_id, amount, category, expense_date, description) 
        VALUES (%s, %s, %s, %s, %s)
    """, (session['user_id'], amount, category, date, description))
    db.commit()
    close_db_connection(db, cursor)
    
    flash("Expense added successfully!", "success")
    return redirect(url_for('dashboard'))

# 6. Delete Expense
@app.route('/delete/<int:id>')
def delete_expense(id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (id, session['user_id']))
    db.commit()
    close_db_connection(db, cursor)
    
    flash("Expense deleted.", "info")
    return redirect(url_for('dashboard'))

# 7. Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)