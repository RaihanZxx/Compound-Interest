import sqlite3
from typing import List, Dict
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "calculations.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    principal REAL,
                    payment REAL,
                    payment_frequency TEXT,
                    rate REAL,
                    time REAL,
                    compounds_per_year INTEGER,
                    tax_rate REAL,
                    fee_rate REAL,
                    amount REAL,
                    interest REAL,
                    target_date TEXT,
                    timestamp TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    principal REAL,
                    payment REAL,
                    payment_frequency TEXT,
                    rate REAL,
                    time REAL,
                    compounds_per_year INTEGER,
                    tax_rate REAL,
                    fee_rate REAL
                )
            """)
            conn.commit()

    def save_calculation(self, principal: float, payment: float, payment_frequency: str, 
                       rate: float, time: float, compounds_per_year: int, 
                       tax_rate: float, fee_rate: float, amount: float, interest: float, 
                       target_date: str = None):
        """Save a calculation to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO calculations (principal, payment, payment_frequency, rate, time, 
                                        compounds_per_year, tax_rate, fee_rate, amount, interest, 
                                        target_date, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (principal, payment, payment_frequency, rate, time, compounds_per_year, 
                  tax_rate, fee_rate, amount, interest, target_date, datetime.now().isoformat()))
            conn.commit()

    def save_template(self, name: str, principal: float, payment: float, payment_frequency: str, 
                    rate: float, time: float, compounds_per_year: int, 
                    tax_rate: float, fee_rate: float):
        """Save a template to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO templates (name, principal, payment, payment_frequency, rate, time, 
                                     compounds_per_year, tax_rate, fee_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, principal, payment, payment_frequency, rate, time, compounds_per_year, 
                  tax_rate, fee_rate))
            conn.commit()

    def get_templates(self) -> List[Dict]:
        """Retrieve all templates."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM templates")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_history(self) -> List[Dict]:
        """Retrieve calculation history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM calculations ORDER BY timestamp DESC")
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_notifications(self) -> List[Dict]:
        """Retrieve calculations with upcoming target dates."""
        today = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Fetch notifications for target dates from today up to 7 days from now
            cursor.execute("SELECT * FROM calculations WHERE target_date IS NOT NULL AND target_date >= ? AND target_date <= date(?, '+7 days')", 
                         (today, today))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def export_to_csv(self, file_path: str):
        """Export history to CSV."""
        history = self.get_history()
        if not history:
            print("No history to export.") # This print will be caught by UI
            return

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                # Write header
                header = ','.join(history[0].keys())
                f.write(header + '\n')
                # Write rows
                for row in history:
                    values = [str(v) if v is not None else '' for v in row.values()] # Handle None values
                    f.write(','.join(values) + '\n')
        except IOError as e:
            raise IOError(f"Could not write to file {file_path}: {e}")