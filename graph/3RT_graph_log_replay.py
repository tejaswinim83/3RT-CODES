GRAPH is not comming correctly line graph not working . strucking in between even though the  display is working . 
error updating real time plot for rt3: list.remove(X):x not in list

file saving is not working properly. 
error processing rt data for : get_timestamp_filename() missing 1 requirement argument: write  to raw

reply code not working 
mouse for all rts, 




=====================================================
I'll help you add the file logging functionality, fix the CNDR plot, and improve the replay feature. Here's the modified code:

## 1. First, add these helper functions at the beginning of your code (after imports):

```python
# Add this near the top after imports
import csv

def get_timestamped_filename(base_name, suffix):
    """Create a timestamped filename for logging"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{base_name}_{suffix}_{timestamp}.csv"

def write_to_rawh2(data, rt_name, project_name):
    """Write raw data to file"""
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "Rawh2")
    header = ['TimeStamp', 'RAW DATA']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_SYN(data, rt_name, project_name):
    """Write sync time data to file"""
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "Sync")
    header = ['TimeStamp', 'SYN_SECOND', 'SYN_NANOSECOND', 'SYN_WEEKNUMBER']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_pvt(data, rt_name, project_name):
    """Write PVT data to file"""
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "PVT")
    header = ['TimeStamp','Counter','Sys_Second','Sys_NanoSecond','Sys_WeekNumber','PPS_Second','PPS_NanoSecond','PPS_WeekNo','PPS_3D FIX','PPS_LEAP SEC',
              'TSM_Counter','Update Counter',
              'Checksum','Checksum 2','PDOP','Clock bais','InterSystem bais','Drift','Inter System Drift',
              'POS_X','POS_Y','POS_Z','POS_VX','POS_VY','POS_VZ',
              'ESt_X','EST_Y','EST_Z','EST_VX','EST_VY','EST_VZ',
              'ACQ1','ACQ2','ACQ3','ACQ4',
              'TM SEL','SWD','HWDT','SBASEN','SYS_MODE','REC MODE','TIME MODE','ALM AV','TIME AV','POS MODE','POS AV',
              'SW RESET COUNTER','HW RESET COUNTER','SW RESET ID','SPS ID','SOL MODE','PORT CONFIG1','PORT CONFIG2','PORT CONFIG3','PORT CONFIG4',
              'NAVIC MSG 22 COUNTER','NAVIC MSG CMD COUNTER','LEO SAT ID','NO OF SAT TRACKED','NAVIC CMD VAR',
              'ODP EST FLAG','ODP EN','PHC USG','PHC EN','EPH RT','MN VON','NUM SPS',
              'LAST CMD EXE','LAST RESET TIME','CMD BASED RT','TOTAL CMD COUNTER',
              'RT ID','MISSION PHASE','FMEM','CR AID','FULL CTRL','S ID','LIG-1','LIG-2','LIG-3','LIG-4','LIN-1','LIN2','PRIME NGC',
              'Rng L','Orbit Phase','Iono C','Iono Sm','Cr Smo','Vel sm','RAIM','PR Rej','Pr Bf Sync','Cfg loop','int crd tst','Elev En','Rst Flag','ODP Rst Sp','Cold Vis','Navic Msg En',
              'DUAL CMD COUNTER','SPS CMD COUNTER','NRFFC RESET COUNTER1','NRFFC RESET COUNTER2',
              'GRFFC RESET COUNTER1','GRFFC RESET COUNTER2','GRFFC RESET COUNTER3','GRFFC RESET COUNTER4']
    
    bit_names = ["A","T","D","E","P","H","R","P1_","I","S","SR","E1_"]
    for ch in range(1, 19):
        header.append(f'CH{ch}')
        header.append(f'SVID{ch}')
        header.append(f'CNDR{ch}')
        for bit in bit_names:
            header.append(f'{bit}{ch}')
        header.append(f'IODE{ch}')
        header.append(f'PR(cm){ch}')
        header.append(f'DR(m/s){ch}')
        header.append(f'ELEV{ch}')
    
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)
```

## 2. Modify the `process_rt_data` function to add logging:

```python
def process_rt_data(hexDecodedData, rt_name):
    """Process data for a specific RT and update its widgets"""
    try:
        # Detect header from first 4 bytes
        header = [hexDecodedData[i:i+2] for i in range(0, 8, 2)]
        
        # Get project name
        project_name = project_name_var.get().strip()
        if not project_name or project_name.lower() == "gaganyaan":
            project_name = "GAGANYAAN"
        
        # Log raw data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        write_to_rawh2([timestamp, hexDecodedData], rt_name, project_name)

        header_map = {
            ("ac", "ca", "1f", "0a"): "RT1_A",
            ("ac", "ca", "1f", "0b"): "RT1_B",
            ("ac", "ca", "1f", "0c"): "RT2_C",
            ("ac", "ca", "1f", "0d"): "RT2_D",
            ("ac", "ca", "1f", "0e"): "RT3_E",
            ("ac", "ca", "1f", "0f"): "RT3_F",
        }

        header_key = header_map.get(tuple(header))
        if header_key is None:
            print("Unknown header")
            return

        # Select widgets and counter
        if rt_name == "RT1":
            widgets = rt1_widgets
        elif rt_name == "RT2":
            widgets = rt2_widgets
        elif rt_name == "RT3":
            widgets = rt3_widgets
        else:
            print("Unknown RT Name")
            return

        # Branch depending on header type
        if header_key.endswith(("A", "C", "E")):
            # Large packet processing (PVT data)
            # ... (keep all your existing parsing code as is) ...
            
            # After parsing all data, prepare PVT data for logging
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Prepare basic data
            pvt_data = [timestamp, UpdateCounter, SYS_Second, SYS_NanoSecond, SYS_WeekNumber,
                       PPS_Sec, PPS_Nanosec, PPS_Week, fix_3D, Leap,
                       TSM_update_counter, UpdateCounter,
                       checksum1, checksum2, PDOP, Bais, ISB, DRIFT, ISD,
                       POS_x, POS_y, POS_z, POS_vx, POS_vy, POS_vz,
                       INS_x, INS_y, INS_z, INS_vx, INS_vy, INS_vz,
                       ACQ1, ACQ2, ACQ3, ACQ4,
                       flag['Tm_sel'], flag["SWDT"], flag["HWDT"], flag["SBASEN"], 
                       flag["System_mode"], flag["Rec_Mode"], flag["Time_Mode"], 
                       flag["Alm_Av"], flag["Time_Av"], flag["Pose_Mode"], flag["Pos_Av"],
                       SW_reset_counter, HW_reset_counter, flag1["SW_Rst_ID"], 
                       flag1["SPS_ID"], flag1["Sol_mode"],
                       flag1["Port_config"]["Antenna_1"], flag1["Port_config"]["Antenna_2"],
                       flag1["Port_config"]["Antenna_3"], flag1["Port_config"]["Antenna_4"],
                       Navic_msg_22_counter, Navic_msg_counter, Leo_sat_id_mil, No_of_Sat, Navic_cmd_var,
                       flag3["ODP_Est flag"], flag3["ODP_ENA"], flag3["PHCUsage"], 
                       flag3["PHCEn"], flag3["Eph RT"], flag3["MNVON"], flag3["NUMSPS"],
                       Last_cmd_ex, Last_reset_time, Cmd_counter_based_rt, Total_cmd_counter,
                       flags["RT_ID"], flags["Mission_Phase"], flags["Fmem"], flags["Cr_Aid"],
                       flags["FLL_Cntr"], flags["S_ID"], flags["LIG_1"], flags["LIG_2"],
                       flags["LIG_3"], flags["LIG_4"], flags["LIN_1"], flags["LIN_2"], flags["Prime_NGC"],
                       flag2["Rng L"], flag2["Orbit Phase"], flag2["Iono C"], flag2["Iono Sm"],
                       flag2["Cr Smo"], flag2["Vel sm"], flag2["RAIM"], flag2["PR Rej"],
                       flag2["Pr Bf Sync"], flag2["Cfg loop"], flag2["int crd tst"],
                       flag2["Elev En"], flag2["Rst Flag"], flag2["ODP Rst Sp"],
                       flag2["Cold Vis"], flag2["Navic Msg En"],
                       Dual_exe_cmd_c, Spu_cmd_c, Nrffc_counter1, Nrffc_counter2,
                       Grffc_counter1, Grffc_counter2, Grffc_counter3, Grffc_counter4]
            
            # Add channel tracking data
            for ch in range(18):
                pvt_data.extend([
                    ch+1,  # CH number
                    SVID_values[ch] if ch < len(SVID_values) else 0,
                    CNDR_values[ch] if ch < len(CNDR_values) else 0
                ])
                
                # Add bit status
                if ch < len(CHANNEL_STATUS):
                    try:
                        status_meaning = decode_channel_status_meaning(CHANNEL_STATUS[ch])
                        pvt_data.extend([
                            status_meaning.get("ANT", ""),
                            status_meaning.get("TRK", ""),
                            status_meaning.get("DR", ""),
                            status_meaning.get("EPH", ""),
                            status_meaning.get("POS", ""),
                            status_meaning.get("URA", ""),
                            status_meaning.get("RIM", ""),
                            status_meaning.get("PR", ""),
                            status_meaning.get("INO", ""),
                            status_meaning.get("SBC", ""),
                            status_meaning.get("SBR", ""),
                            status_meaning.get("UR5", "")
                        ])
                    except:
                        pvt_data.extend([""] * 12)
                else:
                    pvt_data.extend([""] * 12)
                
                # Add remaining channel data
                pvt_data.extend([
                    IODE_values[ch] if ch < len(IODE_values) else 0,
                    PR_values[ch] if ch < len(PR_values) else 0,
                    DR_values[ch] if ch < len(DR_values) else 0,
                    Elev_values[ch] if ch < len(Elev_values) else 0
                ])
            
            # Write to PVT file
            write_to_pvt(pvt_data, rt_name, project_name)
            
        else:
            # Small packet processing (Sync data)
            SYN_NanoSecond_hex=hexDecodedData[12:20]
            SYN_Second_hex=hexDecodedData[20:28]
            SYN_Weeknumber_hex=hexDecodedData[28:32]

            # Convert to decimal
            SYN_NanoSecond = reverse_and_concatenate(SYN_NanoSecond_hex)
            SYN_Second = reverse_and_concatenate(SYN_Second_hex)
            SYN_WeekNumber = reverse_and_concatenate(SYN_Weeknumber_hex)

            # Update GUI
            widgets['nanotime_entry1'].config(state="normal")
            widgets['nanotime_entry1'].delete(0, END)
            widgets['nanotime_entry1'].insert(0, str(SYN_NanoSecond))
            widgets['nanotime_entry1'].config(state="readonly")

            widgets['time_entry1'].config(state="normal")
            widgets['time_entry1'].delete(0, END)
            widgets['time_entry1'].insert(0, str(SYN_Second))
            widgets['time_entry1'].config(state="readonly")

            widgets['week_entry1'].config(state="normal")
            widgets['week_entry1'].delete(0, END)
            widgets['week_entry1'].insert(0, str(SYN_WeekNumber))
            widgets['week_entry1'].config(state="readonly")
            
            # Log sync data
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            write_to_SYN([timestamp, SYN_Second, SYN_NanoSecond, SYN_WeekNumber], rt_name, project_name)
            
    except Exception as e:
        print(f"Error processing RT data for {rt_name}: {e}")
```

