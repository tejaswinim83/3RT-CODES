Yes! Both bar plot and line plot will work perfectly with all 18 channels. Here's the complete solution with line plot properly implemented:

## 1. First, ensure you have these imports:

```python
import numpy as np
from collections import deque
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
```

## 2. Here's the complete working `create_rt_display_widgets` function:

```python
def create_rt_display_widgets(parent_frame, rt_name, bg_color):
    """Create display widgets for each RT with real-time plots"""
    # ... [your existing widget creation code for other sections] ...
    
    # ========================== REAL-TIME PLOTS ============================
    frame_plots = tk.LabelFrame(parent_frame, text=f"REAL-TIME PLOTS ({rt_name})", bg=bg_color,
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=2, pady=2
    )
    frame_plots.grid(row=4, column=3, padx=2, pady=2, sticky="nsew")
    frame_plots.grid_rowconfigure(0, weight=1)
    frame_plots.grid_columnconfigure(0, weight=1)
    
    # Create notebook for tabs
    notebook = ttk.Notebook(frame_plots)
    notebook.grid(row=0, column=0, sticky="nsew")
    
    # --- TAB 1: BAR PLOT ---
    bar_frame = ttk.Frame(notebook)
    notebook.add(bar_frame, text="Bar Plot")
    bar_frame.grid_rowconfigure(0, weight=1)
    bar_frame.grid_columnconfigure(0, weight=1)
    
    # Create bar plot figure
    fig_bar = Figure(figsize=(5.2, 3.6), dpi=100)
    ax_bar = fig_bar.add_subplot(111)
    
    # Initialize bar plot data for 18 channels
    x_positions = np.arange(18)
    initial_values = [0] * 18
    bar_colors = ['lightgray'] * 18
    
    # Create bars for all 18 channels
    bars = ax_bar.bar(x_positions, initial_values, color=bar_colors, 
                     edgecolor='black', width=0.7, alpha=0.8)
    
    # Configure bar plot
    ax_bar.set_title(f"CNDR vs SVID ({rt_name})", fontsize=11, fontweight='bold')
    ax_bar.set_xlabel("SVID / Channel", fontsize=9)
    ax_bar.set_ylabel("CNDR Value", fontsize=9)
    ax_bar.set_ylim(0, 65)
    ax_bar.set_yticks([0, 10, 20, 30, 40, 50, 60])
    ax_bar.set_xticks(x_positions)
    ax_bar.set_xticklabels([f"CH{i+1}" for i in range(18)], rotation=45, ha='right', fontsize=8)
    ax_bar.grid(True, alpha=0.3, linestyle='--')
    fig_bar.tight_layout()
    
    # Create canvas for bar plot
    canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_frame)
    canvas_bar.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    
    # --- TAB 2: LINE PLOT ---
    line_frame = ttk.Frame(notebook)
    notebook.add(line_frame, text="Line Plot")
    line_frame.grid_rowconfigure(0, weight=1)
    line_frame.grid_columnconfigure(0, weight=1)
    
    # Create line plot figure
    fig_line = Figure(figsize=(5.2, 3.6), dpi=100)
    ax_line = fig_line.add_subplot(111)
    
    # Generate distinct colors for 18 channels
    color_cycle = plt.cm.tab20(np.linspace(0, 1, 20))
    line_colors = []
    for i in range(18):
        line_colors.append(color_cycle[i % 20])
    
    # Initialize line plots for all 18 channels
    lines = []
    for i in range(18):
        # Create line with initial empty data
        line, = ax_line.plot([], [], color=line_colors[i], linewidth=1.5, 
                           label=f"CH{i+1}", alpha=0.7, marker='o', markersize=2)
        lines.append(line)
    
    # Configure line plot
    ax_line.set_title(f"CNDR Trend - All 18 Channels ({rt_name})", fontsize=11, fontweight='bold')
    ax_line.set_xlabel("Time (updates)", fontsize=9)
    ax_line.set_ylabel("CNDR Value", fontsize=9)
    ax_line.set_ylim(0, 65)
    ax_line.set_xlim(0, 50)
    ax_line.grid(True, alpha=0.3, linestyle='--')
    
    # Create legend with 3 columns for better readability
    ax_line.legend(loc='upper left', bbox_to_anchor=(1.02, 1), 
                  fontsize=6, ncol=3, framealpha=0.7)
    fig_line.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust for legend on right
    
    # Create canvas for line plot
    canvas_line = FigureCanvasTkAgg(fig_line, master=line_frame)
    canvas_line.get_tk_widget().grid(row=0, column=0, sticky="nsew")
    
    # Draw initial plots
    canvas_bar.draw()
    canvas_line.draw()
    
    # Store all references
    plot_data = {
        # Bar plot references
        'fig_bar': fig_bar,
        'ax_bar': ax_bar,
        'canvas_bar': canvas_bar,
        'bars': bars,
        
        # Line plot references
        'fig_line': fig_line,
        'ax_line': ax_line,
        'canvas_line': canvas_line,
        'lines': lines,
        'line_colors': line_colors,
        
        # Data storage
        'line_data_x': deque(maxlen=100),  # Time points
        'line_data_y': [deque(maxlen=100) for _ in range(18)],  # CNDR values per channel
        'current_values': [0] * 18,
        'value_labels': [None] * 18,
        'update_counter': 0,
        
        # Plot notebook
        'plot_notebook': notebook,
    }
    
    # Store in the appropriate RT dictionary
    if rt_name == "RT1":
        rt1_widgets.update(plot_data)
    elif rt_name == "RT2":
        rt2_widgets.update(plot_data)
    elif rt_name == "RT3":
        rt3_widgets.update(plot_data)
    
    # Add plot controls
    add_plot_controls(frame_plots, rt_name, bg_color)
    
    return frame_plots
```

