import tkinter as tk
from tkinter import messagebox
import os
import schedule
import time
import threading
from plyer import notification
import pyttsx3
from datetime import datetime

REMINDER_FILE = "reminders.txt"

# --- Load and Save Reminders ---
def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        return []   
    with open(REMINDER_FILE, "r") as file:
        return [line.strip() for line in file.readlines()]

def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as file:
        for reminder in reminders:
            file.write(reminder + "\n")

# --- Notification and Voice Alert ---
def notify(reminder):
    notification.notify(
        title="Daily Reminder",
        message=reminder,
        timeout=10  # seconds
    )
    engine = pyttsx3.init()
    engine.say(f"Reminder: {reminder}")
    engine.runAndWait()

def schedule_reminders():
    times = ["09:00", "14:00", "20:00"]  # 9 AM, 2 PM, 8 PM
    for reminder in reminders:
        for t in times:
            schedule.every().day.at(t).do(notify, reminder=reminder)
            print(f"Scheduled reminder '{reminder}' at {t}")

# --- Background scheduler loop ---
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- Add / Remove Reminders ---
def add_reminder():  # Fixed typo: 'ddef' -> 'def'
    text = entry.get().strip()
    if text:
        reminders.append(text)
        listbox.insert(tk.END, text)
        save_reminders(reminders)
        entry.delete(0, tk.END)
        for t in ["09:00", "14:00", "20:00"]:
            schedule.every().day.at(t).do(notify, reminder=text)

def remove_reminder():
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        reminder = listbox.get(index)
        if messagebox.askyesno("Confirm", f"Delete reminder: {reminder}?"):
            listbox.delete(index)
            reminders.remove(reminder)
            save_reminders(reminders)

# --- GUI Setup ---
root = tk.Tk()
root.title("Daily Smart Reminder")
root.geometry("400x450")

reminders = load_reminders()  # Ensure reminders is defined before use

listbox = tk.Listbox(root, font=("Arial", 12), width=40, height=10)
listbox.pack(pady=10)
for reminder in reminders:
    listbox.insert(tk.END, reminder)

entry = tk.Entry(root, font=("Arial", 12), width=30)
entry.pack(pady=5)

tk.Button(root, text="Add Reminder", command=add_reminder).pack(pady=2)
tk.Button(root, text="Remove Selected", command=remove_reminder).pack(pady=2)

tk.Label(root, text="(Reminders will alert daily at 9:00 AM, 2:00 PM, 8:00 PM)", fg="gray").pack(pady=5)

# --- Schedule reminders on startup ---
schedule_reminders()

# --- Start background thread for schedule ---
threading.Thread(target=run_schedule, daemon=True).start()

if __name__ == "__main__":
    try:
        root.mainloop()
    except Exception as e:
        print("Error:", e)
        print("Error:", e)
