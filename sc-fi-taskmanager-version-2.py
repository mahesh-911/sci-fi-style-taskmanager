from ctypes import byref, c_int, sizeof, windll
import tkinter as tk
from tkinter import ttk, font
import psutil
import time
import math
import pygame
import threading
import socket
import platform
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os
import warnings
import winsound

# Suppress matplotlib warnings
warnings.filterwarnings("ignore")

# Initialize pygame for sound
pygame.mixer.init()

class SciFiTaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("NEO-TASK // ADVANCED SYSTEM MONITOR")
        
        # Make window transparent (for sci-fi effect)
        self.root.attributes('-transparentcolor', '#2a2a2a')
        self.root.config(bg='#2a2a2a')
        
        # Remove window decorations (borderless)
        self.root.overrideredirect(True)
        
        # Always on top
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
        self.thermal_colors = ['#00ffcc', '#ffff00', '#ff8000', '#ff0000']
        
        # Main frame
        self.main_frame = tk.Frame(root, bg=self.bg_color, bd=0, highlightthickness=0)
        self.main_frame.pack(padx=0, pady=0)
        
        # Header with close button
        self.header = tk.Label(self.main_frame, 
                              text="≡ NEO-TASK v3.0 ≡", 
                              font=('Courier New', 12, 'bold'),
                              fg=self.highlight_color,
                              bg=self.bg_color)
        self.header.grid(row=0, column=0, columnspan=4, pady=(5, 10), sticky='ew')
        
        # Close button (X)
        self.close_btn = tk.Label(self.main_frame, text="✕", font=('Arial', 10), 
                                fg=self.text_color, bg=self.bg_color, cursor="hand2")
        self.close_btn.grid(row=0, column=3, sticky='e', padx=5)
        self.close_btn.bind("<Button-1>", lambda e: sys.exit())
        
        # ===== [1] CIRCULAR CPU GAUGES =====
        self.cpu_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.cpu_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        
        self.cpu_label = tk.Label(self.cpu_frame, text="CPU CORE STATUS", 
                                 font=('Courier New', 9, 'bold'),
                                 fg=self.highlight_color,
                                 bg=self.bg_color)
        self.cpu_label.pack()
        
        # Create circular CPU gauges
        self.cpu_gauges = []
        for i in range(psutil.cpu_count()):
            gauge_canvas = tk.Canvas(self.cpu_frame, width=80, height=80, bg=self.bg_color, highlightthickness=0)
            gauge_canvas.pack(side='left', padx=5)
            self.cpu_gauges.append(gauge_canvas)
        
        # ===== [2] THERMAL CPU VIEW =====
        self.thermal_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.thermal_frame.grid(row=1, column=2, columnspan=2, padx=10, pady=5)
        
        self.thermal_label = tk.Label(self.thermal_frame, text="CPU THERMAL MAP", 
                                    font=('Courier New', 9, 'bold'),
                                    fg=self.highlight_color,
                                    bg=self.bg_color)
        self.thermal_label.pack()
        
        # Create thermal view (using matplotlib)
        self.fig, self.ax = plt.subplots(figsize=(3, 1.5), facecolor=self.bg_color)
        self.ax.axis('off')
        self.thermal_canvas = FigureCanvasTkAgg(self.fig, master=self.thermal_frame)
        self.thermal_canvas.get_tk_widget().pack()
        
        # ===== [3] MEMORY ARC GAUGES =====
        self.mem_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.mem_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5)
        
        self.mem_label = tk.Label(self.mem_frame, text="MEMORY USAGE", 
                                 font=('Courier New', 9, 'bold'),
                                 fg=self.highlight_color,
                                 bg=self.bg_color)
        self.mem_label.pack()
        
        # RAM Arc Gauge
        self.ram_gauge = tk.Canvas(self.mem_frame, width=150, height=80, bg=self.bg_color, highlightthickness=0)
        self.ram_gauge.pack(side='left', padx=5)
        
        # SWAP Arc Gauge
        self.swap_gauge = tk.Canvas(self.mem_frame, width=150, height=80, bg=self.bg_color, highlightthickness=0)
        self.swap_gauge.pack(side='left', padx=5)
        
        # ===== [4] NETWORK GRAPH =====
        self.net_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.net_frame.grid(row=2, column=2, columnspan=2, padx=10, pady=5)
        
        self.net_label = tk.Label(self.net_frame, text="NETWORK TRAFFIC", 
                                font=('Courier New', 9, 'bold'),
                                fg=self.highlight_color,
                                bg=self.bg_color)
        self.net_label.pack()
        
        self.net_canvas = tk.Canvas(self.net_frame, width=200, height=80, bg=self.bg_color, highlightthickness=0)
        self.net_canvas.pack()
        self.net_data = [0] * 30  # Store last 30 network readings
        
        # ===== [5] OPTIMIZE BUTTON =====
        self.optimize_btn = tk.Button(self.main_frame, 
                                     text="OPTIMIZE SYSTEM", 
                                     command=self.kill_idle_processes,
                                     font=('Courier New', 9, 'bold'),
                                     fg='black',
                                     bg=self.highlight_color,
                                     activebackground='#ff66ff',
                                     bd=0,
                                     padx=10,
                                     pady=5)
        self.optimize_btn.grid(row=3, column=0, columnspan=4, pady=10)
        
        # ===== [6] PROCESS TABLE =====
        self.proc_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.proc_frame.grid(row=4, column=0, columnspan=4, padx=10, pady=5)
        
        self.proc_label = tk.Label(self.proc_frame, text="ACTIVE PROCESSES", 
                                 font=('Courier New', 9, 'bold'),
                                 fg=self.highlight_color,
                                 bg=self.bg_color)
        self.proc_label.pack()
        
        # Treeview for processes
        self.tree = ttk.Treeview(self.proc_frame, 
                                columns=('PID', 'Name', 'CPU', 'Memory'), 
                                show='headings', 
                                height=5)
        self.tree.pack()
        
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
        self.update_interval = 1000  # ms
        self.update_stats()
        self.update_processes()
        
        # Voice alert variables
        self.cpu_alert_triggered = False
        self.ram_alert_triggered = False
        self.voice_thread = None
        
        # Add sci-fi effects
        self.create_scan_lines()
        self.create_corner_brackets()
        
        # Blinking effect for header
        self.blink_state = True
        self.blink_header()
    
    # ===== [NEW] KILL IDLE PROCESSES =====
    def kill_idle_processes(self):
        idle_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] < 1.0 and proc.info['name'] not in ['System Idle Process', 'svchost.exe']:
                    idle_processes.append(proc.info['pid'])
            except:
                pass
        
        for pid in idle_processes:
            try:
                p = psutil.Process(pid)
                p.terminate()
            except:
                pass
        
        # Play sound effect
        winsound.Beep(800, 200)
        winsound.Beep(1200, 200)
        
        # Update process list
        self.update_processes()
    
    # ===== [NEW] DRAW CIRCULAR GAUGE =====
    def draw_circular_gauge(self, canvas, percent, label="", color=None):
        if color is None:
            if percent < 50:
                color = self.text_color
            elif percent < 80:
                color = '#ffff00'
            else:
                color = self.warning_color
        
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        radius = min(width, height) // 2 - 10
        center_x, center_y = width // 2, height // 2
        
        # Draw outer ring
        canvas.create_oval(center_x - radius, center_y - radius,
                          center_x + radius, center_y + radius,
                          outline='#333344', width=3)
        
        # Draw filled arc
        start_angle = -90
        extent = 3.6 * percent  # 360° = 100%
        canvas.create_arc(center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        start=start_angle, extent=extent,
                        outline=color, width=5, style='arc')
        
        # Draw percentage text
        canvas.create_text(center_x, center_y, 
                         text=f"{percent:.0f}%", 
                         font=('Courier New', 10, 'bold'),
                         fill=color)
        
        # Draw label
        canvas.create_text(center_x, center_y + radius + 10, 
                         text=label, 
                         font=('Courier New', 7),
                         fill=self.text_color)
    
    # ===== [NEW] DRAW THERMAL VIEW =====
    def draw_thermal_view(self, cpu_percent):
        # Generate a fake "thermal" gradient (for visual effect)
        thermal_data = np.zeros((10, 10))
        for i in range(10):
            thermal_data[i] = np.linspace(0, cpu_percent, 10)
        
        self.ax.clear()
        self.ax.imshow(thermal_data, cmap='hot', interpolation='gaussian')
        self.ax.axis('off')
        self.thermal_canvas.draw()
    
    # ===== [NEW] DRAW NETWORK GRAPH =====
    def draw_network_graph(self, speed):
        self.net_data.pop(0)
        self.net_data.append(speed / (1024 * 1024))  # Convert to MB/s

        self.net_canvas.delete("all")
        width = self.net_canvas.winfo_width()
        height = self.net_canvas.winfo_height()

        max_val = max(self.net_data) if max(self.net_data) > 0 else 1

        for i in range(1, len(self.net_data)):
            x1 = (i - 1) * (width / len(self.net_data))
            y1 = height - (self.net_data[i - 1] / max_val * height)
            x2 = i * (width / len(self.net_data))
            y2 = height - (self.net_data[i] / max_val * height)

            self.net_canvas.create_line(x1, y1, x2, y2, fill=self.network_color, width=2)

    # ===== [UPDATED] SYSTEM MONITORING =====
    def update_stats(self):
        # CPU Usage (circular gauges)
        cpu_percent = psutil.cpu_percent(percpu=True)
        total_cpu = sum(cpu_percent) / len(cpu_percent)
        
        for i, percent in enumerate(cpu_percent):
            self.draw_circular_gauge(self.cpu_gauges[i], percent, f"CORE {i+1}")
        
        # Thermal View
        self.draw_thermal_view(total_cpu)
        
        # Memory Usage (arc gauges)
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        self.draw_circular_gauge(self.ram_gauge, mem.percent, "RAM")
        self.draw_circular_gauge(self.swap_gauge, swap.percent, "SWAP")
        
        # Network Usage (graph)
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_time
        
        up_speed = (current_net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
        down_speed = (current_net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
        
        self.draw_network_graph(down_speed)  # Show download speed
        
        self.last_net_io = current_net_io
        self.last_time = current_time
        
        # Check for high CPU/RAM usage (voice alerts)
        if total_cpu > 90 and not self.cpu_alert_triggered:
            self.cpu_alert_triggered = True
            self.trigger_alert("Warning! CPU usage critical!")
        elif total_cpu < 80:
            self.cpu_alert_triggered = False
        
        if mem.percent > 90 and not self.ram_alert_triggered:
            self.ram_alert_triggered = True
            self.trigger_alert("Warning! RAM usage critical!")
        elif mem.percent < 80:
            self.ram_alert_triggered = False
        
        # Schedule next update
        self.root.after(self.update_interval, self.update_stats)
    
    # ===== [NEW] VOICE ALERTS =====
    def trigger_alert(self, message):
        def play_alert():
            try:
                # Try playing a sound
                winsound.Beep(1000, 500)
                winsound.Beep(1500, 500)
                
                # Try text-to-speech
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(message)
                engine.runAndWait()
            except:
                pass
        
        if self.voice_thread is None or not self.voice_thread.is_alive():
            self.voice_thread = threading.Thread(target=play_alert, daemon=True)
            self.voice_thread.start()
    
    # ===== [UPDATED] PROCESS TABLE =====
    def update_processes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append((proc.info['pid'], 
                                proc.info['name'], 
                                proc.info['cpu_percent'], 
                                proc.info['memory_percent']))
            except:
                pass
        
        processes.sort(key=lambda x: x[2], reverse=True)
        
        for proc in processes[:5]:
            self.tree.insert('', 'end', values=proc)
        
        self.root.after(self.update_interval * 2, self.update_processes)
    
    # ===== [SCAN LINES ANIMATION] =====
    def create_scan_lines(self):
        self.scan_canvas = tk.Canvas(self.main_frame, bg=self.bg_color, 
                                    highlightthickness=0, height=5)
        self.scan_canvas.grid(row=5, column=0, columnspan=4, sticky='ew', pady=(0, 5))
        
        width = self.main_frame.winfo_reqwidth()
        for i in range(0, width, 3):
            self.scan_canvas.create_line(i, 0, i, 5, fill='#00ffcc', width=1)
        
        self.animate_scan_lines()
    
    def animate_scan_lines(self):
        self.scan_canvas.xview_scroll(1, "units")
        self.root.after(100, self.animate_scan_lines)
    
    # ===== [CORNER BRACKETS] =====
    def create_corner_brackets(self):
        # Top-left corner
        canvas = tk.Canvas(self.main_frame, width=20, height=20, bg=self.bg_color, 
                          highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nw')
        canvas.create_line(0, 15, 0, 0, 15, 0, fill=self.highlight_color, width=2)
        
        # Top-right corner
        canvas = tk.Canvas(self.main_frame, width=20, height=20, bg=self.bg_color, 
                          highlightthickness=0)
        canvas.grid(row=0, column=3, sticky='ne')
        canvas.create_line(20, 0, 5, 0, 5, 15, 20, 15, fill=self.highlight_color, width=2)
        
        # Bottom-left corner
        canvas = tk.Canvas(self.main_frame, width=20, height=20, bg=self.bg_color, 
                          highlightthickness=0)
        canvas.grid(row=5, column=0, sticky='sw')
        canvas.create_line(0, 5, 0, 20, 15, 20, fill=self.highlight_color, width=2)
        
        # Bottom-right corner
        canvas = tk.Canvas(self.main_frame, width=20, height=20, bg=self.bg_color, 
                          highlightthickness=0)
        canvas.grid(row=5, column=3, sticky='se')
        canvas.create_line(20, 20, 5, 20, 5, 5, 20, 5, fill=self.highlight_color, width=2)
    
    # ===== [BLINKING HEADER] =====
    def blink_header(self):
        if self.blink_state:
            self.header.config(fg=self.bg_color)
        else:
            self.header.config(fg=self.highlight_color)
        
        self.blink_state = not self.blink_state
        self.root.after(1000, self.blink_header)
    
    # ===== [WINDOW DRAGGING] =====
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
    window_width = 700
    root.geometry(f"+{screen_width - window_width - 20}+20")
    
    # Apply dark mode to title bar (Windows 10/11)
    if platform.system() == "Windows":
        try:
            HWND = windll.user32.GetParent(root.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            DWMWA_USE_IMMERSIVE_DARK_MODE_BEFORE_20H1 = 19
            value = c_int(1)
            windll.dwmapi.DwmSetWindowAttribute(
                HWND, DWMWA_USE_IMMERSIVE_DARK_MODE,
                byref(value), sizeof(value)
            )
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