## 3. Fix the CNDR plot function:

```python
def update_cndr_plot_func(rt_name, svid_labels, cndr_values):
    """Update CNDR vs SVID plot for specific RT"""
    if rt_name == "RT1":
        ax = ax_cndr_rt1
        canvas = canvas_cndr_rt1
    elif rt_name == "RT2":
        ax = ax_cndr_rt2
        canvas = canvas_cndr_rt2
    elif rt_name == "RT3":
        ax = ax_cndr_rt3
        canvas = canvas_cndr_rt3
    else:
        return
    
    colors = []
    for val in cndr_values:
        if 0 <= val < 20:
            colors.append("orange")
        elif 20 <= val <= 40:
            colors.append("red")
        elif 40 <= val <= 60:
            colors.append("blue")
        else:
            colors.append("gray")
    
    ax.clear()
    ax.set_title(f"CNDR vs SVID ({rt_name})")
    ax.set_xlabel("SVID")
    ax.set_ylabel("CNDR Value")
    ax.set_ylim(0, 60)
    ax.set_yticks([0, 10, 20, 30, 40, 50, 60])
    
    # Create bar chart
    x_positions = range(1, len(svid_labels) + 1)
    bars = ax.bar(x_positions, cndr_values, color=colors, edgecolor='black')
    
    # Add value labels on top of bars
    for bar, value in zip(bars, cndr_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{value:.1f}', ha='center', va='bottom', fontsize=8)
    
    ax.set_xticks(x_positions)
    ax.set_xticklabels(svid_labels, rotation=45, ha='right')
    ax.grid(True, alpha=0.3)
    
    canvas.draw()
```

## 4. Update the CNDR plot creation in `create_rt_display_widgets`:

```python
# In create_rt_display_widgets function, update the graph section:

# ========================== GRAPH ============================
frame_cndr_plot = tk.LabelFrame(parent_frame, text=f"CNDR VS SVID PLOT({rt_name})", bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",
    bd=2,
    padx=2, pady=2
)
frame_cndr_plot.grid(row=4, column=3, padx=2, pady=2, sticky="nsew")

frame_cndr_plot.grid_rowconfigure(0, weight=1)
frame_cndr_plot.grid_columnconfigure(0, weight=1)

fig_cndr = Figure(figsize=(5.2, 3.6), dpi=100)
ax_cndr = fig_cndr.add_subplot(111)

ax_cndr.set_title(f"CNDR Values ({rt_name})")
ax_cndr.set_xlabel("SVIDs")
ax_cndr.set_ylabel("CNDR Values")
ax_cndr.set_ylim(0, 60)
ax_cndr.set_yticks([0, 10, 20, 30, 40, 50, 60])
ax_cndr.grid(True, alpha=0.3)

canvas_cndr = FigureCanvasTkAgg(fig_cndr, master=frame_cndr_plot)
canvas_cndr.get_tk_widget().grid(row=0, column=0, sticky="nsew")

# Store references
if rt_name == "RT1":
    rt1_widgets['fig_cndr'] = fig_cndr
    rt1_widgets['ax_cndr'] = ax_cndr
    rt1_widgets['canvas_cndr'] = canvas_cndr
elif rt_name == "RT2":
    rt2_widgets['fig_cndr'] = fig_cndr
    rt2_widgets['ax_cndr'] = ax_cndr
    rt2_widgets['canvas_cndr'] = canvas_cndr
elif rt_name == "RT3":
    rt3_widgets['fig_cndr'] = fig_cndr
    rt3_widgets['ax_cndr'] = ax_cndr
    rt3_widgets['canvas_cndr'] = canvas_cndr
```

## 5. Improved replay function:

```python
def replay_from_file():
    global replay_running, replay_filepath, replay_paused, replay_thread
    
    if replay_running:
        status_var.set("❌ Replay already running! Stop it first.")
        return
    
    filepath = filedialog.askopenfilename(
        title="Select Telemetry File for Replay",
        filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if not filepath:
        return
    
    replay_filepath = filepath
    replay_running = True
    replay_paused = False
    
    status_var.set(f"▶️ Replay started from {os.path.basename(filepath)}")
    btn_pause_resume.config(text="Pause ⏸", state="normal")
    
    # Start replay in a separate thread
    replay_thread = threading.Thread(target=replay_thread_func, daemon=True)
    replay_thread.start()

def replay_thread_func():
    global replay_running, replay_paused, jump_target_sec, replay_filepath
    
    try:
        with open(replay_filepath, 'r') as f:
            lines = f.readlines()
        
        line_index = 0
        while line_index < len(lines) and replay_running:
            while replay_paused and replay_running:
                time.sleep(0.1)
            
            # Check for jump request
            if jump_target_sec is not None:
                target_found = False
                for i in range(line_index, len(lines)):
                    if f"SYS_SEC: {jump_target_sec}" in lines[i]:
                        line_index = i
                        target_found = True
                        status_var.set(f"↗️ Jumped to SYS_SEC: {jump_target_sec}")
                        break
                
                if not target_found:
                    status_var.set(f"❌ SYS_SEC {jump_target_sec} not found in file")
                
                jump_target_sec = None
            
            if line_index >= len(lines):
                break
            
            line = lines[line_index].strip()
            
            # Parse the line based on your data format
            # This is a simplified example - adjust based on your actual file format
            if "RT1" in line or "RT2" in line or "RT3" in line:
                # Extract RT name and hex data
                parts = line.split("|")
                if len(parts) >= 2:
                    rt_part = parts[0].strip()
                    data_part = parts[-1].strip()
                    
                    # Determine which RT
                    if "RT1" in rt_part:
                        rt_name = "RT1"
                    elif "RT2" in rt_part:
                        rt_name = "RT2"
                    elif "RT3" in rt_part:
                        rt_name = "RT3"
                    else:
                        rt_name = "RT1"  # default
                    
                    # Process the data (simulate receiving data)
                    data_queue.put((rt_name, data_part))
            
            line_index += 1
            
            # Simulate real-time playback (adjust speed as needed)
            time.sleep(0.05)  # 20 lines per second
        
        replay_running = False
        status_var.set("⏹️ Replay finished")
        btn_pause_resume.config(state="disabled")
        
    except Exception as e:
        status_var.set(f"❌ Replay error: {e}")
        replay_running = False
        btn_pause_resume.config(state="disabled")
```

## 6. Add these global variables at the top:

```python
# Add to global variables section
replay_thread = None
```

## 7. Update the CNDR plot refresh in the data processing:

```python
# After updating CNDR values in process_rt_data, add:
if 'cndr_entries' in widgets and 'svid_entries' in widgets:
    svid_labels = [entry.get() or f"CH{i+1}" for i, entry in enumerate(widgets['svid_entries'])]
    cndr_values = [float(entry.get() or 0) for entry in widgets['cndr_entries']]
    update_cndr_plot_func(rt_name, svid_labels, cndr_values)
```

## Key Changes Made:

1. **File Logging**: Added CSV logging for raw data, sync data, and PVT data for each RT separately
2. **CNDR Plot Fix**: Fixed the plot to properly show CNDR values vs SVIDs with colored bars and value labels
3. **Improved Replay**: 
   - Added proper threading control
   - Better error handling
   - Ability to parse different RT data from files
   - Button state management
4. **Project Name Integration**: Uses the project name from the GUI for filenames
5. **Separate Files per RT**: Each RT gets its own set of log files

The logging will create files like:
- `GAGANYAAN_RT1_Rawh2_2025-01-02_12-30-45.csv`
- `GAGANYAAN_RT1_Sync_2025-01-02_12-30-45.csv`
- `GAGANYAAN_RT1_PVT_2025-01-02_12-30-45.csv`


============================================================================










Yes, I understand! You want the CNDR vs SVID plot to be dynamic and continuously update as new data comes in, rather than just showing static bars. Here's the modified code to create a **real-time animated plot**:

## 1. First, modify the plot creation section in `create_rt_display_widgets`:

```python
# ========================== REAL-TIME CNDR VS SVID PLOT ============================
frame_cndr_plot = tk.LabelFrame(parent_frame, text=f"REAL-TIME CNDR VS SVID ({rt_name})", bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",
    bd=2,
    padx=2, pady=2
)
frame_cndr_plot.grid(row=4, column=3, padx=2, pady=2, sticky="nsew")
frame_cndr_plot.grid_rowconfigure(0, weight=1)
frame_cndr_plot.grid_columnconfigure(0, weight=1)

# Create figure with subplots
fig_cndr = Figure(figsize=(5.2, 3.6), dpi=100)

# Create subplot for CNDR bars
ax_cndr = fig_cndr.add_subplot(111)

# Initialize empty data
svid_labels = [str(i+1) for i in range(18)]  # Default CH1-CH18
cndr_values = [0] * 18
bar_colors = ['lightgray'] * 18

# Create initial bar plot
bars = ax_cndr.bar(svid_labels, cndr_values, color=bar_colors, edgecolor='black', alpha=0.8)

# Configure plot
ax_cndr.set_title(f"Real-time CNDR vs SVID ({rt_name})", fontsize=11, fontweight='bold')
ax_cndr.set_xlabel("SVID / Channel", fontsize=9)
ax_cndr.set_ylabel("CNDR Value", fontsize=9)
ax_cndr.set_ylim(0, 60)
ax_cndr.set_yticks([0, 10, 20, 30, 40, 50, 60])
ax_cndr.grid(True, alpha=0.3, linestyle='--')
ax_cndr.tick_params(axis='x', rotation=45, labelsize=8)
ax_cndr.tick_params(axis='y', labelsize=8)

# Add value labels on bars
for bar, value in zip(bars, cndr_values):
    height = bar.get_height()
    if height > 0:
        ax_cndr.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{value:.1f}', ha='center', va='bottom', fontsize=7, fontweight='bold')

# Create canvas
canvas_cndr = FigureCanvasTkAgg(fig_cndr, master=frame_cndr_plot)
canvas_cndr.draw()
canvas_cndr.get_tk_widget().grid(row=0, column=0, sticky="nsew")

# Store references for real-time updates
if rt_name == "RT1":
    rt1_widgets['fig_cndr'] = fig_cndr
    rt1_widgets['ax_cndr'] = ax_cndr
    rt1_widgets['canvas_cndr'] = canvas_cndr
    rt1_widgets['bars_cndr'] = bars  # Store bars for updates
    rt1_widgets['svid_labels'] = svid_labels
    rt1_widgets['cndr_history'] = [[] for _ in range(18)]  # Store history for each channel
elif rt_name == "RT2":
    rt2_widgets['fig_cndr'] = fig_cndr
    rt2_widgets['ax_cndr'] = ax_cndr
    rt2_widgets['canvas_cndr'] = canvas_cndr
    rt2_widgets['bars_cndr'] = bars
    rt2_widgets['svid_labels'] = svid_labels
    rt2_widgets['cndr_history'] = [[] for _ in range(18)]
elif rt_name == "RT3":
    rt3_widgets['fig_cndr'] = fig_cndr
    rt3_widgets['ax_cndr'] = ax_cndr
    rt3_widgets['canvas_cndr'] = canvas_cndr
    rt3_widgets['bars_cndr'] = bars
    rt3_widgets['svid_labels'] = svid_labels
    rt3_widgets['cndr_history'] = [[] for _ in range(18)]
```

## 2. Add this new function for real-time plot updates:

```python
def update_real_time_cndr_plot(rt_name):
    """Update the CNDR plot with real-time animation"""
    if rt_name == "RT1":
        widgets = rt1_widgets
    elif rt_name == "RT2":
        widgets = rt2_widgets
    elif rt_name == "RT3":
        widgets = rt3_widgets
    else:
        return
    
    # Check if we have the necessary widgets
    if not all(key in widgets for key in ['bars_cndr', 'ax_cndr', 'canvas_cndr', 'cndr_entries', 'svid_entries']):
        return
    
    try:
        # Get current values from entries
        cndr_values = []
        svid_labels = []
        
        for i in range(18):
            if i < len(widgets['cndr_entries']):
                try:
                    value = float(widgets['cndr_entries'][i].get() or 0)
                except:
                    value = 0
                cndr_values.append(value)
            else:
                cndr_values.append(0)
            
            if i < len(widgets['svid_entries']):
                svid = widgets['svid_entries'][i].get() or f"CH{i+1}"
                svid_labels.append(svid)
            else:
                svid_labels.append(f"CH{i+1}")
        
        # Update bar heights
        for i, bar in enumerate(widgets['bars_cndr']):
            if i < len(cndr_values):
                # Animate the change
                old_height = bar.get_height()
                new_height = cndr_values[i]
                
                # Smooth transition
                bar.set_height(new_height)
                
                # Update color based on value
                if 0 <= new_height < 20:
                    bar.set_color('orange')
                    bar.set_alpha(0.8)
                elif 20 <= new_height <= 40:
                    bar.set_color('red')
                    bar.set_alpha(0.8)
                elif 40 <= new_height <= 60:
                    bar.set_color('blue')
                    bar.set_alpha(0.8)
                else:
                    bar.set_color('gray')
                    bar.set_alpha(0.3)
                
                # Update value label
                if 'value_texts' not in widgets:
                    widgets['value_texts'] = [None] * 18
                
                # Remove old text
                if widgets['value_texts'][i] is not None:
                    widgets['value_texts'][i].remove()
                
                # Add new text if value > 0
                if new_height > 0:
                    widgets['value_texts'][i] = widgets['ax_cndr'].text(
                        bar.get_x() + bar.get_width()/2., 
                        new_height + 0.5,
                        f'{new_height:.1f}', 
                        ha='center', va='bottom', 
                        fontsize=7, fontweight='bold'
                    )
        
        # Update x-tick labels with SVIDs
        widgets['ax_cndr'].set_xticklabels(svid_labels, rotation=45, ha='right', fontsize=8)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        if 'timestamp_text' not in widgets:
            widgets['timestamp_text'] = widgets['ax_cndr'].text(
                0.02, 0.98, f"Last: {timestamp}", 
                transform=widgets['ax_cndr'].transAxes,
                fontsize=8, color='green', 
                verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8)
            )
        else:
            widgets['timestamp_text'].set_text(f"Last: {timestamp}")
        
        # Redraw canvas
        widgets['canvas_cndr'].draw_idle()
        
    except Exception as e:
        print(f"Error updating real-time plot for {rt_name}: {e}")
```

## 3. Add this function for a LINE PLOT option (alternative view):

```python
def create_line_plot_view(parent_frame, rt_name, bg_color):
    """Create a line plot that shows CNDR trends over time"""
    frame_line_plot = tk.LabelFrame(parent_frame, text=f"CNDR TREND OVER TIME ({rt_name})", bg=bg_color,
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=2, pady=2
    )
    frame_line_plot.grid(row=4, column=3, padx=2, pady=2, sticky="nsew")
    frame_line_plot.grid_rowconfigure(0, weight=1)
    frame_line_plot.grid_columnconfigure(0, weight=1)
    
    fig_line = Figure(figsize=(5.2, 3.6), dpi=100)
    ax_line = fig_line.add_subplot(111)
    
    # Initialize line plot with 18 lines (one for each channel)
    colors = plt.cm.tab20(np.linspace(0, 1, 18))
    lines = []
    for i in range(18):
        line, = ax_line.plot([], [], label=f"CH{i+1}", color=colors[i], linewidth=1.5, alpha=0.7)
        lines.append(line)
    
    ax_line.set_title(f"CNDR Trend ({rt_name})", fontsize=11, fontweight='bold')
    ax_line.set_xlabel("Time (updates)", fontsize=9)
    ax_line.set_ylabel("CNDR Value", fontsize=9)
    ax_line.set_ylim(0, 60)
    ax_line.set_xlim(0, 50)  # Show last 50 updates
    ax_line.grid(True, alpha=0.3, linestyle='--')
    ax_line.legend(loc='upper right', fontsize=6, ncol=3)
    
    canvas_line = FigureCanvasTkAgg(fig_line, master=frame_line_plot)
    canvas_line.draw()
    canvas_line.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    
    # Store references
    if rt_name == "RT1":
        rt1_widgets['fig_line'] = fig_line
        rt1_widgets['ax_line'] = ax_line
        rt1_widgets['canvas_line'] = canvas_line
        rt1_widgets['lines'] = lines
        rt1_widgets['time_points'] = []
        rt1_widgets['cndr_history_matrix'] = [[] for _ in range(18)]
    elif rt_name == "RT2":
        rt2_widgets['fig_line'] = fig_line
        rt2_widgets['ax_line'] = ax_line
        rt2_widgets['canvas_line'] = canvas_line
        rt2_widgets['lines'] = lines
        rt2_widgets['time_points'] = []
        rt2_widgets['cndr_history_matrix'] = [[] for _ in range(18)]
    elif rt_name == "RT3":
        rt3_widgets['fig_line'] = fig_line
        rt3_widgets['ax_line'] = ax_line
        rt3_widgets['canvas_line'] = canvas_line
        rt3_widgets['lines'] = lines
        rt3_widgets['time_points'] = []
        rt3_widgets['cndr_history_matrix'] = [[] for _ in range(18)]
    
    return frame_line_plot

def update_line_plot(rt_name):
    """Update the line plot with new data"""
    if rt_name == "RT1":
        widgets = rt1_widgets
    elif rt_name == "RT2":
        widgets = rt2_widgets
    elif rt_name == "RT3":
        widgets = rt3_widgets
    else:
        return
    
    if 'lines' not in widgets or 'cndr_entries' not in widgets:
        return
    
    try:
        # Get current CNDR values
        current_values = []
        for i in range(min(18, len(widgets['cndr_entries']))):
            try:
                value = float(widgets['cndr_entries'][i].get() or 0)
            except:
                value = 0
            current_values.append(value)
        
        # Add time point
        if 'time_points' not in widgets:
            widgets['time_points'] = []
        if 'cndr_history_matrix' not in widgets:
            widgets['cndr_history_matrix'] = [[] for _ in range(18)]
        
        widgets['time_points'].append(len(widgets['time_points']))
        
        # Keep only last 50 points
        if len(widgets['time_points']) > 50:
            widgets['time_points'].pop(0)
            for i in range(18):
                if len(widgets['cndr_history_matrix'][i]) > 50:
                    widgets['cndr_history_matrix'][i].pop(0)
        
        # Add current values to history
        for i in range(18):
            widgets['cndr_history_matrix'][i].append(current_values[i] if i < len(current_values) else 0)
        
        # Update lines
        for i in range(18):
            if i < len(widgets['lines']):
                widgets['lines'][i].set_data(widgets['time_points'], widgets['cndr_history_matrix'][i])
        
        # Adjust x-axis limits
        widgets['ax_line'].set_xlim(0, max(50, len(widgets['time_points'])))
        
        # Redraw
        widgets['canvas_line'].draw_idle()
        
    except Exception as e:
        print(f"Error updating line plot for {rt_name}: {e}")
```

## 4. Add plot type toggle buttons (in `create_rt_display_widgets`):