## 3. Here's the complete `add_plot_controls` function:

```python
def add_plot_controls(parent_frame, rt_name, bg_color):
    """Add control buttons for plots"""
    controls_frame = tk.Frame(parent_frame, bg=bg_color)
    controls_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
    
    # Auto-refresh checkbox
    auto_refresh_var = tk.BooleanVar(value=True)
    auto_cb = tk.Checkbutton(controls_frame, text="Auto-refresh", 
                           variable=auto_refresh_var,
                           bg=bg_color, font=("Calibri", 9))
    auto_cb.pack(side=tk.LEFT, padx=5)
    
    # Refresh button
    refresh_btn = tk.Button(controls_frame, text="Refresh Now", 
                          font=("Calibri", 9),
                          command=lambda: update_all_plots(rt_name))
    refresh_btn.pack(side=tk.LEFT, padx=5)
    
    # Clear button
    clear_btn = tk.Button(controls_frame, text="Clear Plots", 
                         font=("Calibri", 9),
                         command=lambda: clear_all_plots(rt_name))
    clear_btn.pack(side=tk.LEFT, padx=5)
    
    # Update interval label
    tk.Label(controls_frame, text="Interval:", bg=bg_color, 
             font=("Calibri", 9)).pack(side=tk.LEFT, padx=(10, 2))
    
    # Update interval dropdown
    interval_var = tk.StringVar(value="1.0")
    interval_menu = ttk.Combobox(controls_frame, textvariable=interval_var,
                               values=["0.5", "1.0", "2.0", "5.0"], 
                               width=6, font=("Calibri", 9), state="readonly")
    interval_menu.pack(side=tk.LEFT, padx=2)
    
    # Store controls
    if rt_name == "RT1":
        rt1_widgets['auto_refresh_var'] = auto_refresh_var
        rt1_widgets['refresh_btn'] = refresh_btn
        rt1_widgets['interval_var'] = interval_var
    elif rt_name == "RT2":
        rt2_widgets['auto_refresh_var'] = auto_refresh_var
        rt2_widgets['refresh_btn'] = refresh_btn
        rt2_widgets['interval_var'] = interval_var
    elif rt_name == "RT3":
        rt3_widgets['auto_refresh_var'] = auto_refresh_var
        rt3_widgets['refresh_btn'] = refresh_btn
        rt3_widgets['interval_var'] = interval_var
```

## 4. Here's the complete `update_all_plots` function:

```python
def update_all_plots(rt_name):
    """Update both bar and line plots for the specified RT"""
    try:
        if rt_name == "RT1":
            widgets = rt1_widgets
        elif rt_name == "RT2":
            widgets = rt2_widgets
        elif rt_name == "RT3":
            widgets = rt3_widgets
        else:
            return
        
        # Get current CNDR values from entries
        cndr_values = []
        svid_labels = []
        
        for i in range(18):
            if 'cndr_entries' in widgets and i < len(widgets['cndr_entries']):
                try:
                    val = float(widgets['cndr_entries'][i].get() or 0)
                except:
                    val = 0
            else:
                val = 0
            cndr_values.append(val)
            
            if 'svid_entries' in widgets and i < len(widgets['svid_entries']):
                svid = widgets['svid_entries'][i].get() or f"CH{i+1}"
            else:
                svid = f"CH{i+1}"
            svid_labels.append(svid)
        
        # Update current values
        widgets['current_values'] = cndr_values.copy()
        
        # --- UPDATE BAR PLOT ---
        if 'bars' in widgets and len(widgets['bars']) == 18:
            for i in range(18):
                bar = widgets['bars'][i]
                value = cndr_values[i]
                
                # Update bar height
                bar.set_height(value)
                
                # Update color based on value
                if 0 <= value < 20:
                    color = 'orange'
                elif 20 <= value <= 40:
                    color = 'red'
                elif 40 <= value <= 60:
                    color = 'blue'
                else:
                    color = 'gray'
                
                bar.set_color(color)
                bar.set_alpha(0.8)
                
                # Update value label on top of bar
                if widgets['value_labels'][i] is not None:
                    widgets['value_labels'][i].remove()
                
                if value > 0:
                    # Position text above bar
                    x_pos = bar.get_x() + bar.get_width() / 2
                    widgets['value_labels'][i] = widgets['ax_bar'].text(
                        x_pos, value + 0.5, f'{value:.1f}',
                        ha='center', va='bottom', fontsize=6, fontweight='bold'
                    )
            
            # Update x-tick labels with actual SVIDs
            widgets['ax_bar'].set_xticklabels(svid_labels, rotation=45, ha='right', fontsize=8)
            
            # Update timestamp
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            if 'timestamp_text_bar' not in widgets:
                widgets['timestamp_text_bar'] = widgets['ax_bar'].text(
                    0.02, 0.98, f"Last: {timestamp}",
                    transform=widgets['ax_bar'].transAxes,
                    fontsize=7, color='darkgreen', verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9)
                )
            else:
                widgets['timestamp_text_bar'].set_text(f"Last: {timestamp}")
            
            # Update the bar plot canvas
            widgets['canvas_bar'].draw_idle()
        
        # --- UPDATE LINE PLOT ---
        if 'lines' in widgets and len(widgets['lines']) == 18:
            # Increment update counter
            widgets['update_counter'] += 1
            current_time = widgets['update_counter']
            
            # Add time point
            widgets['line_data_x'].append(current_time)
            
            # Update data for all 18 channels
            for i in range(18):
                widgets['line_data_y'][i].append(cndr_values[i])
            
            # Update all 18 line plots
            for i in range(18):
                if i < len(widgets['lines']):
                    x_data = list(widgets['line_data_x'])
                    y_data = list(widgets['line_data_y'][i])
                    
                    # Update line data
                    widgets['lines'][i].set_data(x_data, y_data)
            
            # Adjust x-axis limits to show last 50 points
            if len(widgets['line_data_x']) > 0:
                visible_points = 50
                current_len = len(widgets['line_data_x'])
                start_x = max(0, current_len - visible_points)
                end_x = max(visible_points, current_len)
                widgets['ax_line'].set_xlim(start_x, end_x)
            
            # Update timestamp for line plot
            if 'timestamp_text_line' not in widgets:
                widgets['timestamp_text_line'] = widgets['ax_line'].text(
                    0.02, 0.98, f"Updates: {current_time} | Last: {timestamp}",
                    transform=widgets['ax_line'].transAxes,
                    fontsize=7, color='darkblue', verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9)
                )
            else:
                widgets['timestamp_text_line'].set_text(
                    f"Updates: {current_time} | Last: {timestamp}"
                )
            
            # Update the line plot canvas
            widgets['canvas_line'].draw_idle()
        
        print(f"✓ Plots updated for {rt_name} at {timestamp}")
        
    except Exception as e:
        print(f"✗ Error updating plots for {rt_name}: {e}")
```

## 5. Here's the complete `clear_all_plots` function:

```python
def clear_all_plots(rt_name):
    """Clear all plot data for the specified RT"""
    try:
        if rt_name == "RT1":
            widgets = rt1_widgets
        elif rt_name == "RT2":
            widgets = rt2_widgets
        elif rt_name == "RT3":
            widgets = rt3_widgets
        else:
            return
        
        # Reset bar plot
        if 'bars' in widgets:
            for bar in widgets['bars']:
                bar.set_height(0)
                bar.set_color('lightgray')
                bar.set_alpha(0.5)
        
        # Clear value labels on bars
        if 'value_labels' in widgets:
            for i, label in enumerate(widgets['value_labels']):
                if label is not None:
                    label.remove()
                widgets['value_labels'][i] = None
        
        # Reset line plot data
        if 'line_data_x' in widgets:
            widgets['line_data_x'].clear()
        
        if 'line_data_y' in widgets:
            for i in range(len(widgets['line_data_y'])):
                widgets['line_data_y'][i].clear()
        
        # Reset lines to empty
        if 'lines' in widgets:
            for line in widgets['lines']:
                line.set_data([], [])
        
        # Reset update counter
        widgets['update_counter'] = 0
        
        # Clear timestamps
        for key in ['timestamp_text_bar', 'timestamp_text_line']:
            if key in widgets and widgets[key] is not None:
                widgets[key].remove()
                widgets[key] = None
        
        # Reset current values
        widgets['current_values'] = [0] * 18
        
        # Redraw canvases
        if 'canvas_bar' in widgets:
            widgets['canvas_bar'].draw_idle()
        
        if 'canvas_line' in widgets:
            widgets['canvas_line'].draw_idle()
        
        print(f"✓ All plots cleared for {rt_name}")
        
    except Exception as e:
        print(f"✗ Error clearing plots for {rt_name}: {e}")
```

