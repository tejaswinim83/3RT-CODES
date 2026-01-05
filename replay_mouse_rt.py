Got it 👍
**Only POS_X, POS_Y, POS_Z extraction check** — no graph, no extras.

---

## ✅ Correct way to extract **POS_X, POS_Y, POS_Z**

(Position values are **SIGNED** and **multi-byte**)

### 1️⃣ What POS values usually are

From your RT3 navigation packets (as used in your code):

* **POS_X, POS_Y, POS_Z**
* **32-bit signed integers (2’s complement)**
* Stored as **4 bytes (1 word × 2 or 2 words × 2 bytes depending on format)**
* **MSB first** after reverse/concatenate

---

## 2️⃣ What is WRONG in your code (root cause)

In your file, POS values are extracted like this pattern (example):

```python
pos_x_hex = hexDecodedData[start:end]
pos_x = int(pos_x_hex, 16)
```

❌ **Problem**
This treats POS_X as **UNSIGNED**, so:

* Negative positions become huge positive numbers
* Values look unstable / incorrect

---

## 3️⃣ ✅ Correct extraction method (SIGNED 32-bit)

### ✅ Use this helper (mandatory)

```python
def get_signed_32bit(hex_str):
    value = int(hex_str, 16)
    if value & 0x80000000:
        value -= 0x100000000
    return value
```

---

## 4️⃣ ✅ Correct POS extraction (FIX)

### Example (adjust indices to your packet)

```python
# POS X
pos_x_hex = reverse_and_concatenate(hexDecodedData[POS_X_START:POS_X_END])
pos_x = get_signed_32bit(pos_x_hex)

# POS Y
pos_y_hex = reverse_and_concatenate(hexDecodedData[POS_Y_START:POS_Y_END])
pos_y = get_signed_32bit(pos_y_hex)

# POS Z
pos_z_hex = reverse_and_concatenate(hexDecodedData[POS_Z_START:POS_Z_END])
pos_z = get_signed_32bit(pos_z_hex)
```

---

## 5️⃣ How to VERIFY quickly (very important)

Add this temporary print once:

```python
print("POS HEX:", pos_x_hex, pos_y_hex, pos_z_hex)
print("POS DEC:", pos_x, pos_y, pos_z)
```

✅ If working correctly:

* POS values can be **positive or negative**
* No sudden jumps like `429496xxxx`
* Smooth change between packets

---

## 6️⃣ Summary (short & clear)

✔ Extraction indices → **OK in your code**
❌ Interpretation → **WRONG (unsigned)**
✅ Fix → **signed 32-bit conversion**

---

If you want, next I can:

* Verify **exact byte indices** for POS_X/Y/Z word numbers
* Check **VEL_X, VEL_Y, VEL_Z** (same issue exists there)
* Match extraction exactly with your **RT3 ICD word numbers**

Just tell 👍



=============================================================================
Here's the **exact** code to add and where to add it:

## Step 1: Replace the existing `bind_mousewheel` function (around line 210 in your original code)

Find this function in your code:
```python
def bind_mousewheel(widget):
    system = platform.system()
    if system == 'Windows' or system == 'Darwin':
        widget.bind_all("<MouseWheel>", lambda e: canvas_rt1.yview_scroll(int(-1*(e.delta/120)), "units"))
    else:  # Linux
        widget.bind_all("<Button-4>", lambda e: canvas_rt1.yview_scroll(-1, "units"))
        widget.bind_all("<Button-5>", lambda e: canvas_rt1.yview_scroll(1, "units"))
```

**REPLACE** it with this improved version:

```python
def bind_mousewheel(canvas):
    """Enable mouse wheel scrolling for a canvas widget"""
    system = platform.system()
    
    def _on_mousewheel(event):
        if system == 'Windows':
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif system == 'Darwin':
            canvas.yview_scroll(int(-1*event.delta), "units")
        else:  # Linux
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
    
    def _bind_to(event):
        if system == 'Windows' or system == 'Darwin':
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        else:  # Linux
            canvas.bind_all("<Button-4>", _on_mousewheel)
            canvas.bind_all("<Button-5>", _on_mousewheel)
    
    def _unbind_from(event):
        if system == 'Windows' or system == 'Darwin':
            canvas.unbind_all("<MouseWheel>")
        else:  # Linux
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
    
    # Bind enter/leave events to control mouse wheel binding
    canvas.bind("<Enter>", _bind_to)
    canvas.bind("<Leave>", _unbind_from)
```

## Step 2: Add mouse wheel binding for RT1 (around line 210-215)

