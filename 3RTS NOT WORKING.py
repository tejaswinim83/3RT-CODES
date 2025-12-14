# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 20:01:56 2025

@author: TEJASWINI M
"""

import serial
import serial.tools.list_ports
import threading
from tkinter import filedialog
import queue
from tkinter import ttk
from tkinter import *
import tkinter as tk
import time
import time as cmdtime
import csv
from tkinter import Radiobutton, StringVar
global status_var
from datetime import datetime
import os
import platform
import time as pytime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure



 
 
 
serialData=False
ser=None
counter_value=0
num_channels = 18
# Threads and running flags for SA3 and SA4
sa3_thread = None
sa3_running = False
sa4_thread = None
sa4_running = False
# Global controls
replay_running = False
replay_paused = False
jump_target_sec = None
replay_filepath = None
# GUI Entries storage
manual_entries = {}
file_entries = {}

SESSION_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
 
# All 18 bit names as per your request
bit_names = ["A","T","D","E","P","H","R","P1","I","S","SR","E1"]

# --- Header mapping for tabs ---
RT_HEADERS = {
    "RT1": ["acca1f0a", "acca1f0b"],
    "RT2": ["acca1f0c", "acca1f0d"],
    "RT3": ["acca1f0e", "acca1f0f"],
}
selected_tab = "RT1"
 
 
data_queue = queue.Queue() 


commands = {
    "playback-off": "0x0002", "playback-on": "0x0003",
    "storage-on": "0x0004", "storage-off": "0x0005",
    "sps-mvn-on": "0x0006", "sps-mvn-off": "0x0007",
    "sps-model1": "0x000A", "sps-model2": "0x000B", "sps-model3": "0x000C",
    "sps-model4": "0x000D", "sps-model5": "0x000E",
    "sps-c-s-E": "0x000F", "sps-c-s-D": "0x0010",
    "sps-iono-c-E": "0x0011", "sps-iono-c-D": "0x0012",
    "sps-raim-chk1-E": "0x0015", "sps-raim-chk1-D": "0x0016",
    "sps-raim-chk2-E": "0x0017", "sps-raim-chk2-D": "0x0018",
    "navic/1g-msg-E": "0x0025", "navic/1g-msg-D": "0x0026",
    "velocity-smoothing-E": "0x0027", "velocity-smoothing-D": "0x0028",
    "port1-conf-gps": "0x0030", "port1-conf-navic": "0x0031", "port1-conf-combained": "0x0032",
    "port1-config-gps": "0x0033", "port1-config-navic": "0x0034", "port1-config-combained": "0x0035",
    "sps iono smoothing E":"0x0038","sps iono smoothing D":"0x0039",
    "pb-ccsds on": "0x003A", "pb-ccsds off": "0x003B",
    "randomizer/scrambler on": "0x003C", "randomizer/scrambler off": "0x003D",
    "pr module new": "0x003E", "pr module old": "0x003F",
    "elevation logic D": "0x0040", "elevation logic E": "0x0041",
    "sps-sw wdt E": "0x0042", "sps-sw wdt D": "0x0043",
    "s/w model change eeprom to prom": "0x0044", "s/w model change prom to eeprom": "0x0045",
    "phase center CAL D": "0x004C", "phase center CAL E": "0x004D",
    "phase center use for SPS D": "0x004E", "phase center use for SPS E": "0x004F",
    "odp1 s/w reset": "0x0050", "odp E": "0x0051", "odp D": "0x0052",
    "odp 10s E": "0x0053", "odp 10s D": "0x0054",
    "filter init commnd": "0x0055", "odp eop E cmd": "0x0056", "odp eop D cmd": "0x0057",
    "odp AnTphc usable": "0x0058", "odp AnTphc not usable": "0x0059",
    "odp Maneuver E": "0x005A", "odp Maneuver D": "0x005B",
    "odp mode change to test mode": "0x005C", "odp mode change to normal mode": "0x005D",
    "odp mode change to disable mode": "0x005E", "odp2 s/w reset": "0x005F",
    "odp power on default config load": "0x0060", "odp clock streeing E": "0x0062",
    "odp clock streeing D": "0x0063",
    "AIS IQ data on": "0x0081", "AIS IQ data off": "0x0082",
    "lais fe reset": "0x0083", "cais fe reset": "0x0084",
    "test demond prbs E": "0x0085", "test demond prbs D": "0x0086",
    "test IQ prbs E": "0x0087", "test IQ prbs D": "0x0088",
    "sps l1 track thres": "0x80B1", "sps l1 acq thres": "0x83B1",
    "sps-c limit value": "0x86B1", "sps-c restart val": "0x87B1",
    "sps iono alpha fac word": "0x90B1", "sps iono height": "0x91B1",
    "sps-storage sampling rate": "0x9300","pb frame length word": "0xAC00",
    "week roll over value": "0xAB00", "pps h/w delay":"0xB000",
    "Elevation Angle Threshold":"0xB100","Navic Tel ID": "0xB300",
    "AIS ch1 thrld_num": "0xC0B1", "AIS ch1 thrld_demon": "0xC1B1",
    "AIS ch1 thrld_ffft": "0xC2B1", "AIS ch1 sync trans": "0xCCB1",
    "AIS ch2 thrld_num": "0xC3B1", "AIS ch2 thrld_demon": "0xC4B1",
    "AIS ch2 thrld_ffft": "0xC5B1", "AIS ch2 sync trans": "0xCDB1",
    "AIS ch3 thrld_num": "0xC6B1", "AIS ch3 thrld_demon": "0xC7B1",
    "AIS ch3 thrld_ffft": "0xC8B1", "AIS ch3 sync trans": "0xCEB1",
    "AIS ch4 thrld_num": "0xC9B1", "AIS ch4 thrld_demon": "0xCAB1",
    "AIS ch4 thrld_ffft": "0xCBB1", "AIS ch4 sync trans": "0xCFB1",
   
}


 

 

 
# BUS command codes
bus_command_buttons = {}
bus_commands = [
    ("Reset", 0x01),
    ("HWDT Enable", 0x02),
    ("HWDT Disable", 0x03),
    ("SWDT Enable", 0x04),
    ("SWDT Disable", 0x05),
    ("DC/DC ON", 0x06),
    ("DC/DC OFF", 0x07),
]

# SUBADDRESS HEADERS (dynamic per RT)
SAx_HEADERS = {
    "RT1": [0x01, 0x02, 0x03, 0x04],
    "RT2": [0x05, 0x06, 0x07, 0x08],
    "RT3": [0x09, 0x0A, 0x0B, 0x0C],
}

class Graphics:
    pass


def make_scrollable_tab(parent):
    # Creates a scrollable frame inside the parent
    canvas = tk.Canvas(parent, bg="burlywood", highlightthickness=0)
    scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x.grid(row=1, column=0, sticky="ew")
    content = tk.Frame(canvas, bg="burlywood")
    canvas.create_window((0, 0), window=content, anchor="nw")
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    for i in range(10): content.grid_columnconfigure(i, weight=1)
    def on_frame_configure(event): canvas.configure(scrollregion=canvas.bbox("all"))
    content.bind("<Configure>", on_frame_configure)
    def bind_mousewheel(widget):
        # Mouse wheel cross-platform
        system = platform.system()
        if system in ['Windows', 'Darwin']:
            widget.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        else:
            widget.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            widget.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    bind_mousewheel(canvas)
    return content


def connect_menu_init():
    global window, notebook, widgets, project_name_var,root_frame
    global Button,Label,LabelFrame,Entry,Tk,NORMAL,END,Frame
    global root,frame1,connect_btn,refresh_btn,graph,output_text,file_bd,file_entry,file_entry1,datetime_label,Canvas
    global frame2,update_entry,update_count,counter,counter_entry,window,tsm_counter_entry
    global frame3,time_entry,nanotime_entry,week_entry,time_entry1,nanotime_entry1,week_entry1,time_entry2,nanotime_entry2,week_entry2,time_h2,nanotime_h2,weeks_h2
    global frame5,position_label,position_label1,position_label2,position_label3,position_label4,position_label5,velocity_label,velocity_label1,velocity_label2,velocity_label3,velocity_label4,velocity_label5
    global frame5,velocity_entry,velocity_entry1,velocity_entry2,velocity_entry3,velocity_entry4,velocity_entry5,position_entry,position_entry1,position_entry2,position_entry3,position_entry4,position_entry5
    global frame6,validation,flags,flag
    global frame7,Checksum,csm,csm1,csm2
    global frame8,channel,svid,cndr,a,t,d,E,p,h,r,P,i,s,sr,e,iode,pr,dr,elev
    global ch1,ch2,ch3,ch4,ch5,ch6,ch7,ch8,ch9,ch10,ch11,ch12,ch13,ch14,ch15,ch16,ch17,ch18
    global svid1,svid2,svid3,svid4,svid5,svid6,svid7,svid8,svid9,svid10,svid11,svid12,svid13,svid14,svid15,svid16,svid17,svid18
    global cndr1,cndr2,cndr3,cndr4,cndr5,cndr6,cndr7,cndr8,cndr9,cndr10,cndr11,cndr12,cndr13,cndr14,cndr15,cndr16,cndr17,cndr18
    global iode1,iode2,iode3,iode4,iode5,iode6,iode7,iode8,iode9,iode10,iode11,iode12,iode13,iode14,iode15,iode16,iode17,iode18
    global pr1,pr2,pr3,pr4,pr5,pr6,pr7,pr8,pr9,pr10,pr11,pr12,pr13,pr14,pr15,pr16,pr17,pr18
    global dr1,dr2,dr3,dr4,dr5,dr6,dr7,dr8,dr9,dr10,dr11,dr12,dr13,dr14,dr15,dr16,dr17,dr18
    global elev1,elev2,elev3,elev4,elev5,elev6,elev7,elev8,elev9,elev10,elev11,elev12,elev13,elev14,elev15,elev16,elev17,elev18
    global frame9,isb,cb,port_conf,port_conf1,port_conf2,port_conf3,sol_mode,sps_id
    global frame10,pdop
    global frame11,drift,isd,rdl,rdm
    global frame12,Table,Last_cmd_ex,TSM_update_counter,SI,crs,delta_n,ma,cuc,ecc,cus,sqrt_a,toe,cic,omega0,incl_0,cis,crc,ap,omega_dot,incl_dot,delta_n,af0,af1,af2_tgd,sbas_ch7,sbas_ch8,sbas_ch9,sbas_ch10
    global frame12,sw_rst_c,hw_rst_c,sw_rst_id,navic_msg_22_c,navic_msg_cmd_c,leo_sat_id,no_sat_trck,navic_cmd_var,last_cmd_exe,last_reset_time,cmd_based_rt,total_cmd_counter,dual_cmd_c_rt,spu_cmd_c_rt
    global frame13,frame_bus,bus_var,dataword_entry
    global frame14,entry_ub1,entry_uw2,acq1,acq2,acq3,acq4,bit_to_entrylist,status_var,rt_address_entry,bus_selected
    global frame15,tm,swdt,hwdt,sbasen,sys_mode,rec_mode,time_mode,alm_av,time_av,pos_mode,pos_av,rt_id,miss_ph,fmem,cr_aid,full_cntr,s_id,lig_1,lig_2,lig_3,lig_4,lin_1,lin_2,prime_ngc
    global rng_l,orbit_phase,iono_c,iono_sm,cr_smo,vel_sm,raim,pr_rej,pr_bf_sync,cfg_loop,int_crd_tst,elev_e,rst_flag,odp_rst_sf,cold_vis,nav_msg_e
    global odp_est,odp_en,phc_usg,phc_en,eph_rt,mnvon,numsps,nrff_rst_counter1,nrff_rst_counter2,grff_rst_counter1,grff_rst_counter2,grff_rst_counter3,grff_rst_counter4,fix_3d,leap
    global frame_cndr_plot,ax_cndr,canvas_cndr,cmd_btn,btn_replay,jump_entry,btn_pause_resume,project_entry

    window = tk.Tk()
    window.title("GAGAN 18 CHANNNEL INTERFACE")
    window.configure(bg="burlywood")

    # Maximized window + configure grid for footer
    try:
        window.state('zoomed')
    except:
        window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}+0+0")
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(0, weight=1)

    project_name_var = tk.StringVar(value="GAGANYAAN")

    # Header highlight logic
    def highlight_tab(tab_name):
        for i in range(tab_notebook.index("end")):
            tab = tab_notebook.tab(i, "text")
            style = "selected.TNotebook.Tab" if tab == tab_name else "TNotebook.Tab"
            tab_notebook.tab(i, style=style)

    # Add custom style for selected tab
    style = ttk.Style()
    style.theme_use('default')
    style.configure("selected.TNotebook.Tab", background="dark red", foreground="white", font=("Algerian", 16, "bold"))
    style.configure("TNotebook.Tab", background="burlywood", foreground="black", font=("Algerian", 14, "bold"))

    header_label = tk.Label(window, text="SPS TELEMETRY AND COMMAND INTERFACE : GAGANYAAN",
        font=("Algerian", 20, "bold"), bg="dark red", fg="WHITE", pady=10)
    header_label.grid(row=0, column=0, sticky="ew")

    tab_notebook = ttk.Notebook(window)
    tab_notebook.grid(row=1, column=0, sticky="nsew")
    tab_frames = {}

    def update_project_name(*args):
        input_name = project_name_var.get().strip()
        display_name = "GAGANYAAN" if not input_name or input_name.lower() == "gaganyaan" else input_name.upper()
        header_label.config(text=f"SPS TELEMETRY AND COMMAND INTERFACE: {display_name}")

    # MAIN TABS (RT1, RT2, RT3) with scrollable content
    for rt_name in ["RT1", "RT2", "RT3"]:
        tab_container = tk.Frame(tab_notebook, bg="burlywood")
        tab_notebook.add(tab_container, text=rt_name)
        tab_frames[rt_name] = tab_container

        # Use scrollable content for ALL tabs
        root = make_scrollable_tab(tab_container)

        # --- COM MANAGER: ONLY IN RT1 ---
        if rt_name == "RT1":
            frame1 = LabelFrame(
            root,
            text="  COM MANAGER  ",  # extra spacing in title gives a round feel
            bg="burlywood",
            fg="dark red",
            font=("Calibri", 13, "bold"),
            relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
            bd=2,                    # border thickness
            padx=2, pady=2         # internal padding simulates rounded spacing
            )
            frame1.grid(row=0,column=0,padx=2,pady=2,sticky="nsew")
            
            project_label = Label(frame1, text = "Project Name: ", font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood")
            project_label.grid(column=0,row=0,pady=2,padx=2)
            project_entry = Entry(frame1, textvariable=project_name_var, font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood", width=15, justify="center")
            project_entry.grid(row=0, column=1,pady=2,padx=2)      
            project_name_var.trace_add("write", update_project_name)                                                    
            port_label = Label(frame1, text = "Available port[s]: ", font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood")
            port_label.grid(column=0,row=1,pady=2,padx=2)
            refresh_btn=Button(frame1,text="Refresh",width=15,font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood",command=update_coms)
            refresh_btn.grid(column=2,row=1,pady=2,padx=2)
            port_bd=Label(frame1,text="Baud Rate:",font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood")
            port_bd.grid(column=3,row=1,pady=2,padx=2)
            file_bd=Label(frame1,text="File:",font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood")
            file_bd.grid(column=5,row=1,pady=2,padx=2)
            file_entry1=Entry(frame1,width=15,font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood")
            file_entry1.grid(column=6,row=1,pady=2,padx=2)
            connect_btn=Button(frame1,text="Connect",width=15,state="disabled",font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood",command=connexion)
            connect_btn.grid(column=7,row=1,pady=2,padx=2)
            btn_replay = tk.Button(frame1, text="Replay", width=15, font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood", command=replay_from_file)
            btn_replay.grid(column=2, row=0, padx=2, pady=2)
           
            tk.Label(frame1, text="Jump to SYS_SEC:", font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood").grid(column=3, row=0, padx=2, pady=2)
            
            jump_entry = tk.Entry(frame1, width=15)
            jump_entry.grid(column=4, row=0, padx=2, pady=2)
            
            btn_jump = tk.Button(frame1, text="Jump", width=10, font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood", command=jump_to_sys_sec)
            btn_jump.grid(column=5, row=0, padx=2, pady=2)
            btn_pause_resume = tk.Button(frame1, text="Pause ⏸", width=12, font=("Calibri", 11,"bold"),bg="light green", command=toggle_pause_resume)
            btn_pause_resume.grid(column=6, row=0, padx=2, pady=2)
            btn_stop_replay = tk.Button(frame1, text="Stop Replay", width=15, font=("Calibri", 11,"bold"),
                                        bg="burlywood", fg="red", command=stop_replay)
            btn_stop_replay.grid(column=7, row=0, padx=2, pady=2)
        
            # =============== COMMAND FRAME ================
        frame13 = LabelFrame(root,
        text="  SA COMMANDS  ",  # extra spacing in title gives a round feel
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame13.grid(row=0, column=3, padx=2,pady=2,sticky="nsew")
        
        
        
        status_var = StringVar(value="CMD Status:")
        
        
        status_label = Label(
            frame1,
            textvariable=status_var,
            anchor="w",
            font=("Calibri", 11,"bold"),
            fg="blue",
            bg="burlywood",
            wraplength=700,  # Adjust as needed to fit frame width
            justify="left"
        )
        status_label.grid(row=2, column=0, columnspan=8, sticky="w", padx=2,pady=2)
        
        '''all_commands = list(command_data.items()) 
        for idx, (cmd_name, cmd_data) in enumerate(all_commands):
            btn = Button(frame13, text=cmd_name, width=10)
            btn.grid(row=5 + idx // 5, column=idx % 5, padx=2, pady=2)
            command_buttons[cmd_name] = btn
        
        def make_show_data_word(name):
            return lambda: show_data_word(name)
        for cmd_name in command_buttons:
            command_buttons[cmd_name].config(command=make_show_data_word(cmd_name))'''
        
        # SA1 Manual Entry
        Label(frame13, text="SA1(hex):",font=("Calibri", 11,"bold"),bg="burlywood",fg="blue").grid(row=1, column=0, padx=2, pady=2, sticky='e')
        manual_entries['SA1'] = Entry(frame13, width=20,font=("Calibri", 11,"bold"))
        manual_entries['SA1'].grid(row=1, column=1, padx=2, pady=2)
        manual_entries['SA1'].insert(0, "0x0000 0x0004 0x0055")
        btn_sa1_send = Button(frame13, text="Send SA1", width=8, command=lambda: send_general_command(manual_entries['SA1'].get(), "SA1"),font=("Calibri", 11,"bold"),bg="chocolate")
        btn_sa1_send.grid(row=1, column=2, padx=2, pady=2)
        
        # SA2 Manual Entry
        Label(frame13, text="SA2(hex):",font=("Calibri", 11,"bold"),bg="burlywood",fg="blue").grid(row=2, column=0, padx=2, pady=2, sticky='e')
        manual_entries['SA2'] = Entry(frame13, width=20,font=("Calibri", 11,"bold"))
        manual_entries['SA2'].grid(row=2, column=1, padx=2, pady=2)
        manual_entries['SA2'].insert(0, "0x0000 0x0004 0x0055")
        btn_sa2_send = Button(frame13, text="Send SA2", width=8, command=lambda: send_general_command(manual_entries['SA2'].get(), "SA2"),font=("Calibri", 11,"bold"),bg="chocolate")
        btn_sa2_send.grid(row=2, column=2, padx=2, pady=2)
        
        # SA3 File Browse + Send + Stop
        Label(frame13, text="SA3(hex):",font=("Calibri", 11,"bold"),bg="burlywood",fg="blue").grid(row=3, column=0, padx=2, pady=2, sticky='e')
        file_entries['SA3'] = Entry(frame13, width=20,font=("Calibri", 11,"bold"))
        file_entries['SA3'].grid(row=3, column=1, padx=2, pady=2)
        
        def browse_file_sa3():
            filename = filedialog.askopenfilename(title="Select SA3 Command File", filetypes=[("All Files", "*.*")])
            if filename:
                file_entries['SA3'].delete(0, tk.END)
                file_entries['SA3'].insert(0, filename)
        
        btn_browse_sa3 = Button(frame13, text="Browse", width=8, command=browse_file_sa3,font=("Calibri", 11,"bold"),bg="chocolate")
        btn_browse_sa3.grid(row=3, column=2, padx=2, pady=2)
        
        btn_sa3_send = Button(frame13, text="Send SA3", width=8, command=lambda: send_general_command(None, "SA3"),font=("Calibri", 11,"bold"),bg="chocolate")
        btn_sa3_send.grid(row=3, column=3, padx=2, pady=2)
        
        btn_sa3_stop = Button(frame13, text="Stop SA3", width=8, command=stop_sa3,font=("Calibri", 11,"bold"),bg="chocolate")
        btn_sa3_stop.grid(row=3, column=4, padx=2, pady=2)
        
        # SA4 File Browse + Send + Stop
        Label(frame13, text="SA4(hex):",font=("Calibri", 11,"bold"),bg="burlywood",fg="blue").grid(row=4, column=0, padx=2, pady=2, sticky='e')
        file_entries['SA4'] = Entry(frame13, width=20,font=("Calibri", 11,"bold"))
        file_entries['SA4'].grid(row=4, column=1, padx=2, pady=2)
        
        def browse_file_sa4():
            filename = filedialog.askopenfilename(title="Select SA4 Command File", filetypes=[("All Files", "*.*")])
            if filename:
                file_entries['SA4'].delete(0, tk.END)
                file_entries['SA4'].insert(0, filename)
        
        btn_browse_sa4 = Button(frame13, text="Browse", width=8, command=browse_file_sa4,font=("Calibri", 11,"bold"),bg="chocolate")
        btn_browse_sa4.grid(row=4, column=2, padx=2, pady=2)
        
        btn_sa4_send = Button(frame13, text="Send SA4", width=8, command=lambda: send_general_command(None, "SA4"),font=("Calibri", 11,"bold"),bg="chocolate")
        btn_sa4_send.grid(row=4, column=3, padx=2, pady=2)
        
        btn_sa4_stop = Button(frame13, text="Stop SA4", width=8, command=stop_sa4,font=("Calibri", 11,"bold"),bg="chocolate")
        btn_sa4_stop.grid(row=4, column=4, padx=2, pady=2)
        
        cmd_btn = Button(frame13, text="List of Commands", font=("Calibri", 11,"bold"),bg="chocolate",command=open_popup)
        cmd_btn.grid(row=1, column=3, padx=2, pady=2)
            
        
        
        
        # ====== BUS COMMAND Section =========
        frame_bus = LabelFrame(root, text="  BUS COMMANDS  ",  # extra spacing in title gives a round feel
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame_bus.grid(row=1, column=3, padx=2, pady=2, sticky="nsew")
        
        bus_var = StringVar(value=" ")  # Start with no selection
        # --- Show Toggle Packet Button ---
        Radiobutton(frame_bus, text="BUS A", variable=bus_var, value="A", font=("Calibri", 11,"bold"),bg="burlywood",fg="blue").grid(row=0, column=0, padx=2, pady=2)
        Radiobutton(frame_bus, text="BUS B", variable=bus_var, value="B", font=("Calibri", 11,"bold"),bg="burlywood",fg="blue").grid(row=0, column=1, padx=2, pady=2)
        
        bus_var.trace_add('write', on_bus_toggle)
        
        Label(frame_bus, text="RT Add(Hex):", font=("Calibri", 11,"bold"),bg="burlywood",fg="dark violet").grid(row=1, column=0, padx=2, pady=2)
        dataword_entry = Entry(frame_bus, width=6,font=("Calibri", 11,"bold"))
        dataword_entry.grid(row=1, column=1, padx=2, pady=2)
        dataword_entry.insert(1, "00")  # default
        
        
        
        for i, (cmd_name, cmd_val) in enumerate(bus_commands):
            btn = Button(frame_bus, text=cmd_name, width=11, font=("Calibri", 11,"bold"),bg="chocolate",command=lambda v=cmd_val: send_bus_command_button(v))
            btn.grid(row=2+i//4, column=i%4, padx=2, pady=2)
            bus_command_buttons[cmd_name] = btn
     
        send_bus_manual = Button(frame_bus, text="Send", width=7,font=("Calibri", 11,"bold"),bg="chocolate", command=send_bus_command_entry)
        send_bus_manual.grid(row=1, column=3, padx=2, pady=2)
        
        
        # ========================== COUNTERS =======================================
        
        frame2=LabelFrame(root, text="  COUNTERS  ",  # extra spacing in title gives a round feel
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame2.grid(row=0,column=2,padx=2,pady=2,sticky="nsew")
       
        update_count=Label(frame2,text="Update counter",font=("Calibri", 11,"bold"),bg="burlywood")
        update_count.grid(row=0, column=0)
        update_entry=Entry(frame2,width=10,font=("Calibri", 11,"bold"),bg="burlywood",fg="blue",state="readonly")
        update_entry.grid(column=1,row=0,pady=2,padx=2)
       
        counter=Label(frame2,text="Display Counter",font=("Calibri", 11,"bold"),bg="burlywood")
        counter.grid(row=1, column=0)
        counter_entry=Entry(frame2,width=10,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="red")
        counter_entry.grid(column=1,row=1,pady=2,padx=2)
        
        sw_rst_c=Label(frame2,text="S/W RST Counter",font=("Calibri", 11,"bold"),bg="burlywood")
        sw_rst_c.grid(row=2, column=0)
        sw_rst_c=Entry(frame2,width=10,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        sw_rst_c.grid(column=1,row=2,pady=2,padx=2)
       
        hw_rst_c=Label(frame2,text="H/W RST Counter",font=("Calibri", 11,"bold"),bg="burlywood")
        hw_rst_c.grid(row=3, column=0)
        hw_rst_c=Entry(frame2,width=10,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        hw_rst_c.grid(column=1,row=3,pady=2,padx=2)
       
        tsm_counter=Label(frame2,text="Tsm_Counter",font=("Calibri", 11,"bold"),bg="burlywood")
        tsm_counter.grid(row=4, column=0)
        tsm_counter_entry=Entry(frame2,width=10,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        tsm_counter_entry.grid(column=1,row=4,pady=2,padx=2)
       
        # ======================== SYSTEM TIME =====================================
        frame3=LabelFrame(root,text="  TIME  ",  # extra spacing in title gives a round feel
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame3.grid(row=1,column=0,padx=2,pady=2,sticky="nsew")
       
        Name=Label(frame3,text=" System Time:",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood",padx=5,pady=5)
        Name.grid(row=1, column=1)
        
        weeks_label=Label(frame3,text="Week Number:",font=("Calibri", 11,"bold"),bg="burlywood")
        weeks_label.grid(row=1, column=6)
        week_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        week_entry.grid(row=1, column=7, pady=5,padx=5)
        
        time_label=Label(frame3,text="Second(s):",font=("Calibri", 11,"bold"),bg="burlywood")
        time_label.grid(row=1, column=8)
        time_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        time_entry.grid(row=1, column=9, pady=5,padx=5)
       
        nanotime_label=Label(frame3,text="Nano Second(ns):",font=("Calibri", 11,"bold"),bg="burlywood")
        nanotime_label.grid(row=1, column=10)
        nanotime_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        nanotime_entry.grid(row=1, column=11, pady=5,padx=5)
       
     
       
       
        # ========================SYC TIME ==========================================
       
        Name=Label(frame3,text=" Sync Time:",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood",padx=5,pady=5)
        Name.grid(row=2, column=1)
        
        weeks_label1=Label(frame3,text="Week Number:",font=("Calibri", 11,"bold"),bg="burlywood")
        weeks_label1.grid(row=2, column=6)
        week_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        week_entry1.grid(row=2, column=7, pady=5,padx=5)
       
        time_label1=Label(frame3,text="Second(s):",font=("Calibri", 11,"bold"),bg="burlywood")
        time_label1.grid(row=2, column=8)
        time_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        time_entry1.grid(row=2, column=9, pady=5,padx=5)
       
        nanotime_label1=Label(frame3,text="Nano Second(ns):",font=("Calibri", 11,"bold"),bg="burlywood")
        nanotime_label1.grid(row=2, column=10)
        nanotime_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        nanotime_entry1.grid(row=2, column=11, pady=5,padx=5)
       
       
        
        # ========================= PPS TIME==========================================
        Name=Label(frame3,text=" PPS Time:",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood",padx=5,pady=5)
        Name.grid(row=3, column=1)
        
        weeks_label2=Label(frame3,text="Week Number:",font=("Calibri", 11,"bold"),bg="burlywood")
        weeks_label2.grid(row=3, column=6)
        week_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        week_entry2.grid(row=3, column=7, pady=5,padx=5)
        
        time_label2=Label(frame3,text="Second(s):",font=("Calibri", 11,"bold"),bg="burlywood")
        time_label2.grid(row=3, column=8)
        time_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        time_entry2.grid(row=3, column=9, pady=5,padx=5)
       
        nanotime_label2=Label(frame3,text="Nano Second(ns):",font=("Calibri", 11,"bold"),bg="burlywood")
        nanotime_label2.grid(row=3, column=10)
        nanotime_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        nanotime_entry2.grid(row=3, column=11, pady=5,padx=5)
       
        fix_3d=Label(frame3,text="PPS_3D_FIX:",font=("Calibri", 11,"bold"),bg="burlywood")
        fix_3d.grid(row=4, column=6)
        fix_3d=Entry(frame3,width=15,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        fix_3d.grid(column=7,row=4,pady=5,padx=5)
        
        leap=Label(frame3,text="PPS_LEAP:",font=("Calibri", 11,"bold"),bg="burlywood")
        leap.grid(row=4, column=8)
        leap=Entry(frame3,width=15,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        leap.grid(column=9,row=4,pady=5,padx=5)
        
        # ==============================HEADER2 TIME =================================
        Name=Label(frame3,text=" header2 Time:",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood",padx=5,pady=5)
        Name.grid(row=5, column=1)
        
        weeks_h2=Label(frame3,text="h2Week Number:",font=("Calibri", 11,"bold"),bg="burlywood")
        weeks_h2.grid(row=5, column=6)
        weeks_h2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        weeks_h2.grid(row=5, column=7, pady=5,padx=5)
        
        time_h2=Label(frame3,text="h2Second(s):",font=("Calibri", 11,"bold"),bg="burlywood")
        time_h2.grid(row=5, column=8)
        time_h2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        time_h2.grid(row=5, column=9, pady=5,padx=5)
        
        nanotime_h2=Label(frame3,text="h2Nano Second(ns):",font=("Calibri", 11,"bold"),bg="burlywood")
        nanotime_h2.grid(row=5, column=10)
        nanotime_h2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="brown")
        nanotime_h2.grid(row=5, column=11, pady=5,padx=5)
        
        
        
       # ============================    ACQ ===========================================
        frame14=LabelFrame(root,text="  ACQ  ",  # extra spacing in title gives a round feel
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame14.grid(row=2,column=3,padx=2,pady=2,sticky="nsew")
       
        acq1=Label(frame14,text="ACQ1",font=("Calibri", 11,"bold"),bg="burlywood")
        acq1.grid(row=0, column=0)
        acq1=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        acq1.grid(column=1,row=0,pady=2,padx=2)
       
        acq2=Label(frame14,text="ACQ-2",font=("Calibri", 11,"bold"),bg="burlywood")
        acq2.grid(row=0, column=2)
        acq2=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")      
        acq2.grid(column=3,row=0,pady=2,padx=2)
       
        acq3=Label(frame14,text="ACQ-3",font=("Calibri", 11,"bold"),bg="burlywood")
        acq3.grid(row=0, column=4)
        acq3=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        acq3.grid(column=5,row=0,pady=2,padx=2)
       
        acq4=Label(frame14,text="ACQ-4",font=("Calibri", 11,"bold"),bg="burlywood")
        acq4.grid(row=0, column=6)
        acq4=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        acq4.grid(column=7,row=0,pady=2,padx=2)
        
        port_conf=Label(frame14,text="ANT1",font=("Calibri", 11,"bold"),bg="burlywood")
        port_conf.grid(row=1, column=0)
        port_conf=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        port_conf.grid(column=1,row=1,pady=2,padx=2)
        
        port_conf1=Label(frame14,text="ANT2",font=("Calibri", 11,"bold"),bg="burlywood")
        port_conf1.grid(row=1, column=2)
        port_conf1=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        port_conf1.grid(column=3,row=1,pady=2,padx=2)
        
        port_conf2=Label(frame14,text="ANT3",font=("Calibri", 11,"bold"),bg="burlywood")
        port_conf2.grid(row=1, column=4)
        port_conf2=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        port_conf2.grid(column=5,row=1,pady=2,padx=2)
        
        port_conf3=Label(frame14,text="ANT4",font=("Calibri", 11,"bold"),bg="burlywood")
        port_conf3.grid(row=1, column=6)
        port_conf3=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        port_conf3.grid(column=7,row=1,pady=2,padx=2)
        
        # ===============   VECTOR DATA =============================================
        frame5=LabelFrame(root,text="  STATE VECTOR DATA  ",  # extra spacing in title gives a round feel
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame5.grid(row=2,column=0,padx=2,pady=2,sticky="nsew")
       
        Name=Label(frame5,text="  INSTANTIATE :",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        Name.grid(row=1, column=1)
        position_label = Label(frame5, text="X(m):",font=("Calibri", 11,"bold"),bg="burlywood")
        position_label.grid(row=1, column=3, sticky="W")
        velocity_label = Label(frame5, text="Vel_x(m/s):",font=("Calibri", 11,"bold"),bg="burlywood")
        velocity_label.grid(row=1, column=9, sticky="W")
        position_label1 = Label(frame5, text="Y(m):",font=("Calibri", 11,"bold"),bg="burlywood")
        position_label1.grid(row=1, column=5, sticky="W")
        velocity_label1 = Label(frame5, text="Vel_y(m/s):",font=("Calibri", 11,"bold"),bg="burlywood")
        velocity_label1.grid(row=1, column=11, sticky="W")
        position_label2 = Label(frame5, text="Z(m):",font=("Calibri", 11,"bold"),bg="burlywood")
        position_label2.grid(row=1, column=7, sticky="W")
        velocity_label2 = Label(frame5, text="Vel_z(m/s):",font=("Calibri", 11,"bold"),bg="burlywood")
        velocity_label2.grid(row=1, column=13, sticky="W")
       
        position_entry = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        position_entry.grid(row=1, column=4, padx=2)
        velocity_entry = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        velocity_entry.grid(row=1, column=10, padx=2)
        position_entry1 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        position_entry1.grid(row=1, column=6, padx=2)
        velocity_entry1 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        velocity_entry1.grid(row=1, column=12, padx=2)
        position_entry2 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        position_entry2.grid(row=1, column=8, padx=2)
        velocity_entry2 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        velocity_entry2.grid(row=1, column=14, padx=2)
       
        Name1=Label(frame5,text=" ESTIMATED    :",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        Name1.grid(row=2, column=1)
        position_label3 = Label(frame5, text="X(m):",font=("Calibri", 11,"bold"),bg="burlywood")
        position_label3.grid(row=2, column=3, sticky="W")
        velocity_label3 = Label(frame5, text="Vel_x(m/s):",font=("Calibri", 11,"bold"),bg="burlywood")
        velocity_label3.grid(row=2, column=9, sticky="W")
        position_label4 = Label(frame5, text="Y(m):",font=("Calibri", 11,"bold"),bg="burlywood")
        position_label4.grid(row=2, column=5, sticky="W")
        velocity_label4 = Label(frame5, text="Vel_y(m/s):",font=("Calibri", 11,"bold"),bg="burlywood")
        velocity_label4.grid(row=2, column=11, sticky="W")
        position_label5 = Label(frame5, text="Z(m):",font=("Calibri", 11,"bold"),bg="burlywood")
        position_label5.grid(row=2, column=7, sticky="W")
        velocity_label5 = Label(frame5, text="Vel_z(m/s):",font=("Calibri", 11,"bold"),bg="burlywood")
        velocity_label5.grid(row=2, column=13, sticky="W")
       
        position_entry3 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        position_entry3.grid(row=2, column=4, padx=2)
        velocity_entry3 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        velocity_entry3.grid(row=2, column=10, padx=2)
        position_entry4 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        position_entry4.grid(row=2, column=6, padx=2)
        velocity_entry4 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        velocity_entry4.grid(row=2, column=12, padx=2)
        position_entry5 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        position_entry5.grid(row=2, column=8, padx=2)
        velocity_entry5 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg="burlywood",fg="dark slate gray")
        velocity_entry5.grid(row=2, column=14, padx=2)
        
        
        # ======================= CHECKSUM ===============================================
        frame7=LabelFrame(root,text='CHECKSUM',
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame7.grid(row=0,column=1,padx=2,pady=2,sticky="nsew")
     
        csm1=Label(frame7,text="CHECKSUM 1",font=("Calibri", 11,"bold"),bg="burlywood")
        csm1.grid(row=3, column=0)
        csm1=Entry(frame7,width=15,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        csm1.grid(column=1,row=3,pady=2,padx=2)
        csm2=Label(frame7,text="CHECKSUM 2",font=("Calibri", 11,"bold"),bg="burlywood")
        csm2.grid(row=4, column=0)
        csm2=Entry(frame7,width=15,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        csm2.grid(column=1,row=4,pady=2,padx=2)
        
        
        # =========================== CLOCK AND DRIFT ================================
        frame9=LabelFrame(root,text='CLOCK and DRIFT',bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame9.grid(row=1,column=1,padx=2,pady=2,sticky="nsew")
     
        cb=Label(frame9,text="Clock Bais",font=("Calibri", 11,"bold"),bg="burlywood")
        cb.grid(row=0, column=0)
        cb=Entry(frame9,width=10,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        cb.grid(column=1,row=0,pady=2,padx=2)
       
        isb=Label(frame9,text="Inter System Bais",font=("Calibri", 11,"bold"),bg="burlywood")
        isb.grid(row=1, column=0)
        isb=Entry(frame9,width=10,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        isb.grid(column=1,row=1,pady=2,padx=2)
       
        drift=Label(frame9,text="Drift",font=("Calibri", 11,"bold"),bg="burlywood")
        drift.grid(row=2, column=0)
        drift=Entry(frame9,width=10,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        drift.grid(column=1,row=2,pady=2,padx=2)
       
        InterSystemDrift=Label(frame9,text="Inter System Drift",font=("Calibri", 11,"bold"),bg="burlywood")
        InterSystemDrift.grid(row=3, column=0)
        isd=Entry(frame9,width=10,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        isd.grid(column=1,row=3,pady=2,padx=2)
        
        # ======================= PDOP AND NO OF SAT =====================================
        frame10=LabelFrame(root,text='PDOP and No of Sat',bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame10.grid(row=2,column=1,padx=2,pady=2,sticky="nsew")
     
        pdop=Label(frame10,text="PDOP",font=("Calibri", 11,"bold"),bg="burlywood")
        pdop.grid(row=3, column=0)
        pdop=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        pdop.grid(column=1,row=3,pady=2,padx=2)
        
        no_sat_trck=Label(frame10,text="No of SAT",font=("Calibri", 11,"bold"),bg="burlywood")
        no_sat_trck.grid(row=6, column=0)
        no_sat_trck=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        no_sat_trck.grid(column=1,row=6,pady=2,padx=2)
        
        # ================ LAST CMD ========================================================
        frame10=LabelFrame(root,text='LAST CMD',bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame10.grid(row=2,column=2,padx=2,pady=2,sticky="nsew")
     
        last_cmd_exe=Label(frame10,text="Last Cmd Exe",font=("Calibri", 11,"bold"),bg="burlywood")
        last_cmd_exe.grid(row=0, column=0)
        last_cmd_exe=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        last_cmd_exe.grid(column=1,row=0,pady=2,padx=2)
       
        last_reset_time=Label(frame10,text="Last reset time",font=("Calibri", 11,"bold"),bg="burlywood")
        last_reset_time.grid(row=1, column=0)
        last_reset_time=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        last_reset_time.grid(column=1,row=1,pady=2,padx=2)
       
        # ========================== TRACKING INFO ==========================
        frame8=LabelFrame(root,text="TRACKING INFO",bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame8.grid(row=4,column=0,padx=2,pady=2,sticky="nsew")
       
        channel=Label(frame8,text="Channel",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        channel.grid(row=4,column=1,padx=5,pady=5)
           
        ch1=Label(frame8,text="1",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch1.grid(row=5, column=1)
        ch2=Label(frame8,text="2",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch2.grid(column=1,row=6)
        ch3=Label(frame8,text="3",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch3.grid(column=1,row=7)
        ch4=Label(frame8,text="4",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch4.grid(column=1,row=8)
        ch5=Label(frame8,text="5",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch5.grid(column=1,row=9)
        ch6=Label(frame8,text="6",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch6.grid(column=1,row=10)
        ch7=Label(frame8,text="7",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch7.grid(column=1,row=11)
        ch8=Label(frame8,text="8",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch8.grid(column=1,row=12)
        ch9=Label(frame8,text="9",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch9.grid(column=1,row=13)
        ch10=Label(frame8,text="10",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch10.grid(column=1,row=14)
        ch11=Label(frame8,text="11",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch11.grid(column=1,row=15)
        ch12=Label(frame8,text="12",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch12.grid(column=1,row=16)
        ch13=Label(frame8,text="13",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch13.grid(column=1,row=17)
        ch14=Label(frame8,text="14",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch14.grid(column=1,row=18)
        ch15=Label(frame8,text="15",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch15.grid(column=1,row=19)
        ch16=Label(frame8,text="16",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch16.grid(column=1,row=20)
        ch17=Label(frame8,text="17",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch17.grid(column=1,row=21)
        ch18=Label(frame8,text="18",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        ch18.grid(column=1,row=22)
       
        svid=Label(frame8,width=5,text="SVID",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        svid.grid(row=4,column=2,padx=5,pady=5)
       
        svid1=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid1.grid(column=2,row=5,pady=2,padx=2)
        svid2=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid2.grid(column=2,row=6,pady=2,padx=2)
        svid3=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid3.grid(column=2,row=7,pady=2,padx=2)
        svid4=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid4.grid(column=2,row=8,pady=2,padx=2)
        svid5=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid5.grid(column=2,row=9,pady=2,padx=2)
        svid6=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid6.grid(column=2,row=10,pady=2,padx=2)
        svid7=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid7.grid(column=2,row=11,pady=2,padx=2)
        svid8=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid8.grid(column=2,row=12,pady=2,padx=2)
        svid9=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid9.grid(column=2,row=13,pady=2,padx=2)
        svid10=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid10.grid(column=2,row=14,pady=2,padx=2)
        svid11=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid11.grid(column=2,row=15,pady=2,padx=2)
        svid12=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid12.grid(column=2,row=16,pady=2,padx=2)
        svid13=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid13.grid(column=2,row=17,pady=2,padx=2)
        svid14=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid14.grid(column=2,row=18,pady=2,padx=2)
        svid15=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid15.grid(column=2,row=19,pady=2,padx=2)
        svid16=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid16.grid(column=2,row=20,pady=2,padx=2)
        svid17=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid17.grid(column=2,row=21,pady=2,padx=2)
        svid18=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        svid18.grid(column=2,row=22,pady=2,padx=2)
       
        cndr=Label(frame8,width=5,text="CNDR",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        cndr.grid(row=4,column=3,padx=5,pady=5)
       
        cndr1=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr1.grid(column=3,row=5,pady=2,padx=2)
        cndr2=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr2.grid(column=3,row=6,pady=2,padx=2)
        cndr3=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr3.grid(column=3,row=7,pady=2,padx=2)
        cndr4=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr4.grid(column=3,row=8,pady=2,padx=2)
        cndr5=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr5.grid(column=3,row=9,pady=2,padx=2)
        cndr6=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr6.grid(column=3,row=10,pady=2,padx=2)
        cndr7=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr7.grid(column=3,row=11,pady=2,padx=2)
        cndr8=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr8.grid(column=3,row=12,pady=2,padx=2)
        cndr9=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr9.grid(column=3,row=13,pady=2,padx=2)
        cndr10=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr10.grid(column=3,row=14,pady=2,padx=2)
        cndr11=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr11.grid(column=3,row=15,pady=2,padx=2)
        cndr12=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr12.grid(column=3,row=16,pady=2,padx=2)
        cndr13=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr13.grid(column=3,row=17,pady=2,padx=2)
        cndr14=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr14.grid(column=3,row=18,pady=2,padx=2)
        cndr15=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr15.grid(column=3,row=19,pady=2,padx=2)
        cndr16=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr16.grid(column=3,row=20,pady=2,padx=2)
        cndr17=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr17.grid(column=3,row=21,pady=2,padx=2)
        cndr18=Entry(frame8,width=5,state="readonly",font=("Calibri", 11,"bold"))
        cndr18.grid(column=3,row=22,pady=2,padx=2)
       
       
        num_channels = 18
     
        # All 16 bit names as per your request
        bit_names = ["A","T","D","E","P","H","R","P1","I","S","SR","E1"]
       
        # Place labels ("A", "T", ..., "Y") at row 4, columns 4 to 19
        for i, bit in enumerate(bit_names):
            Label(frame8, text=bit,font=("Calibri", 11,"bold"),fg="blue",bg="burlywood").grid(row=4, column=4+i, padx=5, pady=5)
       
        # Create Entry widgets for each channel (rows 5-20) and each bit (cols 4-19)
        # Store in bit_to_entrylist[bit] = [entry1, ..., entry16]
        bit_to_entrylist = {bit: [] for bit in bit_names}
        for ch in range(num_channels):
            for i, bit in enumerate(bit_names):
                entry = Entry(frame8, width=4, state="readonly",font=("Calibri", 11,"bold"))
                entry.grid(row=5+ch, column=4+i, pady=2, padx=2)
                bit_to_entrylist[bit].append(entry)
               
        iode=Label(frame8,width=8,text="IODE",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        iode.grid(row=4,column=16,padx=5,pady=5)
       
        iode1=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode1.grid(column=16,row=5,pady=2,padx=2)
        iode2=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode2.grid(column=16,row=6,pady=2,padx=2)
        iode3=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode3.grid(column=16,row=7,pady=2,padx=2)
        iode4=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode4.grid(column=16,row=8,pady=2,padx=2)
        iode5=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode5.grid(column=16,row=9,pady=2,padx=2)
        iode6=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode6.grid(column=16,row=10,pady=2,padx=2)
        iode7=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode7.grid(column=16,row=11,pady=2,padx=2)
        iode8=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode8.grid(column=16,row=12,pady=2,padx=2)
        iode9=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode9.grid(column=16,row=13,pady=2,padx=2)
        iode10=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode10.grid(column=16,row=14,pady=2,padx=2)
        iode11=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode11.grid(column=16,row=15,pady=2,padx=2)
        iode12=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode12.grid(column=16,row=16,pady=2,padx=2)
        iode13=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode13.grid(column=16,row=17,pady=2,padx=2)
        iode14=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode14.grid(column=16,row=18,pady=2,padx=2)
        iode15=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode15.grid(column=16,row=19,pady=2,padx=2)
        iode16=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode16.grid(column=16,row=20,pady=2,padx=2)
        iode17=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode17.grid(column=16,row=21,pady=2,padx=2)
        iode18=Entry(frame8,width=8,state="readonly",font=("Calibri", 11,"bold"))
        iode18.grid(column=16,row=22,pady=2,padx=2)
       
        pr=Label(frame8,width=11,text="PR(cm)",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        pr.grid(row=4,column=17,padx=5,pady=5)
         
        pr1=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr1.grid(column=17,row=5,pady=2,padx=2)
        pr2=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr2.grid(column=17,row=6,pady=2,padx=2)
        pr3=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr3.grid(column=17,row=7,pady=2,padx=2)
        pr4=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr4.grid(column=17,row=8,pady=2,padx=2)
        pr5=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr5.grid(column=17,row=9,pady=2,padx=2)
        pr6=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr6.grid(column=17,row=10,pady=2,padx=2)
        pr7=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr7.grid(column=17,row=11,pady=2,padx=2)
        pr8=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr8.grid(column=17,row=12,pady=2,padx=2)
        pr9=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr9.grid(column=17,row=13,pady=2,padx=2)
        pr10=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr10.grid(column=17,row=14,pady=2,padx=2)
        pr11=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr11.grid(column=17,row=15,pady=2,padx=2)
        pr12=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr12.grid(column=17,row=16,pady=2,padx=2)
        pr13=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr13.grid(column=17,row=17,pady=2,padx=2)
        pr14=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr14.grid(column=17,row=18,pady=2,padx=2)
        pr15=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr15.grid(column=17,row=19,pady=2,padx=2)
        pr16=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr16.grid(column=17,row=20,pady=2,padx=2)
        pr17=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr17.grid(column=17,row=21,pady=2,padx=2)
        pr18=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        pr18.grid(column=17,row=22,pady=2,padx=2)
       
       
        dr=Label(frame8,width=11,text="DR(m/s)",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        dr.grid(row=4,column=18,padx=5,pady=5)
       
        dr1=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr1.grid(column=18,row=5,pady=2,padx=2)
        dr2=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr2.grid(column=18,row=6,pady=2,padx=2)
        dr3=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr3.grid(column=18,row=7,pady=2,padx=2)
        dr4=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr4.grid(column=18,row=8,pady=2,padx=2)
        dr5=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr5.grid(column=18,row=9,pady=2,padx=2)
        dr6=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr6.grid(column=18,row=10,pady=2,padx=2)
        dr7=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr7.grid(column=18,row=11,pady=2,padx=2)
        dr8=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr8.grid(column=18,row=12,pady=2,padx=2)
        dr9=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr9.grid(column=18,row=13,pady=2,padx=2)
        dr10=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr10.grid(column=18,row=14,pady=2,padx=2)
        dr11=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr11.grid(column=18,row=15,pady=2,padx=2)
        dr12=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr12.grid(column=18,row=16,pady=2,padx=2)
        dr13=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr13.grid(column=18,row=17,pady=2,padx=2)
        dr14=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr14.grid(column=18,row=18,pady=2,padx=2)
        dr15=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr15.grid(column=18,row=19,pady=2,padx=2)
        dr16=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr16.grid(column=18,row=20,pady=2,padx=2)
        dr17=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr17.grid(column=18,row=21,pady=2,padx=2)
        dr18=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
        dr18.grid(column=18,row=22,pady=2,padx=2)
       
        elev=Label(frame8,width=11,text="ELEV(m/s)",font=("Calibri", 11,"bold"),fg="blue",bg="burlywood")
        elev.grid(row=4,column=19,padx=5,pady=5)
       
        elev1=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev1.grid(column=19,row=5,pady=2,padx=2)
        elev2=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev2.grid(column=19,row=6,pady=2,padx=2)
        elev3=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev3.grid(column=19,row=7,pady=2,padx=2)
        elev4=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev4.grid(column=19,row=8,pady=2,padx=2)
        elev5=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev5.grid(column=19,row=9,pady=2,padx=2)
        elev6=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev6.grid(column=19,row=10,pady=2,padx=2)
        elev7=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev7.grid(column=19,row=11,pady=2,padx=2)
        elev8=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev8.grid(column=19,row=12,pady=2,padx=2)
        elev9=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev9.grid(column=19,row=13,pady=2,padx=2)
        elev10=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev10.grid(column=19,row=14,pady=2,padx=2)
        elev11=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev11.grid(column=19,row=15,pady=2,padx=2)
        elev12=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev12.grid(column=19,row=16,pady=2,padx=2)
        elev13=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev13.grid(column=19,row=17,pady=2,padx=2)
        elev14=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev14.grid(column=19,row=18,pady=2,padx=2)
        elev15=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev15.grid(column=19,row=19,pady=2,padx=2)
        elev16=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev16.grid(column=19,row=20,pady=2,padx=2)
        elev17=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev17.grid(column=19,row=21,pady=2,padx=2)
        elev18=Entry(frame8,width=10,state="readonly",font=("Calibri", 11,"bold"))
        elev18.grid(column=19,row=22,pady=2,padx=2)
        
        
       
        #  ========================= NAVIC ======================================
        frame12=LabelFrame(root,text='NAVIC',bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame12.grid(row=3,column=2,padx=2,pady=2,sticky="nsew")

        navic_msg_22_c=Label(frame12,text="NAVIC_MSG_22",font=("Calibri", 11,"bold"),bg="burlywood")
        navic_msg_22_c.grid(row=3, column=0)
        navic_msg_22_c=Entry(frame12,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        navic_msg_22_c.grid(column=1,row=3,pady=2,padx=2)
       
        navic_msg_cmd_c=Label(frame12,text="NAVIC_MSG_CMD_C",font=("Calibri", 11,"bold"),bg="burlywood")
        navic_msg_cmd_c.grid(row=4, column=0)
        navic_msg_cmd_c=Entry(frame12,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        navic_msg_cmd_c.grid(column=1,row=4,pady=2,padx=2)
        
        navic_cmd_var=Label(frame12,text="NAVIC CMD VAR",font=("Calibri", 11,"bold"),bg="burlywood")
        navic_cmd_var.grid(row=7, column=0)
        navic_cmd_var=Entry(frame12,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        navic_cmd_var.grid(column=1,row=7,pady=2,padx=2)

        
        # ============================  NRFFC and GRFFC CNT ============================== 
        frame12=LabelFrame(root,text='NRFFC and GRFFC CNT',bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame12.grid(row=3,column=3,padx=2,pady=2,sticky="nsew") 
       
        total_cmd_counter=Label(frame12,text="Total_cmd_c",font=("Calibri", 11,"bold"),bg="burlywood")
        total_cmd_counter.grid(row=0, column=0)
        total_cmd_counter=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        total_cmd_counter.grid(column=1,row=0,pady=2,padx=2)
        
        nrff_rst_counter1=Label(frame12,text="NRFFC_rst_c1",font=("Calibri", 11,"bold"),bg="burlywood")
        nrff_rst_counter1.grid(row=0, column=2)
        nrff_rst_counter1=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        nrff_rst_counter1.grid(column=3,row=0,pady=2,padx=2)
        
        nrff_rst_counter2=Label(frame12,text="NRFFC_rst_c2",font=("Calibri", 11,"bold"),bg="burlywood")
        nrff_rst_counter2.grid(row=0, column=4)
        nrff_rst_counter2=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        nrff_rst_counter2.grid(column=5,row=0,pady=2,padx=2)
        
        grff_rst_counter1=Label(frame12,text="GRFFC_rst_c1",font=("Calibri", 11,"bold"),bg="burlywood")
        grff_rst_counter1.grid(row=1, column=0)
        grff_rst_counter1=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        grff_rst_counter1.grid(column=1,row=1,pady=2,padx=2)
        
        grff_rst_counter2=Label(frame12,text="GRFFC_rst_c2",font=("Calibri", 11,"bold"),bg="burlywood")
        grff_rst_counter2.grid(row=1, column=2)
        grff_rst_counter2=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        grff_rst_counter2.grid(column=3,row=1,pady=2,padx=2)
        
        grff_rst_counter3=Label(frame12,text="GRFFC_rst_c3",font=("Calibri", 11,"bold"),bg="burlywood")
        grff_rst_counter3.grid(row=1, column=4)
        grff_rst_counter3=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        grff_rst_counter3.grid(column=5,row=1,pady=2,padx=2)
        
        grff_rst_counter4=Label(frame12,text="GRFFC_rst_c4",font=("Calibri", 11,"bold"),bg="burlywood")
        grff_rst_counter4.grid(row=2, column=0)
        grff_rst_counter4=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        grff_rst_counter4.grid(column=1,row=2,pady=2,padx=2)
        
        # ===================== MODE and PORT and ID's ====================================
        frame15=LabelFrame(root,text="MODE and PORT and ID's",bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame15.grid(row=3,column=0,padx=2,pady=2,sticky="nsew")
         
       
        TM=Label(frame15,text="TM",font=("Calibri", 11,"bold"),bg="burlywood")
        TM.grid(row=0, column=0)
        tm=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        tm.grid(column=1,row=0,pady=2,padx=2)
       
        SWDT=Label(frame15,text="SWDT",font=("Calibri", 11,"bold"),bg="burlywood")
        SWDT.grid(row=0, column=2)
        swdt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")   
        swdt.grid(column=3,row=0,pady=2,padx=2)
       
        HWDT=Label(frame15,text="HWDT",font=("Calibri", 11,"bold"),bg="burlywood")
        HWDT.grid(row=0, column=4)
        hwdt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        hwdt.grid(column=5,row=0,pady=2,padx=2)
       
        SBASEN=Label(frame15,text="SBASEN",font=("Calibri", 11,"bold"),bg="burlywood")
        SBASEN.grid(row=0, column=6)
        sbasen=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        sbasen.grid(column=7,row=0,pady=2,padx=2)
       
        SYS_MODE=Label(frame15,text="SYS_MODE",font=("Calibri", 11,"bold"),bg="burlywood")
        SYS_MODE.grid(row=0, column=8)
        sys_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        sys_mode.grid(column=9,row=0,pady=2,padx=2)
       
        REC_MODE=Label(frame15,text="REC_MODE",font=("Calibri", 11,"bold"),bg="burlywood")
        REC_MODE.grid(row=1, column=0)
        rec_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        rec_mode.grid(column=1,row=1,pady=2,padx=2)
       
        TIME_MODE=Label(frame15,text="TIME_MODE",font=("Calibri", 11,"bold"),bg="burlywood")
        TIME_MODE.grid(row=1, column=2)
        time_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        time_mode.grid(column=3,row=1,pady=2,padx=2)
         
        ALM_AV=Label(frame15,text="ALM_AV",font=("Calibri", 11,"bold"),bg="burlywood")
        ALM_AV.grid(row=1, column=4)
        alm_av=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        alm_av.grid(column=5,row=1,pady=2,padx=2)
       
        TIME_AV=Label(frame15,text="TIME_AV",font=("Calibri", 11,"bold"),bg="burlywood")
        TIME_AV.grid(row=1, column=6)
        time_av=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        time_av.grid(column=7,row=1,pady=2,padx=2)
       
        POS_MODE=Label(frame15,text="POS_MODE",font=("Calibri", 11,"bold"),bg="burlywood")
        POS_MODE.grid(row=1, column=8)
        pos_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        pos_mode.grid(column=9,row=1,pady=2,padx=2)
       
        POS_AV=Label(frame15,text="POS_AV",font=("Calibri", 11,"bold"),bg="burlywood")
        POS_AV.grid(row=2, column=0)
        pos_av=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        pos_av.grid(column=1,row=2,pady=2,padx=2)
      
        sol_mode=Label(frame15,text="Sol_mode",font=("Calibri", 11,"bold"),bg="burlywood")
        sol_mode.grid(row=2, column=2)
        sol_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")   
        sol_mode.grid(column=3,row=2,pady=2,padx=2)
       
        sps_id=Label(frame15,text="SPS_ID",font=("Calibri", 11,"bold"),bg="burlywood")
        sps_id.grid(row=2, column=4)
        sps_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        sps_id.grid(column=5,row=2,pady=2,padx=2)
        
        sw_rst_id=Label(frame15,text="S/W RESET ID",font=("Calibri", 11,"bold"),bg="burlywood")
        sw_rst_id.grid(row=2, column=6)
        sw_rst_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        sw_rst_id.grid(column=7,row=2,pady=2,padx=2)
       
        leo_sat_id=Label(frame15,text="LEO SAT ID",font=("Calibri", 11,"bold"),bg="burlywood")
        leo_sat_id.grid(row=2, column=8)
        leo_sat_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        leo_sat_id.grid(column=9,row=2,pady=2,padx=2)
       
        rt_id=Label(frame15,text="RT_ID",font=("Calibri", 11,"bold"),bg="burlywood")
        rt_id.grid(row=3, column=0)
        rt_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        rt_id.grid(column=1,row=3,pady=2,padx=2)
        
        s_id=Label(frame15,text="S_ID",font=("Calibri", 11,"bold"),bg="burlywood")
        s_id.grid(row=3, column=2)
        s_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        s_id.grid(column=3,row=3,pady=2,padx=2)
        
        
        # ====================== RT ========================================
        frame15=LabelFrame(root,text="RT",bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame15.grid(row=3,column=1,padx=2,pady=2,sticky="nsew")
        
        cmd_based_rt=Label(frame15,text="CMD BASED RT",font=("Calibri", 11,"bold"),bg="burlywood")
        cmd_based_rt.grid(row=10, column=0)
        cmd_based_rt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        cmd_based_rt.grid(column=1,row=10,pady=2,padx=2)

        spu_cmd_c_rt=Label(frame15,text="SPU CMD C RT",font=("Calibri", 11,"bold"),bg="burlywood")
        spu_cmd_c_rt.grid(row=12, column=0)
        spu_cmd_c_rt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        spu_cmd_c_rt.grid(column=1,row=12,pady=2,padx=2)
       
        dual_cmd_c_rt=Label(frame15,text="DUAL CMD C RT",font=("Calibri", 11,"bold"),bg="burlywood")
        dual_cmd_c_rt.grid(row=13, column=0)
        dual_cmd_c_rt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        dual_cmd_c_rt.grid(column=1,row=13,pady=2,padx=2)
        
        # ============================== GAGAN-SA4W31 =======================================
        frame15=LabelFrame(root,text="GAGAN-SA4W31",bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame15.grid(row=4,column=1,padx=2,pady=2,sticky="nsew")
       
        miss_ph=Label(frame15,text="MISS_PH",font=("Calibri", 11,"bold"),bg="burlywood")
        miss_ph.grid(row=1, column=0)
        miss_ph=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")   
        miss_ph.grid(column=1,row=1,pady=2,padx=2)
       
        fmem=Label(frame15,text="FMEM",font=("Calibri", 11,"bold"),bg="burlywood")
        fmem.grid(row=2, column=0)
        fmem=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        fmem.grid(column=1,row=2,pady=2,padx=2)
       
        cr_aid=Label(frame15,text="CR_AID",font=("Calibri", 11,"bold"),bg="burlywood")
        cr_aid.grid(row=3, column=0)
        cr_aid=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        cr_aid.grid(column=1,row=3,pady=2,padx=2)
       
        full_cntr=Label(frame15,text="FULL_CTRL",font=("Calibri", 11,"bold"),bg="burlywood")
        full_cntr.grid(row=4, column=0)
        full_cntr=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        full_cntr.grid(column=1,row=4,pady=2,padx=2)
       
        lig_1=Label(frame15,text="LIG_1",font=("Calibri", 11,"bold"),bg="burlywood")
        lig_1.grid(row=6, column=0)
        lig_1=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        lig_1.grid(column=1,row=6,pady=2,padx=2)
       
        lig_2=Label(frame15,text="LIG_2",font=("Calibri", 11,"bold"),bg="burlywood")
        lig_2.grid(row=7, column=0)
        lig_2=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        lig_2.grid(column=1,row=7,pady=2,padx=2)
       
        lig_3=Label(frame15,text="LIG_3",font=("Calibri", 11,"bold"),bg="burlywood")
        lig_3.grid(row=8, column=0)
        lig_3=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        lig_3.grid(column=1,row=8,pady=2,padx=2)
       
        lig_4=Label(frame15,text="LIG_4",font=("Calibri", 11,"bold"),bg="burlywood")
        lig_4.grid(row=9, column=0)
        lig_4=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        lig_4.grid(column=1,row=9,pady=2,padx=2)
       
        lin_1=Label(frame15,text="LIN_1",font=("Calibri", 11,"bold"),bg="burlywood")
        lin_1.grid(row=10, column=0)
        lin_1=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        lin_1.grid(column=1,row=10,pady=2,padx=2)
       
        lin_2=Label(frame15,text="LIN_2",font=("Calibri", 11,"bold"),bg="burlywood")
        lin_2.grid(row=11, column=0)
        lin_2=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        lin_2.grid(column=1,row=11,pady=2,padx=2)
       
        prime_ngc=Label(frame15,text="PRIME_NGC",font=("Calibri", 11,"bold"),bg="burlywood")
        prime_ngc.grid(row=12, column=0)
        prime_ngc=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        prime_ngc.grid(column=1,row=12,pady=2,padx=2)
        
        
        # =============================== GAGAN-SA4W32 ===================================
        frame15=LabelFrame(root,text="GAGAN-SA4W32",bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame15.grid(row=4,column=2,padx=2,pady=2,sticky="nsew")
       
        rng_l=Label(frame15,text="Rng L",font=("Calibri", 11,"bold"),bg="burlywood")
        rng_l.grid(row=0, column=0)
        rng_l=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        rng_l.grid(column=1,row=0,pady=2,padx=2)
       
        orbit_phase=Label(frame15,text="Orbit_phase",font=("Calibri", 11,"bold"),bg="burlywood")
        orbit_phase.grid(row=1, column=0)
        orbit_phase=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")   
        orbit_phase.grid(column=1,row=1,pady=2,padx=2)
       
        iono_c=Label(frame15,text="IONO cor",font=("Calibri", 11,"bold"),bg="burlywood")
        iono_c.grid(row=2, column=0)
        iono_c=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        iono_c.grid(column=1,row=2,pady=2,padx=2)
       
        iono_sm=Label(frame15,text="IONO sm",font=("Calibri", 11,"bold"),bg="burlywood")
        iono_sm.grid(row=3, column=0)
        iono_sm=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        iono_sm.grid(column=1,row=3,pady=2,padx=2)
       
        cr_smo=Label(frame15,text="CR_smo",font=("Calibri", 11,"bold"),bg="burlywood")
        cr_smo.grid(row=4, column=0)
        cr_smo=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        cr_smo.grid(column=1,row=4,pady=2,padx=2)
       
        vel_sm=Label(frame15,text="Vel_ms",font=("Calibri", 11,"bold"),bg="burlywood")
        vel_sm.grid(row=5, column=0)
        vel_sm=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        vel_sm.grid(column=1,row=5,pady=2,padx=2)
       
        raim=Label(frame15,text="RAIM",font=("Calibri", 11,"bold"),bg="burlywood")
        raim.grid(row=6, column=0)
        raim=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        raim.grid(column=1,row=6,pady=2,padx=2)
       
        pr_rej=Label(frame15,text="PR Rej",font=("Calibri", 11,"bold"),bg="burlywood")
        pr_rej.grid(row=7, column=0)
        pr_rej=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        pr_rej.grid(column=1,row=7,pady=2,padx=2)
       
        pr_bf_sync=Label(frame15,text="PR BF Sync",font=("Calibri", 11,"bold"),bg="burlywood")
        pr_bf_sync.grid(row=8, column=0)
        pr_bf_sync=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        pr_bf_sync.grid(column=1,row=8,pady=2,padx=2)
       
        cfg_loop=Label(frame15,text="Cfg_loop",font=("Calibri", 11,"bold"),bg="burlywood")
        cfg_loop.grid(row=9, column=0)
        cfg_loop=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        cfg_loop.grid(column=1,row=9,pady=2,padx=2)
       
        int_crd_tst=Label(frame15,text="Int crd Tst",font=("Calibri", 11,"bold"),bg="burlywood")
        int_crd_tst.grid(row=10, column=0)
        int_crd_tst=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        int_crd_tst.grid(column=1,row=10,pady=2,padx=2)
       
        elev_e=Label(frame15,text="Elev En",font=("Calibri", 11,"bold"),bg="burlywood")
        elev_e.grid(row=11, column=0)
        elev_e=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        elev_e.grid(column=1,row=11,pady=2,padx=2)
       
        rst_flag=Label(frame15,text="Rst_flag",font=("Calibri", 11,"bold"),bg="burlywood")
        rst_flag.grid(row=12, column=0)
        rst_flag=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        rst_flag.grid(column=1,row=12,pady=2,padx=2)
        
        odp_rst_sf=Label(frame15,text="ODP Rst SF",font=("Calibri", 11,"bold"),bg="burlywood")
        odp_rst_sf.grid(row=13, column=0)
        odp_rst_sf=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        odp_rst_sf.grid(column=1,row=13,pady=2,padx=2)
        
        cold_vis=Label(frame15,text="Cold Vis",font=("Calibri", 11,"bold"),bg="burlywood")
        cold_vis.grid(row=14, column=0)
        cold_vis=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        cold_vis.grid(column=1,row=14,pady=2,padx=2)
        
        nav_msg_e=Label(frame15,text="Nav Msg En",font=("Calibri", 11,"bold"),bg="burlywood")
        nav_msg_e.grid(row=15, column=0)
        nav_msg_e=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg="burlywood")
        nav_msg_e.grid(column=1,row=15,pady=2,padx=2)
        
        # ====================== GAGAN-SA3W31MSB ==============================
        frame15=LabelFrame(root,text="GAGAN-SA3W31MSB",bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )
        frame15.grid(row=1,column=2,padx=2,pady=2,sticky="nsew")
       
        odp_est=Label(frame15,text="ODP_Est",font=("Calibri", 11,"bold"),bg="burlywood")
        odp_est.grid(row=0, column=0)
        odp_est=Entry(frame15,width=5,state="readonly",bg='light grey',fg="black")
        odp_est.grid(column=1,row=0,pady=2,padx=2)
       
        odp_en=Label(frame15,text="ODP_EN",font=("Calibri", 11,"bold"),bg="burlywood")
        odp_en.grid(row=1, column=0)
        odp_en=Entry(frame15,width=5,state="readonly",bg='light grey',fg="black")   
        odp_en.grid(column=1,row=1,pady=2,padx=2)
       
        phc_usg=Label(frame15,text="PHCUsg",font=("Calibri", 11,"bold"),bg="burlywood")
        phc_usg.grid(row=2, column=0)
        phc_usg=Entry(frame15,width=5,state="readonly",bg='light grey',fg="black")
        phc_usg.grid(column=1,row=2,pady=2,padx=2)
       
        phc_en=Label(frame15,text="PHC En",font=("Calibri", 11,"bold"),bg="burlywood")
        phc_en.grid(row=3, column=0)
        phc_en=Entry(frame15,width=5,state="readonly",bg='light grey',fg="black")
        phc_en.grid(column=1,row=3,pady=2,padx=2)
       
        eph_rt=Label(frame15,text="Eph RT",font=("Calibri", 11,"bold"),bg="burlywood")
        eph_rt.grid(row=0, column=2)
        eph_rt=Entry(frame15,width=5,state="readonly",bg='light grey',fg="black")
        eph_rt.grid(column=3,row=0,pady=2,padx=2)
       
        mnvon=Label(frame15,text="MNVON",font=("Calibri", 11,"bold"),bg="burlywood")
        mnvon.grid(row=1, column=2)
        mnvon=Entry(frame15,width=5,state="readonly",bg='light grey',fg="black")
        mnvon.grid(column=3,row=1,pady=2,padx=2)
       
        numsps=Label(frame15,text="NumSPS",font=("Calibri", 11,"bold"),bg="burlywood")
        numsps.grid(row=2, column=2)
        numsps=Entry(frame15,width=5,state="readonly",bg='light grey',fg="black")
        numsps.grid(column=3,row=2,pady=2,padx=2)
        
        
        # ========================== GRAPH ============================
        frame_cndr_plot = tk.LabelFrame(root, text="CNDR VS SVID PLOT",bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
        bd=2,                    # border thickness
        padx=2, pady=2         # internal padding simulates rounded spacing
        )

        frame_cndr_plot.grid(row=4, column=3, padx=2, pady=2, sticky="n")
        
         
        
        frame_cndr_plot.grid_rowconfigure(0, weight=1)
        frame_cndr_plot.grid_columnconfigure(0, weight=1)
        
        fig_cndr = Figure(figsize=(5.2, 3.6), dpi=100)
        ax_cndr = fig_cndr.add_subplot(111)
        
        ax_cndr.set_title("CNDR Values")
        ax_cndr.set_xlabel("SVIDs")
        ax_cndr.set_ylabel("CNDR Values")
        ax_cndr.set_ylim(0, 60)
        ax_cndr.set_yticks([0, 10, 20, 30, 35, 40, 45, 50, 60])
        
        canvas_cndr = FigureCanvasTkAgg(fig_cndr, master=frame_cndr_plot)
        canvas_cndr.get_tk_widget().grid(row=0, column=0, sticky="SW")
        if rt_name == "RT1":
        
            baud_select()
            update_coms()
        
        # === Footer Section inside scrollable area ===
        separator = tk.Frame(root, bg="black", height=2)
        separator.grid(row=99, column=0, columnspan=40, sticky="ew", pady=(10, 0))
        footer_label = tk.Label(window, text="copyright@2025, Space Navigation Group/URSC/ISRO | Version 1.0",
            font=("Segoe UI", 10, "italic"), bg="navy blue", fg="white", pady=2)
        footer_label.grid(row=100, column=0, columnspan=20, sticky="nsew")
        # --- Footer only in RT1 ---
        
        
       
       
        root.grid_rowconfigure(0, weight=2)
        root.grid_rowconfigure(1, weight=2)
        root.grid_rowconfigure(2, weight=2)
        root.grid_rowconfigure(3, weight=2)
        root.grid_columnconfigure(0,weight=2)
        root.grid_columnconfigure(1,weight=2)
        root.grid_columnconfigure(2,weight=2)
        root.grid_columnconfigure(3,weight=2)
       
        

    def on_tab_change(event):
        global selected_tab
        selected_tab = tab_notebook.tab(tab_notebook.select(), "text")
        #print(f"Tab changed to {selected_tab}. Headers: {RT_HEADERS[selected_tab]}")
        # Use RT_HEADERS[selected_tab] in your extraction logic

    tab_notebook.bind("<<NotebookTabChanged>>", on_tab_change)
    root.mainloop()
        
       
     
def connect_check(args):
    global clicked_bd,clicked_com
    if "-" in clicked_com.get() or "-" in clicked_bd.get():
        connect_btn["state"]="disabled"
    else:
         connect_btn["state"]="active"
def baud_select():
    global clicked_bd,drop_bd,frame1,StringVar,OptionMenu
    clicked_bd=StringVar()
    bds = ["-",
           "300",
           "600",
           "1200",
           "2400",
           "4800",
           "9600",
           "14400",
           "19200",
           "28800",
           "38400",
           "56000",
           "57600",
           "115200",
           "128000",
           "256000"]
    clicked_bd.set(bds[0])
    drop_bd = OptionMenu(frame1, clicked_bd, *bds, command=connect_check)
    drop_bd.config(height=1,width=10,font=("Calibri", 12),bg="burlywood")
    drop_bd.grid(column=4, row=1, padx=2)
def update_coms():
    global clicked_com, drop_COM, frame1
    ports = serial.tools.list_ports.comports()
    # Use .device so this works across platforms and with the ListPortInfo object
    coms = [p.device for p in ports]
    coms.insert(0, "-")
    try:
        drop_COM.destroy()
    except Exception:
        pass
    clicked_com = StringVar()
    clicked_com.set(coms[0])
    drop_COM = OptionMenu(frame1, clicked_com, *coms, command=connect_check)
    drop_COM.config(height=1, width=10, font=("Calibri", 12), bg="burlywood")
    drop_COM.grid(column=1, row=1, padx=2)
    connect_check(0)
   
def reverse_and_concatenate(hex_input, scale=1, is_signed=False):
    """
    Accept either:
      - a hex string (e.g. 'AABBCCDD' or 'aa bb cc dd')
      - a list/tuple of byte-strings like ['AA','BB','CC','DD']
    Returns integer. If is_signed=True, performs sign extension for 32-bit values.
    Behavior:
      - if byte length == 1,2,3,4: treat as given; for 4 bytes swaps 16-bit halves (keeps original behavior)
      - if 8 bytes (16 hex chars) performs the 8-byte reversal logic similar to your previous code.
    """
    if hex_input is None:
        return None

    # If it's a list/tuple, join elements
    if isinstance(hex_input, (list, tuple)):
        hex_str = ''.join(hex_input)
    else:
        # string: remove spaces and 0x prefixes
        hex_str = str(hex_input).replace("0x", "").replace("0X", "").replace(" ", "").replace(",", "")

    # must be even length
    if len(hex_str) % 2 != 0:
        # cannot parse odd length reliably
        return None

    byte_count = len(hex_str) // 2

    try:
        if byte_count in (1, 2, 3):
            val = int(hex_str, 16)
        elif byte_count == 4:
            # original code swapped 16-bit halves: AB CD EF GH -> EF GH AB CD
            first_half = hex_str[:4]
            second_half = hex_str[4:]
            concatenated_hex = second_half + first_half
            val = int(concatenated_hex, 16)
        elif byte_count == 8:
            # reverse bytes within 4-byte halves then concat (preserve your previous behavior)
            first_half = hex_str[:8]
            second_half = hex_str[8:]
            reversed_first_half = first_half[6:8] + first_half[4:6] + first_half[2:4] + first_half[0:2]
            reversed_second_half = second_half[6:8] + second_half[4:6] + second_half[2:4] + second_half[0:2]
            concatenated_hex = reversed_first_half + reversed_second_half
            val = int(concatenated_hex, 16)
        else:
            # fallback: parse as big-endian integer
            val = int(hex_str, 16)
    except Exception:
        return None

    if is_signed:
        # sign-extend for 32-bit values
        if val & (1 << (byte_count*8 - 1)):
            # negative: compute signed value
            val = val - (1 << (byte_count*8))
    return val
 
def decode_channel_status_meaning(status_word):
    """
    Decodes a 16-bit channel status word according to the custom mapping:
    T   - Bits 0+1: Track/Bit Sync
    E   - Bit 2: Ephemeris Av
    P   - Bit 3: Used in Pos
    I   - Bit 4: Iono Correction Av
    S   - Bit 5: SBAS Correction Av
    P1  - Bit 6: PR Validity Reject
    H   - Bit 7: URA/Health
    A   - Bits 8+9: Antenna select (2 bits)
    SR  - Bit 10: SBAS Reject
    R   - Bit 11: RAIM Reject
    E1  - Bit 12: L1/L2 Ephem Indicator
    D   - Bit 14: DR Status
    """
    bits = [(status_word >> i) & 1 for i in range(16)]
    # T: Bits 0 and 1 combined description
    T = "T" if bits[0] else "NT"
    S = "S" if bits[1] else "NS"
    # A: Bits 8 and 9 combined (antenna select)
    antenna_bits = (bits[9] << 1) | bits[8]
    antenna_map = {
        0b00: "1",
        0b01: "2",
        0b10: "3",
        0b11: "4",
    }
    
    return {
        "T": f"{T}/{S}",
        "E": "Y" if bits[2] else "N",
        "P": "Y" if bits[3] else "N",
        "I": "Y" if bits[4] else "N",
        "S": "Y" if bits[5] else "N",
        "P1": "P" if bits[6] else "R",
        "H": "G" if bits[7] else "B",
        "A": antenna_map.get(antenna_bits, "UK"),
        "SR": "P" if bits[10] else "R",
        "R": "P" if bits[11] else "R",
        "E1": "Y" if bits[12] else "N",
        "D": "Y" if bits[14] else "N",
    }
def convert_to_decimal(hex_str):
    reversed_hex = ''.join([hex_str[i:i+2]for i in range(0,len(hex_str),2)][::-1])
    return int(reversed_hex,16)
def chechsum_calulation_covert_decimal(SYN_NanoSecond_hex,SYN_Second_hex,SYN_Weeknumber_hex,Tsm_UpdateCounter_hex,Checksum1):
    global checksum1
    NanoSecond_part1 = convert_to_decimal(SYN_NanoSecond_hex[:4]) 
    NanoSecond_part2 = convert_to_decimal(SYN_NanoSecond_hex[4:])
    Second_part1 = convert_to_decimal(SYN_Second_hex[:4])
    Second_part2 = convert_to_decimal(SYN_Second_hex[4:])
    Week = convert_to_decimal(SYN_Weeknumber_hex)
    Tsm_UpdateCounter=convert_to_decimal(Tsm_UpdateCounter_hex)
    total = NanoSecond_part1+NanoSecond_part2+Second_part1+Second_part2+Week+Tsm_UpdateCounter
    exepected_checksum = (0-total) & 0xFFFF
    
    #print(exepected_checksum)
    #print(CHECKSUM)
    if exepected_checksum == Checksum1:
        
        checksum1 = "Pass"
        csm1.config(fg="dark green")
    else:
        checksum1 =  "Fail"
        csm1.config(fg="dark red")
    return checksum1

def SA4chechsum_calulation_covert_decimal(SYS_NanoSecond_hex,SYS_Second_hex,SYS_Weeknumber_hex,POS_X_hex,POS_Y_hex,POS_Z_hex,POS_Vx_hex,POS_Vy_hex,POS_Vz_hex,UpdateCounter_hex,PDOP_hex ,word20_hex ,Bais_hex ,ISB_hex ,DRIFT_hex ,ISD_hex ,SW_HW_RST_CTR_hex,word28_sw_rst_id_hex,word29_hex,word30_hex,word31_hex,Checksum2):
    global checksum2
    SYS_NanoSecond_part1 = convert_to_decimal(SYS_NanoSecond_hex[:4]) 
    SYS_NanoSecond_part2 = convert_to_decimal(SYS_NanoSecond_hex[4:])
    SYS_Second_part1 = convert_to_decimal(SYS_Second_hex[:4])
    SYS_Second_part2 = convert_to_decimal(SYS_Second_hex[4:])
    SYS_Weeknumber = convert_to_decimal(SYS_Weeknumber_hex)
    SPS_x_part1 = convert_to_decimal(POS_X_hex[:4])
    SPS_x_part2 = convert_to_decimal(POS_X_hex[4:])
    SPS_y_part1 = convert_to_decimal(POS_Y_hex[:4])
    SPS_y_part2 = convert_to_decimal(POS_Y_hex[4:])
    SPS_z_part1 = convert_to_decimal(POS_Z_hex[:4])
    SPS_z_part2 = convert_to_decimal(POS_Z_hex[4:])
    SPS_vx_part1 = convert_to_decimal(POS_Vx_hex[:4])
    SPS_vx_part2 = convert_to_decimal(POS_Vx_hex[4:])
    SPS_vy_part1 = convert_to_decimal(POS_Vy_hex[:4])
    SPS_vy_part2 = convert_to_decimal(POS_Vy_hex[4:])
    SPS_vz_part1 = convert_to_decimal(POS_Vz_hex[:4])
    SPS_vz_part2 = convert_to_decimal(POS_Vz_hex[4:])
    UpdateCounter_part = convert_to_decimal(UpdateCounter_hex)
    pdop_part = convert_to_decimal(PDOP_hex)
    word20_part = convert_to_decimal(word20_hex)
    Bais_part1 = convert_to_decimal(Bais_hex [4:])
    Bais_part2 = convert_to_decimal(Bais_hex [:4])
    ISB_part = convert_to_decimal(ISB_hex)
    DRIFT_part1 = convert_to_decimal(DRIFT_hex [:4])
    DRIFT_part2 = convert_to_decimal(DRIFT_hex [4:])
    ISD_part1 = convert_to_decimal(ISD_hex)
    
    SW_HW_RST_CTR_part = convert_to_decimal(SW_HW_RST_CTR_hex)
    word28_sw_rst_id_part = convert_to_decimal(word28_sw_rst_id_hex )
    word29_part = convert_to_decimal(word29_hex)
    word30_part = convert_to_decimal(word30_hex)
    word31_part = convert_to_decimal(word31_hex)
    
    
    total = SYS_NanoSecond_part1+SYS_NanoSecond_part2+SYS_Second_part1+SYS_Second_part2+SYS_Weeknumber+SPS_x_part1+SPS_x_part2+SPS_y_part1+SPS_y_part2+SPS_z_part1+SPS_z_part2+SPS_vx_part1+SPS_vx_part2+SPS_vy_part1+SPS_vy_part2+SPS_vz_part1+SPS_vz_part2+UpdateCounter_part+pdop_part+word20_part+Bais_part1+Bais_part2+ISB_part+DRIFT_part1+DRIFT_part2+ISD_part1+SW_HW_RST_CTR_part+word28_sw_rst_id_part+word29_part+word30_part+word31_part
            
    exepected_checksum = (0-total) & 0xFFFF
    print(f"Expected_cksm:{exepected_checksum}")
    print(f"checksum2:{Checksum2}")
    
    if exepected_checksum == Checksum2:
        
        checksum2 = "Pass"
        csm1.config(fg="dark green")
    else:
        checksum2 =  "Fail"
        csm1.config(fg="dark red")
    return checksum2
   
   
 
def open_popup():
    popup = tk.Toplevel()
    popup.title("Commands")
    popup.geometry("300x300")

    popup.grid_rowconfigure(1, weight=1)
    popup.grid_columnconfigure(0, weight=1)

    search_var = tk.StringVar()

    search_entry = tk.Entry(popup, textvariable=search_var, fg="blue")
    search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    search_entry.insert(0, " ")

    text_area = tk.Text(popup, wrap=tk.WORD, height=10)
    text_area.grid(row=1, column=0, sticky="nsew", padx=(5,0), pady=(0,5))

    scrollbar = tk.Scrollbar(popup, command=text_area.yview)
    scrollbar.grid(row=1, column=1, sticky="ns", pady=(0,5))
    text_area.config(yscrollcommand=scrollbar.set)

    def highlight(term):
        text_area.tag_remove("highlight", "1.0", tk.END)
        if not term:
            return
        start = "1.0"
        while True:
            pos = text_area.search(term, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(term)}c"
            text_area.tag_add("highlight", pos, end)
            start = end
        text_area.tag_config("highlight", background="yellow")

    def display_commands():
        term = search_var.get().strip().lower()
        text_area.delete("1.0", tk.END)
        for cmd, desc in commands.items():
            combined = f"{cmd}: {desc}".lower()
            if term in combined:
                text_area.insert(tk.END, f"{cmd}: {desc}\n")
        highlight(term)

    def on_focus_in(event):
        if search_entry.get() == "Search cmd":
            search_entry.delete(0, tk.END)
            search_entry.config(fg="black")

    def on_focus_out(event):
        if not search_entry.get():
            search_entry.insert(0, "Search cmd")
            search_entry.config(fg="grey")

    search_entry.bind("<FocusIn>", on_focus_in)
    search_entry.bind("<FocusOut>", on_focus_out)
    search_entry.bind("<KeyRelease>", lambda e: display_commands())

    display_commands()
    
    
# command_functions.py
# Replace your previous command-related functions with these improved, drop-in versions.
# They:
# - Log commands per-RT into a session-stamped CSV
# - For SA3/SA4, capture the RT at thread start (rt_for_send) so replay/commands target the intended RT
# - Accept ASCII-hex or binary files for SA3/SA4
# - Use safer checks for serial port and UI variables
# - Report status via status_var when available
#
# Required globals in your main script:
#   ser, status_var, selected_tab, SAx_HEADERS, file_entries, SESSION_TIMESTAMP,
#   sa3_thread, sa3_running, sa4_thread, sa4_running, dataword_entry, bus_var
#
# Usage: just replace/insert these functions into your existing script.


def get_sa_header(rt, sa_index):
    """ Return proper SA header (list of 4 bytes) for given RT and SA index. """
    rt = rt if rt in SAx_HEADERS else "RT1"
    return [0xAC, 0xCA, 0x1F, SAx_HEADERS[rt][sa_index]]


def log_command(rt, cmd_type, packet):
    """ Log command activity into CSV file per RT. """
    try:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        safe_rt = rt if rt else "UNKNOWN_RT"
        log_file = os.path.join(log_dir, f"{SESSION_TIMESTAMP}_{safe_rt}_commands.csv")
        pkt_bytes = packet if isinstance(packet, (bytes, bytearray)) else bytes(packet)
        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             safe_rt, cmd_type,
                             " ".join(f"{b:02X}" for b in pkt_bytes)])
    except Exception as e:
        print("log_command error:", e)


def send_general_command(data_str, cmd_type):
    """
    Handles manual SA1/SA2 and file-based SA3/SA4:
    - SA1/SA2: data_str like '0x0000 0x0004 0x0055'
    - SA3/SA4: uses file path from file_entries[cmd_type] and streams blocks in background thread
    NOTE: captures current selected_tab when starting SA3/SA4 so the thread uses that RT.
    """
    global sa3_thread, sa3_running, sa4_thread, sa4_running, selected_tab

    # Check serial port
    if not (ser and getattr(ser, "is_open", False)):
        try:
            status_var.set("❌ Serial port not open.")
        except Exception:
            pass
        return

    # File-based SA3/SA4
    if cmd_type in ("SA3", "SA4"):
        filepath = ""
        try:
            filepath = file_entries.get(cmd_type).get()
        except Exception:
            filepath = None

        if not filepath or not os.path.exists(filepath):
            try:
                status_var.set(f"❌ Please select a valid file for {cmd_type} commands.")
            except Exception:
                pass
            return

        # capture the RT that user currently selected at the time of starting send
        rt_for_send = selected_tab

        if cmd_type == "SA3":
            if sa3_thread and sa3_thread.is_alive():
                try:
                    status_var.set("❌ SA3 sending already running!")
                except Exception:
                    pass
                return
            sa3_running = True
            sa3_thread = threading.Thread(
                target=send_sax_from_file,
                args=(filepath, 0.064, cmd_type, rt_for_send),
                daemon=True
            )
            sa3_thread.start()
            try:
                status_var.set("▶️ SA3 sending started.")
            except Exception:
                pass
        else:  # SA4
            if sa4_thread and sa4_thread.is_alive():
                try:
                    status_var.set("❌ SA4 sending already running!")
                except Exception:
                    pass
                return
            sa4_running = True
            sa4_thread = threading.Thread(
                target=send_sax_from_file,
                args=(filepath, 1.0, cmd_type, rt_for_send),
                daemon=True
            )
            sa4_thread.start()
            try:
                status_var.set("▶️ SA4 sending started.")
            except Exception:
                pass
        return

    # SA1 / SA2 MANUAL
    try:
        parts = data_str.strip().split()
        if len(parts) != 3:
            try:
                status_var.set("❌ Enter exactly 3 words (e.g. 0x0000 0x0004 0x0055)")
            except Exception:
                pass
            return

        words = [int(word, 16) for word in parts]
        sa_index = int(cmd_type[-1]) - 1  # SA1 -> 0, SA2 -> 1
        header = get_sa_header(selected_tab, sa_index)

        # convert 3 x 16-bit words -> bytes
        data_bytes = []
        for word in words:
            data_bytes.extend(word.to_bytes(2, byteorder='big'))
        full_packet = bytes(header + data_bytes)

        ser.write(full_packet)
        log_command(selected_tab, cmd_type, full_packet)

        sent_str = f"{cmd_type} command sent ({selected_tab}): {[f'0x{b:02X}' for b in full_packet]}"
        try:
            status_var.set(f"✅ {sent_str}")
        except Exception:
            pass
        print(sent_str)

    except ValueError:
        try:
            status_var.set("❌ Invalid hex format. Use e.g. 0x0000 0x0004 0x0055")
        except Exception:
            pass
    except Exception as e:
        try:
            status_var.set(f"❌ Error sending {cmd_type}: {e}")
        except Exception:
            pass


def send_sax_from_file(filepath, interval, cmd_type, rt_for_send):
    """
    Handles SA3/SA4 file-based packet sending with headers for rt_for_send.
    - Supports ASCII-hex file (text containing only hex chars) or binary file.
    - Splits file_bytes into 64-byte chunks and prefixes each chunk with 4-byte SA header.
    - interval: approximate seconds between chunks (loop uses small sleeps for responsiveness).
    """
    global sa3_running, sa4_running

    try:
        with open(filepath, 'rb') as f:
            raw = f.read()

        # Attempt to decode ASCII hex file (some SA files may be ascii hex). If that fails, treat as binary.
        try:
            as_text = raw.decode('ascii')
            hexstr = ''.join(c for c in as_text if c in '0123456789abcdefABCDEF')
            file_bytes = bytes.fromhex(hexstr)
        except Exception:
            file_bytes = raw

        if len(file_bytes) < 64:
            try:
                status_var.set(f"❌ File must contain at least 64 bytes of data for {cmd_type}.")
            except Exception:
                pass
            if cmd_type == "SA3":
                sa3_running = False
            else:
                sa4_running = False
            return

        sa_index = int(cmd_type[-1]) - 1  # SA3 -> 2, SA4 -> 3
        header = get_sa_header(rt_for_send, sa_index)
        num_blocks = (len(file_bytes) + 63) // 64

        idx = 0
        while (sa3_running if cmd_type == "SA3" else sa4_running) and ser and getattr(ser, "is_open", False):
            start = idx * 64
            end = start + 64
            if start >= len(file_bytes):
                # finished
                if cmd_type == "SA3":
                    sa3_running = False
                else:
                    sa4_running = False
                try:
                    status_var.set(f"⏹️ {cmd_type} sending finished.")
                except Exception:
                    pass
                break

            chunk = file_bytes[start:end]
            packet = bytes(header) + chunk
            ser.write(packet)
            log_command(rt_for_send, cmd_type, packet)

            sent_str = f"{cmd_type} packet ({rt_for_send}) block {idx+1}/{num_blocks}"
            try:
                status_var.set(f"✅ {sent_str}")
            except Exception:
                pass
            print(sent_str)

            idx += 1
            # interval loop uses small sleeps to remain responsive to stop flags
            steps = max(1, int(interval * 1000 / 10))
            for _ in range(steps):
                if not (sa3_running if cmd_type == "SA3" else sa4_running):
                    try:
                        status_var.set(f"⏹️ {cmd_type} sending stopped.")
                    except Exception:
                        pass
                    return
                cmdtime.sleep(0.01)

    except Exception as e:
        try:
            status_var.set(f"❌ Error in {cmd_type} send: {e}")
        except Exception:
            pass
        if cmd_type == "SA3":
            sa3_running = False
        else:
            sa4_running = False


def stop_sa3():
    global sa3_running
    if sa3_running:
        sa3_running = False
        try:
            status_var.set("⏹️ Stopping SA3 sending...")
        except Exception:
            pass


def stop_sa4():
    global sa4_running
    if sa4_running:
        sa4_running = False
        try:
            status_var.set("⏹️ Stopping SA4 sending...")
        except Exception:
            pass


# ===================== BUS COMMANDS =====================
def send_bus_command_button(value):
    """ Send bus command from button (value is integer) """
    if not (ser and getattr(ser, "is_open", False)):
        try:
            status_var.set("❌ Serial port not open.")
        except Exception:
            pass
        return
    try:
        packet = bytes([0xAC, 0xCA, 0x1F, value])
        ser.write(packet)
        # Log with the currently selected RT
        log_command(selected_tab, "BUS", packet)
        try:
            status_var.set(f"✅ BUS command sent ({selected_tab}): {value:02X}")
        except Exception:
            pass
    except Exception as e:
        try:
            status_var.set(f"❌ Error sending BUS command: {e}")
        except Exception:
            pass


def send_bus_command_entry():
    """ Send bus command using value from dataword_entry (hex string) """
    if not (ser and getattr(ser, "is_open", False)):
        try:
            status_var.set("❌ Serial port not open.")
        except Exception:
            pass
        return
    try:
        val = int(dataword_entry.get(), 16)
        packet = bytes([0xAC, 0xCA, 0x1F, val])
        ser.write(packet)
        log_command(selected_tab, "BUS", packet)
        try:
            status_var.set(f"✅ BUS command sent ({selected_tab}): {val:02X}")
        except Exception:
            pass
    except Exception as e:
        try:
            status_var.set(f"❌ Error sending BUS command: {e}")
        except Exception:
            pass


def on_bus_toggle(*args):
    """ Toggle BUS A/B (sends a small packet). """
    try:
        if not (ser and getattr(ser, "is_open", False)):
            try:
                status_var.set("❌ Serial port not open.")
            except Exception:
                pass
            return
        if bus_var.get() not in ["A", "B"]:
            return
        rt_address = 0x00
        bus_val = 0x78 if bus_var.get() == "A" else 0x77
        packet = bytes([0xAC, 0xCA, 0x1F, 0x0B, rt_address, bus_val])
        ser.write(packet)
        bus_name = "BUS A" if bus_val == 0x78 else "BUS B"
        sent_str = f"Packet for toggle: {[f'0x{b:02X}' for b in packet]} ({bus_name})"
        try:
            status_var.set(sent_str)
        except Exception:
            pass
        with open("Buscmd.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | BUS_TOGGLE | {sent_str}\n")
    except Exception as e:
        try:
            status_var.set(f"❌ Error sending bus command (button): {e}")
        except Exception:
            pass
def get_timestamped_filename(base_name: str, suffix: str, rt: str = None) -> str:
    """
    Generate filename:
      GAGANYAN_{SESSION_TIMESTAMP}_{base_name}_{suffix}[_RT].csv
    Pass rt (e.g. 'RT1') to keep files separated per RT.
    """
    rt_part = f"_{rt}" if rt else ""
    safe_base = base_name if base_name else "unspecified"
    filename = f"GAGANYAN_{SESSION_TIMESTAMP}_{safe_base}_{suffix}{rt_part}.csv"
    return filename

def write_to_raw(data, base_name, rt=None):
    file_name = get_timestamped_filename(base_name, "Raw", rt)
    header = ['TimeStamp','RAW DATA']
    os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)
    with open(file_name, mode='a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_rawh2(data, base_name, rt=None):
    file_name = get_timestamped_filename(base_name, "Rawh2", rt)
    header = ['TimeStamp','RAW DATA']
    os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)
    with open(file_name, mode='a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_rawh3(data, base_name, rt=None):
    file_name = get_timestamped_filename(base_name, "Rawh3", rt)
    header = ['TimeStamp','RAW DATA']
    os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)
    with open(file_name, mode='a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_rawh4(data, base_name, rt=None):
    file_name = get_timestamped_filename(base_name, "Rawh4", rt)
    header = ['TimeStamp','RAW DATA']
    os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)
    with open(file_name, mode='a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_SYN(data, base_name, rt=None):
    file_name = get_timestamped_filename(base_name, "Sync", rt)
    header = ['TimeStamp','SYN_SECOND','SYN_NANOSECOND','SYN_WEEKNUMBER']
    os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)
    with open(file_name, mode='a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_SYNh2(data, base_name, rt=None):
    file_name = get_timestamped_filename(base_name, "Synch2", rt)
    header = ['TimeStamp','h2SYN_SECOND','h2SYN_NANOSECOND','h2SYN_WEEKNUMBER']
    os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)
    with open(file_name, mode='a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_pvt(data, base_name, rt=None):
    file_name = get_timestamped_filename(base_name, "PVT", rt)
    os.makedirs(os.path.dirname(file_name) or ".", exist_ok=True)
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
    with open(file_name, mode='a', newline='') as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def update_cndr_plot_func(svid_labels, cndr_values):
    colors = []
    for val in cndr_values:
        if 0 <= val < 20:
            colors.append("pink")  # low range
        elif 20 <= val <= 40:
            colors.append("orange")   # Mid range
        elif 40 <= val <= 60:
            colors.append("green")   # High range
        else:
            colors.append("red")  # Other values
    ax_cndr.clear()
    ax_cndr.set_title("CNDR Values")
    ax_cndr.set_xlabel("SVIDs")
    ax_cndr.set_ylabel("CNDR Values")
    ax_cndr.set_ylim(0, 60)
    ax_cndr.set_yticks([0, 10, 20, 30, 35, 40, 45, 50, 60])

    ax_cndr.bar(range(1, 19), cndr_values, color=colors,edgecolor='black')
    ax_cndr.set_xticks(range(1, 19))
    ax_cndr.set_xticklabels(svid_labels, rotation=45)

    canvas_cndr.draw_idle()


def refresh_cndr_plot():
    try:
        root.update_idletasks()  # make sure entries are updated

        cndr_list_values = [
            float(cndr1.get() or 0), float(cndr2.get() or 0), float(cndr3.get() or 0), float(cndr4.get() or 0),
            float(cndr5.get() or 0), float(cndr6.get() or 0), float(cndr7.get() or 0), float(cndr8.get() or 0),
            float(cndr9.get() or 0), float(cndr10.get() or 0), float(cndr11.get() or 0), float(cndr12.get() or 0),
            float(cndr13.get() or 0), float(cndr14.get() or 0),float(cndr15.get() or 0), float(cndr16.get() or 0), 
            float(cndr17.get() or 0), float(cndr18.get() or 0),
        ]

        svid_labels = [
            svid1.get() or "CH1", svid2.get() or "CH2", svid3.get() or "CH3", svid4.get() or "CH4",
            svid5.get() or "CH5", svid6.get() or "CH6", svid7.get() or "CH7", svid8.get() or "CH8",
            svid9.get() or "CH9", svid10.get() or "CH10", svid11.get() or "CH11", svid12.get() or "CH12",
            svid13.get() or "CH13", svid14.get() or "CH14", svid15.get() or "CH15", svid16.get() or "CH16",
             svid17.get() or "CH17", svid18.get() or "CH18",
        ]

        update_cndr_plot_func(svid_labels, cndr_list_values)

    except Exception as e:
        print("CNDR plot update error:", e)

# read_serial.py
# Drop this function into your existing script (replace old readSerial).
# Requirements (must exist in your program): ser (pyserial Serial), serialData (bool),
# RT_HEADERS (dict mapping RT name -> [header_hex_str,...]), data_queue (queue.Queue),
# counter_value (int) - will be incremented, PACKET_PAYLOAD_SIZE optionally (int).
# If PACKET_PAYLOAD_SIZE isn't defined elsewhere, it defaults to 1206 (same as your previous ser.read(1206)).



# read_serial.py
# Drop this function into your existing script (replace old readSerial).
# Requirements (must exist in your program): ser (pyserial Serial), serialData (bool),
# RT_HEADERS (dict mapping RT name -> [header_hex_str,...]), data_queue (queue.Queue),
# counter_value (int) - will be incremented.
# If PACKET_PAYLOAD_SIZE isn't defined elsewhere, it defaults to 1206 (same as your previous ser.read(1206)).


def readSerial():
    """
    Buffer-based serial reader that searches for any RT header (full 4-byte sequences).
    Pushes tuples (rt_name, hexString) into data_queue.
    """
    global serialData, ser, counter_value

    PACKET_PAYLOAD_SIZE = globals().get("PACKET_PAYLOAD_SIZE", 1206)

    # Precompute header bytes
    headers_bytes_map = {rt: [bytes.fromhex(h) for h in headers] for rt, headers in RT_HEADERS.items()}

    buf = bytearray()
    try:
        while serialData:
            if ser and getattr(ser, "in_waiting", 0) > 0:
                chunk = ser.read(ser.in_waiting)
                if chunk:
                    buf.extend(chunk)

                # scan for complete packets
                found = True
                while found:
                    found = False
                    for rt_name, hdr_list in headers_bytes_map.items():
                        for hdr in hdr_list:
                            idx = buf.find(hdr)
                            if idx != -1:
                                total_needed = idx + len(hdr) + PACKET_PAYLOAD_SIZE
                                if len(buf) >= total_needed:
                                    pkt = bytes(buf[idx:total_needed])
                                    del buf[:total_needed]
                                    hexDecodedData = pkt.hex()
                                    data_queue.put((rt_name, hexDecodedData))
                                    counter_value += 1
                                    found = True
                                    break
                                else:
                                    # header present but we don't yet have full payload
                                    found = False
                                    break
                        if found:
                            break

                # limit buffer size to avoid memory growth
                max_keep = PACKET_PAYLOAD_SIZE * 4
                if len(buf) > max_keep:
                    buf = buf[-(PACKET_PAYLOAD_SIZE + 32):]
            else:
                time.sleep(0.01)
    except Exception as e:
        print("readSerial error:", e)
       
def extract_word20_flags(word20):
    
    sbasen_map = {
        0b00: "DISABLE",
        0b01: "ENABLE",
    }
 
    sys_mode_map = {
        0b01: "GPS",
        0b10: "NAVIC",
        0b11: "GPS+NAVIC",
    }
    
    rec_mode_map = {
        0b01: "GPS",
        0b10: "NAVIC",
        0b11: "GPS+NAVIC",
    }
 
    time_mode_map = {
        0b00: "NOT AV",
        0b01: "GPS",
        0b10: "NAVIC",
    }
 
    alm_av_map = {
        0b00: "ALM AV",
        0b01: "ALM NOT AV",
        
    }
 
    time_av_map = {
        0b00: "TIME NOT AV",
        0b01: "TIME AV",
    }
    pose_mode_map = {
        0b00: "3D",
        0b01: "01-2D",
        0b10: "NOT AV"
        }
 
    pose_av_map = {
        0b00: "POS NOT AV",
        0b01: "POS AV",
        
    }
    
    
 
    # Extract values
    tm_sel_val      = (word20 >> 15) & 0x1  # BIT15
    swdt_val        = (word20 >> 14) & 0x1  # BIT14
    hwdt_val        = (word20 >> 13) & 0x1 # BIT13
    sbasen_val      = (word20 >> 12) & 0x1 # BIT12
    system_mode_val = (word20 >> 10) & 0x3 # BIT11 & BIT10 
    rec_mode_val    = (word20 >> 8) & 0x3 # BIT9 & BIT8
    time_mode_val   = (word20 >> 6) & 0x3  # BIT7 & BIT6
    alm_av_val      = (word20 >> 4) & 0x3 # BIT5 & BIT4
    time_av_val     = (word20 >> 3) & 0x1  # BIT3
    pose_mode_val   = (word20 >> 1) & 0x3 # BIT2 & BIT1
    pos_av_val      = word20 & 0x1 # BIT0
 
    # Compose result
    return {
        "Tm_sel":      tm_sel_val,  # No mapping provided
        "SWDT":        swdt_val,    # No mapping provided
        "HWDT":        hwdt_val,    # No mapping provided
        "SBASEN":      sbasen_map.get(sbasen_val, str(sbasen_val)),
        "System_mode": sys_mode_map.get(system_mode_val, str(system_mode_val)),
        "Rec_Mode":    rec_mode_map.get(rec_mode_val, str(rec_mode_val)),
        "Time_Mode":   time_mode_map.get(time_mode_val, str(time_mode_val)),
        "Alm_Av":      alm_av_map.get(alm_av_val, str(alm_av_val)),
        "Time_Av":     time_av_map.get(time_av_val, str(time_av_val)),
        "Pose_Mode":   pose_mode_map.get(pose_mode_val, str(pose_mode_val)),
        "Pos_Av":      pose_av_map.get(pos_av_val, str(pos_av_val)),
    }
    
    
 
 
 
 
def extract_word28LSB_flags(word28):
    sps_id_map = {
        0b01: "SPS-10",
        0b10: "SPS-20",
        0b11: "SPS-30"
    }
 
    # Extract raw values
    sw_rst_id_val = (word28 >> 8) & 0xFF  # Bits 15-8
    sps_id_val = (word28 >> 6) & 0x3      # Bits 7-6
    sol_mode_val = (word28 >> 4) & 0x3    # Bits 5-4
    port_config_val = word28 & 0xF        # Bits 3-0
 
    # Map SPS_ID to human-readable string, default to raw value if not mapped
    sps_id_str = sps_id_map.get(sps_id_val, str(sps_id_val))
 
    # Decode Port_config bits for each antenna
    port_config_bits = {
        "Antenna_1": "GPS" if (port_config_val & 0x1) else "NAVIC",
        "Antenna_2": "GPS" if (port_config_val & 0x2) else "NAVIC",
        "Antenna_3": "GPS" if (port_config_val & 0x4) else "NAVIC",
        "Antenna_4": "GPS" if (port_config_val & 0x8) else "NAVIC",
    }
 
    return {
        "SW_Rst_ID":   sw_rst_id_val,
        "SPS_ID":      sps_id_str,
        "Sol_mode":     sol_mode_val,
        "Port_config": port_config_bits
    }
   
 
def extract_sps3word31LSB_flags(word31Lsb):
    return {
        "ODP_Est flag":  (word31Lsb >> 6) & 0x3,    # BIT7 & BIT6
        "ODP_ENA":         (word31Lsb >> 5) & 0x1,   # BIT5
        "PHCUsage":         (word31Lsb >> 4) & 0x1,   # BIT4
        "PHCEn":         (word31Lsb >> 3) & 0x1,   # BIT3
        "Eph RT":         (word31Lsb >> 2) & 0x1,   # BIT2
        "MNVON":         (word31Lsb >> 1) & 0x1,   # BIT1
        "NUMSPS":     (word31Lsb >> 0) & 0x1,        # BITS0
    }
 
 
def extract_word31_flags(word31):
    return {
        "RT_ID":         (word31 >> 14) & 0x3,  # 2 bits: 15-14
        "Mission_Phase": (word31 >> 12) & 0x3,  # 2 bits: 13-12
        "Fmem":          (word31 >> 11) & 0x1,  # BIT11
        "Cr_Aid":        (word31 >> 10) & 0x1,  # BIT10
        "FLL_Cntr":      (word31 >> 9) & 0x1,   # BIT9
        "S_ID":          (word31 >> 8) & 0x1,   # BIT8
        "LIG_1":         (word31 >> 7) & 0x1,   # BIT7
        "LIG_2":         (word31 >> 6) & 0x1,   # BIT6
        "LIG_3":         (word31 >> 5) & 0x1,   # BIT5
        "LIG_4":         (word31 >> 4) & 0x1,   # BIT4
        "LIN_1":         (word31 >> 3) & 0x1,   # BIT3
        "LIN_2":         (word31 >> 2) & 0x1,   # BIT2
        "Prime_NGC":     word31 & 0x3,          # BITS 1-0
    }
 
def extract_sa4w32_flags(word32):
    return {
        "Rng L":         (word32 >> 15) & 0x1,  # bit:15
        "Orbit Phase": (word32 >> 14) & 0x3,  # bit 14
        "Iono C":          (word32 >> 13) & 0x1,  # BIT 13
        "Iono Sm":        (word32 >> 12) & 0x1,  # BIT 12
        "Cr Smo":      (word32 >> 11) & 0x1,   # BIT 11
        "Vel sm":          (word32 >> 10) & 0x1,   # BIT 10
        "RAIM":         (word32 >> 9) & 0x1,   # BIT 9
        "PR Rej":         (word32 >> 8) & 0x1,   # BIT 8
        "Pr Bf Sync":         (word32 >> 7) & 0x1,   # BIT 7
        "Cfg loop":         (word32 >> 6) & 0x1,   # BIT 6
        "int crd tst":         (word32 >> 5) & 0x1,   # BIT 5
        "Elev En":         (word32 >> 4) & 0x1,   # BIT 4
        "Rst Flag":     (word32 >> 3) & 0x1,      # BITS 3
        "ODP Rst Sp":         (word32 >> 1) & 0x1,   # BIT 2
        "Cold Vis":         (word32 >> 1) & 0x1,   # BIT 1
        "Navic Msg En":         (word32 >> 0) & 0x1,   # BIT 0
    }
 
 
 
def process_data():
    global selected_tab
   # Replace the top portion of process_data where you get item from queue and pick headers.
# Original lines like:
#    item = data_queue.get()
#    if not item:
#        continue
#    data_type, hexDecodedData = item
#    # Instead of just the tab, we process by header
#    headers = RT_HEADERS[selected_tab]
# Replace with the following:
    
    
    try:
        while True:
            item = data_queue.get()
    

        
            if not item:
                continue
            data_type, hexDecodedData = item
            # data_type is the RT name we queued (e.g., "RT1", "RT2", "RT3")
            rt_name = data_type
            # Ensure header lookup uses rt_name (fall back to selected_tab if missing)
            headers = RT_HEADERS.get(rt_name, RT_HEADERS.get(selected_tab))
            main_header = headers[0].lower()
            secondary_header = headers[1].lower() if len(headers) > 1 else None
            
            # Normalize hexDecodedData to lower-case for safe startswith checks
            hexDecodedData = hexDecodedData.lower()
            if hexDecodedData.startswith(main_header):
           
                                SYN_NanoSecond_hex=hexDecodedData[12:20]
                                SYN_Second_hex=hexDecodedData[20:28]
                                SYN_Weeknumber_hex=hexDecodedData[28:32]
                                Tsm_UpdateCounter_hex=hexDecodedData[32:36]
                                csm1_hex = hexDecodedData[36:40]
                                SYS_NanoSecond_hex=hexDecodedData[140:148]
                                SYS_Second_hex=hexDecodedData[148:156]
                                SYS_Weeknumber_hex=hexDecodedData[156:160]
                                
                                
                                
                               
                                POS_X_hex = hexDecodedData[160:168]
                                POS_Y_hex = hexDecodedData[168:176]
                                POS_Z_hex = hexDecodedData[176:184]
                                POS_Vx_hex = hexDecodedData[184:192]
                                POS_Vy_hex = hexDecodedData[192:200]
                                POS_Vz_hex = hexDecodedData[200:208]
                               
                                UpdateCounter_hex=hexDecodedData[208:212]# Update Counter
                                PDOP_hex = hexDecodedData[212:216]
                               
                                word20_hex = hexDecodedData[216:220]   
                                word20 = int(word20_hex, 16)
                                flag = extract_word20_flags(word20)
                                #print(flags)
                               
     
     
                               
                                Bais_hex=hexDecodedData[220:228]
                                ISB_hex = hexDecodedData[228:232]
                                DRIFT_hex = hexDecodedData[232:240]
                                ISD_hex=hexDecodedData[240:244]
                                HW_reset_counter_hex=hexDecodedData[244:246]
                                SW_reset_counter_hex=hexDecodedData[246:248]
                                SW_HW_RST_CTR_hex = HW_reset_counter_hex+SW_reset_counter_hex
                                
                               
                                word28_hex = hexDecodedData[248:250]   
                                word28 = reverse_and_concatenate(word28_hex)
                                flag1 = extract_word28LSB_flags(word28)
                                #print(flags)
                                sw_rst_id_hex=hexDecodedData[250:252]
                                word28_sw_rst_id_hex = word28_hex + sw_rst_id_hex
                                
                                Navic_msg_counter_hex=hexDecodedData[252:254]
                                Navic_msg_22_counter_hex=hexDecodedData[254:256]
                                word29_hex = Navic_msg_counter_hex+Navic_msg_counter_hex
                                No_of_Sat_hex=hexDecodedData[256:258]
                                Leo_sat_id_mil_hex=hexDecodedData[258:260]
                                word30_hex = No_of_Sat_hex+Leo_sat_id_mil_hex
                                
                                word31Lsb_hex = hexDecodedData[260:262]   
                                word31Lsb = reverse_and_concatenate(word31Lsb_hex)
                                flag3 = extract_sps3word31LSB_flags(word31Lsb)
                                
                                Navic_cmd_var_hex = hexDecodedData[262:264]
                                word31_hex = word31Lsb_hex + Navic_cmd_var_hex
                                
                                csm2_hex=hexDecodedData[264:268]   
                                Checksum2=reverse_and_concatenate(csm2_hex)
                                SA4chechsum_calulation_covert_decimal(SYS_NanoSecond_hex,SYS_Second_hex,SYS_Weeknumber_hex,POS_X_hex,POS_Y_hex,POS_Z_hex,POS_Vx_hex,POS_Vy_hex,POS_Vz_hex,UpdateCounter_hex,PDOP_hex ,word20_hex ,Bais_hex ,ISB_hex ,DRIFT_hex ,ISD_hex ,SW_HW_RST_CTR_hex,word28_sw_rst_id_hex,word29_hex,word30_hex,word31_hex,Checksum2)
                               
                               
               
                       
                               
                                SVID1_hex = hexDecodedData[270:272]
                                SVID2_hex = hexDecodedData[268:270]
                                SVID3_hex = hexDecodedData[274:276]
                                SVID4_hex = hexDecodedData[272:274]
                                SVID5_hex = hexDecodedData[278:280]
                                SVID6_hex = hexDecodedData[276:278]
                                SVID7_hex = hexDecodedData[282:284]
                                SVID8_hex = hexDecodedData[280:282]
                                SVID9_hex = hexDecodedData[286:288]
                                SVID10_hex = hexDecodedData[284:286]
                                SVID11_hex = hexDecodedData[290:292]
                                SVID12_hex = hexDecodedData[288:290]
                                SVID13_hex = hexDecodedData[294:296]
                                SVID14_hex = hexDecodedData[292:294]
                                SVID15_hex = hexDecodedData[298:300]
                                SVID16_hex = hexDecodedData[296:298]
                                SVID17_hex = hexDecodedData[1166:1168]
                                SVID18_hex = hexDecodedData[1164:1166]
                               
                                IODE1_hex = hexDecodedData[302:304]
                                IODE2_hex = hexDecodedData[300:302]
                                IODE3_hex = hexDecodedData[306:308]
                                IODE4_hex = hexDecodedData[304:306]
                                IODE5_hex = hexDecodedData[310:312]                         
                                IODE6_hex = hexDecodedData[308:310]
                                IODE7_hex = hexDecodedData[314:316]
                                IODE8_hex = hexDecodedData[312:314]
                                IODE9_hex = hexDecodedData[318:320]
                                IODE10_hex = hexDecodedData[316:318]
                                IODE11_hex = hexDecodedData[322:324]
                                IODE12_hex = hexDecodedData[320:322]
                                IODE13_hex = hexDecodedData[326:328]
                                IODE14_hex = hexDecodedData[324:326]
                                IODE15_hex = hexDecodedData[330:332]                         
                                IODE16_hex = hexDecodedData[328:330]
                                IODE17_hex = hexDecodedData[1170:1172]
                                IODE18_hex = hexDecodedData[1168:1170]
                               
                               
                                CNDR1_hex = hexDecodedData[334:336]
                                CNDR2_hex = hexDecodedData[332:334]
                                CNDR3_hex = hexDecodedData[338:340]
                                CNDR4_hex = hexDecodedData[336:338]
                                CNDR5_hex = hexDecodedData[342:344]
                                CNDR6_hex = hexDecodedData[340:342]
                                CNDR7_hex = hexDecodedData[346:348]
                                CNDR8_hex = hexDecodedData[344:346]
                                CNDR9_hex = hexDecodedData[350:352]
                                CNDR10_hex = hexDecodedData[348:350]
                                CNDR11_hex = hexDecodedData[354:356]
                                CNDR12_hex = hexDecodedData[352:354]
                                CNDR13_hex = hexDecodedData[358:360]
                                CNDR14_hex = hexDecodedData[356:358]
                                CNDR15_hex = hexDecodedData[362:364]
                                CNDR16_hex = hexDecodedData[360:362]
                                CNDR17_hex = hexDecodedData[1174:1176]
                                CNDR18_hex = hexDecodedData[1172:1174]
                               
                                Last_cmd_ex_hex=hexDecodedData[364:372]
                                Last_reset_time_hex = hexDecodedData[372:376]
                                Total_cmd_counter_hex = hexDecodedData[376:378]
                                Cmd_counter_based_rt_hex = hexDecodedData[378:380]
                               
                                ACQ1_hex = hexDecodedData[382:384]
                                ACQ2_hex = hexDecodedData[380:382]
                                ACQ3_hex = hexDecodedData[386:388]
                                ACQ4_hex = hexDecodedData[384:386]
                               
                                word31_hex = hexDecodedData[388:392]   # Update indices as needed
                                word31 = reverse_and_concatenate(word31_hex)
                                flags = extract_word31_flags(word31)
                               
                                word32_hex = hexDecodedData[392:396]   # Update indices as needed
                                word32 = reverse_and_concatenate(word32_hex)
                                flag2 = extract_sa4w32_flags(word32)
                               
                                CHANNEL_STATUS_hex = [
                                    hexDecodedData[396:400],  # 1
                                    hexDecodedData[400:404],  # 2
                                    hexDecodedData[404:408],  # 3
                                    hexDecodedData[408:412],  # 4
                                    hexDecodedData[412:416],  # 5
                                    hexDecodedData[416:420],  # 6
                                    hexDecodedData[420:424],  # 7
                                    hexDecodedData[424:428],  # 8
                                    hexDecodedData[428:432],  # 9
                                    hexDecodedData[432:436],  # 10
                                    hexDecodedData[436:440],  # 11
                                    hexDecodedData[440:444],  # 12
                                    hexDecodedData[444:448],  # 13
                                    hexDecodedData[448:452],  # 14
                                    hexDecodedData[452:456],  # 15
                                    hexDecodedData[456:460],  # 16
                                    hexDecodedData[1176:1180],  # 17
                                    hexDecodedData[1180:1184],  # 18
                                ]
                                 
                                #SV1
                                PR1_hex = hexDecodedData[524:532]
                                PR2_hex = hexDecodedData[532:540]
                                PR3_hex = hexDecodedData[540:548]
                                PR4_hex = hexDecodedData[548:556]
                                PR5_hex = hexDecodedData[556:564]
                                PR6_hex = hexDecodedData[564:572]
                                PR7_hex = hexDecodedData[572:580]
                                PR8_hex = hexDecodedData[580:588]
                                PR9_hex = hexDecodedData[588:596]
                                PR10_hex = hexDecodedData[596:604]
                                PR11_hex = hexDecodedData[604:612]
                                PR12_hex = hexDecodedData[612:620]
                                PR13_hex = hexDecodedData[620:628]
                                PR14_hex = hexDecodedData[628:636]
                                PR15_hex = hexDecodedData[636:644]
                                PR16_hex = hexDecodedData[644:652]
                                PR17_hex = hexDecodedData[1188:1196]
                                PR18_hex = hexDecodedData[1196:1204]
                               
                                #Delta SV1
                                DR1_hex = hexDecodedData[652:660]
                                DR2_hex = hexDecodedData[660:668]
                                DR3_hex = hexDecodedData[668:676]
                                DR4_hex = hexDecodedData[676:684]
                                DR5_hex = hexDecodedData[684:692]
                                DR6_hex = hexDecodedData[692:700]
                                DR7_hex = hexDecodedData[700:708]
                                DR8_hex = hexDecodedData[708:716]
                                DR9_hex = hexDecodedData[716:724]
                                DR10_hex = hexDecodedData[724:732]
                                DR11_hex = hexDecodedData[732:740]
                                DR12_hex = hexDecodedData[740:748]
                                DR13_hex = hexDecodedData[748:756]
                                DR14_hex = hexDecodedData[756:764]
                                DR15_hex = hexDecodedData[764:772]
                                DR16_hex = hexDecodedData[772:780]
                                DR17_hex = hexDecodedData[1204:1212]
                                DR18_hex = hexDecodedData[1212:1220]
                               
                                Dual_exe_cmd_c_hex = hexDecodedData[1186:1188]
                                Spu_cmd_c_hex =hexDecodedData[1184:1186]
                                Nrffc_counter1_hex = hexDecodedData[1244:1246]
                                Nrffc_counter2_hex = hexDecodedData[1246:1248]
                                Grffc_counter1_hex = hexDecodedData[1248:1250]
                                Grffc_counter2_hex = hexDecodedData[1250:1252]
                                Grffc_counter3_hex = hexDecodedData[1252:1254]
                                Grffc_counter4_hex = hexDecodedData[1254:1256]
                                
                               
                                 #ELEV
                                Elev1_hex = hexDecodedData[1258:1260]
                                Elev2_hex = hexDecodedData[1256:1258]
                                Elev3_hex = hexDecodedData[1262:1264]
                                Elev4_hex = hexDecodedData[1260:1262]
                                Elev5_hex = hexDecodedData[1266:1268]
                                Elev6_hex = hexDecodedData[1264:1266]
                                Elev7_hex = hexDecodedData[1270:1272]
                                Elev8_hex = hexDecodedData[1268:1270]
                                Elev9_hex = hexDecodedData[1274:1276]
                                Elev10_hex = hexDecodedData[1272:1274]
                                Elev11_hex = hexDecodedData[1278:1280]
                                Elev12_hex = hexDecodedData[1276:1278]
                                Elev13_hex = hexDecodedData[1282:1284]
                                Elev14_hex = hexDecodedData[1280:1282]
                                Elev15_hex = hexDecodedData[1286:1288]
                                Elev16_hex = hexDecodedData[1284:1286]
                                Elev17_hex = hexDecodedData[1290:1292]
                                Elev18_hex = hexDecodedData[1288:1290]
                               
                               
                                INS_x_hex = hexDecodedData[1292:1300]
                                INS_y_hex = hexDecodedData[1300:1308]
                                INS_z_hex = hexDecodedData[1308:1316]
                                INS_vx_hex = hexDecodedData[1316:1324]
                                INS_vy_hex = hexDecodedData[1324:1332]
                                INS_vz_hex = hexDecodedData[1332:1340]
                                
                                fix_3D_hex = hexDecodedData[1676:1680]
                                PPS_Nanosec_hex = hexDecodedData[1680:1688]
                                PPS_Sec_hex = hexDecodedData[1688:1696]
                                PPS_Week_hex = hexDecodedData[1696:1700]
                                Leap_hex = hexDecodedData[1700:1704]
                                
                            
                                # Convert hex to decimal and scale as needed
                                SYN_NanoSecond=reverse_and_concatenate(SYN_NanoSecond_hex)
                                SYN_Second=reverse_and_concatenate(SYN_Second_hex)
                                SYN_WeekNumber=reverse_and_concatenate(SYN_Weeknumber_hex)
                                TSM_update_counter=reverse_and_concatenate(Tsm_UpdateCounter_hex)
                               
           
                                Checksum1=reverse_and_concatenate(csm1_hex)
                                chechsum_calulation_covert_decimal(SYN_NanoSecond_hex,SYN_Second_hex,SYN_Weeknumber_hex,Tsm_UpdateCounter_hex,Checksum1)
                               
                                 
                                SYS_Second=reverse_and_concatenate(SYS_Second_hex)
                                SYS_NanoSecond=reverse_and_concatenate(SYS_NanoSecond_hex)
                                SYS_WeekNumber=reverse_and_concatenate(SYS_Weeknumber_hex)
                               
                                POS_x = reverse_and_concatenate(POS_X_hex, is_signed=True)/100.0
                                POS_y = reverse_and_concatenate(POS_Y_hex, is_signed=True)/100.0
                                POS_z = reverse_and_concatenate(POS_Z_hex, is_signed=True)/100.0
                                POS_vx = reverse_and_concatenate(POS_Vx_hex, is_signed=True)/1000.0
                                POS_vy = reverse_and_concatenate(POS_Vy_hex, is_signed=True)/1000.0
                                POS_vz = reverse_and_concatenate(POS_Vz_hex, is_signed=True)/1000.0
                               
                               
                               
                                UpdateCounter=reverse_and_concatenate(UpdateCounter_hex)
                                PDOP = reverse_and_concatenate(PDOP_hex, is_signed=True)/100.0
                                word20 =  reverse_and_concatenate(word20_hex)
                               
                                Bais=reverse_and_concatenate(Bais_hex)
                                ISB = reverse_and_concatenate(ISB_hex)
                               
                                DRIFT = reverse_and_concatenate(DRIFT_hex, is_signed=True)/100.0
                                ISD=reverse_and_concatenate(ISD_hex)
                               
                               
                                SW_reset_counter=reverse_and_concatenate(SW_reset_counter_hex)
                                HW_reset_counter=reverse_and_concatenate(HW_reset_counter_hex)
                                SW_RST_ID=reverse_and_concatenate(sw_rst_id_hex)
                                Navic_msg_22_counter=reverse_and_concatenate(Navic_msg_22_counter_hex)
                                Navic_msg_counter=reverse_and_concatenate(Navic_msg_counter_hex)
                                Leo_sat_id_mil=reverse_and_concatenate(Leo_sat_id_mil_hex)
                                No_of_Sat=reverse_and_concatenate(No_of_Sat_hex)
                                Navic_cmd_var=reverse_and_concatenate (Navic_cmd_var_hex)
                                
                               
                                SVID1 = reverse_and_concatenate(SVID1_hex)
                                SVID2 = reverse_and_concatenate(SVID2_hex)
                                SVID3 = reverse_and_concatenate(SVID3_hex)
                                SVID4 = reverse_and_concatenate(SVID4_hex)
                                SVID5 = reverse_and_concatenate(SVID5_hex)
                                SVID6 = reverse_and_concatenate(SVID6_hex)
                                SVID7 = reverse_and_concatenate(SVID7_hex)
                                SVID8 = reverse_and_concatenate(SVID8_hex)
                                SVID9 = reverse_and_concatenate(SVID9_hex)
                                SVID10 = reverse_and_concatenate(SVID10_hex)
                                SVID11 = reverse_and_concatenate(SVID11_hex)
                                SVID12 = reverse_and_concatenate(SVID12_hex)
                                SVID13 = reverse_and_concatenate(SVID13_hex)
                                SVID14 = reverse_and_concatenate(SVID14_hex)
                                SVID15 = reverse_and_concatenate(SVID15_hex)
                                SVID16 = reverse_and_concatenate(SVID16_hex)
                                SVID17 = reverse_and_concatenate(SVID17_hex)
                                SVID18 = reverse_and_concatenate(SVID18_hex)
                               
                                IODE1 = reverse_and_concatenate(IODE1_hex)
                                IODE2 = reverse_and_concatenate(IODE2_hex)
                                IODE3 = reverse_and_concatenate(IODE3_hex)
                                IODE4 = reverse_and_concatenate(IODE4_hex)
                                IODE5 = reverse_and_concatenate(IODE5_hex)
                                IODE6 = reverse_and_concatenate(IODE6_hex)
                                IODE7 = reverse_and_concatenate(IODE7_hex)
                                IODE8 = reverse_and_concatenate(IODE8_hex)
                                IODE9 = reverse_and_concatenate(IODE9_hex)
                                IODE10 = reverse_and_concatenate(IODE10_hex)
                                IODE11 = reverse_and_concatenate(IODE11_hex)
                                IODE12 = reverse_and_concatenate(IODE12_hex)
                                IODE13 = reverse_and_concatenate(IODE13_hex)
                                IODE14 = reverse_and_concatenate(IODE14_hex)
                                IODE15 = reverse_and_concatenate(IODE15_hex)
                                IODE16 = reverse_and_concatenate(IODE16_hex)
                                IODE17 = reverse_and_concatenate(IODE17_hex)
                                IODE18 = reverse_and_concatenate(IODE18_hex)
                               
                                CNDR1 = reverse_and_concatenate(CNDR1_hex)
                                CNDR2 = reverse_and_concatenate(CNDR2_hex)
                                CNDR3 = reverse_and_concatenate(CNDR3_hex)
                                CNDR4 = reverse_and_concatenate(CNDR4_hex)
                                CNDR5 = reverse_and_concatenate(CNDR5_hex)
                                CNDR6 = reverse_and_concatenate(CNDR6_hex)
                                CNDR7 = reverse_and_concatenate(CNDR7_hex)
                                CNDR8 = reverse_and_concatenate(CNDR8_hex)
                                CNDR9 = reverse_and_concatenate(CNDR9_hex)
                                CNDR10 = reverse_and_concatenate(CNDR10_hex)
                                CNDR11 = reverse_and_concatenate(CNDR11_hex)
                                CNDR12 = reverse_and_concatenate(CNDR12_hex)
                                CNDR13 = reverse_and_concatenate(CNDR13_hex)
                                CNDR14 = reverse_and_concatenate(CNDR14_hex)
                                CNDR15 = reverse_and_concatenate(CNDR15_hex)
                                CNDR16 = reverse_and_concatenate(CNDR16_hex)
                                CNDR17 = reverse_and_concatenate(CNDR17_hex)
                                CNDR18 = reverse_and_concatenate(CNDR18_hex)
                                
                               
                               
                                Last_cmd_ex=reverse_and_concatenate(Last_cmd_ex_hex)
                                Last_reset_time = reverse_and_concatenate(Last_reset_time_hex)
                                Total_cmd_counter = reverse_and_concatenate(Total_cmd_counter_hex)
                                Cmd_counter_based_rt = reverse_and_concatenate(Cmd_counter_based_rt_hex)
                               
                                ACQ1 = reverse_and_concatenate(ACQ1_hex)
                                ACQ2 = reverse_and_concatenate(ACQ2_hex)
                                ACQ3 = reverse_and_concatenate(ACQ3_hex)
                                ACQ4 = reverse_and_concatenate(ACQ4_hex)
                               
                                CHANNEL_STATUS = [reverse_and_concatenate(h) for h in CHANNEL_STATUS_hex]
                               
                                PR1 = reverse_and_concatenate(PR1_hex)
                                PR2 = reverse_and_concatenate(PR2_hex)
                                PR3 = reverse_and_concatenate(PR3_hex)
                                PR4 = reverse_and_concatenate(PR4_hex)
                                PR5 = reverse_and_concatenate(PR5_hex)
                                PR6 = reverse_and_concatenate(PR6_hex)
                                PR7 = reverse_and_concatenate(PR7_hex)
                                PR8 = reverse_and_concatenate(PR8_hex)
                                PR9 = reverse_and_concatenate(PR9_hex)
                                PR10 = reverse_and_concatenate(PR10_hex)
                                PR11 = reverse_and_concatenate(PR11_hex)
                                PR12 = reverse_and_concatenate(PR12_hex)
                                PR13 = reverse_and_concatenate(PR13_hex)
                                PR14 = reverse_and_concatenate(PR14_hex)
                                PR15 = reverse_and_concatenate(PR15_hex)
                                PR16 = reverse_and_concatenate(PR16_hex)
                                PR17 = reverse_and_concatenate(PR17_hex)
                                PR18 = reverse_and_concatenate(PR18_hex)
                               
                               
                                DR1 = reverse_and_concatenate(DR1_hex,is_signed=True)/1000.0
                                DR2 = reverse_and_concatenate(DR2_hex,is_signed=True)/1000.0
                                DR3 = reverse_and_concatenate(DR3_hex,is_signed=True)/1000.0
                                DR4 = reverse_and_concatenate(DR4_hex,is_signed=True)/1000.0
                                DR5 = reverse_and_concatenate(DR5_hex,is_signed=True)/1000.0
                                DR6 = reverse_and_concatenate(DR6_hex,is_signed=True)/1000.0
                                DR7 = reverse_and_concatenate(DR7_hex,is_signed=True)/1000.0
                                DR8 = reverse_and_concatenate(DR8_hex,is_signed=True)/1000.0
                                DR9 = reverse_and_concatenate(DR9_hex,is_signed=True)/1000.0
                                DR10 = reverse_and_concatenate(DR10_hex,is_signed=True)/1000.0
                                DR11 = reverse_and_concatenate(DR11_hex,is_signed=True)/1000.0
                                DR12 = reverse_and_concatenate(DR12_hex,is_signed=True)/1000.0
                                DR13 = reverse_and_concatenate(DR13_hex,is_signed=True)/1000.0
                                DR14 = reverse_and_concatenate(DR14_hex,is_signed=True)/1000.0
                                DR15 = reverse_and_concatenate(DR15_hex,is_signed=True)/1000.0
                                DR16 = reverse_and_concatenate(DR16_hex,is_signed=True)/1000.0
                                DR17 = reverse_and_concatenate(DR17_hex,is_signed=True)/1000.0
                                DR18 = reverse_and_concatenate(DR18_hex,is_signed=True)/1000.0
                               
                                Dual_exe_cmd_c = reverse_and_concatenate(Dual_exe_cmd_c_hex)
                                Spu_cmd_c = reverse_and_concatenate(Spu_cmd_c_hex)
                                
                                Nrffc_counter1 =  reverse_and_concatenate(Nrffc_counter1_hex)
                                Nrffc_counter2 =  reverse_and_concatenate(Nrffc_counter2_hex)
                                Grffc_counter1 =  reverse_and_concatenate(Grffc_counter1_hex)
                                Grffc_counter2 =  reverse_and_concatenate(Grffc_counter2_hex)
                                Grffc_counter3 =  reverse_and_concatenate(Grffc_counter3_hex)
                                Grffc_counter4 =  reverse_and_concatenate(Grffc_counter4_hex)
                               
                                Elev1 = reverse_and_concatenate(Elev1_hex)
                                Elev2 = reverse_and_concatenate(Elev2_hex)
                                Elev3 = reverse_and_concatenate(Elev3_hex)
                                Elev4 = reverse_and_concatenate(Elev4_hex)
                                Elev5 = reverse_and_concatenate(Elev5_hex)
                                Elev6 = reverse_and_concatenate(Elev6_hex)
                                Elev7 = reverse_and_concatenate(Elev7_hex)
                                Elev8 = reverse_and_concatenate(Elev8_hex)
                                Elev9 = reverse_and_concatenate(Elev9_hex)
                                Elev10 = reverse_and_concatenate(Elev10_hex)
                                Elev11 = reverse_and_concatenate(Elev11_hex)
                                Elev12 = reverse_and_concatenate(Elev12_hex)
                                Elev13 = reverse_and_concatenate(Elev13_hex)
                                Elev14 = reverse_and_concatenate(Elev14_hex)
                                Elev15 = reverse_and_concatenate(Elev15_hex)
                                Elev16 = reverse_and_concatenate(Elev16_hex)
                                Elev17 = reverse_and_concatenate(Elev17_hex)
                                Elev18 = reverse_and_concatenate(Elev18_hex)
                               
                                INS_x = reverse_and_concatenate(INS_x_hex, is_signed=True)/100.0
                                INS_y = reverse_and_concatenate(INS_y_hex, is_signed=True)/100.0
                                INS_z = reverse_and_concatenate(INS_z_hex, is_signed=True)/100.0
                                INS_vx = reverse_and_concatenate(INS_vx_hex, is_signed=True)/1000.0
                                INS_vy = reverse_and_concatenate(INS_vy_hex, is_signed=True)/1000.0
                                INS_vz = reverse_and_concatenate(INS_vz_hex, is_signed=True)/1000.0
                                
                                fix_3D = reverse_and_concatenate(fix_3D_hex)
                                PPS_Nanosec = reverse_and_concatenate(PPS_Nanosec_hex)
                                PPS_Sec = reverse_and_concatenate(PPS_Sec_hex)
                                PPS_Week = reverse_and_concatenate(PPS_Week_hex)
                                Leap = reverse_and_concatenate(Leap_hex)
                                 
                               
                                #GUI ENTRY
                                counter_entry.config(state="normal")
                                counter_entry.delete(0,END)
                                counter_entry.insert(0, str(counter_value))
                                counter_entry.config(state="readonly")
                                
                                nanotime_entry1.config(state="normal")
                                nanotime_entry1.delete(0,END)
                                nanotime_entry1.insert(0, str(SYN_NanoSecond))
                                nanotime_entry1.config(state="readonly")
                               
                                time_entry1.config(state="normal")
                                time_entry1.delete(0,END)
                                time_entry1.insert(0, str(SYN_Second))
                                time_entry1.config(state="readonly")
                               
                                week_entry1.config(state="normal")
                                week_entry1.delete(0,END)
                                week_entry1.insert(0, str(SYN_WeekNumber))
                                week_entry1.config(state="readonly")
                               
                                tsm_counter_entry.config(state="normal")
                                tsm_counter_entry.delete(0,END)
                                tsm_counter_entry.insert(0, f"{TSM_update_counter}")
                                tsm_counter_entry.config(state="readonly")
                               
                                csm1.config(state=NORMAL)
                                csm1.delete(0,END)
                                csm1.insert(0, f"{checksum1}")
                                csm1.config(state="readonly")
                               
                                time_entry.config(state="normal")
                                time_entry.delete(0,END)
                                time_entry.insert(0, str(SYS_Second))
                                time_entry.config(state="readonly")
                               
                                nanotime_entry.config(state="normal")
                                nanotime_entry.delete(0,END)
                                nanotime_entry.insert(0, str(SYS_NanoSecond))
                                nanotime_entry.config(state="readonly")
                               
                                week_entry.config(state="normal")
                                week_entry.delete(0,END)
                                week_entry.insert(0, str(SYS_WeekNumber))
                                week_entry.config(state="readonly")
                               
                                position_entry.config(state="normal")
                                position_entry.delete(0,END)
                                position_entry.insert(0, str(POS_x))
                                position_entry.config(state="readonly")
                               
                                position_entry1.config(state="normal")
                                position_entry1.delete(0,END)
                                position_entry1.insert(0, str(POS_y))
                                position_entry1.config(state="readonly")
                               
                                position_entry2.config(state="normal")
                                position_entry2.delete(0,END)
                                position_entry2.insert(0, str(POS_z))
                                position_entry2.config(state="readonly")
                               
                                velocity_entry.config(state="normal")
                                velocity_entry.delete(0,END)
                                velocity_entry.insert(0, str(POS_vx))
                                velocity_entry.config(state="readonly")
                               
                                velocity_entry1.config(state="normal")
                                velocity_entry1.delete(0,END)
                                velocity_entry1.insert(0, str(POS_vy))
                                velocity_entry1.config(state="readonly")
                               
                                velocity_entry2.config(state="normal")
                                velocity_entry2.delete(0,END)
                                velocity_entry2.insert(0, str(POS_vz))
                                velocity_entry2.config(state="readonly")
                             
                                update_entry.config(state=NORMAL)
                                update_entry.delete(0,END)
                                update_entry.insert(0, f"{UpdateCounter}")
                                update_entry.config(state="readonly")
                               
                                pdop.config(state=NORMAL)
                                pdop.delete(0,END)
                                pdop.insert(0, f"{PDOP}")
                                pdop.config(state="readonly")
                               
                                tm.config(state="normal")
                                tm.delete(0, "end")
                                tm.insert(0, str(flag['Tm_sel']))
                                tm.config(state="readonly")
                               
                                swdt.config(state="normal")
                                swdt.delete(0, "end")
                                swdt.insert(0, str(flag["SWDT"]))
                                swdt.config(state="readonly")
                               
                                hwdt.config(state="normal")
                                hwdt.delete(0, "end")
                                hwdt.insert(0, str(flag["HWDT"]))
                                hwdt.config(state="readonly")
                               
                                sbasen.config(state="normal")
                                sbasen.delete(0, "end")
                                sbasen.insert(0, str(flag["SBASEN"]))
                                sbasen.config(state="readonly")
                               
                                sys_mode.config(state="normal")
                                sys_mode.delete(0, "end")
                                sys_mode.insert(0, str(flag["System_mode"]))
                                sys_mode.config(state="readonly")
                                
                                
                               
                                rec_mode.config(state="normal")
                                rec_mode.delete(0, "end")
                                rec_mode.insert(0, str(flag["Rec_Mode"]))
                                rec_mode.config(state="readonly")
                               
                                time_mode.config(state="normal")
                                time_mode.delete(0, "end")
                                time_mode.insert(0, str(flag["Time_Mode"]))
                                time_mode.config(state="readonly")
                               
                                alm_av.config(state="normal")
                                alm_av.delete(0, "end")
                                alm_av.insert(0, str(flag["Alm_Av"]))
                                alm_av.config(state="readonly")
                               
                                time_av.config(state="normal")
                                time_av.delete(0, "end")
                                time_av.insert(0, str(flag["Time_Av"]))
                                time_av.config(state="readonly")
                               
                                pos_mode.config(state="normal")
                                pos_mode.delete(0, "end")
                                pos_mode.insert(0, str(flag["Pose_Mode"]))
                                pos_mode.config(state="readonly")
                               
                                pos_av.config(state="normal")
                                pos_av.delete(0, "end")
                                pos_av.insert(0, str(flag["Pos_Av"]))
                                pos_av.config(state="readonly")
                               
                               
                               
                                cb.config(state=NORMAL)
                                cb.delete(0,END)
                                cb.insert(0, f"{Bais}")
                                cb.config(state="readonly")
                               
                                isb.config(state=NORMAL)
                                isb.delete(0,END)
                                isb.insert(0, f"{ISB}")
                                isb.config(state="readonly")
                               
                                drift.config(state=NORMAL)
                                drift.delete(0,END)
                                drift.insert(0, f"{DRIFT}")
                                drift.config(state="readonly")
                               
                                isd.config(state=NORMAL)
                                isd.delete(0,END)
                                isd.insert(0, f"{ISD}")
                                isd.config(state="readonly")
                               
                                sw_rst_c.config(state=NORMAL)
                                sw_rst_c.delete(0,END)
                                sw_rst_c.insert(0, f"{SW_reset_counter}")
                                sw_rst_c.config(state="readonly")
                               
                                hw_rst_c.config(state=NORMAL)
                                hw_rst_c.delete(0,END)
                                hw_rst_c.insert(0, f"{HW_reset_counter}")
                                hw_rst_c.config(state="readonly")
                               
                                sw_rst_id.config(state=NORMAL)
                                sw_rst_id.delete(0,END)
                                sw_rst_id.insert(0, f"{SW_RST_ID}")
                                sw_rst_id.config(state="readonly")
                               
                                port_conf.config(state=NORMAL)
                                port_conf.delete(0,END)
                                port_conf.insert(0, flag1["Port_config"]["Antenna_1"])
                                port_conf.config(state="readonly")
                                
                                port_conf1.config(state=NORMAL)
                                port_conf1.delete(0,END)
                                port_conf1.insert(0, flag1["Port_config"]["Antenna_2"])
                                port_conf1.config(state="readonly")
                                
                                port_conf2.config(state=NORMAL)
                                port_conf2.delete(0,END)
                                port_conf2.insert(0, flag1["Port_config"]["Antenna_3"])
                                port_conf2.config(state="readonly")
                                
                                port_conf3.config(state=NORMAL)
                                port_conf3.delete(0,END)
                                port_conf3.insert(0, flag1["Port_config"]["Antenna_4"])
                                port_conf3.config(state="readonly")
                               
                                sol_mode.config(state=NORMAL)
                                sol_mode.delete(0,END)
                                sol_mode.insert(0,str(flag1["Sol_mode"]))
                                sol_mode.config(state="readonly")
                               
                                sps_id.config(state=NORMAL)
                                sps_id.delete(0,END)
                                sps_id.insert(0,str(flag1["SPS_ID"]))
                                sps_id.config(state="readonly")
                               
                               
                               
                                navic_msg_22_c.config(state=NORMAL)
                                navic_msg_22_c.delete(0,END)
                                navic_msg_22_c.insert(0, f"{Navic_msg_22_counter}")
                                navic_msg_22_c.config(state="readonly")
                               
                                navic_msg_cmd_c.config(state=NORMAL)
                                navic_msg_cmd_c.delete(0,END)
                                navic_msg_cmd_c.insert(0, f"{Navic_msg_counter}")
                                navic_msg_cmd_c.config(state="readonly")
                               
                                leo_sat_id.config(state=NORMAL)
                                leo_sat_id.delete(0,END)
                                leo_sat_id.insert(0, f"{Leo_sat_id_mil}")
                                leo_sat_id.config(state="readonly")
                               
                                no_sat_trck.config(state=NORMAL)
                                no_sat_trck.delete(0,END)
                                no_sat_trck.insert(0, f"{No_of_Sat}")
                                no_sat_trck.config(state="readonly")
                                
                                odp_est.config(state=NORMAL)
                                odp_est.delete(0,END)
                                odp_est.insert(0, str(flag3["ODP_Est flag"]))
                                odp_est.config(state="readonly")
                                
                                odp_en.config(state=NORMAL)
                                odp_en.delete(0,END)
                                odp_en.insert(0,  str(flag3["ODP_ENA"]))
                                odp_en.config(state="readonly")
                                
                                phc_usg.config(state=NORMAL)
                                phc_usg.delete(0,END)
                                phc_usg.insert(0,  str(flag3["PHCUsage"]))
                                phc_usg.config(state="readonly")
                                
                                phc_en.config(state=NORMAL)
                                phc_en.delete(0,END)
                                phc_en.insert(0,  str(flag3["PHCEn"]))
                                phc_en.config(state="readonly")
                                
                                eph_rt.config(state=NORMAL)
                                eph_rt.delete(0,END)
                                eph_rt.insert(0,  str(flag3["Eph RT"]))
                                eph_rt.config(state="readonly")
                                
                                mnvon.config(state=NORMAL)
                                mnvon.delete(0,END)
                                mnvon.insert(0,  str(flag3["MNVON"]))
                                mnvon.config(state="readonly")
                                
                                numsps.config(state=NORMAL)
                                numsps.delete(0,END)
                                numsps.insert(0, str(flag3["NUMSPS"]))
                                numsps.config(state="readonly")
                                
                                
                               
                                navic_cmd_var.config(state=NORMAL)
                                navic_cmd_var.delete(0,END)
                                navic_cmd_var.insert(0, f"{Navic_cmd_var}")
                                navic_cmd_var.config(state="readonly")
                               
                                csm2.config(state=NORMAL)
                                csm2.delete(0,END)
                                csm2.insert(0, f"{checksum2}")
                                csm2.config(state="readonly")
                               
                             
                                svid1.config(state=NORMAL)
                                svid1.delete(0,END)
                                svid1.insert(0, f"{SVID1}")
                                svid1.config(state="readonly")
                               
                                svid2.config(state=NORMAL)
                                svid2.delete(0,END)
                                svid2.insert(0, f"{SVID2}")
                                svid2.config(state="readonly")
                               
                                svid3.config(state=NORMAL)
                                svid3.delete(0,END)
                                svid3.insert(0, f"{SVID3}")
                                svid3.config(state="readonly")
                               
                                svid4.config(state=NORMAL)
                                svid4.delete(0,END)
                                svid4.insert(0, f"{SVID4}")
                                svid4.config(state="readonly")
                               
                                svid5.config(state=NORMAL)
                                svid5.delete(0,END)
                                svid5.insert(0, f"{SVID5}")
                                svid5.config(state="readonly")
                               
                                svid6.config(state=NORMAL)
                                svid6.delete(0,END)
                                svid6.insert(0, f"{SVID6}")
                                svid6.config(state="readonly")
                               
                                svid7.config(state=NORMAL)
                                svid7.delete(0,END)
                                svid7.insert(0, f"{SVID7}")
                                svid7.config(state="readonly")
                               
                                svid8.config(state=NORMAL)
                                svid8.delete(0,END)
                                svid8.insert(0, f"{SVID8}")
                                svid8.config(state="readonly")
                               
                                svid9.config(state=NORMAL)
                                svid9.delete(0,END)
                                svid9.insert(0, f"{SVID9}")
                                svid9.config(state="readonly")
                               
                                svid10.config(state=NORMAL)
                                svid10.delete(0,END)
                                svid10.insert(0, f"{SVID10}")
                                svid10.config(state="readonly")
                               
                                svid11.config(state=NORMAL)
                                svid11.delete(0,END)
                                svid11.insert(0, f"{SVID11}")
                                #svid11.config(fg="green")
                                svid11.config(state="readonly")
                               
                                svid12.config(state=NORMAL)
                                svid12.delete(0,END)
                                svid12.insert(0, f"{SVID12}")
                                svid12.config(state="readonly")
                               
                                svid13.config(state=NORMAL)
                                svid13.delete(0,END)
                                svid13.insert(0, f"{SVID13}")
                                svid13.config(state="readonly")
                               
                                svid14.config(state=NORMAL)
                                svid14.delete(0,END)
                                svid14.insert(0, f"{SVID14}")
                                svid14.config(state="readonly")
                               
                                svid15.config(state=NORMAL)
                                svid15.delete(0,END)
                                svid15.insert(0, f"{SVID15}")
                                svid15.config(state="readonly")
                               
                                svid16.config(state=NORMAL)
                                svid16.delete(0,END)
                                svid16.insert(0, f"{SVID16}")
                                svid16.config(state="readonly")
                               
                                svid17.config(state=NORMAL)
                                svid17.delete(0,END)
                                svid17.insert(0, f"{SVID17}")
                                svid17.config(state="readonly")
                               
                                svid18.config(state=NORMAL)
                                svid18.delete(0,END)
                                svid18.insert(0, f"{SVID18}")
                                svid18.config(state="readonly")
                               
                                iode1.config(state=NORMAL)
                                iode1.delete(0,END)
                                iode1.insert(0, f"{IODE1}")
                                iode1.config(state="readonly")
                               
                                iode2.config(state=NORMAL)
                                iode2.delete(0,END)
                                iode2.insert(0, f"{IODE2}")
                                iode2.config(state="readonly")
                               
                                iode3.config(state=NORMAL)
                                iode3.delete(0,END)
                                iode3.insert(0, f"{IODE3}")
                                iode3.config(state="readonly")
                               
                                iode4.config(state=NORMAL)
                                iode4.delete(0,END)
                                iode4.insert(0, f"{IODE4}")
                                iode4.config(state="readonly")
                               
                                iode5.config(state=NORMAL)
                                iode5.delete(0,END)
                                iode5.insert(0, f"{IODE5}")
                                iode5.config(state="readonly")
                               
                                iode6.config(state=NORMAL)
                                iode6.delete(0,END)
                                iode6.insert(0, f"{IODE6}")
                                iode6.config(state="readonly")
                               
                                iode7.config(state=NORMAL)
                                iode7.delete(0,END)
                                iode7.insert(0, f"{IODE7}")
                                iode7.config(state="readonly")
                               
                                iode8.config(state=NORMAL)
                                iode8.delete(0,END)
                                iode8.insert(0, f"{IODE8}")
                                iode8.config(state="readonly")
                               
                                iode9.config(state=NORMAL)
                                iode9.delete(0,END)
                                iode9.insert(0, f"{IODE9}")
                                iode9.config(state="readonly")
                               
                                iode10.config(state=NORMAL)
                                iode10.delete(0,END)
                                iode10.insert(0, f"{IODE10}")
                                iode10.config(state="readonly")
                               
                                iode11.config(state=NORMAL)
                                iode11.delete(0,END)
                                iode11.insert(0, f"{IODE11}")
                                #iode11.config(fg="green")
                                iode11.config(state="readonly")
                               
                                iode12.config(state=NORMAL)
                                iode12.delete(0,END)
                                iode12.insert(0, f"{IODE12}")
                                iode12.config(state="readonly")
                               
                                iode13.config(state=NORMAL)
                                iode13.delete(0,END)
                                iode13.insert(0, f"{IODE13}")
                                iode13.config(state="readonly")
                               
                                iode14.config(state=NORMAL)
                                iode14.delete(0,END)
                                iode14.insert(0, f"{IODE14}")
                                iode14.config(state="readonly")
                               
                                iode15.config(state=NORMAL)
                                iode15.delete(0,END)
                                iode15.insert(0, f"{IODE15}")
                                iode15.config(state="readonly")
                               
                                iode16.config(state=NORMAL)
                                iode16.delete(0,END)
                                iode16.insert(0, f"{IODE16}")
                                iode16.config(state="readonly")
                               
                                iode17.config(state=NORMAL)
                                iode17.delete(0,END)
                                iode17.insert(0, f"{IODE17}")
                                iode17.config(state="readonly")
                               
                                iode18.config(state=NORMAL)
                                iode18.delete(0,END)
                                iode18.insert(0, f"{IODE18}")
                                iode18.config(state="readonly")
                               
                                cndr1.config(state=NORMAL)
                                cndr1.delete(0,END)
                                cndr1.insert(0, f"{CNDR1}")
                                cndr1.config(state="readonly")
                               
                                cndr2.config(state=NORMAL)
                                cndr2.delete(0,END)
                                cndr2.insert(0, f"{CNDR2}")
                                cndr2.config(state="readonly")
                               
                                cndr3.config(state=NORMAL)
                                cndr3.delete(0,END)
                                cndr3.insert(0, f"{CNDR3}")
                                cndr3.config(state="readonly")
                               
                                cndr4.config(state=NORMAL)
                                cndr4.delete(0,END)
                                cndr4.insert(0, f"{CNDR4}")
                                cndr4.config(state="readonly")
                               
                                cndr5.config(state=NORMAL)
                                cndr5.delete(0,END)
                                cndr5.insert(0, f"{CNDR5}")
                                cndr5.config(state="readonly")
                               
                                cndr6.config(state=NORMAL)
                                cndr6.delete(0,END)
                                cndr6.insert(0, f"{CNDR6}")
                                cndr6.config(state="readonly")
                               
                                cndr7.config(state=NORMAL)
                                cndr7.delete(0,END)
                                cndr7.insert(0, f"{CNDR7}")
                                cndr7.config(state="readonly")
                               
                                cndr8.config(state=NORMAL)
                                cndr8.delete(0,END)
                                cndr8.insert(0, f"{CNDR8}")
                                cndr8.config(state="readonly")
                               
                                cndr9.config(state=NORMAL)
                                cndr9.delete(0,END)
                                cndr9.insert(0, f"{CNDR9}")
                                cndr9.config(state="readonly")
                               
                                cndr10.config(state=NORMAL)
                                cndr10.delete(0,END)
                                cndr10.insert(0, f"{CNDR10}")
                                cndr10.config(state="readonly")
                               
                                cndr11.config(state=NORMAL)
                                cndr11.delete(0,END)
                                cndr11.insert(0, f"{CNDR11}")
                                #cndr11.config(fg="green")
                                cndr11.config(state="readonly")
                               
                                cndr12.config(state=NORMAL)
                                cndr12.delete(0,END)
                                cndr12.insert(0, f"{CNDR12}")
                                cndr12.config(state="readonly")
                               
                                cndr13.config(state=NORMAL)
                                cndr13.delete(0,END)
                                cndr13.insert(0, f"{CNDR13}")
                                cndr13.config(state="readonly")
                               
                                cndr14.config(state=NORMAL)
                                cndr14.delete(0,END)
                                cndr14.insert(0, f"{CNDR14}")
                                cndr14.config(state="readonly")
                               
                                cndr15.config(state=NORMAL)
                                cndr15.delete(0,END)
                                cndr15.insert(0, f"{CNDR15}")
                                cndr15.config(state="readonly")
                               
                                cndr16.config(state=NORMAL)
                                cndr16.delete(0,END)
                                cndr16.insert(0, f"{CNDR16}")
                                cndr16.config(state="readonly")
                               
                                cndr17.config(state=NORMAL)
                                cndr17.delete(0,END)
                                cndr17.insert(0, f"{CNDR17}")
                                cndr17.config(state="readonly")
                               
                                cndr18.config(state=NORMAL)
                                cndr18.delete(0,END)
                                cndr18.insert(0, f"{CNDR18}")
                                cndr18.config(state="readonly")
                                
                                refresh_cndr_plot()
                               
                                last_cmd_exe.config(state=NORMAL)
                                last_cmd_exe.delete(0,END)
                                last_cmd_exe.insert(0, f"{Last_cmd_ex}")
                                last_cmd_exe.config(state="readonly")
                               
                                last_reset_time.config(state=NORMAL)
                                last_reset_time.delete(0,END)
                                last_reset_time.insert(0, f"{Last_reset_time}")
                                last_reset_time.config(state="readonly")
                               
                                cmd_based_rt.config(state=NORMAL)
                                cmd_based_rt.delete(0,END)
                                cmd_based_rt.insert(0, f"{Cmd_counter_based_rt}")
                                cmd_based_rt.config(state="readonly")
                               
                                total_cmd_counter.config(state=NORMAL)
                                total_cmd_counter.delete(0,END)
                                total_cmd_counter.insert(0, f"{Total_cmd_counter}")
                                total_cmd_counter.config(state="readonly")
                               
                                acq1.config(state=NORMAL)
                                acq1.delete(0,END)
                                acq1.insert(0, f"{ACQ1}")
                                acq1.config(state="readonly")
                               
                                acq2.config(state=NORMAL)
                                acq2.delete(0,END)
                                acq2.insert(0, f"{ACQ2}")
                                acq2.config(state="readonly")
                               
                                acq3.config(state=NORMAL)
                                acq3.delete(0,END)
                                acq3.insert(0, f"{ACQ3}")
                                acq3.config(state="readonly")
                               
                                acq4.config(state=NORMAL)
                                acq4.delete(0,END)
                                acq4.insert(0, f"{ACQ4}")
                                acq4.config(state="readonly")
                                
                                
                                rt_id.config(state="normal")
                                rt_id.delete(0, "end")
                                rt_id.insert(0, str(flags["RT_ID"]))
                                rt_id.config(state="readonly")
                               
                                miss_ph.config(state="normal")
                                miss_ph.delete(0, "end")
                                miss_ph.insert(0, str(flags["Mission_Phase"]))
                                miss_ph.config(state="readonly")
                               
                                fmem.config(state="normal")
                                fmem.delete(0, "end")
                                fmem.insert(0, str(flags["Fmem"]))
                                fmem.config(state="readonly")
                               
                                cr_aid.config(state="normal")
                                cr_aid.delete(0, "end")
                                cr_aid.insert(0, str(flags["Cr_Aid"]))
                                cr_aid.config(state="readonly")
                               
                                full_cntr.config(state="normal")
                                full_cntr.delete(0, "end")
                                full_cntr.insert(0, str(flags["FLL_Cntr"]))
                                full_cntr.config(state="readonly")
                               
                                s_id.config(state="normal")
                                s_id.delete(0, "end")
                                s_id.insert(0, str(flags["S_ID"]))
                                s_id.config(state="readonly")
                               
                                lig_1.config(state="normal")
                                lig_1.delete(0, "end")
                                lig_1.insert(0, str(flags["LIG_1"]))
                                lig_1.config(state="readonly")
                               
                                lig_2.config(state="normal")
                                lig_2.delete(0, "end")
                                lig_2.insert(0, str(flags["LIG_2"]))
                                lig_2.config(state="readonly")
                               
                                lig_3.config(state="normal")
                                lig_3.delete(0, "end")
                                lig_3.insert(0, str(flags["LIG_3"]))
                                lig_3.config(state="readonly")
                               
                               
                                lig_4.config(state="normal")
                                lig_4.delete(0, "end")
                                lig_4.insert(0, str(flags["LIG_4"]))
                                lig_4.config(state="readonly")
                               
                                lin_1.config(state="normal")
                                lin_1.delete(0, "end")
                                lin_1.insert(0, str(flags["LIN_1"]))
                                lin_1.config(state="readonly")
                               
                                lin_2.config(state="normal")
                                lin_2.delete(0, "end")
                                lin_2.insert(0, str(flags["LIN_2"]))
                                lin_2.config(state="readonly")
                               
                                prime_ngc.config(state="normal")
                                prime_ngc.delete(0, "end")
                                prime_ngc.insert(0, str(flags["Prime_NGC"]))
                                prime_ngc.config(state="readonly")
                                
                                rng_l.config(state=NORMAL)
                                rng_l.delete(0,END)
                                rng_l.insert(0,  str(flag2["Rng L"]))
                                rng_l.config(state="readonly")
                                
                                orbit_phase.config(state=NORMAL)
                                orbit_phase.delete(0,END)
                                orbit_phase.insert(0, str(flag2["Orbit Phase"]))
                                orbit_phase.config(state="readonly")
                                
                                iono_c.config(state=NORMAL)
                                iono_c.delete(0,END)
                                iono_c.insert(0, str(flag2["Iono C"]))
                                iono_c.config(state="readonly")
                                
                                iono_sm.config(state=NORMAL)
                                iono_sm.delete(0,END)
                                iono_sm.insert(0, str(flag2["Iono Sm"]))
                                iono_sm.config(state="readonly")
                                
                                cr_smo.config(state=NORMAL)
                                cr_smo.delete(0,END)
                                cr_smo.insert(0, str(flag2["Cr Smo"]))
                                cr_smo.config(state="readonly")
                                
                                vel_sm.config(state=NORMAL)
                                vel_sm.delete(0,END)
                                vel_sm.insert(0, str(flag2["Vel sm"]))
                                vel_sm.config(state="readonly")
                                
                                raim.config(state=NORMAL)
                                raim.delete(0,END)
                                raim.insert(0, str(flag2["RAIM"]))
                                raim.config(state="readonly")
                                
                                pr_rej.config(state=NORMAL)
                                pr_rej.delete(0,END)
                                pr_rej.insert(0, str(flag2["PR Rej"]))
                                pr_rej.config(state="readonly")
                                
                                pr_bf_sync.config(state=NORMAL)
                                pr_bf_sync.delete(0,END)
                                pr_bf_sync.insert(0, str(flag2["Pr Bf Sync"]))
                                pr_bf_sync.config(state="readonly")
                                
                                cfg_loop.config(state=NORMAL)
                                cfg_loop.delete(0,END)
                                cfg_loop.insert(0, str(flag2["Cfg loop"]))
                                cfg_loop.config(state="readonly")
                                
                                int_crd_tst.config(state=NORMAL)
                                int_crd_tst.delete(0,END)
                                int_crd_tst.insert(0, str(flag2["int crd tst"]))
                                int_crd_tst.config(state="readonly")
                                
                                elev_e.config(state=NORMAL)
                                elev_e.delete(0,END)
                                elev_e.insert(0, str(flag2["Elev En"]))
                                elev_e.config(state="readonly")
                                
                                rst_flag.config(state=NORMAL)
                                rst_flag.delete(0,END)
                                rst_flag.insert(0, str(flag2["Rst Flag"]))
                                rst_flag.config(state="readonly")
                                
                                odp_rst_sf.config(state=NORMAL)
                                odp_rst_sf.delete(0,END)
                                odp_rst_sf.insert(0, str(flag2["ODP Rst Sp"]))
                                odp_rst_sf.config(state="readonly")
                                
                                cold_vis.config(state=NORMAL)
                                cold_vis.delete(0,END)
                                cold_vis.insert(0, str(flag2["Cold Vis"]))
                                cold_vis.config(state="readonly")
                                
                                nav_msg_e.config(state=NORMAL)
                                nav_msg_e.delete(0,END)
                                nav_msg_e.insert(0, str(flag2["Navic Msg En"]))
                                nav_msg_e.config(state="readonly")
                                
                                
                               
                               
                               
                                for idx, status_hex in enumerate(CHANNEL_STATUS):
                                    try:
                                        status_word = int(status_hex, 16)
                                    except Exception:
                                        status_word = 0
                                    status_meaning = decode_channel_status_meaning(status_word)

                                    for bit in bit_names:
                                        entry = bit_to_entrylist[bit][idx]
                                        entry.config(state=NORMAL)
                                        entry.delete(0, END)
                                        entry.insert(0, status_meaning.get(bit, ""))
                                        entry.config(state="readonly")
                               
                                pr1.config(state=NORMAL)
                                pr1.delete(0,END)
                                pr1.insert(0, f"{PR1}")
                                pr1.config(state="readonly")
                               
                                pr2.config(state=NORMAL)
                                pr2.delete(0,END)
                                pr2.insert(0, f"{PR2}")
                                pr2.config(state="readonly")
                               
                                pr3.config(state=NORMAL)
                                pr3.delete(0,END)
                                pr3.insert(0, f"{PR3}")
                                pr3.config(state="readonly")
                               
                                pr4.config(state=NORMAL)
                                pr4.delete(0,END)
                                pr4.insert(0, f"{PR4}")
                                pr4.config(state="readonly")
                               
                                pr5.config(state=NORMAL)
                                pr5.delete(0,END)
                                pr5.insert(0, f"{PR5}")
                                pr5.config(state="readonly")
                           
                                pr6.config(state=NORMAL)
                                pr6.delete(0,END)
                                pr6.insert(0, f"{PR6}")
                                pr6.config(state="readonly")
                               
                                pr7.config(state=NORMAL)
                                pr7.delete(0,END)
                                pr7.insert(0, f"{PR7}")
                                pr7.config(state="readonly")
                               
                                pr8.config(state=NORMAL)
                                pr8.delete(0,END)
                                pr8.insert(0, f"{PR8}")
                                pr8.config(state="readonly")
                               
                                pr9.config(state=NORMAL)
                                pr9.delete(0,END)
                                pr9.insert(0, f"{PR9}")
                                pr9.config(state="readonly")
                               
                                pr10.config(state=NORMAL)
                                pr10.delete(0,END)
                                pr10.insert(0, f"{PR10}")
                                pr10.config(state="readonly")
                               
                                pr11.config(state=NORMAL)
                                pr11.delete(0,END)
                                pr11.insert(0, f"{PR11}")
                                #pr11.config(fg="green")
                                pr11.config(state="readonly")
                               
                                pr12.config(state=NORMAL)
                                pr12.delete(0,END)
                                pr12.insert(0, f"{PR12}")
                                pr12.config(state="readonly")
                               
                                pr13.config(state=NORMAL)
                                pr13.delete(0,END)
                                pr13.insert(0, f"{PR13}")
                                pr13.config(state="readonly")
                               
                                pr14.config(state=NORMAL)
                                pr14.delete(0,END)
                                pr14.insert(0, f"{PR14}")
                                pr14.config(state="readonly")
                               
                                pr15.config(state=NORMAL)
                                pr15.delete(0,END)
                                pr15.insert(0, f"{PR15}")
                                pr15.config(state="readonly")
                           
                                pr16.config(state=NORMAL)
                                pr16.delete(0,END)
                                pr16.insert(0, f"{PR16}")
                                pr16.config(state="readonly")
                               
                                pr17.config(state=NORMAL)
                                pr17.delete(0,END)
                                pr17.insert(0, f"{PR17}")
                                pr17.config(state="readonly")
                               
                                pr18.config(state=NORMAL)
                                pr18.delete(0,END)
                                pr18.insert(0, f"{PR18}")
                                pr18.config(state="readonly")
                               
                                dr1.config(state=NORMAL)
                                dr1.delete(0,END)
                                dr1.insert(0, f"{DR1}")
                                dr1.config(state="readonly")
                               
                                dr2.config(state=NORMAL)
                                dr2.delete(0,END)
                                dr2.insert(0, f"{DR2}")
                                dr2.config(state="readonly")
                               
                                dr3.config(state=NORMAL)
                                dr3.delete(0,END)
                                dr3.insert(0, f"{DR3}")
                                dr3.config(state="readonly")
                               
                                dr4.config(state=NORMAL)
                                dr4.delete(0,END)
                                dr4.insert(0, f"{DR4}")
                                dr4.config(state="readonly")
                               
                                dr5.config(state=NORMAL)
                                dr5.delete(0,END)
                                dr5.insert(0, f"{DR5}")
                                dr5.config(state="readonly")
                               
                                dr6.config(state=NORMAL)
                                dr6.delete(0,END)
                                dr6.insert(0, f"{DR6}")
                                dr6.config(state="readonly")
                               
                                dr7.config(state=NORMAL)
                                dr7.delete(0,END)
                                dr7.insert(0, f"{DR7}")
                                dr7.config(state="readonly")
                               
                                dr8.config(state=NORMAL)
                                dr8.delete(0,END)
                                dr8.insert(0, f"{DR8}")
                                dr8.config(state="readonly")
                               
                                dr9.config(state=NORMAL)
                                dr9.delete(0,END)
                                dr9.insert(0, f"{DR9}")
                                dr9.config(state="readonly")
                               
                                dr10.config(state=NORMAL)
                                dr10.delete(0,END)
                                dr10.insert(0, f"{DR10}")
                                dr10.config(state="readonly")
                               
                                dr11.config(state=NORMAL)
                                dr11.delete(0,END)
                                dr11.insert(0, f"{DR11}")
                                dr11.config(state="readonly")
                               
                                dr12.config(state=NORMAL)
                                dr12.delete(0,END)
                                dr12.insert(0, f"{DR12}")
                                dr12.config(state="readonly")
                               
                                dr13.config(state=NORMAL)
                                dr13.delete(0,END)
                                dr13.insert(0, f"{DR13}")
                                dr13.config(state="readonly")
                               
                                dr14.config(state=NORMAL)
                                dr14.delete(0,END)
                                dr14.insert(0, f"{DR14}")
                                dr14.config(state="readonly")
                               
                                dr15.config(state=NORMAL)
                                dr15.delete(0,END)
                                dr15.insert(0, f"{DR15}")
                                dr15.config(state="readonly")
                               
                                dr16.config(state=NORMAL)
                                dr16.delete(0,END)
                                dr16.insert(0, f"{DR16}")
                                dr16.config(state="readonly")
                               
                                dr17.config(state=NORMAL)
                                dr17.delete(0,END)
                                dr17.insert(0, f"{DR17}")
                                dr17.config(state="readonly")
                               
                                dr18.config(state=NORMAL)
                                dr18.delete(0,END)
                                dr18.insert(0, f"{DR18}")
                                dr18.config(state="readonly")
                               
                                dual_cmd_c_rt.config(state=NORMAL)
                                dual_cmd_c_rt.delete(0,END)
                                dual_cmd_c_rt.insert(0, f"{Dual_exe_cmd_c}")
                                dual_cmd_c_rt.config(state="readonly")
                               
                                spu_cmd_c_rt.config(state=NORMAL)
                                spu_cmd_c_rt.delete(0,END)
                                spu_cmd_c_rt.insert(0, f"{Spu_cmd_c}")
                                spu_cmd_c_rt.config(state="readonly")
                                
                                nrff_rst_counter1.config(state=NORMAL)
                                nrff_rst_counter1.delete(0,END)
                                nrff_rst_counter1.insert(0, f"{Nrffc_counter1}")
                                nrff_rst_counter1.config(state="readonly")
                                
                                nrff_rst_counter2.config(state=NORMAL)
                                nrff_rst_counter2.delete(0,END)
                                nrff_rst_counter2.insert(0, f"{Nrffc_counter2}")
                                nrff_rst_counter2.config(state="readonly")
                                
                                grff_rst_counter1.config(state=NORMAL)
                                grff_rst_counter1.delete(0,END)
                                grff_rst_counter1.insert(0, f"{Grffc_counter1}")
                                grff_rst_counter1.config(state="readonly")
                                
                                grff_rst_counter2.config(state=NORMAL)
                                grff_rst_counter2.delete(0,END)
                                grff_rst_counter2.insert(0, f"{Grffc_counter2}")
                                grff_rst_counter2.config(state="readonly")
                                
                                grff_rst_counter3.config(state=NORMAL)
                                grff_rst_counter3.delete(0,END)
                                grff_rst_counter3.insert(0, f"{Grffc_counter3}")
                                grff_rst_counter3.config(state="readonly")
                                
                                grff_rst_counter4.config(state=NORMAL)
                                grff_rst_counter4.delete(0,END)
                                grff_rst_counter4.insert(0, f"{Grffc_counter4}")
                                grff_rst_counter4.config(state="readonly")
                               
                               
                                elev1.config(state=NORMAL)
                                elev1.delete(0,END)
                                elev1.insert(0, f"{Elev1}")
                                elev1.config(state="readonly")
                               
                                elev2.config(state=NORMAL)
                                elev2.delete(0,END)
                                elev2.insert(0, f"{Elev2}")
                                elev2.config(state="readonly")
                               
                                elev3.config(state=NORMAL)
                                elev3.delete(0,END)
                                elev3.insert(0, f"{Elev3}")
                                elev3.config(state="readonly")
                               
                                elev4.config(state=NORMAL)
                                elev4.delete(0,END)
                                elev4.insert(0, f"{Elev4}")
                                elev4.config(state="readonly")
                               
                                elev5.config(state=NORMAL)
                                elev5.delete(0,END)
                                elev5.insert(0, f"{Elev5}")
                                elev5.config(state="readonly")
                               
                                elev6.config(state=NORMAL)
                                elev6.delete(0,END)
                                elev6.insert(0, f"{Elev6}")
                                elev6.config(state="readonly")
                               
                                elev7.config(state=NORMAL)
                                elev7.delete(0,END)
                                elev7.insert(0, f"{Elev7}")
                                elev7.config(state="readonly")
                               
                                elev8.config(state=NORMAL)
                                elev8.delete(0,END)
                                elev8.insert(0, f"{Elev8}")
                                elev8.config(state="readonly")
                               
                                elev9.config(state=NORMAL)
                                elev9.delete(0,END)
                                elev9.insert(0, f"{Elev9}")
                                elev9.config(state="readonly")
                               
                                elev10.config(state=NORMAL)
                                elev10.delete(0,END)
                                elev10.insert(0, f"{Elev10}")
                                elev10.config(state="readonly")
                               
                                elev11.config(state=NORMAL)
                                elev11.delete(0,END)
                                elev11.insert(0, f"{Elev11}")
                                #elev11.config(fg="green")
                                elev11.config(state="readonly")
                               
                                elev12.config(state=NORMAL)
                                elev12.delete(0,END)
                                elev12.insert(0, f"{Elev12}")
                                elev12.config(state="readonly")
                               
                                elev13.config(state=NORMAL)
                                elev13.delete(0,END)
                                elev13.insert(0, f"{Elev13}")
                                elev13.config(state="readonly")
     
                               
                                elev14.config(state=NORMAL)
                                elev14.delete(0,END)
                                elev14.insert(0, f"{Elev14}")
                                elev14.config(state="readonly")
                               
                                elev15.config(state=NORMAL)
                                elev15.delete(0,END)
                                elev15.insert(0, f"{Elev15}")
                                elev15.config(state="readonly")
                               
                                elev16.config(state=NORMAL)
                                elev16.delete(0,END)
                                elev16.insert(0, f"{Elev16}")
                                elev16.config(state="readonly")
                               
                                elev17.config(state=NORMAL)
                                elev17.delete(0,END)
                                elev17.insert(0, f"{Elev17}")
                                elev17.config(state="readonly")
                               
                                elev18.config(state=NORMAL)
                                elev18.delete(0,END)
                                elev18.insert(0, f"{Elev18}")
                                elev18.config(state="readonly")
                               
                                position_entry3.config(state="normal")
                                position_entry3.delete(0,END)
                                position_entry3.insert(0, str(INS_x))
                                position_entry3.config(state="readonly")
                               
                                position_entry4.config(state="normal")
                                position_entry4.delete(0,END)
                                position_entry4.insert(0, str(INS_y))
                                position_entry4.config(state="readonly")
                               
                                position_entry5.config(state="normal")
                                position_entry5.delete(0,END)
                                position_entry5.insert(0, str(INS_z))
                                position_entry5.config(state="readonly")
                               
                                velocity_entry3.config(state="normal")
                                velocity_entry3.delete(0,END)
                                velocity_entry3.insert(0, str(INS_vx))
                                velocity_entry3.config(state="readonly")
                               
                                velocity_entry4.config(state="normal")
                                velocity_entry4.delete(0,END)
                                velocity_entry4.insert(0, str(INS_vy))
                                velocity_entry4.config(state="readonly")
                               
                                velocity_entry5.config(state="normal")
                                velocity_entry5.delete(0,END)
                                velocity_entry5.insert(0, str(INS_vz))
                                velocity_entry5.config(state="readonly")
                                
                                fix_3d.config(state="normal")
                                fix_3d.delete(0,END)
                                fix_3d.insert(0, f"{fix_3D}")
                                fix_3d.config(state="readonly")
                                
                                nanotime_entry2.config(state="normal")
                                nanotime_entry2.delete(0,END)
                                nanotime_entry2.insert(0, str(PPS_Nanosec))
                                nanotime_entry2.config(state="readonly")
                               
                                time_entry2.config(state="normal")
                                time_entry2.delete(0,END)
                                time_entry2.insert(0, str(PPS_Sec))
                                time_entry2.config(state="readonly")
                               
                                week_entry2.config(state="normal")
                                week_entry2.delete(0,END)
                                week_entry2.insert(0, str(PPS_Week))
                                week_entry2.config(state="readonly")
                                
                                leap.config(state="normal")
                                leap.delete(0,END)
                                leap.insert(0, f"{Leap}")
                                leap.config(state="readonly")
                                
                                
                                SVIDs = [SVID1, SVID2, SVID3, SVID4, SVID5, SVID6, SVID7, SVID8, SVID9, SVID10, SVID11, SVID12, SVID13, SVID14, SVID15, SVID16, SVID17, SVID18]
                                CNDRs = [CNDR1, CNDR2, CNDR3, CNDR4, CNDR5, CNDR6, CNDR7, CNDR8, CNDR9, CNDR10, CNDR11, CNDR12, CNDR13, CNDR14, CNDR15, CNDR16, CNDR17, CNDR18]
                                IODEs = [IODE1, IODE2, IODE3, IODE4, IODE5, IODE6, IODE7, IODE8, IODE9, IODE10, IODE11, IODE12, IODE13, IODE14, IODE15, IODE16, IODE17, IODE18]
                                PRs   = [PR1, PR2, PR3, PR4, PR5, PR6, PR7, PR8, PR9, PR10, PR11, PR12, PR13, PR14, PR15, PR16, PR17, PR18]
                                DRs   = [DR1, DR2, DR3, DR4, DR5, DR6, DR7, DR8, DR9, DR10, DR11, DR12, DR13, DR14, DR15, DR16, DR17, DR18]
                                ELEV  = [Elev1, Elev2, Elev3, Elev4, Elev5, Elev6, Elev7, Elev8, Elev9, Elev10, Elev11, Elev12, Elev13, Elev14, Elev15, Elev16, Elev17, Elev18]
                                
                                
                                
                                
                                current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                
                                base_name = file_entry1.get()
                                
                                
                                data_row = [current_timestamp,SYN_Second,SYN_NanoSecond,SYN_WeekNumber]
                                write_to_SYN(data_row,base_name)
                                
                                data_row = [current_timestamp,hexDecodedData] 
                                write_to_raw(data_row,base_name)
                                
                               
                               
                                
                                data_row = [current_timestamp,counter_value,SYS_Second,SYS_NanoSecond,SYS_WeekNumber,PPS_Sec,PPS_Nanosec,PPS_Week,fix_3D,Leap,
                                            TSM_update_counter,UpdateCounter,
                                            checksum1,checksum2,PDOP,Bais,ISB,DRIFT,ISD,
                                            POS_x,POS_y,POS_z,POS_vx,POS_vy,POS_vz,
                                            INS_x,INS_y,INS_z,INS_vx,INS_vy,INS_vz,
                                            ACQ1,ACQ2,ACQ3,ACQ4,
                                            flag['Tm_sel'],flag["SWDT"],flag["HWDT"],flag["SBASEN"],flag["System_mode"],flag["Rec_Mode"],flag["Time_Mode"],flag["Alm_Av"],flag["Time_Av"],flag["Pose_Mode"],flag["Pos_Av"],
                                            SW_reset_counter,HW_reset_counter,SW_RST_ID,flag1["SPS_ID"],flag1["Sol_mode"],flag1["Port_config"]["Antenna_1"],flag1["Port_config"]["Antenna_2"],flag1["Port_config"]["Antenna_3"],flag1["Port_config"]["Antenna_4"],
                                            Navic_msg_22_counter,Navic_msg_counter,Leo_sat_id_mil,No_of_Sat,Navic_cmd_var,
                                            flag3["ODP_Est flag"],flag3["ODP_ENA"],flag3["PHCUsage"],flag3["PHCEn"],flag3["Eph RT"],flag3["MNVON"],flag3["NUMSPS"],
                                            Last_cmd_ex,Last_reset_time,Cmd_counter_based_rt,Total_cmd_counter,
                                            flags["RT_ID"],flags["Mission_Phase"],flags["Fmem"],flags["Cr_Aid"],flags["FLL_Cntr"],flags["S_ID"],
                                            flags["LIG_1"],flags["LIG_2"],flags["LIG_3"],flags["LIG_4"],flags["LIN_1"],flags["LIN_2"],flags["Prime_NGC"],
                                            flag2["Rng L"],flag2["Orbit Phase"],flag2["Iono C"],flag2["Iono Sm"],flag2["Cr Smo"],flag2["Vel sm"],flag2["RAIM"],flag2["PR Rej"],flag2["Pr Bf Sync"],
                                            flag2["Cfg loop"],flag2["int crd tst"],flag2["Elev En"],flag2["Rst Flag"],flag2["ODP Rst Sp"],flag2["Cold Vis"],flag2["Navic Msg En"],
                                            Dual_exe_cmd_c,Spu_cmd_c,Nrffc_counter1,Nrffc_counter2,Grffc_counter1,Grffc_counter2,Grffc_counter3,Grffc_counter4,
                                            ]
                                # --- Append 18-channel grouped data to the row ---
                                for ch in range(18):
                                    data_row.append(ch+1)
                                    data_row.append(SVIDs[ch])
                                    data_row.append(CNDRs[ch])
                                    for bit in bit_names:
                                        data_row.append(status_meaning.get(bit, ""))
                                    data_row.append(IODEs[ch])
                                    data_row.append(PRs[ch])
                                    data_row.append(DRs[ch])
                                    data_row.append(ELEV[ch])
                                write_to_pvt(data_row,base_name)
                                pass
            elif hexDecodedData.startswith(secondary_header):
                                
                                h2Second_hex=hexDecodedData[20:28]
                                h2NanoSecond_hex=hexDecodedData[12:20]
                                h2Weeknumber_hex=hexDecodedData[28:32]
                                
                                # Convert hex to decimal and scale as needed
                                SYN_h2NanoSecond=reverse_and_concatenate(h2NanoSecond_hex)
                               
                                SYN_h2Second=reverse_and_concatenate(h2Second_hex)
                                
                                SYN_h2WeekNumber=reverse_and_concatenate(h2Weeknumber_hex)
                                
                                time_entry2.config(state="normal")
                                time_entry2.delete(0,END)
                                time_entry2.insert(0, str(SYN_h2Second))
                                time_entry2.config(state="readonly")
                                
                                nanotime_entry2.config(state="normal")
                                nanotime_entry2.delete(0,END)
                                nanotime_entry2.insert(0, str(SYN_h2NanoSecond))
                                nanotime_entry2.config(state="readonly")
                                
                                week_entry2.config(state="normal")
                                week_entry2.delete(0,END)
                                week_entry2.insert(0, str(SYN_h2WeekNumber))
                                week_entry2.config(state="readonly")
                                
                                base_name = file_entry1.get()
                                
                                data_row = [current_timestamp,hexDecodedData] 
                                write_to_rawh3(data_row,base_name)
                                
                                data_row = [current_timestamp,SYN_h2Second,SYN_h2NanoSecond,SYN_h2WeekNumber]
                                write_to_SYNh2(data_row,base_name)
                                pass
            else:
                # Unrecognized header, you can skip or log
                print("Unknown header or not for this RT")
                continue
    except KeyboardInterrupt:
        print("Stopped")
 
# replay_functions.py
# Two functions: replay_from_file() to be bound to your Replay button,
# and process_replay_file(filepath) which performs the line-by-line replay.
# Also includes helpers: stop_replay, toggle_pause_resume, jump_to_sys_sec.
# Requirements in your program: data_queue (queue.Queue), RT_HEADERS (dict), reverse_and_concatenate (function),
# btn_replay, btn_pause_resume, jump_entry, replay_running, replay_paused, replay_filepath



# replay_functions.py
# Drop these functions into your existing script (replace old replay functions).
# Requirements: data_queue (queue.Queue), RT_HEADERS (dict), reverse_and_concatenate (function),
# globals used: replay_running, replay_paused, jump_target_sec, replay_filepath
# UI widgets used optionally: btn_replay, btn_pause_resume, jump_entry



def replay_from_file():
    """
    Ask user to select a file and start a replay thread.
    Supports:
      - CSV where hex is in column index 1 (your existing raw CSV)
      - Plain text where each line is a hex string like: acca1f0a12a36...
    Queues (rt_name, normalized_hex) into data_queue.
    """
    global replay_running, replay_filepath
    filepath = filedialog.askopenfilename(
        title="Select Raw/Hex Data File",
        filetypes=[("CSV/HEX/TXT files", "*.csv *.txt *.hex"), ("All files", "*.*")]
    )
    if not filepath:
        return
    replay_filepath = filepath
    replay_running = True
    filename = os.path.basename(filepath)
    try:
        btn_replay.config(text=filename, fg="blue")
    except Exception:
        pass
    threading.Thread(target=process_replay_file, args=(filepath,), daemon=True).start()


def process_replay_file(filepath):
    """
    Read file and queue parsed hex lines to data_queue as (rt_name, normalized_hex).
    Normalization removes spaces, 0x/0X prefixes and commas and converts to lowercase to match RT_HEADERS keys.
    Supports jump_target_sec to fast-skip until desired SYS_Second is reached.
    """
    global replay_running, replay_paused, jump_target_sec

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            # Try CSV first (safe): csv.reader will also work on single-column plain files
            reader = csv.reader(f)
            # If file has a header/first row that isn't hex we still attempt to parse subsequent lines
            next(reader, None)
            fast_skip_mode = jump_target_sec is not None
            line_no = 0
            for row in reader:
                line_no += 1
                if not replay_running:
                    break
                # choose hex string from column 1 if present else column 0
                if len(row) >= 2 and row[1].strip():
                    raw_hex = row[1].strip()
                elif len(row) >= 1 and row[0].strip():
                    raw_hex = row[0].strip()
                else:
                    # empty row
                    print(f"[Replay] Line {line_no} skipped (empty)")
                    continue

                # Normalize: lower-case, remove spaces, remove 0x prefix and commas
                normalized = raw_hex.lower().replace(" ", "").replace("0x", "").replace(",", "")

                # debug small preview for first lines
                if line_no <= 6:
                    print(f"[Replay] Line {line_no} preview: {normalized[:80]}")

                # Try to read SYS_Second for jump logic (safe)
                SYS_Second = None
                try:
                    SYS_Second_hex = normalized[148:156]
                    if len(SYS_Second_hex) == 8:
                        SYS_Second = reverse_and_concatenate(SYS_Second_hex)
                except Exception:
                    SYS_Second = None

                # Jump handling
                if jump_target_sec is not None and SYS_Second is not None:
                    if SYS_Second < jump_target_sec:
                        continue
                    else:
                        print(f"[Replay] Jump reached at SYS_Second={SYS_Second}")
                        jump_target_sec = None
                        fast_skip_mode = False

                # Header detection across all RTs (RT_HEADERS keys are lowercase like 'acca1f0a')
                matched_rt = None
                for rt, headers in RT_HEADERS.items():
                    for h in headers:
                        if normalized.startswith(h.lower()):
                            matched_rt = rt
                            break
                    if matched_rt:
                        break

                if matched_rt:
                    # Queue with explicit RT name so process_data knows where to route
                    data_queue.put((matched_rt, normalized))
                    print(f"[Replay] Line {line_no} queued for {matched_rt}")
                else:
                    print(f"[Replay] Line {line_no} NO HEADER MATCH (starts '{normalized[:16]}')")

                # Pause handling
                while replay_paused and replay_running:
                    pytime.sleep(0.2)

                # pacing delay
                if not fast_skip_mode:
                    pytime.sleep(0.5)

        print("[Replay] finished or stopped.")
    except UnicodeDecodeError:
        print("[Replay] File encoding error: try saving the file as UTF-8.")
    except Exception as e:
        print("process_replay_file error:", e)


def stop_replay():
    global replay_running
    replay_running = False
    print("[Replay] stopped by user.")


def toggle_pause_resume():
    global replay_paused
    if replay_paused:
        replay_paused = False
        try:
            btn_pause_resume.config(text="Pause ⏸", bg="light green")
        except Exception:
            pass
        print("[Replay] resumed")
    else:
        replay_paused = True
        try:
            btn_pause_resume.config(text="Resume ▶", bg="dark green")
        except Exception:
            pass
        print("[Replay] paused")


def jump_to_sys_sec():
    """
    Ask for SYS_Second in jump_entry and restart replay thread so process_replay_file will honor the new jump target.
    """
    global jump_target_sec, replay_running, replay_filepath, replay_paused
    if not replay_filepath:
        print("[Replay] No replay file loaded yet.")
        return
    try:
        val = int(jump_entry.get())
        jump_target_sec = val
        print(f"[Replay] Jump requested to SYS_Second = {val}")
        replay_paused = False
        try:
            btn_pause_resume.config(text="Pause ⏸", bg="lightchocolate")
        except Exception:
            pass
        # restart replay so new jump is used
        replay_running = False
        pytime.sleep(0.2)
        replay_running = True
        threading.Thread(target=process_replay_file, args=(replay_filepath,), daemon=True).start()
    except ValueError:
        print("[Replay] Invalid SYS_Second value entered.")
    
def start_thread():
    """Start reader and processor threads as daemons so they stop when main thread exits."""
    t1 = threading.Thread(target=readSerial, daemon=True)
    t1.start()
    t2 = threading.Thread(target=process_data, daemon=True)
    t2.start()
 
    
        
def connexion():
    global ser, serialData, drop_COM, drop_bd

    # Basic validation
    port = clicked_com.get() if 'clicked_com' in globals() else None
    baud_str = clicked_bd.get() if 'clicked_bd' in globals() else None

    # If currently connected, disconnect
    if connect_btn["text"] == "Disconnect":
        serialData = False
        connect_btn["text"] = "Connect"
        try:
            refresh_btn["state"] = "active"
            drop_bd["state"] = "active"
            drop_COM["state"] = "active"
            file_entry1.config(state="normal")
            project_entry.config(state="normal")
        except Exception:
            pass
        try:
            if ser and getattr(ser, "is_open", False):
                ser.close()
                print("Serial port closed")
        except Exception as e:
            print("Error closing serial:", e)
        return

    # Else attempt to connect
    if not port or port == "-" or port.strip() == "":
        status_var.set("❌ Select a valid COM port.")
        return

    # Parse baud
    try:
        baud = int(baud_str) if baud_str and baud_str.isdigit() else 115200
    except Exception:
        baud = 115200

    try:
        ser = serial.Serial(port, baud, timeout=1)
    except Exception as e:
        status_var.set(f"❌ Unable to open {port} at {baud}: {e}")
        print("Serial open error:", e)
        return

    # mark UI as connected
    serialData = True
    connect_btn["text"] = "Disconnect"
    try:
        refresh_btn["state"] = "disabled"
        drop_bd["state"] = "disabled"
        drop_COM["state"] = "disabled"
        file_entry1.config(state="disabled")
        project_entry.config(state="disabled")
    except Exception:
        pass

    # Start background threads
    start_thread()
 
 
 
 
def close_window():
    global window, serialData, ser
    serialData = False
    try:
        if ser and getattr(ser, "is_open", False):
            ser.close()
    except Exception:
        pass
    try:
        window.destroy()
    except Exception:
        pass
 
if __name__=="__main__":
    connect_menu_init()
 