```python
# Add this after creating the plot frame
plot_type_var = StringVar(value="bar")

# Frame for plot controls
plot_controls_frame = Frame(frame_cndr_plot, bg=bg_color)
plot_controls_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))

# Plot type toggle buttons
tk.Radiobutton(plot_controls_frame, text="Bar Plot", variable=plot_type_var, value="bar",
               bg=bg_color, font=("Calibri", 9)).pack(side=LEFT, padx=5)
tk.Radiobutton(plot_controls_frame, text="Line Plot", variable=plot_type_var, value="line",
               bg=bg_color, font=("Calibri", 9)).pack(side=LEFT, padx=5)

# Refresh button
refresh_btn = tk.Button(plot_controls_frame, text="Refresh Plot", font=("Calibri", 9),
                       command=lambda: update_real_time_cndr_plot(rt_name))
refresh_btn.pack(side=LEFT, padx=5)

# Auto-refresh checkbox
auto_refresh_var = BooleanVar(value=True)
auto_refresh_cb = tk.Checkbutton(plot_controls_frame, text="Auto-refresh", variable=auto_refresh_var,
                                 bg=bg_color, font=("Calibri", 9))
auto_refresh_cb.pack(side=LEFT, padx=5)

# Store plot controls
if rt_name == "RT1":
    rt1_widgets['plot_type_var'] = plot_type_var
    rt1_widgets['auto_refresh_var'] = auto_refresh_var
elif rt_name == "RT2":
    rt2_widgets['plot_type_var'] = plot_type_var
    rt2_widgets['auto_refresh_var'] = auto_refresh_var
elif rt_name == "RT3":
    rt3_widgets['plot_type_var'] = plot_type_var
    rt3_widgets['auto_refresh_var'] = auto_refresh_var
```

## 5. Modify the main update function to include plot updates:

```python
# In the process_rt_data function, after updating all entries, add:

# Update the real-time plot
if widgets.get('auto_refresh_var', BooleanVar(value=True)).get():
    update_real_time_cndr_plot(rt_name)
    
# Optionally update line plot if it exists
if 'fig_line' in widgets:
    update_line_plot(rt_name)
```

## 6. Add this function for smooth animations:

```python
def animate_plot_transition(rt_name, old_values, new_values, duration=0.3):
    """Animate smooth transition between old and new values"""
    if rt_name == "RT1":
        widgets = rt1_widgets
    elif rt_name == "RT2":
        widgets = rt2_widgets
    elif rt_name == "RT3":
        widgets = rt3_widgets
    else:
        return
    
    if 'bars_cndr' not in widgets:
        return
    
    frames = 10  # Number of animation frames
    steps = []
    
    # Calculate intermediate steps
    for frame in range(frames):
        step_values = []
        for i in range(len(old_values)):
            if i < len(new_values):
                diff = new_values[i] - old_values[i]
                step_value = old_values[i] + (diff * (frame + 1) / frames)
                step_values.append(step_value)
        steps.append(step_values)
    
    # Animate each frame
    def animate_frame(frame_idx):
        if frame_idx < len(steps):
            step_values = steps[frame_idx]
            for i, bar in enumerate(widgets['bars_cndr']):
                if i < len(step_values):
                    bar.set_height(step_values[i])
            
            widgets['canvas_cndr'].draw_idle()
            
            # Schedule next frame
            if frame_idx + 1 < len(steps):
                window.after(int(duration * 1000 / frames), lambda: animate_frame(frame_idx + 1))
    
    # Start animation
    animate_frame(0)
```

## 7. Add matplotlib colormap import at the top:

```python
# Add to imports at the top
import numpy as np
import matplotlib.pyplot as plt
```

## Key Features of the Dynamic Plot:

1. **Real-time Updates**: The plot continuously updates as new data arrives
2. **Smooth Animations**: Bars animate smoothly between values
3. **Color Coding**: 
   - Orange: 0-20 (Low)
   - Red: 20-40 (Medium) 
   - Blue: 40-60 (High)
   - Gray: Out of range
4. **Value Labels**: Current values displayed on top of bars
5. **Timestamp**: Shows last update time
6. **Interactive Controls**:
   - Toggle between bar and line plots
   - Auto-refresh toggle
   - Manual refresh button
7. **Line Plot Option**: Shows CNDR trends over time for each channel
8. **Responsive Design**: Plot adjusts to available space

## How to Use:

1. **Auto-refresh**: Check the "Auto-refresh" box for continuous updates
2. **Plot Type**: Switch between "Bar Plot" (current values) and "Line Plot" (trend over time)
3. **Manual Refresh**: Click "Refresh Plot" button if auto-refresh is off

The plot will now **dynamically update** every time new data is received, creating a live monitoring experience. The bars will smoothly transition between values, and the colors will change based on the CNDR value ranges.

And similarly for RT2 and RT3.

I'll show you visually how the dynamic plots will look with different states. Here's a comprehensive example of what you'll see:

## **1. INITIAL STATE (No Data)**

```
┌──────────────────────────────────────────────────────┐
│           REAL-TIME CNDR VS SVID (RT1)               │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 60 ┤                                                  │
│    │                                                  │
│ 50 ┤                                                  │
│    │                                                  │
│ 40 ┤                                                  │
│    │                                                  │
│ 30 ┤                                                  │
│    │                                                  │
│ 20 ┤                                                  │
│    │                                                  │
│ 10 ┤                                                  │
│    │                                                  │
│  0 ┼──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬──│
│      CH1 CH2 CH3 CH4 CH5 CH6 CH7 CH8 CH9 CH10CH11CH12│
│                                                      │
│  Last: --:--:--                                      │
└──────────────────────────────────────────────────────┘
[Bar Plot] ● [Line Plot] ○ [Refresh] [✓ Auto-refresh]
```

## **2. DATA FLOWING IN (Active Monitoring)**

```
┌──────────────────────────────────────────────────────┐
│           REAL-TIME CNDR VS SVID (RT1)               │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 60 ┤                      ██ 42.5                    │
│    │                 ████  ██                        │
│ 50 ┤                ██  ██ ██                        │
│    │                ██  ██ ██  ████  ████  ████      │
│ 40 ┤                ██  ██ ██  ██ ██ ██ ██ ██ ██     │
│    │    38.2 ████   ██  ██ ██  ██ ██ ██ ██ ██ ██     │
│ 30 ┤    ██ ██ ██ ██ ██  ██ ██  ██ ██ ██ ██ ██ ██     │
│    │ 25.1██ ██ ██ ██ ██  ██ ██  ██ ██ ██ ██ ██ ██    │
│ 20 ┤    ██ ██ ██ ██ ██  ██ ██  ██ ██ ██ ██ ██ ██     │
│    │    ██ ██ ██ ██ ██  ██ ██  ██ ██ ██ ██ ██ ██     │
│ 10 ┤    ██ ██ ██ ██ ██  ██ ██  ██ ██ ██ ██ ██ ██     │
│    │    ██ ██ ██ ██ ██  ██ ██  ██ ██ ██ ██ ██ ██     │
│  0 ┼────██─██─██─██─██──██─██──██─██─██─██─██─██─────│
│      G01 G02 G03 G05 G07 G08 G10 G12 G14 G16 G18 G19 │
│                                                      │
│  Last: 14:32:45                                      │
└──────────────────────────────────────────────────────┘
[Bar Plot] ● [Line Plot] ○ [Refresh] [✓ Auto-refresh]
```

**Color Legend in Bars:**
- 🟠 **ORANGE** (0-20): CH7 (18.5), CH9 (15.2)
- 🔴 **RED** (20-40): CH1 (25.1), CH2 (38.2), CH4 (35.7), CH6 (32.4)
- 🔵 **BLUE** (40-60): CH3 (42.5), CH8 (45.3), CH10 (48.1), CH12 (52.7)

## **3. LINE PLOT VIEW (Trend Over Time)**