Find this section in your RT1 frame code:
```python
# Enable mouse wheel scrolling
bind_mousewheel(canvas_rt1)
```

**CHANGE** it to:
```python
# Enable mouse wheel scrolling
bind_mousewheel(canvas_rt1)  # This line already exists, keep it
```

## Step 3: Add mouse wheel binding for RT2 (around line 290-295)

In the RT2 Frame section, find where `canvas_rt2` is created and add this **RIGHT AFTER** creating it:

```python
# === Scrollable Canvas Setup for RT2 ===
canvas_rt2 = Canvas(rt2_frame, bg="burlywood", highlightthickness=0)
scrollbar_y_rt2 = ttk.Scrollbar(rt2_frame, orient="vertical", command=canvas_rt2.yview)
scrollbar_x_rt2 = ttk.Scrollbar(rt2_frame, orient="horizontal", command=canvas_rt2.xview)
canvas_rt2.configure(yscrollcommand=scrollbar_y_rt2.set, xscrollcommand=scrollbar_x_rt2.set)

# ADD THIS LINE HERE:
bind_mousewheel(canvas_rt2)  # <-- ADD THIS LINE

canvas_rt2.grid(row=0, column=0, sticky="nsew")
```

## Step 4: Add mouse wheel binding for RT3 (around line 340-345)

In the RT3 Frame section, find where `canvas_rt3` is created and add this **RIGHT AFTER** creating it:

```python
# === Scrollable Canvas Setup for RT3 ===
canvas_rt3 = Canvas(rt3_frame, bg="burlywood", highlightthickness=0)
scrollbar_y_rt3 = ttk.Scrollbar(rt3_frame, orient="vertical", command=canvas_rt3.yview)
scrollbar_x_rt3 = ttk.Scrollbar(rt3_frame, orient="horizontal", command=canvas_rt3.xview)
canvas_rt3.configure(yscrollcommand=scrollbar_y_rt3.set, xscrollcommand=scrollbar_x_rt3.set)

# ADD THIS LINE HERE:
bind_mousewheel(canvas_rt3)  # <-- ADD THIS LINE

canvas_rt3.grid(row=0, column=0, sticky="nsew")
```

## Summary of changes:

1. **Replace** the `bind_mousewheel` function with the improved version
2. **Keep** the existing `bind_mousewheel(canvas_rt1)` call for RT1
3. **Add** `bind_mousewheel(canvas_rt2)` after creating `canvas_rt2`
4. **Add** `bind_mousewheel(canvas_rt3)` after creating `canvas_rt3`

This will give you mouse wheel scrolling for all three RT frames (RT1, RT2, and RT3). The mouse wheel will only affect the canvas that the mouse is currently hovering over.

===================================================================================




Looking at your code, I can see that you have the replay function stubs but they're not fully implemented. The main issue is that your replay system needs to actually parse and process the data to update the displays. Here's the corrected and complete replay implementation:

```python
def replay_from_file():
    global replay_running, replay_filepath, replay_paused, replay_thread
    
    if replay_running:
        status_var.set("❌ Replay already running! Stop it first.")
        return
    
    filepath = filedialog.askopenfilename(
        title="Select Telemetry File for Replay",
        filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("Hex files", "*.hex"), ("All files", "*.*")]
    )
    
    if not filepath:
        return
    
    replay_filepath = filepath
    replay_running = True
    replay_paused = False
    
    status_var.set(f"▶️ Replay started from {os.path.basename(filepath)}")
    
    # Start replay in a separate thread
    replay_thread = threading.Thread(target=replay_thread_func, daemon=True)
    replay_thread.start()

def replay_thread_func():
    global replay_running, replay_paused, jump_target_sec, replay_filepath
    
    try:
        with open(replay_filepath, 'r') as f:
            content = f.read().strip()
        
        # Parse the file - assuming it contains hex strings like your serial data
        # Each line or packet should be in the format you print in readSerial()
        lines = content.split('\n')
        
        line_index = 0
        while replay_running and line_index < len(lines):
            # Handle pause
            while replay_paused and replay_running:
                time.sleep(0.1)
            
            if not replay_running:
                break
            
            # Handle jump request
            if jump_target_sec is not None:
                # Search for the target SYS_SEC in subsequent lines
                found = False
                for i in range(line_index, len(lines)):
                    line = lines[i].strip()
                    if line and len(line) > 0:
                        # Try to extract hex data and find SYS_SEC
                        hex_match = re.search(r'([0-9a-fA-F]+)', line)
                        if hex_match:
                            hex_data = hex_match.group(1)
                            if len(hex_data) >= 1200:  # Assuming SA packet
                                # Extract SYS_SEC from position 140-148 (SYS_Second_hex)
                                sys_sec_start = 148
                                sys_sec_end = 156
                                if len(hex_data) > sys_sec_end:
                                    sys_sec_hex = hex_data[sys_sec_start:sys_sec_end]
                                    # Parse as little-endian
                                    sys_sec_bytes = bytes.fromhex(sys_sec_hex)
                                    sys_sec = int.from_bytes(sys_sec_bytes, byteorder='little', signed=False)
                                    
                                    if sys_sec >= jump_target_sec:
                                        line_index = i
                                        found = True
                                        status_var.set(f"↗️ Jumped to SYS_SEC: {sys_sec}")
                                        break
                
                jump_target_sec = None
                if not found:
                    status_var.set(f"❌ SYS_SEC {jump_target_sec} not found")
                    break
                continue
            
            # Process current line
            line = lines[line_index].strip()
            line_index += 1
            
            if not line:
                continue
            
            # Extract hex data from the line
            hex_match = re.search(r'([0-9a-fA-F]+)', line)
            if not hex_match:
                continue
            
            hex_data = hex_match.group(1).lower()
            
            # Determine which RT this data belongs to based on header
            if hex_data.startswith('acca1f0a'):
                rt_name = "RT1"
            elif hex_data.startswith('acca1f0b'):
                rt_name = "RT1"
            elif hex_data.startswith('acca1f0c'):
                rt_name = "RT2"
            elif hex_data.startswith('acca1f0d'):
                rt_name = "RT2"
            elif hex_data.startswith('acca1f0e'):
                rt_name = "RT3"
            elif hex_data.startswith('acca1f0f'):
                rt_name = "RT3"
            else:
                continue
            
            # Process the data to update the GUI
            # Put the data in the queue just like serial data
            data_queue.put((rt_name, hex_data))
            
            # Simulate real-time playback speed (adjust as needed)
            time.sleep(0.1)  # 10Hz playback
        
        replay_running = False
        status_var.set("⏹️ Replay finished")
        btn_pause_resume.config(text="Pause ⏸")
        
    except Exception as e:
        status_var.set(f"❌ Replay error: {e}")
        print(f"Replay error: {e}")
        replay_running = False
        btn_pause_resume.config(text="Pause ⏸")

def jump_to_sys_sec():
    global jump_target_sec
    
    try:
        target = int(jump_entry.get())
        jump_target_sec = target
        status_var.set(f"⏩ Jump to SYS_SEC {target} requested...")
    except ValueError:
        status_var.set("❌ Enter a valid integer for SYS_SEC")

def toggle_pause_resume():
    global replay_paused
    
    if not replay_running:
        status_var.set("❌ No replay running")
        return
    
    replay_paused = not replay_paused
    
    if replay_paused:
        btn_pause_resume.config(text="Resume ▶", bg="light green")
        status_var.set("⏸️ Replay paused")
    else:
        btn_pause_resume.config(text="Pause ⏸", bg="lightcoral")
        status_var.set("▶️ Replay resumed")

def stop_replay():
    global replay_running, replay_paused
    
    if replay_running:
        replay_running = False
        replay_paused = False
        status_var.set("⏹️ Replay stopped")
        btn_pause_resume.config(text="Pause ⏸", bg="light green")
    else:
        status_var.set("❌ No replay running")
```

Also, you need to add the import for `re` at the top of your file:
```python
import re
```

**Key improvements made:**

1. **Actual data processing**: The replay function now properly extracts hex data from the file and puts it in the data queue, just like serial data.

2. **Header detection**: It detects which RT the data belongs to based on the header bytes.

3. **Jump functionality**: Implements searching for SYS_SEC in the data by parsing the actual hex packets.

4. **Error handling**: Added better error handling and status updates.

5. **Button state management**: Updates button text and colors appropriately.

6. **File format handling**: Can handle various file formats (text, CSV, hex files).

**To use the replay function properly:**

1. Make sure your telemetry file contains the raw hex strings that your serial port outputs (like `acca1f0a...`).

2. The file can be in any format (txt, csv, etc.) as long as it contains the hex strings.

3. When you click "Replay", select your telemetry file.

4. Use "Jump to SYS_SEC" to skip to a specific system second in the data.

5. Use "Pause/Resume" to control playback.

6. Use "Stop Replay" to stop playback.

The replay system now properly feeds data through the same `process_rt_data()` function that your serial data uses, so all displays will update exactly as they do with live data.
