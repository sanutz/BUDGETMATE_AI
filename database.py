import sqlite3
import os
import tempfile
import shutil
from datetime import datetime, timedelta
import random

REPO_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'budgetiq.db')
TARGET_DB = os.path.join(tempfile.gettempdir(), 'budgetiq.db') if os.environ.get('VERCEL') else REPO_DB

def ensure_db():
    if os.environ.get('VERCEL') and not os.path.exists(TARGET_DB):
        if os.path.exists(REPO_DB):
            try:
                shutil.copy2(REPO_DB, TARGET_DB)
            except Exception as e:
                print(f"Error copying DB: {e}")

def get_db_connection():
    ensure_db()
    conn = sqlite3.connect(TARGET_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    ensure_db()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    conn.commit()
    conn.close()

def add_transaction(amount, category, description, type_, date):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO transactions (amount, category, description, type, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (amount, category, description, type_, date))
    conn.commit()
    inserted_id = c.lastrowid
    conn.close()
    return get_transaction(inserted_id)

def get_transaction(transaction_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_transactions(type_filter=None, category_filter=None):
    conn = get_db_connection()
    c = conn.cursor()
    
    query = 'SELECT * FROM transactions WHERE 1=1'
    params = []
    
    if type_filter:
        query += ' AND type = ?'
        params.append(type_filter)
    if category_filter:
        query += ' AND category = ?'
        params.append(category_filter)
        
    query += ' ORDER BY date DESC, id DESC'
    c.execute(query, tuple(params))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_transaction(transaction_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    changes = conn.total_changes
    conn.close()
    return changes > 0

def seed_data():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as cnt FROM transactions')
    if c.fetchone()['cnt'] > 0:
        c.execute('DELETE FROM transactions') # Clean start
        conn.commit()
    
    sample_categories = [
        ('Salary', 'income', ['Monthly salary', 'Bonus', 'Freelance work']),
        ('Investment', 'income', ['Stock dividends', 'Interest']),
        ('Food', 'expense', ['Groceries at Supermarket', 'Dinner at Restaurant', 'Coffee shop', 'Lunch delivery']),
        ('Transport', 'expense', ['Uber ride', 'Gas station', 'Subway ticket', 'Car maintenance']),
        ('Shopping', 'expense', ['Clothes online', 'Electronics', 'Amazon purchase', 'Shoes']),
        ('Entertainment', 'expense', ['Movie tickets', 'Netflix subscription', 'Concert', 'Video games']),
        ('Health', 'expense', ['Pharmacy', 'Gym membership', 'Doctor visit']),
        ('Education', 'expense', ['Online course', 'Books', 'Workshop']),
        ('Utilities', 'expense', ['Electric bill', 'Internet bill', 'Water bill', 'Phone plan']),
        ('Other', 'expense', ['Gift for friend', 'Home repair'])
    ]

    for _ in range(15):
        cat_info = random.choice(sample_categories)
        category = cat_info[0]
        type_ = cat_info[1]
        description = random.choice(cat_info[2])
        
        if type_ == 'income':
            amount = round(random.uniform(1000, 5000), 2)
        else:
            amount = round(random.uniform(10, 300), 2)
            
        # Random date within last 90 days
        days_ago = random.randint(0, 90)
        date_obj = datetime.now() - timedelta(days=days_ago)
        date_str = date_obj.strftime("%Y-%m-%d")
        
        c.execute('''
            INSERT INTO transactions (amount, category, description, type, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (amount, category, description, type_, date_str))
        
    conn.commit()
    conn.close()
