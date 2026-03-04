import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")
        self.root.geometry("950x600")
        
        # Modern Color Palette
        self.bg_color = "#F5F7FA"     # Soft app background
        self.panel_color = "#FFFFFF"  # Pure white panels
        self.text_color = "#2D3748"   # Slate dark gray for text
        self.accent_color = "#4A5568" # Muted slate for buttons
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.running = False
        self.seconds_passed = 0
        self.current_category = None
        self.start_datetime = None
        
        # Database Setup
        self.conn = sqlite3.connect("tracker_v2.db")
        self.cursor = self.conn.cursor()
        self.setup_db()

        # UI Layout
        self.setup_styles()
        self.create_left_panel()
        self.create_right_panel()
        
        # Load initial tabs
        self.refresh_tabs()

    def setup_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories 
                            (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
                            (id INTEGER PRIMARY KEY, category_name TEXT, 
                            log_name TEXT, log_date TEXT, log_time TEXT, duration INTEGER)''')
        self.conn.commit()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') 
        
        # Base App Styling
        style.configure("TFrame", background=self.bg_color)
        
        # Notebook (Tabs) Styling
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#E2E8F0", foreground=self.text_color, 
                        padding=[20, 10], font=("Segoe UI", 10), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", self.panel_color)])
        
        # Table (Treeview) Styling
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=35, 
                        background=self.panel_color, fieldbackground=self.panel_color, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), 
                        background=self.panel_color, foreground="#A0AEC0", borderwidth=0)
        style.map("Treeview", background=[("selected", "#EDF2F7")], foreground=[("selected", self.text_color)])
        
        # Typography
        style.configure("Timer.TLabel", font=("Segoe UI", 46, "bold"), 
                        background=self.panel_color, foreground=self.text_color)

    def create_left_panel(self):
        # White card for the timer
        left_frame = tk.Frame(self.root, width=300, bg=self.panel_color)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)
        left_frame.pack_propagate(False)

        # Timer Display
        self.timer_label = ttk.Label(left_frame, text="00:00:00", style="Timer.TLabel")
        self.timer_label.pack(pady=(40, 50))

        # Start/Stop Button
        self.btn_toggle = tk.Button(left_frame, text="START", bg=self.accent_color, fg="#FFFFFF", 
                                    font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", command=self.toggle_timer)
        self.btn_toggle.pack(fill="x", padx=20, pady=10, ipady=12)

        # Reset Button
        self.btn_reset = tk.Button(left_frame, text="Reset Timer", bg=self.panel_color, fg="#718096", 
                                   font=("Segoe UI", 10), relief="flat", cursor="hand2", command=self.reset_timer)
        self.btn_reset.pack(fill="x", padx=20, pady=5)

        # Add Entry Button
        self.btn_add = tk.Button(left_frame, text="ADD ENTRY", bg="#E2E8F0", fg="#A0AEC0",
                                 font=("Segoe UI", 11, "bold"), relief="flat", state="disabled", command=self.save_log)
        self.btn_add.pack(fill="x", side="bottom", padx=20, pady=30, ipady=12)

    def create_right_panel(self):
        right_frame = tk.Frame(self.root, bg=self.bg_color)
        right_frame.pack(side="right", expand=True, fill="both", padx=(0, 20), pady=20)

        # Top Bar
        top_bar = tk.Frame(right_frame, bg=self.bg_color)
        top_bar.pack(fill="x", pady=(0, 15))

        btn_new_cat = tk.Button(top_bar, text="+ New Category", bg=self.panel_color, fg=self.text_color, 
                                font=("Segoe UI", 10), relief="flat", cursor="hand2", command=self.add_category)
        btn_new_cat.pack(side="right", ipady=6, ipadx=15)

        # Notebook for Tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(expand=True, fill="both")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def toggle_timer(self):
        if not self.running:
            self.running = True
            if not self.start_datetime or self.seconds_passed == 0:
                self.start_datetime = datetime.now()
            self.btn_toggle.config(text="STOP", bg="#E2E8F0", fg=self.text_color)
            self.update_clock()
        else:
            self.running = False
            self.btn_toggle.config(text="RESUME", bg=self.accent_color, fg="#FFFFFF")
            if self.seconds_passed > 0:
                self.btn_add.config(state="normal", bg=self.text_color, fg="#FFFFFF", cursor="hand2")

    def update_clock(self):
        if self.running:
            self.seconds_passed += 1
            self.display_time()
            self.root.after(1000, self.update_clock)
            
    def display_time(self):
        h, m = divmod(self.seconds_passed, 3600)
        m, s = divmod(m, 60)
        self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")

    def reset_timer(self):
        self.running = False
        self.seconds_passed = 0
        self.start_datetime = None
        self.display_time()
        self.btn_toggle.config(text="START", bg=self.accent_color, fg="#FFFFFF")
        self.btn_add.config(state="disabled", bg="#E2E8F0", fg="#A0AEC0", cursor="arrow")

    def add_category(self):
        name = simpledialog.askstring("New Category", "Enter category name:")
        if name and name.strip():
            try:
                self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name.strip(),))
                self.conn.commit()
                self.refresh_tabs()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Category already exists.")

    def refresh_tabs(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        self.cursor.execute("SELECT name FROM categories")
        categories = self.cursor.fetchall()
        
        for (name,) in categories:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f" {name} ")
            
            # Treeview Table
            cols = ("ID", "Name", "Date", "Time", "Duration")
            tree = ttk.Treeview(frame, columns=cols, show="headings")
            
            tree.heading("ID", text="ID")
            tree.heading("Name", text="NAME")
            tree.heading("Date", text="DATE")
            tree.heading("Time", text="TIME")
            tree.heading("Duration", text="DURATION")
            
            tree.column("ID", width=0, stretch=tk.NO) 
            tree.column("Name", width=250, anchor="w")
            tree.column("Date", width=120, anchor="center")
            tree.column("Time", width=120, anchor="center")
            tree.column("Duration", width=120, anchor="center")
            
            tree.pack(expand=True, fill="both")
            tree.bind("<Double-1>", self.on_row_double_click)
            
            self.cursor.execute("SELECT id, log_name, log_date, log_time, duration FROM logs WHERE category_name=? ORDER BY id DESC", (name,))
            for log in self.cursor.fetchall():
                log_id, log_name, log_date, log_time, duration_sec = log
                h, m = divmod(duration_sec, 3600)
                m, s = divmod(m, 60)
                duration_str = f"{h:02d}:{m:02d}:{s:02d}"
                tree.insert("", "end", values=(log_id, log_name, log_date, log_time, duration_str))

    def on_tab_change(self, event):
        selected_id = self.notebook.select()
        if selected_id:
            self.current_category = self.notebook.tab(selected_id, "text").strip()

    def save_log(self):
        if not self.current_category:
            messagebox.showwarning("Warning", "Please create and select a category tab first.")
            return
        
        log_date = self.start_datetime.strftime("%m/%d/%Y")
        log_time = self.start_datetime.strftime("%I:%M %p")
        log_name = "Untitled Task"
        
        self.cursor.execute("INSERT INTO logs (category_name, log_name, log_date, log_time, duration) VALUES (?, ?, ?, ?, ?)",
                            (self.current_category, log_name, log_date, log_time, self.seconds_passed))
        self.conn.commit()
        self.reset_timer()
        self.refresh_tabs()

    def on_row_double_click(self, event):
        tree = event.widget
        selected = tree.selection()
        if not selected:
            return
            
        item = tree.item(selected[0])
        values = item['values']
        log_id = values[0]
        current_name = values[1]
        
        new_name = simpledialog.askstring("Rename Entry", "Update task name:", initialvalue=current_name)
        
        if new_name and new_name.strip():
            self.cursor.execute("UPDATE logs SET log_name = ? WHERE id = ?", (new_name.strip(), log_id))
            self.conn.commit()
            self.refresh_tabs()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")
        self.root.geometry("950x600")
        
        # Modern Color Palette
        self.bg_color = "#F5F7FA"     # Soft app background
        self.panel_color = "#FFFFFF"  # Pure white panels
        self.text_color = "#2D3748"   # Slate dark gray for text
        self.accent_color = "#4A5568" # Muted slate for buttons
        
        self.root.configure(bg=self.bg_color)
        
        # Variables
        self.running = False
        self.seconds_passed = 0
        self.current_category = None
        self.start_datetime = None
        
        # Database Setup
        self.conn = sqlite3.connect("tracker_v2.db")
        self.cursor = self.conn.cursor()
        self.setup_db()

        # UI Layout
        self.setup_styles()
        self.create_left_panel()
        self.create_right_panel()
        
        # Load initial tabs
        self.refresh_tabs()

    def setup_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories 
                            (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
                            (id INTEGER PRIMARY KEY, category_name TEXT, 
                            log_name TEXT, log_date TEXT, log_time TEXT, duration INTEGER)''')
        self.conn.commit()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam') 
        
        # Base App Styling
        style.configure("TFrame", background=self.bg_color)
        
        # Notebook (Tabs) Styling
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#E2E8F0", foreground=self.text_color, 
                        padding=[20, 10], font=("Segoe UI", 10), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", self.panel_color)])
        
        # Table (Treeview) Styling
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=35, 
                        background=self.panel_color, fieldbackground=self.panel_color, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), 
                        background=self.panel_color, foreground="#A0AEC0", borderwidth=0)
        style.map("Treeview", background=[("selected", "#EDF2F7")], foreground=[("selected", self.text_color)])
        
        # Typography
        style.configure("Timer.TLabel", font=("Segoe UI", 46, "bold"), 
                        background=self.panel_color, foreground=self.text_color)

    def create_left_panel(self):
        # White card for the timer
        left_frame = tk.Frame(self.root, width=300, bg=self.panel_color)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)
        left_frame.pack_propagate(False)

        # Timer Display
        self.timer_label = ttk.Label(left_frame, text="00:00:00", style="Timer.TLabel")
        self.timer_label.pack(pady=(40, 50))

        # Start/Stop Button
        self.btn_toggle = tk.Button(left_frame, text="START", bg=self.accent_color, fg="#FFFFFF", 
                                    font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", command=self.toggle_timer)
        self.btn_toggle.pack(fill="x", padx=20, pady=10, ipady=12)

        # Reset Button
        self.btn_reset = tk.Button(left_frame, text="Reset Timer", bg=self.panel_color, fg="#718096", 
                                   font=("Segoe UI", 10), relief="flat", cursor="hand2", command=self.reset_timer)
        self.btn_reset.pack(fill="x", padx=20, pady=5)

        # Add Entry Button
        self.btn_add = tk.Button(left_frame, text="ADD ENTRY", bg="#E2E8F0", fg="#A0AEC0",
                                 font=("Segoe UI", 11, "bold"), relief="flat", state="disabled", command=self.save_log)
        self.btn_add.pack(fill="x", side="bottom", padx=20, pady=30, ipady=12)

    def create_right_panel(self):
        right_frame = tk.Frame(self.root, bg=self.bg_color)
        right_frame.pack(side="right", expand=True, fill="both", padx=(0, 20), pady=20)

        # Top Bar
        top_bar = tk.Frame(right_frame, bg=self.bg_color)
        top_bar.pack(fill="x", pady=(0, 15))

        btn_new_cat = tk.Button(top_bar, text="+ New Category", bg=self.panel_color, fg=self.text_color, 
                                font=("Segoe UI", 10), relief="flat", cursor="hand2", command=self.add_category)
        btn_new_cat.pack(side="right", ipady=6, ipadx=15)

        # Notebook for Tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(expand=True, fill="both")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def toggle_timer(self):
        if not self.running:
            self.running = True
            if not self.start_datetime or self.seconds_passed == 0:
                self.start_datetime = datetime.now()
            self.btn_toggle.config(text="STOP", bg="#E2E8F0", fg=self.text_color)
            self.update_clock()
        else:
            self.running = False
            self.btn_toggle.config(text="RESUME", bg=self.accent_color, fg="#FFFFFF")
            if self.seconds_passed > 0:
                self.btn_add.config(state="normal", bg=self.text_color, fg="#FFFFFF", cursor="hand2")

    def update_clock(self):
        if self.running:
            self.seconds_passed += 1
            self.display_time()
            self.root.after(1000, self.update_clock)
            
    def display_time(self):
        h, m = divmod(self.seconds_passed, 3600)
        m, s = divmod(m, 60)
        self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")

    def reset_timer(self):
        self.running = False
        self.seconds_passed = 0
        self.start_datetime = None
        self.display_time()
        self.btn_toggle.config(text="START", bg=self.accent_color, fg="#FFFFFF")
        self.btn_add.config(state="disabled", bg="#E2E8F0", fg="#A0AEC0", cursor="arrow")

    def add_category(self):
        name = simpledialog.askstring("New Category", "Enter category name:")
        if name and name.strip():
            try:
                self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name.strip(),))
                self.conn.commit()
                self.refresh_tabs()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Category already exists.")

    def refresh_tabs(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        
        self.cursor.execute("SELECT name FROM categories")
        categories = self.cursor.fetchall()
        
        for (name,) in categories:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=f" {name} ")
            
            # Treeview Table
            cols = ("ID", "Name", "Date", "Time", "Duration")
            tree = ttk.Treeview(frame, columns=cols, show="headings")
            
            tree.heading("ID", text="ID")
            tree.heading("Name", text="NAME")
            tree.heading("Date", text="DATE")
            tree.heading("Time", text="TIME")
            tree.heading("Duration", text="DURATION")
            
            tree.column("ID", width=0, stretch=tk.NO) 
            tree.column("Name", width=250, anchor="w")
            tree.column("Date", width=120, anchor="center")
            tree.column("Time", width=120, anchor="center")
            tree.column("Duration", width=120, anchor="center")
            
            tree.pack(expand=True, fill="both")
            tree.bind("<Double-1>", self.on_row_double_click)
            
            self.cursor.execute("SELECT id, log_name, log_date, log_time, duration FROM logs WHERE category_name=? ORDER BY id DESC", (name,))
            for log in self.cursor.fetchall():
                log_id, log_name, log_date, log_time, duration_sec = log
                h, m = divmod(duration_sec, 3600)
                m, s = divmod(m, 60)
                duration_str = f"{h:02d}:{m:02d}:{s:02d}"
                tree.insert("", "end", values=(log_id, log_name, log_date, log_time, duration_str))

    def on_tab_change(self, event):
        selected_id = self.notebook.select()
        if selected_id:
            self.current_category = self.notebook.tab(selected_id, "text").strip()

    def save_log(self):
        if not self.current_category:
            messagebox.showwarning("Warning", "Please create and select a category tab first.")
            return
        
        log_date = self.start_datetime.strftime("%m/%d/%Y")
        log_time = self.start_datetime.strftime("%I:%M %p")
        log_name = "Untitled Task"
        
        self.cursor.execute("INSERT INTO logs (category_name, log_name, log_date, log_time, duration) VALUES (?, ?, ?, ?, ?)",
                            (self.current_category, log_name, log_date, log_time, self.seconds_passed))
        self.conn.commit()
        self.reset_timer()
        self.refresh_tabs()

    def on_row_double_click(self, event):
        tree = event.widget
        selected = tree.selection()
        if not selected:
            return
            
        item = tree.item(selected[0])
        values = item['values']
        log_id = values[0]
        current_name = values[1]
        
        new_name = simpledialog.askstring("Rename Entry", "Update task name:", initialvalue=current_name)
        
        if new_name and new_name.strip():
            self.cursor.execute("UPDATE logs SET log_name = ? WHERE id = ?", (new_name.strip(), log_id))
            self.conn.commit()
            self.refresh_tabs()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()