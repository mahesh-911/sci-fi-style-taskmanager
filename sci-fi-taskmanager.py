import tkinter as tk
from tkinter import ttk, font
import psutil
import time
import math
import pygame
import threading
import socket
import platform
from ctypes import windll, byref, sizeof, c_int
import winsound
from PIL import Image, ImageTk
import sys

# Initialize pygame for voice alerts
pygame.mixer.init()

class SciFiTaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("NEO-TASK // SYSTEM MONITOR")
        
        # Make window transparent
        self.root.attributes('-transparentcolor', '#2a2a2a')
        self.root.config(bg='#2a2a2a')
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Set window to stay on top
        self.root.attributes('-topmost', True)
        
        # Make window draggable
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.on_move)
        
        # Sci-fi colors
        self.bg_color = '#0a0a12'
        self.text_color = '#00ffcc'
        self.highlight_color = '#ff00ff'
        self.warning_color = '#ff5555'
        self.network_color = '#00aaff'
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg=self.bg_color, bd=0, highlightthickness=0)
        self.main_frame.pack(padx=0, pady=0)
        
        # Header
        self.header = tk.Label(self.main_frame, 
                              text="≡ NEO-TASK v2.4.7 ≡", 
                              font=('Courier New', 12, 'bold'),
                              fg=self.highlight_color,
                              bg=self.bg_color)
        self.header.grid(row=0, column=0, columnspan=3, pady=(5, 10), sticky='ew')
        
        # Close button
        self.close_btn = tk.Label(self.main_frame, text="✕", font=('Arial', 10), 
                                fg=self.text_color, bg=self.bg_color, cursor="hand2")
        self.close_btn.grid(row=0, column=2, sticky='e', padx=5)
        self.close_btn.bind("<Button-1>", lambda e: sys.exit())
        
        # CPU Section
        self.cpu_label = self.create_section_label("CPU CORE STATUS")
        self.cpu_label.grid(row=1, column=0, sticky='w', padx=10, pady=(0, 5))
        
        self.cpu_bars = []
        for i in range(psutil.cpu_count()):
            frame = tk.Frame(self.main_frame, bg=self.bg_color)
            frame.grid(row=2+i, column=0, sticky='ew', padx=10, pady=2)
            
            label = tk.Label(frame, text=f"CORE {i+1}:", width=7, anchor='w',
                            font=('Courier New', 8), fg=self.text_color, bg=self.bg_color)
            label.pack(side='left')
            
            canvas = tk.Canvas(frame, height=15, width=150, bg=self.bg_color, 
                             highlightthickness=0)
            canvas.pack(side='left', padx=5)
            self.cpu_bars.append(canvas)
        
        # Memory Section
        self.mem_label = self.create_section_label("MEMORY ALLOCATION")
        self.mem_label.grid(row=1, column=1, sticky='w', padx=10, pady=(0, 5))
        
        self.ram_bar = self.create_progress_bar(2, 1, "RAM:")
        self.swap_bar = self.create_progress_bar(3, 1, "SWAP:")
        
        # Network Section
        self.net_label = self.create_section_label("NETWORK STREAM")
        self.net_label.grid(row=1, column=2, sticky='w', padx=10, pady=(0, 5))
        
        self.net_up_label = tk.Label(self.main_frame, text="UP: 0.0 KB/s", 
                                   font=('Courier New', 8), fg=self.network_color, 
                                   bg=self.bg_color)
        self.net_up_label.grid(row=2, column=2, sticky='w', padx=10, pady=2)
        
        self.net_down_label = tk.Label(self.main_frame, text="DOWN: 0.0 KB/s", 
                                     font=('Courier New', 8), fg=self.network_color, 
                                     bg=self.bg_color)
        self.net_down_label.grid(row=3, column=2, sticky='w', padx=10, pady=2)
        
        # System Info
        self.sys_label = self.create_section_label("SYSTEM SPECS")
        self.sys_label.grid(row=4, column=0, columnspan=3, sticky='w', padx=10, pady=(15, 5))
        
        self.sys_info = tk.Label(self.main_frame, 
                                text=self.get_system_info(),
                                font=('Courier New', 8),
                                fg=self.text_color,
                                bg=self.bg_color,
                                justify='left')
        self.sys_info.grid(row=5, column=0, columnspan=3, sticky='w', padx=10, pady=(0, 10))
        
        # Process Table
        self.proc_label = self.create_section_label("ACTIVE PROCESSES")
        self.proc_label.grid(row=6, column=0, columnspan=3, sticky='w', padx=10, pady=(5, 5))
        
        self.tree = ttk.Treeview(self.main_frame, columns=('PID', 'Name', 'CPU', 'Memory'), 
                                show='headings', height=5)
        self.tree.grid(row=7, column=0, columnspan=3, padx=10, pady=(0, 10))
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                       background="#111122", 
                       foreground=self.text_color,
                       fieldbackground="#111122",
                       rowheight=20)
        style.configure("Treeview.Heading", 
                       background="#222233", 
                       foreground=self.highlight_color,
                       font=('Courier New', 8, 'bold'))
        style.map('Treeview', background=[('selected', '#333344')])
        
        self.tree.heading('PID', text='PID')
        self.tree.heading('Name', text='NAME')
        self.tree.heading('CPU', text='CPU%')
        self.tree.heading('Memory', text='MEM%')
        
        self.tree.column('PID', width=60, anchor='center')
        self.tree.column('Name', width=150, anchor='w')
        self.tree.column('CPU', width=60, anchor='center')
        self.tree.column('Memory', width=60, anchor='center')
        
        # Initialize network stats
        self.last_net_io = psutil.net_io_counters()
        self.last_time = time.time()
        
        # Start updates
        self.update_interval = 2000  # ms
        self.update_stats()
        self.update_processes()
        
        # Voice alert variables
        self.cpu_alert_triggered = False
        self.voice_thread = None
        
        # Add some sci-fi effects
        self.create_scan_lines()
        self.create_corner_brackets()
        
        # Blinking effect for header
        self.blink_state = True
        self.blink_header()
    
    def create_section_label(self, text):
        return tk.Label(self.main_frame, text=text, 
                       font=('Courier New', 9, 'bold'),
                       fg=self.highlight_color,
                       bg=self.bg_color)
    
    def create_progress_bar(self, row, column, label_text):
        frame = tk.Frame(self.main_frame, bg=self.bg_color)
        frame.grid(row=row, column=column, sticky='ew', padx=10, pady=2)
        
        label = tk.Label(frame, text=label_text, width=5, anchor='w',
                        font=('Courier New', 8), fg=self.text_color, bg=self.bg_color)
        label.pack(side='left')
        
        canvas = tk.Canvas(frame, height=15, width=150, bg=self.bg_color, 
                         highlightthickness=0)
        canvas.pack(side='left', padx=5)
        return canvas
    
    def create_scan_lines(self):
        self.scan_canvas = tk.Canvas(self.main_frame, bg=self.bg_color, 
                                    highlightthickness=0, height=5)
        self.scan_canvas.grid(row=8, column=0, columnspan=3, sticky='ew', pady=(0, 5))
        
        width = self.main_frame.winfo_reqwidth()
        for i in range(0, width, 3):
            self.scan_canvas.create_line(i, 0, i, 5, fill='#00ffcc', width=1)
        
        self.animate_scan_lines()
    
    def animate_scan_lines(self):
        self.scan_canvas.xview_scroll(1, "units")
        self.root.after(100, self.animate_scan_lines)
    
    def create_corner_brackets(self):
        # Top-left corner
        canvas = tk.Canvas(self.main_frame, width=20, height=20, bg=self.bg_color, 
                          highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nw')
        canvas.create_line(0, 15, 0, 0, 15, 0, fill=self.highlight_color, width=2)
        
        # Top-right corner
        canvas = tk.Canvas(self.main_frame, width=20, height=20, bg=self.bg_color, 
                          highlightthickness=0)
        canvas.grid(row=0, column=2, sticky='ne')
        canvas.create_line(20, 0, 5, 0, 5, 15, 20, 15, fill=self.highlight_color, width=2)
        
        # Bottom-left corner
        canvas = tk.Canvas(self.main_frame, width=20, height=20, bg=self.bg_color, 
                          highlightthickness=0)
        canvas.grid(row=8, column=0, sticky='sw')
        canvas.create_line(0, 5, 0, 20, 15, 20, fill=self.highlight_color, width=2)
        
        # Bottom-right corner
        canvas = tk.Canvas(self.main_frame, width=20, height=20, bg=self.bg_color, 
                          highlightthickness=0)
        canvas.grid(row=8, column=2, sticky='se')
        canvas.create_line(20, 20, 5, 20, 5, 5, 20, 5, fill=self.highlight_color, width=2)
    
    def blink_header(self):
        if self.blink_state:
            self.header.config(fg=self.bg_color)
        else:
            self.header.config(fg=self.highlight_color)
        
        self.blink_state = not self.blink_state
        self.root.after(1000, self.blink_header)
    
    def get_system_info(self):
        info = []
        info.append(f"OS: {platform.system()} {platform.release()}")
        info.append(f"Arch: {platform.machine()}")
        info.append(f"CPU: {psutil.cpu_percent()}% active")
        info.append(f"Boot: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(psutil.boot_time()))}")
        
        # Get private IP
        try:
            hostname = socket.gethostname()
            private_ip = socket.gethostbyname(hostname)
            info.append(f"IP: {private_ip}")
        except:
            info.append("IP: Not connected")
        
        return "\n".join(info)
    
    def draw_bar(self, canvas, percentage, color=None):
        if color is None:
            color = self.text_color

        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()

        # Draw background
        canvas.create_rectangle(0, 0, width, height, fill='#111122', outline='')

        # Draw bar
        bar_width = int(width * percentage / 100)
        canvas.create_rectangle(0, 0, bar_width, height, fill=color, outline='')

        # Draw pulse effect if high usage
        if percentage > 70:
            pulse_width = int(width * 0.1)
            for i in range(3):
                offset = (time.time() * 2 + i * 10) % width
                canvas.create_rectangle(offset, 0, offset + pulse_width, height,
                                        fill=self.highlight_color, stipple="gray50")

        # Draw percentage text
        canvas.create_text(width - 5, height // 2, anchor='e',
                           text=f"{int(percentage)}%", fill=self.text_color,
                           font=('Courier New', 7, 'bold'))

    def update_stats(self):
        # CPU Usage
        cpu_percent = psutil.cpu_percent(percpu=True)
        total_cpu = sum(cpu_percent) / len(cpu_percent)
        
        for i, percent in enumerate(cpu_percent):
            color = self.warning_color if percent > 80 else self.text_color
            self.draw_bar(self.cpu_bars[i], percent, color)
        
        # Memory Usage
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.draw_bar(self.ram_bar, mem.percent)
        self.draw_bar(self.swap_bar, swap.percent)
        
        # Network Usage
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_time
        
        up_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
        down_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
        
        self.net_up_label.config(text=f"UP: {self.format_speed(up_speed)}")
        self.net_down_label.config(text=f"DOWN: {self.format_speed(down_speed)}")
        
        self.last_net_io = current_net_io
        self.last_time = current_time
        
        # Check for high CPU usage
        if total_cpu > 90 and not self.cpu_alert_triggered:
            self.cpu_alert_triggered = True
            self.trigger_cpu_alert()
        elif total_cpu < 80:
            self.cpu_alert_triggered = False
        
        # Update system info
        self.sys_info.config(text=self.get_system_info())
        
        # Schedule next update
        self.root.after(self.update_interval, self.update_stats)
    
    def format_speed(self, bytes_per_sec):
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:.1f} B/s"
        elif bytes_per_sec < 1024*1024:
            return f"{bytes_per_sec/1024:.1f} KB/s"
        else:
            return f"{bytes_per_sec/(1024*1024):.1f} MB/s"
    
    def update_processes(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get and sort processes by CPU usage
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append((proc.info['pid'], 
                                 proc.info['name'], 
                                 proc.info['cpu_percent'], 
                                 proc.info['memory_percent']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU usage (descending)
        processes.sort(key=lambda x: x[2], reverse=True)
        
        # Add top processes to the table
        for proc in processes[:5]:
            self.tree.insert('', 'end', values=proc)
        
        # Schedule next update
        self.root.after(self.update_interval * 2, self.update_processes)
    
    def trigger_cpu_alert(self):
        # Play beep sound
        winsound.Beep(1000, 500)
        
        # Speak alert in a separate thread to avoid GUI freeze
        if self.voice_thread is None or not self.voice_thread.is_alive():
            self.voice_thread = threading.Thread(target=self.speak_alert, daemon=True)
            self.voice_thread.start()
    
    def speak_alert(self):
        try:
            # Try using pygame mixer to play a voice alert
            alert_sound = pygame.mixer.Sound("alert.wav")  # You'd need this file
            alert_sound.play()
        except:
            # Fallback to text-to-speech
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say("Warning! CPU usage critical!")
                engine.runAndWait()
            except:
                # Final fallback - just print to console
                print("CPU usage very high!")
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def stop_move(self, event):
        self.x = None
        self.y = None
    
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

def main():
    root = tk.Tk()
    
    # Set window position (top-right corner)
    screen_width = root.winfo_screenwidth()
    window_width = 600
    root.geometry(f"+{screen_width - window_width - 20}+20")
    
    # Apply dark mode to title bar (Windows 10/11)
    if platform.system() == "Windows":
        try:
            HWND = windll.user32.GetParent(root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
            value = c_int(1)
            # Try with parameter 20 first
            windll.dwmapi.DwmSetWindowAttribute(
                HWND, DWMWA_USE_IMMERSIVE_DARK_MODE,
                byref(value), sizeof(value)
            )
            # Then try with parameter 19
            windll.dwmapi.DwmSetWindowAttribute(
                HWND, DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1,
                byref(value), sizeof(value)
            )
        except:
            pass
    
    app = SciFiTaskManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()