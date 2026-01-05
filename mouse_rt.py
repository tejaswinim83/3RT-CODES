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