## 6. Add auto-update functionality:

```python
# Add these global variables at the top
plot_auto_update_active = False
plot_auto_update_thread = None

def start_auto_plot_updates():
    """Start background thread for automatic plot updates"""
    global plot_auto_update_active, plot_auto_update_thread
    
    if plot_auto_update_active:
        return
    
    plot_auto_update_active = True
    
    def auto_update_loop():
        while plot_auto_update_active:
            try:
                # Get update interval from each RT (default to 1.0)
                intervals = []
                for rt_name, widgets in [("RT1", rt1_widgets), ("RT2", rt2_widgets), ("RT3", rt3_widgets)]:
                    interval = 1.0
                    if 'interval_var' in widgets:
                        try:
                            interval = float(widgets['interval_var'].get())
                        except:
                            interval = 1.0
                    intervals.append((rt_name, interval))
                
                # Update each RT if auto-refresh is enabled
                for rt_name, interval in intervals:
                    widgets = None
                    if rt_name == "RT1":
                        widgets = rt1_widgets
                    elif rt_name == "RT2":
                        widgets = rt2_widgets
                    elif rt_name == "RT3":
                        widgets = rt3_widgets
                    
                    if widgets and 'auto_refresh_var' in widgets:
                        if widgets['auto_refresh_var'].get():
                            window.after(0, lambda r=rt_name: update_all_plots(r))
                
                # Sleep for shortest interval among all RTs
                min_interval = min([interval for _, interval in intervals])
                time.sleep(min_interval)
                
            except Exception as e:
                print(f"Auto-update error: {e}")
                time.sleep(1)
    
    plot_auto_update_thread = threading.Thread(target=auto_update_loop, daemon=True)
    plot_auto_update_thread.start()

def stop_auto_plot_updates():
    """Stop automatic plot updates"""
    global plot_auto_update_active
    plot_auto_update_active = False
```

## 7. Modify your data processing to trigger plot updates:

```python
def process_rt_data(rt_name, data_str):
    """Process received data for a specific RT"""
    try:
        # ... [your existing data processing code] ...
        
        # After updating CNDR entries, update plots if auto-refresh is on
        if rt_name == "RT1" and 'auto_refresh_var' in rt1_widgets:
            if rt1_widgets['auto_refresh_var'].get():
                window.after(0, lambda: update_all_plots("RT1"))
        elif rt_name == "RT2" and 'auto_refresh_var' in rt2_widgets:
            if rt2_widgets['auto_refresh_var'].get():
                window.after(0, lambda: update_all_plots("RT2"))
        elif rt_name == "RT3" and 'auto_refresh_var' in rt3_widgets:
            if rt3_widgets['auto_refresh_var'].get():
                window.after(0, lambda: update_all_plots("RT3"))
        
    except Exception as e:
        print(f"Error processing {rt_name} data: {e}")
```

## 8. Start auto-updates when your application launches:

```python
# Add this to your main application startup
def main():
    # ... [your existing initialization code] ...
    
    # Start automatic plot updates
    start_auto_plot_updates()
    
    # ... [rest of your code] ...
```

## Key Features of this Solution:

1. **Both plots work**: Bar plot AND line plot for all 18 channels
2. **Tabbed interface**: Switch between bar and line plots
3. **No freezing**: Uses `draw_idle()` and proper threading
4. **Auto-refresh**: Works with checkbox control
5. **Manual refresh**: Button for immediate updates
6. **Clear plots**: Reset all data
7. **Update interval**: Control how often plots update
8. **Timestamps**: Shows last update time on both plots
9. **Line plot with history**: Shows last 100 data points per channel
10. **Color-coded**: Distinct colors for all 18 channels
11. **Value labels**: Shows values on top of bars
12. **Legend**: Line plot has legend with all 18 channels

The line plot will show all 18 channels with different colors, and you can see the trend of each channel over time. Both plots will update smoothly without freezing!
