import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
# Database setup
conn = sqlite3.connect('expenses.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount REAL,
                date TEXT
            )''')
conn.commit()


class ExpenseTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("600x500")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (HomePage, AddExpensePage, ViewExpensesPage, SummaryPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


# Page 1: Home
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="💰 Expense Tracker", font=("Helvetica", 20)).pack(pady=30)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="➕ Add Expense", command=lambda: controller.show_frame("AddExpensePage"),
                  width=20).grid(row=0, column=0, padx=10, pady=10)
        tk.Button(btn_frame, text="📋 View Expenses", command=lambda: controller.show_frame("ViewExpensesPage"),
                  width=20).grid(row=1, column=0, padx=10, pady=10)
        tk.Button(btn_frame, text="📊 Show Summary", command=lambda: controller.show_frame("SummaryPage"),
                  width=20).grid(row=2, column=0, padx=10, pady=10)


# Page 2: Add Expense
class AddExpensePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="➕ Add New Expense", font=("Helvetica", 18)).pack(pady=20)

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.date_var = tk.StringVar()

        # Category
        tk.Label(form_frame, text="Category:", anchor='w', width=20).grid(row=0, column=0, pady=5, sticky='e')
        tk.Entry(form_frame, textvariable=self.category_var, width=30).grid(row=0, column=1, pady=5)

        # Amount
        tk.Label(form_frame, text="Amount:", anchor='w', width=20).grid(row=1, column=0, pady=5, sticky='e')
        tk.Entry(form_frame, textvariable=self.amount_var, width=30).grid(row=1, column=1, pady=5)

        # Date
        tk.Label(form_frame, text="Date (YYYY-MM-DD):", anchor='w', width=20).grid(row=2, column=0, pady=5, sticky='e')
        tk.Entry(form_frame, textvariable=self.date_var, width=30).grid(row=2, column=1, pady=5)

        # Buttons
        tk.Button(self, text="💾 Save Expense", command=self.save_expense, width=20).pack(pady=10)
        tk.Button(self, text="⬅ Back", command=lambda: controller.show_frame("HomePage")).pack()

    def save_expense(self):
        category = self.category_var.get()
        amount = self.amount_var.get()
        date = self.date_var.get()

        if not category or not amount or not date:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        # Insert into DB
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (category, amount, date) VALUES (?, ?, ?)",
                  (category, amount, date))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Expense added successfully!")

        self.category_var.set("")
        self.amount_var.set("")
        self.date_var.set("")


# Page 3: View Expenses
class ViewExpensesPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="📋 All Expenses", font=("Helvetica", 18)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("ID", "Category", "Amount", "Date"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Date", text="Date")
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(self, text="🔄 Refresh", command=self.load_expenses).pack(pady=5)
        tk.Button(self, text="⬅ Back", command=lambda: controller.show_frame("HomePage")).pack()

    def load_expenses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT * FROM expenses")
        rows = c.fetchall()
        for row in rows:
            self.tree.insert('', tk.END, values=row)
        conn.close()


# Page 4: Summary Output Page
class SummaryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="📊 Expense Summary", font=("Helvetica", 18)).pack(pady=20)

        self.output_text = tk.Text(self, width=60, height=15)
        self.output_text.pack(pady=10)

        tk.Button(self, text="🔁 Generate Summary", command=self.generate_summary).pack(pady=5)
        tk.Button(self, text="⬅ Back", command=lambda: controller.show_frame("HomePage")).pack()

    def generate_summary(self):
        self.output_text.delete(1.0, tk.END)

        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()

        c.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        summary_data = c.fetchall()

        c.execute("SELECT SUM(amount) FROM expenses")
        total = c.fetchone()[0] or 0

        output = "Summary by Category:\n\n"
        for category, amount in summary_data:
            output += f"{category}: Rs. {amount:.2f}\n"

        output += f"\nTotal Spent: Rs. {total:.2f}"
        self.output_text.insert(tk.END, output)

        conn.close()


# Start the application
if __name__ == "__main__":
    app = ExpenseTrackerApp()
    app.mainloop()
