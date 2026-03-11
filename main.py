import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime

class TimeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")
        self.root.geometry("950x600")
        
        # --- THEME CONFIGURATION ---
        self.bg_color = "#E8DCC4"      
        self.panel_color = "#F5EFE1"   
        self.text_color = "#2C1E1A"    
        self.accent_color = "#8B261D"  
        self.notebook_color = "#F0EDE2" 
        
        self.root.configure(bg=self.bg_color)
        
        # --- STATE VARIABLES ---
        self.running = False           
        self.seconds_passed = 0        
        self.current_category = None   
        self.start_datetime = None     
        
        # --- DATABASE INITIALIZATION ---
        self.conn = sqlite3.connect("tracker_v2.db")
        self.cursor = self.conn.cursor()
        self.setup_db()

        # --- UI CONSTRUCTION ---
        self.setup_styles()            
        self.create_left_panel()       
        self.create_right_panel()      
        self.create_context_menu()     
        
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
        
        style.configure("TFrame", background=self.bg_color)
        
        style.configure("TNotebook", 
                        background=self.bg_color, 
                        borderwidth=0, 
                        tabmargins=[2, 5, 2, 0])

        # Tab Styling: Inactive tabs now match the main app background
        style.configure("TNotebook.Tab", 
                        background=self.bg_color, 
                        foreground=self.text_color, 
                        padding=[30, 8], 
                        font=("Segoe UI", 10), 
                        borderwidth=0, 
                        focuscolor="",
                        shiftrelief=0)
        
        # Tab Selection: Active tab gets the panel color and red text
        style.map("TNotebook.Tab", 
                  background=[("selected", self.panel_color)],
                  foreground=[("selected", self.accent_color)], 
                  padding=[("selected", [30, 8]), ("!selected", [30, 8])],
                  expand=[("selected", 0), ("!selected", 0)]) 
        
        style.configure("Treeview", 
                        font=("Segoe UI", 10), 
                        rowheight=35, 
                        background=self.panel_color, 
                        fieldbackground=self.panel_color, 
                        foreground=self.text_color,
                        borderwidth=0)
        
        style.configure("Treeview.Heading", 
                        font=("Segoe UI", 10, "bold"), 
                        background=self.notebook_color, 
                        foreground=self.text_color, 
                        borderwidth=0, 
                        relief="flat")
        
        style.map("Treeview", 
                  background=[("selected", self.accent_color)], 
                  foreground=[("selected", self.panel_color)])
        
        style.configure("Timer.TLabel", 
                        font=("Segoe UI", 46, "bold"), 
                        background=self.panel_color, 
                        foreground=self.text_color)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0, bg=self.panel_color, fg=self.text_color)
        self.context_menu.add_command(label="Edit Task Name", command=self.edit_selected_row)
        self.context_menu.add_command(label="Delete Entry", command=self.delete_selected_row)

    def show_context_menu(self, event):
        item = event.widget.identify_row(event.y)
        if item:
            event.widget.selection_set(item) 
            self.context_menu.post(event.x_root, event.y_root)

    def create_left_panel(self):
        left_frame = tk.Frame(self.root, width=300, bg=self.panel_color)
        left_frame.pack(side="left", fill="y", padx=20, pady=20)
        left_frame.pack_propagate(False) 

        self.timer_label = ttk.Label(left_frame, text="00:00:00", style="Timer.TLabel")
        self.timer_label.pack(pady=(40, 50))

        self.btn_toggle = tk.Button(left_frame, text="START", bg=self.accent_color, fg=self.panel_color, 
                                    font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", command=self.toggle_timer)
        self.btn_toggle.pack(fill="x", padx=20, pady=10, ipady=12)

        self.btn_reset = tk.Button(left_frame, text="Reset Timer", bg=self.panel_color, fg=self.text_color, 
                                   font=("Segoe UI", 10), relief="flat", cursor="hand2", command=self.reset_timer)
        self.btn_reset.pack(fill="x", padx=20, pady=5)

        self.btn_add = tk.Button(left_frame, text="ADD ENTRY", bg=self.notebook_color, fg=self.text_color,
                                 font=("Segoe UI", 11, "bold"), relief="flat", state="disabled", command=self.save_log)
        self.btn_add.pack(fill="x", side="bottom", padx=20, pady=30, ipady=12)

    def create_right_panel(self):
        right_frame = tk.Frame(self.root, bg=self.bg_color)
        right_frame.pack(side="right", expand=True, fill="both", padx=(0, 20), pady=20)

        top_bar = tk.Frame(right_frame, bg=self.bg_color)
        top_bar.pack(fill="x", pady=(0, 15))

        btn_new_cat = tk.Button(top_bar, text="+ New Category", bg=self.panel_color, fg=self.text_color, 
                                font=("Segoe UI", 10), relief="flat", cursor="hand2", command=self.add_category)
        btn_new_cat.pack(side="right", ipady=6, ipadx=15)

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(expand=True, fill="both")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def toggle_timer(self):
        if not self.running:
            self.running = True
            if not self.start_datetime or self.seconds_passed == 0:
                self.start_datetime = datetime.now()
            self.btn_toggle.config(text="STOP", bg=self.notebook_color, fg=self.text_color)
            self.update_clock()
        else:
            self.running = False
            self.btn_toggle.config(text="RESUME", bg=self.accent_color, fg=self.panel_color)
            if self.seconds_passed > 0:
                self.btn_add.config(state="normal", bg=self.text_color, fg=self.panel_color, cursor="hand2")

    def update_clock(self):
        if self.running:
            self.seconds_passed += 1
            h, m = divmod(self.seconds_passed, 3600)
            m, s = divmod(m, 60)
            self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
            self.root.after(1000, self.update_clock)
            
    def reset_timer(self):
        self.running = False
        self.seconds_passed = 0
        self.start_datetime = None
        self.timer_label.config(text="00:00:00")
        self.btn_toggle.config(text="START", bg=self.accent_color, fg=self.panel_color)
        self.btn_add.config(state="disabled", bg=self.notebook_color, fg=self.text_color, cursor="arrow")

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
            
            cols = ("ID", "Name", "Date", "Time", "Duration")
            tree = ttk.Treeview(frame, columns=cols, show="headings")
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, anchor="center")
            
            tree.column("ID", width=0, stretch=tk.NO) 
            tree.column("Name", width=250, anchor="w")
            
            tree.pack(expand=True, fill="both")
            
            tree.bind("<Double-1>", self.on_row_double_click) 
            tree.bind("<Button-3>", self.show_context_menu)   
            tree.bind("<Button-2>", self.show_context_menu)   
            
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
            messagebox.showwarning("Warning", "Select a category tab first.")
            return
        log_date = self.start_datetime.strftime("%m/%d/%Y")
        log_time = self.start_datetime.strftime("%I:%M %p")
        self.cursor.execute("INSERT INTO logs (category_name, log_name, log_date, log_time, duration) VALUES (?, ?, ?, ?, ?)",
                            (self.current_category, "New Task", log_date, log_time, self.seconds_passed))
        self.conn.commit()
        self.reset_timer()
        self.refresh_tabs()

    def edit_selected_row(self):
        selected_tab = self.notebook.nametowidget(self.notebook.select())
        tree = selected_tab.winfo_children()[0] 
        selected = tree.selection()
        if not selected: return
        
        log_id, current_name = tree.item(selected[0])['values'][0:2]
        new_name = simpledialog.askstring("Edit", "Update task name:", initialvalue=current_name)
        
        if new_name:
            self.cursor.execute("UPDATE logs SET log_name = ? WHERE id = ?", (new_name.strip(), log_id))
            self.conn.commit()
            self.refresh_tabs()

    def delete_selected_row(self):
        selected_tab = self.notebook.nametowidget(self.notebook.select())
        tree = selected_tab.winfo_children()[0]
        selected = tree.selection()
        if not selected: return
        
        log_id = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            self.cursor.execute("DELETE FROM logs WHERE id = ?", (log_id,))
            self.conn.commit()
            self.refresh_tabs()

    def on_row_double_click(self, event):
        self.edit_selected_row()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)
    root.mainloop()