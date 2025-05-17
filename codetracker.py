import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import csv
import matplotlib.pyplot as plt
from collections import Counter
import os

DB_FILE = "codetrackr.db"
CSV_FILE = "codetrackr_export.csv"
CHART_IMAGE = "status_chart.png"

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            platform TEXT,
            link TEXT,
            tags TEXT,
            difficulty TEXT,
            status TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def export_data_to_csv():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems")
    all_rows = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    conn.close()

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(all_rows)

    messagebox.showinfo("Exported", f"Data has been exported to '{CSV_FILE}'")

def show_status_chart():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM problems")
    statuses = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not statuses:
        messagebox.showinfo("No Data", "No data to display in chart.")
        return

    count = Counter(statuses)
    labels = list(count.keys())
    values = list(count.values())

    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=["skyblue", "lightgreen", "salmon"])
    plt.title("Problems by Status")
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(CHART_IMAGE)
    plt.close()

    if os.name == 'nt':
        os.startfile(CHART_IMAGE)
    else:
        os.system(f"open {CHART_IMAGE}")

class CodeTrackrApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CodeTrackr - CP Tracker")
        self.fields = ["Problem Name", "Platform", "Link", "Tags", "Difficulty", "Status", "Notes"]
        self.entries = {}

        for i, label in enumerate(self.fields):
            tk.Label(master, text=label).grid(row=i, column=0, padx=5, pady=2, sticky="e")
            entry = tk.Entry(master, width=50)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[label] = entry

        tk.Button(master, text="Add", command=self.save_problem).grid(row=8, column=0, pady=10)
        tk.Button(master, text="Show All", command=self.load_problems).grid(row=8, column=1, pady=10)
        tk.Button(master, text="Export to CSV", command=export_data_to_csv).grid(row=9, column=0)
        tk.Button(master, text="View Status Chart", command=show_status_chart).grid(row=9, column=1)

        self.tree = ttk.Treeview(master, columns=("Name", "Platform", "Tags", "Difficulty", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

    def save_problem(self):
        data = [self.entries[field].get() for field in self.fields]
        if not data[0]:
            messagebox.showerror("Error", "Problem Name is required.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO problems (name, platform, link, tags, difficulty, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        conn.close()

        for entry in self.entries.values():
            entry.delete(0, tk.END)

        messagebox.showinfo("Success", "Problem saved!")

    def load_problems(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, platform, tags, difficulty, status FROM problems")
        records = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in records:
            self.tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = CodeTrackrApp(root)
    root.mainloop()