```
┌──────────────────────────────────────────────────────┐
│           CNDR TREND OVER TIME (RT1)                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│ 60 ┤                                                •│
│    │                                              •• │
│ 50 ┤          CH3 ─────────────────────•─────────•   │
│    │                    CH10 ───────•──•───────•     │
│ 40 ┤        CH2 ───────•───────•────•────•───•       │
│    │      CH1 •─────•──•────•──•────•────•──• CH12   │
│ 30 ┤    CH4 •──•───•──•───•───•───•────•─•────•──•   │
│    │  CH6 •─•───•──•──•───•──•───•───•───•───•───•   │
│ 20 ┤ CH7 ••──•──•──•──•──•──•──•──•───•───•───•──•   │
│    │ CH9 ••─•──•──•──•──•──•──•──•──•───•───•───•    │
│ 10 ┤      ••─•──•──•──•──•──•──•──•──•───•───•──•    │
│    │        ••─•──•──•──•──•──•──•──•──•───•───•     │
│  0 ┼────────•••─────────────────────────────────────│
│       0    10    20    30    40    50               │
│                    Time (updates)                   │
│                                                      │
│  Legend: CH1-CH18 (colored lines)                   │
└──────────────────────────────────────────────────────┘
[Bar Plot] ○ [Line Plot] ● [Refresh] [✓ Auto-refresh]
```

## **4. ANIMATION IN PROGRESS (Smooth Transition)**

**Frame 1:**
```
    CH3: ████ 25.0 → ████████ 42.5
    (Smoothly growing from orange to blue)
```

**Frame 5 (Mid-transition):**
```
    CH3: ███████ 34.2
    (Transition color: orange-red mix)
```

**Frame 10 (Final):**
```
    CH3: ████████ 42.5
    (Final blue color)
```

## **5. MULTIPLE RT VIEWS SIDE-BY-SIDE**

```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│     RT1         │ │     RT2         │ │     RT3         │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│   ██ 42.5       │ │   ████ 38.2     │ │   ███ 45.3      │
│  ██ ██          │ │  ██ ██          │ │  ██ ██          │
│  ██ ██  ████    │ │  ██ ██  ████    │ │  ██ ██  ████    │
│  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │
│  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │
│  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │
│  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │
│  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │ │  ██ ██  ██ ██   │
│ G01 G03 G07 G12 │ │ G02 G04 G08 G14 │ │ G05 G09 G11 G16 │
│ Last: 14:32:45  │ │ Last: 14:32:46  │ │ Last: 14:32:47  │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## **6. DATA PATTERNS YOU'LL SEE:**

### **A. Normal Operation:**
```
Healthy satellites show stable high CNDR values (Blue bars)
┌─────────────────┐
│ ████████ 55.2   │
│ ████████ 58.7   │
│ ████████ 52.3   │
│ ███████ 48.5    │
└─────────────────┘
```

### **B. Satellite Acquisition:**
```
Watching a satellite being acquired (growing bars)
Time 1: CH5 █ 15.2 (orange)
Time 2: CH5 ███ 28.7 (red) 
Time 3: CH5 ██████ 42.1 (blue)
```

### **C. Signal Loss:**
```
Satellite signal degrading (shrinking bars)
Time 1: CH8 ████████ 52.3 (blue)
Time 2: CH8 ████ 35.1 (red)
Time 3: CH8 █ 12.4 (orange)
Time 4: CH8  0.0 (gray)
```

### **D. Multiple RT Comparison:**
```
RT1: CH3 ████████ 55.2  (Strong signal)
RT2: CH3 ███ 32.1       (Weaker signal)
RT3: CH3 █ 18.7         (Very weak)
```

## **7. GUI INTEGRATION VIEW:**

```
┌───────────────────────────────────────────────────────────────────┐
│ SPS TELEMETRY AND COMMAND INTERFACE: GAGANYAAN                    │
├───────────────────────────────────────────────────────────────────┤
│ [RT1] ● [RT2] ○ [RT3] ○                                           │
├───────────────────────────────────────────────────────────────────┤
│ COUNTERS          │ TRACKING INFO       │ REAL-TIME CNDR VS SVID  │
│ Update: 125       │ CH SVID CNDR ANT... │                         │
│ SW RST: 2         │ 1  G01  42.5  1 ... │  60 ┤                  █│
│ HW RST: 0         │ 2  G02  38.2  1 ... │     │                ███│
│ TSM: 45           │ 3  G03  55.2  2 ... │  50 ┤              ██ ██│
│                   │ 4  G05  35.7  2 ... │     │              ██ ██│
│ TIME              │ 5  G07  18.5  3 ... │  40 ┤              ██ ██│
│ Sys: W1234 456.12s│ 6  G08  45.3  3 ... │     │    38.2 ████ ██ ██│
│ Sync: W1234 456.1s│ 7  G10  48.1  4 ... │  30 ┤    ██ ██ ██ ██ ██│
│ PPS: W1234 456.0s │ 8  G12  52.7  4 ... │     │ 25.1██ ██ ██ ██ ██│
│                   │ ...                 │  20 ┤    ██ ██ ██ ██ ██│
│ STATE VECTOR      │                     │     │    ██ ██ ██ ██ ██│
│ X: 1234.56 m      │ MODE & PORT         │  10 ┤    ██ ██ ██ ██ ██│
│ Vx: 12.34 m/s     │ TM: 0 SWDT: 1 ...   │     │    ██ ██ ██ ██ ██│
│ ...               │                     │   0 ┼────██─██─██─██─██│
│                   │                     │      G01 G03 G07 G12 G16│
│                   │                     │                         │
│                   │                     │  Last: 14:32:45         │
│                   │                     │ [Bar]●[Line]○[Refresh]  │
└───────────────────────────────────────────────────────────────────┘
```

## **8. WHAT YOU'LL EXPERIENCE:**

1. **Live Updates**: Bars smoothly grow/shrink as values change
2. **Color Changes**: Instant visual feedback on signal quality
3. **Value Labels**: Exact numbers displayed on top of bars
4. **Timestamp**: Always shows when last data was received
5. **Multi-RT**: Each RT has its own independent, updating plot
6. **Trend View**: Line plot shows historical patterns
7. **Interactive**: Switch views, refresh manually, or let it auto-update

The plot becomes a **living visualization** of your satellite signal health, with bars that:
- **Pulse** when values change rapidly
- **Transition smoothly** between colors as values cross thresholds
- **Show trends** over time in the line view
- **Provide instant visual status** of all 18 channels simultaneously

You'll be able to watch satellites being acquired, track signal quality degradation, monitor multiple RTs side-by-side, and see patterns emerge over time - all in real-time!


=================================================


I'll provide you with two options for PVT data logging: **with headers** (standard CSV) and **without headers** (simple data-only format). Here's the complete solution:

## 1. Add Configuration Variables at the Top:

```python
# Add these to your global variables section
LOG_WITH_HEADERS = True  # Set to False for header-less CSV
LOG_RAW_DATA = True      # Log raw hex data
LOG_SYNC_DATA = True     # Log sync time data
LOG_PVT_DATA = True      # Log PVT data
```

## 2. Modified File Logging Functions:

```python
def write_to_rawh2(data, rt_name, project_name):
    """Write raw data to file with or without headers"""
    if not LOG_RAW_DATA:
        return
    
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "Rawh2")
    
    if LOG_WITH_HEADERS:
        header = ['TimeStamp', 'RAW_DATA']
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(header)
            writer.writerow(data)
    else:
        # Header-less format - just data
        with open(file_name, mode='a', newline='') as file:
            file.write(f"{data[0]},{data[1]}\n")

def write_to_SYN(data, rt_name, project_name):
    """Write sync time data to file with or without headers"""
    if not LOG_SYNC_DATA:
        return
    
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "Sync")
    
    if LOG_WITH_HEADERS:
        header = ['TimeStamp', 'SYN_SECOND', 'SYN_NANOSECOND', 'SYN_WEEKNUMBER']
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(header)
            writer.writerow(data)
    else:
        # Header-less format
        with open(file_name, mode='a', newline='') as file:
            file.write(f"{','.join(map(str, data))}\n")

