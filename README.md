# Expense-tracer2
#Adding my part (Page # 3)
class ViewExpensesPage(tk.Frame):
    def _init_(self, parent, controller):
        super()._init_(parent)
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
