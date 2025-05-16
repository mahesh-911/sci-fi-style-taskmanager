# sci-fi-task-manager v2.0

## Overview

**NEO-TASK** is a futuristic, sci-fi inspired system monitor for Windows that provides real-time insights into your system's CPU, memory, thermal, and network performance. With interactive and visually dynamic gauges, it blends technical functionality with an immersive visual experience. It also includes a utility to optimize your system by terminating idle processes.

![sci-fi monitor preview](screenshot.png)

---

## Features

### ⚛ Visual System Dashboard

* **Circular CPU Core Gauges**: Displays usage per core with animated arcs.
* **Thermal CPU Map**: Graphically represents CPU load as a thermal heatmap.
* **Memory Arc Gauges**: Real-time RAM and Swap usage arcs.
* **Network Traffic Graph**: Live line chart of network speed in MB/s.
* **Process Table**: Interactive list of running processes with PID, CPU%, and Memory%.

### ⚡ Optimization Tool

* **"Optimize System" Button**: Kills low-CPU processes (excluding essential services) and plays a system beep alert.

### 🔎 Sci-Fi UI/UX

* Transparent window with no border.
* Always-on-top and draggable interface.
* Animated scan lines and corner brackets for a sci-fi HUD effect.
* Blinking title bar and color-coded warnings.

---

## Requirements

* **OS**: Windows
* **Python**: 3.8 or above

### Python Dependencies

Install required packages using pip:

```bash
pip install pygame psutil matplotlib pillow numpy
```

---

## Usage

1. Run the Python script:

```bash
python sci-fi-taskmanager.py
```

2. The GUI will launch in a sci-fi themed window.
3. Interact with:

   * CPU and Memory gauges
   * Network traffic visualization
   * Real-time process management
4. Click "Optimize System" to kill idle processes and refresh the process list.

---

## Known Limitations

* Designed specifically for Windows (due to usage of `winsound`, `windll`, etc.)
* Thermal visualization is illustrative (not based on actual temperature sensors).

---

## Roadmap

* Add actual thermal sensor integration using WMI.
* Extend support for Linux using platform-agnostic audio and thermal APIs.
* Add more advanced process management options.
* Export usage data for diagnostics.

---

## Author

Made with ❤ by Mahesh

## License

This project is open-source under the MIT License.