def write_to_pvt(data, rt_name, project_name):
    """Write PVT data to file with or without headers"""
    if not LOG_PVT_DATA:
        return
    
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "PVT")
    
    if LOG_WITH_HEADERS:
        header = ['TimeStamp','Counter','Sys_Second','Sys_NanoSecond','Sys_WeekNumber',
                 'PPS_Second','PPS_NanoSecond','PPS_WeekNo','PPS_3D FIX','PPS_LEAP SEC',
                 'TSM_Counter','Update Counter',
                 'Checksum','Checksum 2','PDOP','Clock_bais','InterSystem_bais','Drift','Inter_System_Drift',
                 'POS_X','POS_Y','POS_Z','POS_VX','POS_VY','POS_VZ',
                 'ESt_X','EST_Y','EST_Z','EST_VX','EST_VY','EST_VZ',
                 'ACQ1','ACQ2','ACQ3','ACQ4',
                 'TM_SEL','SWD','HWDT','SBASEN','SYS_MODE','REC_MODE','TIME_MODE','ALM_AV','TIME_AV','POS_MODE','POS_AV',
                 'SW_RESET_COUNTER','HW_RESET_COUNTER','SW_RESET_ID','SPS_ID','SOL_MODE',
                 'PORT_CONFIG1','PORT_CONFIG2','PORT_CONFIG3','PORT_CONFIG4',
                 'NAVIC_MSG_22_COUNTER','NAVIC_MSG_CMD_COUNTER','LEO_SAT_ID','NO_OF_SAT_TRACKED','NAVIC_CMD_VAR',
                 'ODP_EST_FLAG','ODP_EN','PHC_USG','PHC_EN','EPH_RT','MN_VON','NUM_SPS',
                 'LAST_CMD_EXE','LAST_RESET_TIME','CMD_BASED_RT','TOTAL_CMD_COUNTER',
                 'RT_ID','MISSION_PHASE','FMEM','CR_AID','FULL_CTRL','S_ID',
                 'LIG-1','LIG-2','LIG-3','LIG-4','LIN-1','LIN-2','PRIME_NGC',
                 'Rng_L','Orbit_Phase','Iono_C','Iono_Sm','Cr_Smo','Vel_sm','RAIM',
                 'PR_Rej','Pr_Bf_Sync','Cfg_loop','int_crd_tst','Elev_En','Rst_Flag',
                 'ODP_Rst_Sp','Cold_Vis','Navic_Msg_En',
                 'DUAL_CMD_COUNTER','SPS_CMD_COUNTER',
                 'NRFFC_RESET_COUNTER1','NRFFC_RESET_COUNTER2',
                 'GRFFC_RESET_COUNTER1','GRFFC_RESET_COUNTER2',
                 'GRFFC_RESET_COUNTER3','GRFFC_RESET_COUNTER4']
        
        # Add channel data headers
        bit_names = ["A","T","D","E","P","H","R","P1_","I","S","SR","E1_"]
        for ch in range(1, 19):
            header.append(f'CH{ch}')
            header.append(f'SVID{ch}')
            header.append(f'CNDR{ch}')
            for bit in bit_names:
                header.append(f'{bit}{ch}')
            header.append(f'IODE{ch}')
            header.append(f'PR_cm_{ch}')
            header.append(f'DR_ms_{ch}')
            header.append(f'ELEV_{ch}')
        
        with open(file_name, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(header)
            writer.writerow(data)
    else:
        # Header-less format - optimized for data processing
        with open(file_name, mode='a', newline='') as file:
            # Write all data as a single comma-separated line
            line_data = []
            for item in data:
                if isinstance(item, (int, float)):
                    line_data.append(str(item))
                elif item is None:
                    line_data.append('')
                else:
                    # Escape commas in strings
                    item_str = str(item).replace(',', ';')
                    line_data.append(item_str)
            
            file.write(','.join(line_data) + '\n')
```

## 3. Alternative: SIMPLE Column-Based Format (No Headers):

```python
def write_to_pvt_simple(data, rt_name, project_name):
    """Write PVT data in simple column format without headers"""
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "PVT_Simple")
    
    # Define column positions (0-based)
    COLUMNS = {
        'timestamp': 0,
        'counter': 1,
        'sys_sec': 2,
        'sys_nanosec': 3,
        'sys_week': 4,
        'cndr_ch1': 100,  # Example - you need to map all columns
        # ... add all column mappings
    }
    
    with open(file_name, mode='a', newline='') as file:
        file.write(','.join(map(str, data)) + '\n')
```

## 4. Add GUI Controls for Logging Options:

Add this to your `connect_menu_init()` function, in the COM MANAGER frame:

```python
# Add logging controls to frame1 (COM MANAGER)
logging_frame = LabelFrame(frame1, text="  LOGGING OPTIONS  ", 
                          bg="burlywood", fg="dark green",
                          font=("Calibri", 10, "bold"),
                          relief="solid", bd=1)
logging_frame.grid(row=3, column=0, columnspan=8, sticky="ew", padx=2, pady=5)

# Header toggle
header_var = BooleanVar(value=LOG_WITH_HEADERS)
header_cb = Checkbutton(logging_frame, text="CSV Headers", variable=header_var,
                       bg="burlywood", font=("Calibri", 9),
                       command=lambda: toggle_headers(header_var))
header_cb.grid(row=0, column=0, padx=5)

# Data type toggles
raw_var = BooleanVar(value=LOG_RAW_DATA)
raw_cb = Checkbutton(logging_frame, text="Log Raw Data", variable=raw_var,
                    bg="burlywood", font=("Calibri", 9),
                    command=lambda: toggle_logging('raw', raw_var))
raw_cb.grid(row=0, column=1, padx=5)

sync_var = BooleanVar(value=LOG_SYNC_DATA)
sync_cb = Checkbutton(logging_frame, text="Log Sync Data", variable=sync_var,
                     bg="burlywood", font=("Calibri", 9),
                     command=lambda: toggle_logging('sync', sync_var))
sync_cb.grid(row=0, column=2, padx=5)

pvt_var = BooleanVar(value=LOG_PVT_DATA)
pvt_cb = Checkbutton(logging_frame, text="Log PVT Data", variable=pvt_var,
                    bg="burlywood", font=("Calibri", 9),
                    command=lambda: toggle_logging('pvt', pvt_var))
pvt_cb.grid(row=0, column=3, padx=5)

# Log directory button
log_dir_btn = Button(logging_frame, text="Open Log Dir", width=12,
                    font=("Calibri", 9), bg="lightblue",
                    command=open_log_directory)
log_dir_btn.grid(row=0, column=4, padx=5)

# Add callback functions
def toggle_headers(var):
    global LOG_WITH_HEADERS
    LOG_WITH_HEADERS = var.get()
    status_var.set(f"CSV Headers: {'ON' if LOG_WITH_HEADERS else 'OFF'}")

def toggle_logging(log_type, var):
    global LOG_RAW_DATA, LOG_SYNC_DATA, LOG_PVT_DATA
    if log_type == 'raw':
        LOG_RAW_DATA = var.get()
    elif log_type == 'sync':
        LOG_SYNC_DATA = var.get()
    elif log_type == 'pvt':
        LOG_PVT_DATA = var.get()
    status_var.set(f"Logging {log_type}: {'ON' if var.get() else 'OFF'}")

def open_log_directory():
    import subprocess, os
    log_dir = os.getcwd()  # Current directory
    try:
        if os.name == 'nt':  # Windows
            os.startfile(log_dir)
        elif os.name == 'posix':  # Linux/Mac
            subprocess.run(['xdg-open', log_dir])
    except:
        status_var.set(f"Log directory: {log_dir}")
