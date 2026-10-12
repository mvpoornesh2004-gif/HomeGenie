import calendar
import datetime as date_module
import tkinter as tk
from tkinter import messagebox, ttk


TODAY = date_module.date.today().isoformat()


class HomeGenie(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HomeGenie - Household Management System")
        self.geometry("1180x760")
        self.minsize(1000, 650)
        self.configure(bg="#f4f7fb")

        self.categories = [
            "Education", "Entertainment", "Food", "Healthcare",
            "Maintenance", "Other", "Rent", "Shopping",
            "Transport", "Utilities"
        ]
        self.expenses = []
        self.bills = []
        self.subscriptions = []
        self.groceries = []
        self.maintenance = []
        self.budgets = []
        self.next_id = 1

        self.configure_styles()
        self.build_header()
        self.build_tabs()
        self.refresh_all()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def configure_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"),
                        foreground="#17324d", background="#f4f7fb")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10),
                        foreground="#547086", background="#f4f7fb")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", foreground="white",
                        background="#237a73", padding=7)
        style.map("Accent.TButton", background=[("active", "#185d58")])

    def build_header(self):
        header = ttk.Frame(self, padding=(22, 16))
        header.pack(fill="x")
        ttk.Label(header, text="HomeGenie", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="AI-powered household finances, bills, groceries and maintenance",
            style="Subtitle.TLabel"
        ).pack(anchor="w")

    def build_tabs(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.dashboard_tab = ttk.Frame(self.tabs, padding=14)
        self.expense_tab = ttk.Frame(self.tabs, padding=14)
        self.planning_tab = ttk.Frame(self.tabs, padding=14)
        self.report_tab = ttk.Frame(self.tabs, padding=14)
        self.ai_tab = ttk.Frame(self.tabs, padding=14)

        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.expense_tab, text="Expenses & Categories")
        self.tabs.add(self.planning_tab, text="Bills & Planning")
        self.tabs.add(self.report_tab, text="Reports & Analysis")
        self.tabs.add(self.ai_tab, text="Ask HomeGenie AI")

        self.build_dashboard()
        self.build_expenses()
        self.build_planning()
        self.build_reports()
        self.build_ai()

    def entry(self, parent, label, row, column, width=18, default=""):
        ttk.Label(parent, text=label).grid(
            row=row, column=column, sticky="w", padx=5, pady=4
        )
        widget = ttk.Entry(parent, width=width)
        widget.insert(0, default)
        widget.grid(row=row, column=column + 1, sticky="ew", padx=5, pady=4)
        return widget

    def tree(self, parent, columns, headings, widths):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=(8, 0))
        widget = ttk.Treeview(frame, columns=columns, show="headings")
        for column, heading, width in zip(columns, headings, widths):
            widget.heading(column, text=heading)
            widget.column(column, width=width, anchor="w")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=widget.yview)
        widget.configure(yscrollcommand=scroll.set)
        widget.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return widget

    def build_dashboard(self):
        summary = ttk.Frame(self.dashboard_tab)
        summary.pack(fill="x")
        self.summary_labels = {}
        cards = [
            ("expenses", "This Month's Expenses"),
            ("bills", "Pending Bills"),
            ("subscriptions", "Active Subscriptions"),
            ("budget", "Budget Usage"),
        ]
        for key, title in cards:
            card = ttk.LabelFrame(summary, text=title, padding=14)
            card.pack(side="left", fill="x", expand=True, padx=5)
            value = ttk.Label(card, text="0.00", font=("Segoe UI", 19, "bold"),
                              foreground="#237a73")
            value.pack(anchor="w")
            self.summary_labels[key] = value

        visual_area = ttk.Frame(self.dashboard_tab)
        visual_area.pack(fill="x", pady=(14, 10))
        chart_box = ttk.LabelFrame(
            visual_area, text="Overall Budget and Expense Usage", padding=8
        )
        chart_box.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.dashboard_chart = tk.Canvas(
            chart_box, height=245, bg="white", highlightthickness=0
        )
        self.dashboard_chart.pack(fill="both", expand=True)

        usage_box = ttk.LabelFrame(
            visual_area, text="Usage Summary", padding=12
        )
        usage_box.pack(side="right", fill="y", padx=(8, 0))
        self.usage_text = tk.Text(
            usage_box, width=32, height=13, wrap="word",
            state="disabled", font=("Segoe UI", 10), bg="white", relief="flat"
        )
        self.usage_text.pack(fill="both", expand=True)

        lower = ttk.Frame(self.dashboard_tab)
        lower.pack(fill="both", expand=True, pady=(18, 0))
        left = ttk.LabelFrame(lower, text="Recent Expenses", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.recent_tree = self.tree(
            left, ("date", "title", "category", "amount"),
            ("Date", "Description", "Category", "Amount"),
            (110, 220, 150, 100)
        )
        right = ttk.LabelFrame(lower, text="Household Alerts", padding=10)
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))
        self.alerts = tk.Text(right, state="disabled", wrap="word",
                              font=("Segoe UI", 10), bg="white", relief="flat")
        self.alerts.pack(fill="both", expand=True)

    def build_expenses(self):
        top = ttk.Frame(self.expense_tab)
        top.pack(fill="x")
        form = ttk.LabelFrame(top, text="Add Household Expense", padding=10)
        form.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.expense_title = self.entry(form, "Description", 0, 0, 20)
        self.expense_amount = self.entry(form, "Amount", 0, 2, 12)
        self.expense_date = self.entry(form, "Date", 0, 4, 12, TODAY)
        ttk.Label(form, text="Category").grid(row=1, column=0, sticky="w", padx=5)
        self.expense_category = ttk.Combobox(form, state="readonly", width=18)
        self.expense_category.grid(row=1, column=1, padx=5, pady=4)
        self.expense_notes = self.entry(form, "Notes", 1, 2, 20)
        self.expense_recurring = tk.BooleanVar()
        ttk.Checkbutton(form, text="Recurring",
                        variable=self.expense_recurring).grid(row=1, column=4)
        ttk.Button(form, text="Add Expense", style="Accent.TButton",
                   command=self.add_expense).grid(row=1, column=5, padx=5)

        category_box = ttk.LabelFrame(top, text="Manage Categories", padding=10)
        category_box.pack(side="right", fill="y")
        self.new_category = ttk.Entry(category_box, width=16)
        self.new_category.pack(side="left", padx=(0, 5))
        ttk.Button(category_box, text="Add",
                   command=self.add_category).pack(side="left")

        self.expense_tree = self.tree(
            self.expense_tab,
            ("id", "date", "title", "category", "amount", "recurring", "notes"),
            ("ID", "Date", "Description", "Category", "Amount", "Recurring", "Notes"),
            (45, 105, 220, 140, 90, 85, 260)
        )
        ttk.Button(self.expense_tab, text="Delete Selected Expense",
                   command=self.delete_expense).pack(anchor="e", pady=(8, 0))

    def build_planning(self):
        self.planning_tabs = ttk.Notebook(self.planning_tab)
        self.planning_tabs.pack(fill="both", expand=True)
        self.bill_page = ttk.Frame(self.planning_tabs, padding=10)
        self.subscription_page = ttk.Frame(self.planning_tabs, padding=10)
        self.grocery_page = ttk.Frame(self.planning_tabs, padding=10)
        self.maintenance_page = ttk.Frame(self.planning_tabs, padding=10)
        self.budget_page = ttk.Frame(self.planning_tabs, padding=10)
        pages = [
            (self.bill_page, "Bills"),
            (self.subscription_page, "Subscriptions"),
            (self.grocery_page, "Groceries"),
            (self.maintenance_page, "Maintenance"),
            (self.budget_page, "Budgets"),
        ]
        for page, title in pages:
            self.planning_tabs.add(page, text=title)
        self.build_bills()
        self.build_subscriptions()
        self.build_groceries()
        self.build_maintenance()
        self.build_budgets()

    def build_bills(self):
        form = ttk.LabelFrame(self.bill_page, text="Record Bill", padding=10)
        form.pack(fill="x")
        self.bill_name = self.entry(form, "Bill Name", 0, 0)
        self.bill_amount = self.entry(form, "Amount", 0, 2)
        self.bill_due = self.entry(form, "Due Date", 0, 4, 12, TODAY)
        ttk.Label(form, text="Status").grid(row=1, column=0, sticky="w", padx=5)
        self.bill_status = ttk.Combobox(
            form, values=("Pending", "Paid", "Overdue"),
            state="readonly", width=15
        )
        self.bill_status.set("Pending")
        self.bill_status.grid(row=1, column=1, padx=5, pady=4)
        self.bill_notes = self.entry(form, "Notes", 1, 2)
        ttk.Button(form, text="Save Bill", style="Accent.TButton",
                   command=self.add_bill).grid(row=1, column=5, padx=5)
        self.bill_tree = self.tree(
            self.bill_page, ("id", "name", "amount", "due", "status", "notes"),
            ("ID", "Bill", "Amount", "Due Date", "Status", "Notes"),
            (45, 220, 100, 110, 100, 280)
        )
        ttk.Button(self.bill_page, text="Mark Selected Bill as Paid",
                   command=self.mark_bill_paid).pack(anchor="e", pady=(8, 0))

    def build_subscriptions(self):
        form = ttk.LabelFrame(self.subscription_page, text="Manage Subscription",
                              padding=10)
        form.pack(fill="x")
        self.sub_name = self.entry(form, "Service", 0, 0)
        self.sub_amount = self.entry(form, "Amount", 0, 2)
        self.sub_next = self.entry(form, "Next Payment", 0, 4, 12, TODAY)
        ttk.Label(form, text="Billing Cycle").grid(row=1, column=0, padx=5)
        self.sub_cycle = ttk.Combobox(
            form, values=("Monthly", "Yearly", "Weekly"),
            state="readonly", width=15
        )
        self.sub_cycle.set("Monthly")
        self.sub_cycle.grid(row=1, column=1, padx=5, pady=4)
        ttk.Button(form, text="Add Subscription", style="Accent.TButton",
                   command=self.add_subscription).grid(row=1, column=5, padx=5)
        self.sub_tree = self.tree(
            self.subscription_page,
            ("id", "name", "amount", "cycle", "next", "active"),
            ("ID", "Service", "Amount", "Cycle", "Next Payment", "Active"),
            (45, 230, 100, 100, 130, 80)
        )
        ttk.Button(self.subscription_page, text="Toggle Selected Subscription",
                   command=self.toggle_subscription).pack(anchor="e", pady=(8, 0))

    def build_groceries(self):
        form = ttk.LabelFrame(self.grocery_page, text="Track Grocery Expense",
                              padding=10)
        form.pack(fill="x")
        self.grocery_item = self.entry(form, "Item", 0, 0)
        self.grocery_quantity = self.entry(form, "Quantity", 0, 2, 12, "1")
        self.grocery_cost = self.entry(form, "Estimated Cost", 0, 4, 12, "0")
        ttk.Button(form, text="Add Grocery Item", style="Accent.TButton",
                   command=self.add_grocery).grid(row=1, column=5, padx=5)
        self.grocery_tree = self.tree(
            self.grocery_page,
            ("id", "item", "quantity", "cost", "purchased"),
            ("ID", "Item", "Quantity", "Estimated Cost", "Purchased"),
            (45, 280, 120, 140, 100)
        )
        ttk.Button(self.grocery_page, text="Mark Selected Item Purchased",
                   command=self.mark_grocery).pack(anchor="e", pady=(8, 0))

    def build_maintenance(self):
        form = ttk.LabelFrame(self.maintenance_page,
                              text="Record Maintenance Activity", padding=10)
        form.pack(fill="x")
        self.maintenance_activity = self.entry(form, "Activity", 0, 0)
        self.maintenance_area = self.entry(form, "Area", 0, 2)
        self.maintenance_date = self.entry(form, "Date", 0, 4, 12, TODAY)
        self.maintenance_cost = self.entry(form, "Cost", 1, 0, 12, "0")
        ttk.Label(form, text="Status").grid(row=1, column=2, padx=5)
        self.maintenance_status = ttk.Combobox(
            form, values=("Planned", "In Progress", "Completed"),
            state="readonly", width=15
        )
        self.maintenance_status.set("Planned")
        self.maintenance_status.grid(row=1, column=3, padx=5, pady=4)
        self.maintenance_notes = self.entry(form, "Notes", 1, 4)
        ttk.Button(form, text="Save Activity", style="Accent.TButton",
                   command=self.add_maintenance).grid(row=1, column=7, padx=5)
        self.maintenance_tree = self.tree(
            self.maintenance_page,
            ("id", "activity", "area", "date", "cost", "status", "notes"),
            ("ID", "Activity", "Area", "Date", "Cost", "Status", "Notes"),
            (45, 220, 130, 110, 100, 110, 260)
        )

    def build_budgets(self):
        form = ttk.LabelFrame(self.budget_page, text="Set Household Budget",
                              padding=10)
        form.pack(fill="x")
        ttk.Label(form, text="Category").grid(row=0, column=0, padx=5)
        self.budget_category = ttk.Combobox(form, state="readonly", width=18)
        self.budget_category.grid(row=0, column=1, padx=5)
        self.budget_month = self.entry(form, "Month (YYYY-MM)", 0, 2, 12,
                                       TODAY[:7])
        self.budget_limit = self.entry(form, "Limit", 0, 4, 12)
        ttk.Button(form, text="Save Budget", style="Accent.TButton",
                   command=self.add_budget).grid(row=0, column=6, padx=5)
        self.budget_tree = self.tree(
            self.budget_page,
            ("id", "category", "month", "limit", "spent", "remaining"),
            ("ID", "Category", "Month", "Budget Limit", "Spent", "Remaining"),
            (45, 180, 110, 130, 110, 120)
        )

    def build_reports(self):
        controls = ttk.Frame(self.report_tab)
        controls.pack(fill="x")
        ttk.Label(controls, text="Report month (YYYY-MM):").pack(side="left")
        self.report_month = ttk.Entry(controls, width=12)
        self.report_month.insert(0, TODAY[:7])
        self.report_month.pack(side="left", padx=8)
        ttk.Button(controls, text="Generate Monthly Report",
                   style="Accent.TButton",
                   command=self.generate_report).pack(side="left")
        ttk.Button(controls, text="Analyze Categories",
                   command=self.analyze_categories).pack(side="left", padx=8)
        self.report_text = tk.Text(
            self.report_tab, wrap="word", font=("Consolas", 10),
            bg="white", relief="solid", borderwidth=1
        )
        self.report_text.pack(fill="both", expand=True, pady=(12, 0))

    def build_ai(self):
        ttk.Label(
            self.ai_tab,
            text="Ask about expenses, categories, bills, subscriptions, groceries, "
                 "budgets or maintenance."
        ).pack(anchor="w", pady=(0, 10))
        self.question = ttk.Entry(self.ai_tab, font=("Segoe UI", 12))
        self.question.pack(fill="x", ipady=5)
        ttk.Button(self.ai_tab, text="Ask HomeGenie",
                   style="Accent.TButton", command=self.answer_question).pack(
                       anchor="e", pady=8
                   )
        self.answer = tk.Text(self.ai_tab, wrap="word", font=("Segoe UI", 11),
                              bg="white", relief="solid", borderwidth=1)
        self.answer.pack(fill="both", expand=True)

    def amount(self, widget, label):
        try:
            value = float(widget.get().strip())
            if value < 0:
                raise ValueError
            return value
        except ValueError:
            messagebox.showerror("Invalid value",
                                 label + " must be a non-negative number.")
            return None

    def text(self, widget, label):
        value = widget.get().strip()
        if not value:
            messagebox.showerror("Missing value", label + " is required.")
            return None
        return value

    def new_id(self):
        value = self.next_id
        self.next_id += 1
        return value

    def selected_id(self, tree_widget):
        selected = tree_widget.selection()
        if not selected:
            messagebox.showinfo("Select a record", "Select a record first.")
            return None
        return int(tree_widget.item(selected[0], "values")[0])

    def add_category(self):
        value = self.text(self.new_category, "Category name")
        if not value:
            return
        if value in self.categories:
            messagebox.showerror("Duplicate category", "That category already exists.")
            return
        self.categories.append(value)
        self.categories.sort()
        self.new_category.delete(0, "end")
        self.refresh_all()

    def add_expense(self):
        title = self.text(self.expense_title, "Description")
        amount = self.amount(self.expense_amount, "Amount")
        expense_date = self.text(self.expense_date, "Date")
        if not title or amount is None or not expense_date:
            return
        self.expenses.append({
            "id": self.new_id(), "title": title, "amount": amount,
            "category": self.expense_category.get(),
            "date": expense_date, "notes": self.expense_notes.get().strip(),
            "recurring": self.expense_recurring.get()
        })
        self.expense_title.delete(0, "end")
        self.expense_amount.delete(0, "end")
        self.expense_notes.delete(0, "end")
        self.refresh_all()

    def delete_expense(self):
        record_id = self.selected_id(self.expense_tree)
        if record_id is not None:
            self.expenses = [item for item in self.expenses
                             if item["id"] != record_id]
            self.refresh_all()

    def add_bill(self):
        name = self.text(self.bill_name, "Bill name")
        amount = self.amount(self.bill_amount, "Amount")
        due = self.text(self.bill_due, "Due date")
        if not name or amount is None or not due:
            return
        self.bills.append({
            "id": self.new_id(), "name": name, "amount": amount,
            "due": due, "status": self.bill_status.get(),
            "notes": self.bill_notes.get().strip()
        })
        self.bill_name.delete(0, "end")
        self.bill_amount.delete(0, "end")
        self.bill_notes.delete(0, "end")
        self.refresh_all()

    def mark_bill_paid(self):
        record_id = self.selected_id(self.bill_tree)
        if record_id is not None:
            for item in self.bills:
                if item["id"] == record_id:
                    item["status"] = "Paid"
            self.refresh_all()

    def add_subscription(self):
        name = self.text(self.sub_name, "Service name")
        amount = self.amount(self.sub_amount, "Amount")
        next_payment = self.text(self.sub_next, "Next payment date")
        if not name or amount is None or not next_payment:
            return
        self.subscriptions.append({
            "id": self.new_id(), "name": name, "amount": amount,
            "cycle": self.sub_cycle.get(), "next": next_payment, "active": True
        })
        self.sub_name.delete(0, "end")
        self.sub_amount.delete(0, "end")
        self.refresh_all()

    def toggle_subscription(self):
        record_id = self.selected_id(self.sub_tree)
        if record_id is not None:
            for item in self.subscriptions:
                if item["id"] == record_id:
                    item["active"] = not item["active"]
            self.refresh_all()

    def add_grocery(self):
        item = self.text(self.grocery_item, "Item")
        cost = self.amount(self.grocery_cost, "Estimated cost")
        if not item or cost is None:
            return
        self.groceries.append({
            "id": self.new_id(), "item": item,
            "quantity": self.grocery_quantity.get().strip() or "1",
            "cost": cost, "purchased": False
        })
        self.grocery_item.delete(0, "end")
        self.grocery_cost.delete(0, "end")
        self.refresh_all()

    def mark_grocery(self):
        record_id = self.selected_id(self.grocery_tree)
        if record_id is not None:
            for item in self.groceries:
                if item["id"] == record_id:
                    item["purchased"] = not item["purchased"]
            self.refresh_all()

    def add_maintenance(self):
        activity = self.text(self.maintenance_activity, "Activity")
        area = self.text(self.maintenance_area, "Area")
        activity_date = self.text(self.maintenance_date, "Date")
        cost = self.amount(self.maintenance_cost, "Cost")
        if not activity or not area or not activity_date or cost is None:
            return
        self.maintenance.append({
            "id": self.new_id(), "activity": activity, "area": area,
            "date": activity_date, "cost": cost,
            "status": self.maintenance_status.get(),
            "notes": self.maintenance_notes.get().strip()
        })
        self.maintenance_activity.delete(0, "end")
        self.maintenance_area.delete(0, "end")
        self.maintenance_cost.delete(0, "end")
        self.maintenance_notes.delete(0, "end")
        self.refresh_all()

    def add_budget(self):
        month = self.text(self.budget_month, "Budget month")
        limit = self.amount(self.budget_limit, "Budget limit")
        if not month or limit is None:
            return
        category = self.budget_category.get()
        for item in self.budgets:
            if item["month"] == month and item["category"] == category:
                item["limit"] = limit
                self.refresh_all()
                return
        self.budgets.append({
            "id": self.new_id(), "category": category,
            "month": month, "limit": limit
        })
        self.refresh_all()

    def month_expenses(self, month):
        return [item for item in self.expenses if item["date"][:7] == month]

    def spent_for_budget(self, category, month):
        return sum(item["amount"] for item in self.expenses
                   if item["category"] == category and item["date"][:7] == month)

    def fill(self, tree_widget, rows):
        for item in tree_widget.get_children():
            tree_widget.delete(item)
        for row in rows:
            tree_widget.insert("", "end", values=row)

    def refresh_categories(self):
        self.expense_category["values"] = self.categories
        self.budget_category["values"] = self.categories
        if not self.expense_category.get() and self.categories:
            self.expense_category.set(self.categories[0])
        if not self.budget_category.get() and self.categories:
            self.budget_category.set(self.categories[0])

    def refresh_all(self):
        self.refresh_categories()
        self.fill(self.expense_tree, [
            (item["id"], item["date"], item["title"], item["category"],
             f"{item['amount']:.2f}", "Yes" if item["recurring"] else "No",
             item["notes"])
            for item in sorted(self.expenses, key=lambda x: (x["date"], x["id"]),
                               reverse=True)
        ])
        self.fill(self.bill_tree, [
            (item["id"], item["name"], f"{item['amount']:.2f}", item["due"],
             item["status"], item["notes"])
            for item in sorted(self.bills, key=lambda x: x["due"])
        ])
        self.fill(self.sub_tree, [
            (item["id"], item["name"], f"{item['amount']:.2f}", item["cycle"],
             item["next"], "Yes" if item["active"] else "No")
            for item in sorted(self.subscriptions, key=lambda x: x["next"])
        ])
        self.fill(self.grocery_tree, [
            (item["id"], item["item"], item["quantity"], f"{item['cost']:.2f}",
             "Yes" if item["purchased"] else "No")
            for item in sorted(self.groceries, key=lambda x: x["purchased"])
        ])
        self.fill(self.maintenance_tree, [
            (item["id"], item["activity"], item["area"], item["date"],
             f"{item['cost']:.2f}", item["status"], item["notes"])
            for item in sorted(self.maintenance,
                               key=lambda x: (x["date"], x["id"]), reverse=True)
        ])
        self.fill(self.budget_tree, [
            (
                item["id"], item["category"], item["month"],
                f"{item['limit']:.2f}",
                f"{self.spent_for_budget(item['category'], item['month']):.2f}",
                f"{item['limit'] - self.spent_for_budget(item['category'], item['month']):.2f}"
            )
            for item in sorted(self.budgets, key=lambda x: x["month"], reverse=True)
        ])
        self.refresh_dashboard()

    def refresh_dashboard(self):
        month_items = self.month_expenses(TODAY[:7])
        month_total = sum(item["amount"] for item in month_items)
        pending_total = sum(item["amount"] for item in self.bills
                            if item["status"] != "Paid")
        active_count = sum(1 for item in self.subscriptions if item["active"])
        budget_total = sum(item["limit"] for item in self.budgets
                           if item["month"] == TODAY[:7])
        self.summary_labels["expenses"].configure(text=f"{month_total:,.2f}")
        self.summary_labels["bills"].configure(text=f"{pending_total:,.2f}")
        self.summary_labels["subscriptions"].configure(text=str(active_count))
        self.summary_labels["budget"].configure(
            text=f"{month_total:,.2f} / {budget_total:,.2f}"
            if budget_total else f"{month_total:,.2f}"
        )
        self.fill(self.recent_tree, [
            (item["date"], item["title"], item["category"],
             f"{item['amount']:.2f}")
            for item in sorted(self.expenses, key=lambda x: (x["date"], x["id"]),
                               reverse=True)[:12]
        ])
        alerts = []
        overdue = [item["name"] for item in self.bills
                   if item["status"] == "Pending" and item["due"] < TODAY]
        if overdue:
            alerts.append("Overdue bills: " + ", ".join(overdue))
        upcoming = [item for item in self.bills if item["status"] == "Pending"]
        if upcoming:
            upcoming.sort(key=lambda x: x["due"])
            alerts.append("Upcoming bills: " + "; ".join(
                f"{item['name']} ({item['due']})" for item in upcoming[:3]
            ))
        recurring_names = sorted({
            item["title"] for item in self.expenses if item["recurring"]
        })
        if recurring_names:
            alerts.append("Recurring expenses: " + ", ".join(recurring_names))
        if not alerts:
            alerts.append("No urgent alerts. Your household is up to date.")
        self.alerts.configure(state="normal")
        self.alerts.delete("1.0", "end")
        self.alerts.insert("1.0", "\n\n".join("- " + item for item in alerts))
        self.alerts.configure(state="disabled")
        self.draw_dashboard_chart(month_total, budget_total)

    def draw_dashboard_chart(self, month_total, budget_total):
        canvas = self.dashboard_chart
        canvas.delete("all")
        canvas.update_idletasks()
        width = max(canvas.winfo_width(), 620)
        height = max(canvas.winfo_height(), 245)
        left = 62
        right = width - 22
        top = 22
        bottom = height - 42

        category_budgets = {
            item["category"]: item["limit"]
            for item in self.budgets if item["month"] == TODAY[:7]
        }
        category_expenses = {}
        for item in self.month_expenses(TODAY[:7]):
            category_expenses[item["category"]] = (
                category_expenses.get(item["category"], 0) + item["amount"]
            )
        chart_categories = sorted(
            set(category_budgets) | set(category_expenses),
            key=lambda name: max(category_budgets.get(name, 0),
                                  category_expenses.get(name, 0)),
            reverse=True
        )[:7]

        if chart_categories:
            values = []
            for category in chart_categories:
                values.extend([
                    category_budgets.get(category, 0),
                    category_expenses.get(category, 0)
                ])
            chart_title = "Budget and Expense by Category"
        else:
            chart_categories = ["This Month"]
            values = [budget_total, month_total]
            chart_title = "Monthly Budget and Expense"

        maximum = max(values + [1])
        maximum *= 1.15
        canvas.create_text(
            left, 8, anchor="w", text=chart_title,
            font=("Segoe UI", 11, "bold"), fill="#17324d"
        )
        canvas.create_rectangle(
            left, top, right, bottom, outline="#dce5eb", fill="#fbfdfe"
        )
        canvas.create_text(
            right - 4, top - 7, anchor="e",
            text="Budget", fill="#2bb5a6", font=("Segoe UI", 9, "bold")
        )
        canvas.create_rectangle(right - 104, top - 13, right - 91, top - 1,
                                fill="#2bb5a6", outline="")
        canvas.create_text(
            right - 4, top + 12, anchor="e",
            text="Expenses", fill="#e3424b", font=("Segoe UI", 9, "bold")
        )
        canvas.create_rectangle(right - 104, top + 6, right - 91, top + 18,
                                fill="#e3424b", outline="")

        for tick in range(5):
            value = maximum * tick / 4
            y = bottom - (bottom - top - 12) * tick / 4
            canvas.create_line(left, y, right, y, fill="#e7eef2")
            canvas.create_text(
                left - 8, y, anchor="e",
                text=f"{value:,.0f}", font=("Segoe UI", 8), fill="#607786"
            )

        group_width = (right - left) / max(len(chart_categories), 1)
        bar_width = min(24, group_width / 3)
        for index, category in enumerate(chart_categories):
            center = left + group_width * (index + 0.5)
            if len(chart_categories) == 1 and category == "This Month":
                budget_value = budget_total
                expense_value = month_total
            else:
                budget_value = category_budgets.get(category, 0)
                expense_value = category_expenses.get(category, 0)
            for offset, value, color in (
                (-bar_width / 2, budget_value, "#2bb5a6"),
                (bar_width / 2, expense_value, "#e3424b"),
            ):
                bar_height = (bottom - top - 12) * value / maximum
                x1 = center + offset - bar_width / 2
                x2 = center + offset + bar_width / 2
                y1 = bottom - bar_height
                canvas.create_rectangle(x1, y1, x2, bottom,
                                        fill=color, outline="")
                if value:
                    canvas.create_text(
                        (x1 + x2) / 2, y1 - 5, text=f"{value:,.0f}",
                        font=("Segoe UI", 8), fill="#435967"
                    )
            label = category if len(category) <= 12 else category[:11] + "..."
            canvas.create_text(
                center, bottom + 18, text=label,
                font=("Segoe UI", 8), fill="#435967"
            )

        if budget_total:
            usage = month_total / budget_total * 100
            status = "Over budget" if usage > 100 else "Within budget"
            remaining = budget_total - month_total
            usage_lines = [
                f"Month: {TODAY[:7]}",
                f"Budget set: {budget_total:,.2f}",
                f"Expenses: {month_total:,.2f}",
                f"Usage: {usage:.1f}%",
                f"Remaining: {remaining:,.2f}",
                "",
                status,
            ]
        else:
            usage_lines = [
                f"Month: {TODAY[:7]}",
                f"Expenses: {month_total:,.2f}",
                "",
                "No monthly budget has been set.",
                "Add a budget to compare",
                "budget versus expenses.",
            ]
        self.usage_text.configure(state="normal")
        self.usage_text.delete("1.0", "end")
        self.usage_text.insert("1.0", "\n".join(usage_lines))
        self.usage_text.configure(state="disabled")

    def generate_report(self):
        month = self.report_month.get().strip()
        try:
            year, month_number = [int(value) for value in month.split("-")]
            if month_number < 1 or month_number > 12:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid month", "Use YYYY-MM format.")
            return
        items = self.month_expenses(month)
        category_totals = {}
        for item in items:
            category_totals[item["category"]] = (
                category_totals.get(item["category"], 0) + item["amount"]
            )
        last_day = calendar.monthrange(year, month_number)[1]
        bills = [item for item in self.bills
                 if item["due"] >= f"{month}-01" and
                 item["due"] <= f"{month}-{last_day:02d}"]
        grocery_total = sum(item["cost"] for item in self.groceries
                            if item["purchased"])
        lines = [
            f"HOMEGENIE MONTHLY REPORT - {month}",
            "=" * 50,
            f"Total expenses: {sum(item['amount'] for item in items):,.2f}",
            f"Number of expenses: {len(items)}",
            f"Bills due in period: {len(bills)}",
            f"Purchased grocery estimate: {grocery_total:,.2f}",
            "",
            "CATEGORY-WISE EXPENSES",
            "-" * 30
        ]
        if category_totals:
            lines.extend(
                f"{category:<22} {total:>10,.2f}"
                for category, total in sorted(category_totals.items(),
                                              key=lambda x: x[1], reverse=True)
            )
        else:
            lines.append("No expenses recorded for this month.")
        self.show_report("\n".join(lines))

    def analyze_categories(self):
        totals = {category: 0 for category in self.categories}
        counts = {category: 0 for category in self.categories}
        for item in self.expenses:
            totals[item["category"]] = totals.get(item["category"], 0) + item["amount"]
            counts[item["category"]] = counts.get(item["category"], 0) + 1
        total = sum(totals.values())
        lines = ["CATEGORY-WISE EXPENSE ANALYSIS", "=" * 45]
        for category, value in sorted(totals.items(), key=lambda x: x[1],
                                      reverse=True):
            percentage = value / total * 100 if total else 0
            lines.append(
                f"{category:<20} {value:>10,.2f} "
                f"({percentage:5.1f}%, {counts[category]} entries)"
            )
        self.show_report("\n".join(lines))

    def show_report(self, text):
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", text)
        self.tabs.select(self.report_tab)

    def answer_question(self):
        question = self.question.get().strip().lower()
        if not question:
            messagebox.showinfo("Ask a question", "Type a question first.")
            return
        month = TODAY[:7]
        if any(word in question for word in ("spent", "expense", "cost")):
            total = sum(item["amount"] for item in self.month_expenses(month))
            response = f"You recorded {total:,.2f} in expenses for {month}."
        elif "category" in question or "highest" in question or "most" in question:
            totals = {}
            for item in self.expenses:
                totals[item["category"]] = totals.get(item["category"], 0) + item["amount"]
            if totals:
                category = max(totals, key=totals.get)
                response = f"Your highest spending category is {category}: {totals[category]:,.2f}."
            else:
                response = "There are no expenses yet."
        elif "bill" in question:
            pending = [item for item in self.bills if item["status"] != "Paid"]
            response = ("Pending bills: " + "; ".join(
                f"{item['name']} ({item['amount']:,.2f}, due {item['due']})"
                for item in pending
            )) if pending else "There are no pending bills."
        elif "subscription" in question:
            active = [item for item in self.subscriptions if item["active"]]
            response = ("Active subscriptions: " + "; ".join(
                f"{item['name']} ({item['amount']:,.2f}/{item['cycle'].lower()})"
                for item in active
            )) if active else "There are no active subscriptions."
        elif "grocery" in question or "shopping" in question:
            items = [item for item in self.groceries if not item["purchased"]]
            response = (
                f"You have {len(items)} unpurchased grocery items, estimated at "
                f"{sum(item['cost'] for item in items):,.2f}."
            )
        elif "budget" in question:
            budget = sum(item["limit"] for item in self.budgets
                         if item["month"] == month)
            spent = sum(item["amount"] for item in self.month_expenses(month))
            response = f"For {month}, budget is {budget:,.2f} and spending is {spent:,.2f}."
        elif "maintenance" in question or "repair" in question:
            open_items = [item for item in self.maintenance
                          if item["status"] != "Completed"]
            response = ("Open maintenance: " + "; ".join(
                f"{item['activity']} ({item['area']}, {item['status']})"
                for item in open_items
            )) if open_items else "There are no open maintenance activities."
        else:
            response = (
                "Ask about expenses, categories, bills, subscriptions, groceries, "
                "budgets or maintenance."
            )
        self.answer.delete("1.0", "end")
        self.answer.insert("1.0", "HomeGenie AI\n\n" + response)


if __name__ == "__main__":
    app = HomeGenie()
    app.mainloop()