```

## 5. Example Output Formats:

### **A. WITH HEADERS (Standard CSV):**
```
TimeStamp,Counter,Sys_Second,Sys_NanoSecond,Sys_WeekNumber,PPS_Second,PPS_NanoSecond,...
2025-01-02 14:30:45.123,125,456.123,123456789,2345,456.000,123456000,...
2025-01-02 14:30:45.223,126,457.123,123456890,2345,457.000,123456100,...
```

### **B. WITHOUT HEADERS (Data-only CSV):**
```
2025-01-02 14:30:45.123,125,456.123,123456789,2345,456.000,123456000,38.2,25.1,...
2025-01-02 14:30:45.223,126,457.123,123456890,2345,457.000,123456100,39.1,26.2,...
```

## 6. Alternative: BINARY LOGGING (Most Efficient):

```python
import struct
import pickle

def write_to_pvt_binary(data, rt_name, project_name):
    """Write PVT data in binary format (most efficient)"""
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "PVT_Bin")
    
    # Convert data to bytes
    binary_data = pickle.dumps(data)
    
    with open(file_name, mode='ab') as file:
        file.write(binary_data)

def read_pvt_binary(file_name):
    """Read binary PVT data"""
    with open(file_name, mode='rb') as file:
        while True:
            try:
                data = pickle.load(file)
                yield data
            except EOFError:
                break
```

## 7. COMPACT FORMAT (Space-Separated):

```python
def write_to_pvt_compact(data, rt_name, project_name):
    """Write PVT data in compact space-separated format"""
    file_name = get_timestamped_filename(f"{project_name}_{rt_name}", "PVT_Compact")
    
    with open(file_name, mode='a', newline='') as file:
        # Format: timestamp value1 value2 value3 ...
        line_parts = []
        for item in data:
            if isinstance(item, float):
                line_parts.append(f"{item:.3f}")
            elif isinstance(item, int):
                line_parts.append(str(item))
            elif item is None:
                line_parts.append("NA")
            else:
                line_parts.append(str(item).replace(' ', '_'))
        
        file.write(' '.join(line_parts) + '\n')
```

## 8. Complete Logging Manager Class:

```python
class DataLogger:
    def __init__(self, project_name, rt_name):
        self.project_name = project_name
        self.rt_name = rt_name
        self.log_with_headers = True
        self.enable_raw = True
        self.enable_sync = True
        self.enable_pvt = True
        
        # Create log directory
        self.log_dir = f"logs_{datetime.now().strftime('%Y%m%d')}"
        os.makedirs(self.log_dir, exist_ok=True)
    
    def get_filename(self, data_type, extension="csv"):
        timestamp = datetime.now().strftime("%H%M%S")
        return os.path.join(self.log_dir, 
                           f"{self.project_name}_{self.rt_name}_{data_type}_{timestamp}.{extension}")
    
    def log_raw(self, hex_data):
        if not self.enable_raw:
            return
        
        filename = self.get_filename("RAW")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        if self.log_with_headers:
            with open(filename, 'a', newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(['TIMESTAMP', 'HEX_DATA', 'RT_NAME'])
                writer.writerow([timestamp, hex_data, self.rt_name])
        else:
            with open(filename, 'a') as f:
                f.write(f"{timestamp},{hex_data},{self.rt_name}\n")
    
    def log_pvt(self, pvt_dict):
        if not self.enable_pvt:
            return
        
        filename = self.get_filename("PVT")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        
        # Prepare data row
        row_data = [timestamp]
        
        # Add all PVT fields in consistent order
        fields = [
            'counter', 'sys_second', 'sys_nanosecond', 'sys_week',
            'pdop', 'pos_x', 'pos_y', 'pos_z',
            # ... add all fields
        ]
        
        for field in fields:
            row_data.append(pvt_dict.get(field, ''))
        
        if self.log_with_headers:
            with open(filename, 'a', newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(['TIMESTAMP'] + [f.upper() for f in fields])
                writer.writerow(row_data)
        else:
            with open(filename, 'a') as f:
                f.write(','.join(map(str, row_data)) + '\n')
    
    def get_log_summary(self):
        """Get summary of logged files"""
        files = os.listdir(self.log_dir)
        rt_files = [f for f in files if self.rt_name in f]
        
        summary = {
            'total_files': len(rt_files),
            'raw_files': len([f for f in rt_files if 'RAW' in f]),
            'pvt_files': len([f for f in rt_files if 'PVT' in f]),
            'sync_files': len([f for f in rt_files if 'SYNC' in f]),
            'log_dir': self.log_dir
        }
        return summary

# Initialize loggers for each RT
rt1_logger = None
rt2_logger = None
rt3_logger = None

def init_loggers():
    global rt1_logger, rt2_logger, rt3_logger
    project_name = project_name_var.get().strip()
    if not project_name or project_name.lower() == "gaganyaan":
        project_name = "GAGANYAAN"
    
    rt1_logger = DataLogger(project_name, "RT1")
    rt2_logger = DataLogger(project_name, "RT2")
    rt3_logger = DataLogger(project_name, "RT3")
```

## 9. Usage in Your Code:

In `process_rt_data`, replace the direct file writes with:

```python
# Instead of write_to_rawh2([timestamp, hexDecodedData], rt_name, project_name)
if rt_name == "RT1" and rt1_logger:
    rt1_logger.log_raw(hexDecodedData)
elif rt_name == "RT2" and rt2_logger:
    rt2_logger.log_raw(hexDecodedData)
elif rt_name == "RT3" and rt3_logger:
    rt3_logger.log_raw(hexDecodedData)

# For PVT data, create a dictionary
pvt_dict = {
    'counter': UpdateCounter,
    'sys_second': SYS_Second,
    'sys_nanosecond': SYS_NanoSecond,
    'sys_week': SYS_WeekNumber,
    'pdop': PDOP,
    'pos_x': POS_x,
    'pos_y': POS_y,
    'pos_z': POS_z,
    'pos_vx': POS_vx,
    'pos_vy': POS_vy,
    'pos_vz': POS_vz,
    # ... add all other fields
}

if rt_name == "RT1" and rt1_logger:
    rt1_logger.log_pvt(pvt_dict)
# ... similarly for RT2 and RT3
```

## 10. Output Examples:

### **Header CSV (Easy to read in Excel):**
```
TIMESTAMP,COUNTER,SYS_SECOND,SYS_NANOSECOND,SYS_WEEK,PDOP,POS_X,POS_Y,POS_Z
2025-01-02 14:30:45.123,125,456.123,123456789,2345,1.25,1234.56,5678.90,9012.34
2025-01-02 14:30:45.223,126,457.123,123456890,2345,1.23,1234.78,5679.12,9013.45
```

### **No-Header CSV (Compact, for processing):**
```
2025-01-02 14:30:45.123,125,456.123,123456789,2345,1.25,1234.56,5678.90,9012.34
2025-01-02 14:30:45.223,126,457.123,123456890,2345,1.23,1234.78,5679.12,9013.45
```

### **Space-Separated (MATLAB/Python friendly):**
```
2025-01-02_14:30:45.123 125 456.123 123456789 2345 1.250 1234.560 5678.900 9012.340
2025-01-02_14:30:45.223 126 457.123 123456890 2345 1.230 1234.780 5679.120 9013.450
```

## Key Features:

1. **Flexible Formats**: Choose between header/no-header CSV
2. **Selective Logging**: Enable/disable different data types
3. **Organized Files**: Files organized by RT and timestamp
4. **Efficient**: Binary option for high-volume logging
5. **GUI Controls**: Toggle options from the interface
6. **Easy Access**: "Open Log Dir" button to view files
7. **Project-based**: Files named with project and RT identifiers

You can now choose:
- **With Headers**: Best for manual analysis in Excel
- **Without Headers**: Best for automated data processing
- **Binary**: Best for high-speed logging
- **Compact**: Best for limited storage space
