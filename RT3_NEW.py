
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 11:32:02 2025
 
@author: Adminservice
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
import time as ptime
import csv
from tkinter import Radiobutton, StringVar
global status_var
from datetime import datetime
import os
import platform
import time as pytime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


global root
 
 
 
serialData=False
ser=None
counter_value=0
counter_value2=0
counter_value3=0
counter_value4=0
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
bit_names = ["ANT","TRK","DR","EPH","POS","URA","RIM","PR","INO","SBC","SBR","UR5"]
 
 
 
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
 
class Graphics:
    pass
    
# RT1 widgets (original widgets)
rt1_widgets = {}
rt2_widgets = {}
rt3_widgets = {}

def connect_menu_init():
    global Button,Label,LabelFrame,Entry,Tk,NORMAL,END,Frame
    global parent_frame,frame1,connect_btn,refresh_btn,graph,output_text,file_bd,file_entry,file_entry1,datetime_label,Canvas
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
    
    window = Tk()
    window.title("GAGAN 18 CHANNNEL INTERFACE - MULTI-RT")
    window.configure(bg="burlywood")
    window.geometry("1800x1200")
    project_name_var = StringVar(value="GAGANYAAN")

    # === Header Banner ===
    header_label = Label(
        window,
        text="SPS TELEMETRY AND COMMAND INTERFACE : GAGANYAAN",
        font=("Algerian", 20, "bold"),
        bg="dark red",
        fg="WHITE",
        pady=10
    )
    header_label.grid(row=0, column=0, columnspan=6, sticky="ew")

    # === RT Selection Tabs ===
    rt_tab_frame = Frame(window, bg="burlywood")
    rt_tab_frame.grid(row=1, column=0, columnspan=6, sticky="ew", padx=10, pady=5)
    
    rt_tab_var = StringVar(value="RT1")
    
    def switch_rt_view(rt_name):
        # Hide all RT frames
        rt1_frame.grid_remove()
        rt2_frame.grid_remove()
        rt3_frame.grid_remove()
        
        # Show selected RT frame
        if rt_name == "RT1":
            rt1_frame.grid()
        elif rt_name == "RT2":
            rt2_frame.grid()
        elif rt_name == "RT3":
            rt3_frame.grid()
    
    rt1_tab = Radiobutton(rt_tab_frame, text="RT1 (ACC A1F0A/B)", variable=rt_tab_var, value="RT1", 
                         font=("Calibri", 12, "bold"), bg="lightblue", command=lambda: switch_rt_view("RT1"))
    rt1_tab.grid(row=0, column=0, padx=5)
    
    rt2_tab = Radiobutton(rt_tab_frame, text="RT2 (ACC A1F0C/D)", variable=rt_tab_var, value="RT2",
                         font=("Calibri", 12, "bold"), bg="lightgreen", command=lambda: switch_rt_view("RT2"))
    rt2_tab.grid(row=0, column=1, padx=5)
    
    rt3_tab = Radiobutton(rt_tab_frame, text="RT3 (ACC A1F0E/F)", variable=rt_tab_var, value="RT3",
                         font=("Calibri", 12, "bold"), bg="lightcoral", command=lambda: switch_rt_view("RT3"))
    rt3_tab.grid(row=0, column=2, padx=5)

    # === RT1 Frame (with COM Manager and Commands) ===
    rt1_frame = Frame(window, bg="burlywood")
    rt1_frame.grid(row=2, column=0, columnspan=6, sticky="nsew")
    
    # === Scrollable Canvas Setup for RT1 ===
    canvas_rt1 = Canvas(rt1_frame, bg="burlywood", highlightthickness=0)
    scrollbar_y_rt1 = ttk.Scrollbar(rt1_frame, orient="vertical", command=canvas_rt1.yview)
    scrollbar_x_rt1 = ttk.Scrollbar(rt1_frame, orient="horizontal", command=canvas_rt1.xview)
    canvas_rt1.configure(yscrollcommand=scrollbar_y_rt1.set, xscrollcommand=scrollbar_x_rt1.set)

    canvas_rt1.grid(row=0, column=0, sticky="nsew")
    scrollbar_y_rt1.grid(row=0, column=1, sticky="ns")
    scrollbar_x_rt1.grid(row=1, column=0, sticky="ew")

    root_rt1 = Frame(canvas_rt1, bg="burlywood")
    canvas_rt1.create_window((0, 0), window=root_rt1, anchor="nw")

    # Configure grid expansion
    rt1_frame.grid_rowconfigure(0, weight=1)
    rt1_frame.grid_columnconfigure(0, weight=1)

    # Allow root columns to expand
    for i in range(5):
        root_rt1.grid_columnconfigure(i, weight=1)

    # Update scroll region
    def on_frame_configure_rt1(event):
        canvas_rt1.configure(scrollregion=canvas_rt1.bbox("all"))
    root_rt1.bind("<Configure>", on_frame_configure_rt1)
    
     # Enable mouse wheel scrolling
    def bind_mousewheel(widget):
        system = platform.system()
        if system == 'Windows' or system == 'Darwin':
            widget.bind_all("<MouseWheel>", lambda e: canvas_rt1.yview_scroll(int(-1*(e.delta/120)), "units"))
        else:  # Linux
            widget.bind_all("<Button-4>", lambda e: canvas_rt1.yview_scroll(-1, "units"))
            widget.bind_all("<Button-5>", lambda e: canvas_rt1.yview_scroll(1, "units"))

    bind_mousewheel(canvas_rt1)
    # ======================= COM MANAGER for RT1 only ===============
    
    frame1 = LabelFrame(
        root_rt1,
        text="  COM MANAGER (RT1 ONLY)  ",
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=2, pady=2
    )
    frame1.grid(row=0,column=0,padx=2,pady=2,sticky="nsew")
    
    project_label = Label(frame1, text = "Project Name: ", font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood")
    project_label.grid(column=0,row=0,pady=2,padx=2)
    project_entry = Entry(frame1, textvariable=project_name_var, font=("Calibri", 11,"bold"),fg="dark green",bg="burlywood", width=15, justify="center")
    project_entry.grid(row=0, column=1,pady=2,padx=2)      
    project_name_var.trace_add("write", lambda *args: update_project_name(project_name_var, header_label))
    
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
    
    status_var = StringVar(value="CMD Status:")
    status_label = Label(
        frame1,
        textvariable=status_var,
        anchor="w",
        font=("Calibri", 11,"bold"),
        fg="blue",
        bg="burlywood",
        wraplength=700,
        justify="left"
    )
    status_label.grid(row=2, column=0, columnspan=8, sticky="w", padx=2,pady=2)
    
    # =============== COMMAND FRAME for RT1 only ================
    frame13 = LabelFrame(root_rt1,
        text="  SA COMMANDS (RT1 ONLY)  ",
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=2, pady=2
    )
    frame13.grid(row=0, column=3, padx=2,pady=2,sticky="nsew")
    
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
    
    # ====== BUS COMMAND Section for RT1 only =========
    frame_bus = LabelFrame(root_rt1, text="  BUS COMMANDS (RT1 ONLY)  ",
        bg="burlywood",
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=2, pady=2
    )
    frame_bus.grid(row=1, column=3, padx=2, pady=2, sticky="nsew")
    
    bus_var = StringVar(value=" ")
    Radiobutton(frame_bus, text="BUS A", variable=bus_var, value="A", font=("Calibri", 11,"bold"),bg="burlywood",fg="blue").grid(row=0, column=0, padx=2, pady=2)
    Radiobutton(frame_bus, text="BUS B", variable=bus_var, value="B", font=("Calibri", 11,"bold"),bg="burlywood",fg="blue").grid(row=0, column=1, padx=2, pady=2)
    
    bus_var.trace_add('write', on_bus_toggle)
    
    Label(frame_bus, text="RT Add(Hex):", font=("Calibri", 11,"bold"),bg="burlywood",fg="dark violet").grid(row=1, column=0, padx=2, pady=2)
    dataword_entry = Entry(frame_bus, width=6,font=("Calibri", 11,"bold"))
    dataword_entry.grid(row=1, column=1, padx=2, pady=2)
    dataword_entry.insert(1, "00")
    
    for i, (cmd_name, cmd_val) in enumerate(bus_commands):
        btn = Button(frame_bus, text=cmd_name, width=11, font=("Calibri", 11,"bold"),bg="chocolate",command=lambda v=cmd_val: send_bus_command_button(v))
        btn.grid(row=2+i//4, column=i%4, padx=2, pady=2)
        bus_command_buttons[cmd_name] = btn
 
    send_bus_manual = Button(frame_bus, text="Send", width=7,font=("Calibri", 11,"bold"),bg="chocolate", command=send_bus_command_entry)
    send_bus_manual.grid(row=1, column=3, padx=2, pady=2)
    
    # Create RT1 display widgets (rest of the original GUI)
    create_rt_display_widgets(root_rt1, "RT1")
    
    # Store RT1 widgets
    store_rt_widgets("RT1")
    
    # ========================== RT2 Frame (without COM Manager and Commands) ======================
    rt2_frame = Frame(window, bg="burlywood")
    rt2_frame.grid(row=2, column=0, columnspan=6, sticky="nsew")
    
    # === Scrollable Canvas Setup for RT2 ===
    canvas_rt2 = Canvas(rt2_frame, bg="burlywood", highlightthickness=0)
    scrollbar_y_rt2 = ttk.Scrollbar(rt2_frame, orient="vertical", command=canvas_rt2.yview)
    scrollbar_x_rt2 = ttk.Scrollbar(rt2_frame, orient="horizontal", command=canvas_rt2.xview)
    canvas_rt2.configure(yscrollcommand=scrollbar_y_rt2.set, xscrollcommand=scrollbar_x_rt2.set)

    canvas_rt2.grid(row=0, column=0, sticky="nsew")
    scrollbar_y_rt2.grid(row=0, column=1, sticky="ns")
    scrollbar_x_rt2.grid(row=1, column=0, sticky="ew")

    root_rt2 = Frame(canvas_rt2, bg="burlywood")
    canvas_rt2.create_window((0, 0), window=root_rt2, anchor="nw")

    rt2_frame.grid_rowconfigure(0, weight=1)
    rt2_frame.grid_columnconfigure(0, weight=1)

    for i in range(5):
        root_rt2.grid_columnconfigure(i, weight=1)

    def on_frame_configure_rt2(event):
        canvas_rt2.configure(scrollregion=canvas_rt2.bbox("all"))
    root_rt2.bind("<Configure>", on_frame_configure_rt2)
    
    # RT2 Header
    rt2_header = Label(root_rt2, text="RT2 DISPLAY (ACC A1F0C/D)", font=("antony", 16, "bold"),
                      bg="darkred", fg="yellow", pady=10)
    rt2_header.grid(row=0, column=0, sticky="nw", pady=1)
    
    # Create RT2 display widgets (same layout but different background)
    create_rt_display_widgets(root_rt2, "RT2")
    
    # Store RT2 widgets
    store_rt_widgets("RT2")
    
    # ========================== RT3 Frame (without COM Manager and Commands) ======================
    rt3_frame = Frame(window, bg="burlywood")
    rt3_frame.grid(row=2, column=0, columnspan=6, sticky="nsew")
    
    # === Scrollable Canvas Setup for RT3 ===
    canvas_rt3 = Canvas(rt3_frame, bg="burlywood", highlightthickness=0)
    scrollbar_y_rt3 = ttk.Scrollbar(rt3_frame, orient="vertical", command=canvas_rt3.yview)
    scrollbar_x_rt3 = ttk.Scrollbar(rt3_frame, orient="horizontal", command=canvas_rt3.xview)
    canvas_rt3.configure(yscrollcommand=scrollbar_y_rt3.set, xscrollcommand=scrollbar_x_rt3.set)

    canvas_rt3.grid(row=0, column=0, sticky="nsew")
    scrollbar_y_rt3.grid(row=0, column=1, sticky="ns")
    scrollbar_x_rt3.grid(row=1, column=0, sticky="ew")

    root_rt3 = Frame(canvas_rt3, bg="burlywood")
    canvas_rt3.create_window((0, 0), window=root_rt3, anchor="nw")

    rt3_frame.grid_rowconfigure(0, weight=1)
    rt3_frame.grid_columnconfigure(0, weight=1)

    for i in range(5):
        root_rt3.grid_columnconfigure(i, weight=1)

    def on_frame_configure_rt3(event):
        canvas_rt3.configure(scrollregion=canvas_rt3.bbox("all"))
    root_rt3.bind("<Configure>", on_frame_configure_rt3)
    
    # RT3 Header
    rt3_header = Label(root_rt3, text="RT3 DISPLAY (ACC A1F0E/F)", font=("antony", 16, "bold"),
                      bg="darkred", fg="yellow", pady=10)
    rt3_header.grid(row=0, column=0, sticky="nw", pady=1)
    
    # Create RT3 display widgets (same layout but different background)
    create_rt_display_widgets(root_rt3, "RT3")
    
    # Store RT3 widgets
    store_rt_widgets("RT3")
    
    # Initially show RT1
    switch_rt_view("RT1")
    
    # === Footer Section ===
    separator = Frame(window, bg="black", height=2)
    separator.grid(row=3, column=0, columnspan=6, sticky="ew", pady=(10, 0))

    footer_label = Label(
        window,
        text="copyright@2025, Space Navigation Group/URSC/ISRO | Version 1.0 | Multi-RT Display",
        font=("Segoe UI", 10, "italic"),
        bg="navy blue",
        fg="white",
        pady=2
    )
    footer_label.grid(row=4, column=0, columnspan=6, sticky="nsew")
    
    # Configure window grid
    window.grid_rowconfigure(2, weight=1)
    window.grid_columnconfigure(0, weight=1)
    
    baud_select()
    update_coms()
    
    window.mainloop()

def create_rt_display_widgets(parent_frame, rt_name):
    """Create display widgets for a specific RT"""
    bg_color = "burlywood" if rt_name == "RT1" else ("burlywood" if rt_name == "RT2" else "burlywood")
    
    # ========================== COUNTERS =======================================
    frame2=LabelFrame(parent_frame, text=f"  COUNTERS ({rt_name})  ",
        bg=bg_color,
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=2, pady=2
    )
    frame2.grid(row=0,column=2,padx=2,pady=2,sticky="nsew")
   
    update_count=Label(frame2,text="Update counter",font=("Calibri", 11,"bold"),bg=bg_color)
    update_count.grid(row=0, column=0)
    update_entry=Entry(frame2,width=10,font=("Calibri", 11,"bold"),bg=bg_color,fg="blue",state="readonly")
    update_entry.grid(column=1,row=0,pady=2,padx=2)
    
    sw_rst_c=Label(frame2,text="S/W RST Counter",font=("Calibri", 11,"bold"),bg=bg_color)
    sw_rst_c.grid(row=2, column=0)
    sw_rst_c=Entry(frame2,width=10,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    sw_rst_c.grid(column=1,row=2,pady=2,padx=2)
   
    hw_rst_c=Label(frame2,text="H/W RST Counter",font=("Calibri", 11,"bold"),bg=bg_color)
    hw_rst_c.grid(row=3, column=0)
    hw_rst_c=Entry(frame2,width=10,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    hw_rst_c.grid(column=1,row=3,pady=2,padx=2)
   
    tsm_counter=Label(frame2,text="Tsm_Counter",font=("Calibri", 11,"bold"),bg=bg_color)
    tsm_counter.grid(row=4, column=0)
    tsm_counter_entry=Entry(frame2,width=10,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    tsm_counter_entry.grid(column=1,row=4,pady=2,padx=2)
   
    # ======================== SYSTEM TIME =====================================
    frame3=LabelFrame(parent_frame,text=f"  TIME ({rt_name})  ",
        bg=bg_color,
        fg="dark red",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=2, pady=2
    )
    frame3.grid(row=1,column=0,padx=2,pady=2,sticky="nsew")
   
    Name=Label(frame3,text=" System Time:",font=("Calibri", 11,"bold"),fg="blue",bg=bg_color,padx=5,pady=5)
    Name.grid(row=1, column=1)
    
    weeks_label=Label(frame3,text="Week Number:",font=("Calibri", 11,"bold"),bg=bg_color)
    weeks_label.grid(row=1, column=6)
    week_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    week_entry.grid(row=1, column=7, pady=5,padx=5)
    
    time_label=Label(frame3,text="Second(s):",font=("Calibri", 11,"bold"),bg=bg_color)
    time_label.grid(row=1, column=8)
    time_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    time_entry.grid(row=1, column=9, pady=5,padx=5)
   
    nanotime_label=Label(frame3,text="Nano Second(ns):",font=("Calibri", 11,"bold"),bg=bg_color)
    nanotime_label.grid(row=1, column=10)
    nanotime_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    nanotime_entry.grid(row=1, column=11, pady=5,padx=5)
   
    Name=Label(frame3,text=" Sync Time:",font=("Calibri", 11,"bold"),fg="blue",bg=bg_color,padx=5,pady=5)
    Name.grid(row=2, column=1)
    
    weeks_label1=Label(frame3,text="Week Number:",font=("Calibri", 11,"bold"),bg=bg_color)
    weeks_label1.grid(row=2, column=6)
    week_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    week_entry1.grid(row=2, column=7, pady=5,padx=5)
   
    time_label1=Label(frame3,text="Second(s):",font=("Calibri", 11,"bold"),bg=bg_color)
    time_label1.grid(row=2, column=8)
    time_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    time_entry1.grid(row=2, column=9, pady=5,padx=5)
   
    nanotime_label1=Label(frame3,text="Nano Second(ns):",font=("Calibri", 11,"bold"),bg=bg_color)
    nanotime_label1.grid(row=2, column=10)
    nanotime_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    nanotime_entry1.grid(row=2, column=11, pady=5,padx=5)
   
    Name=Label(frame3,text=" PPS Time:",font=("Calibri", 11,"bold"),fg="blue",bg=bg_color,padx=5,pady=5)
    Name.grid(row=3, column=1)
    
    weeks_label2=Label(frame3,text="Week Number:",font=("Calibri", 11,"bold"),bg=bg_color)
    weeks_label2.grid(row=3, column=6)
    week_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    week_entry2.grid(row=3, column=7, pady=5,padx=5)
    
    time_label2=Label(frame3,text="Second(s):",font=("Calibri", 11,"bold"),bg=bg_color)
    time_label2.grid(row=3, column=8)
    time_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    time_entry2.grid(row=3, column=9, pady=5,padx=5)
   
    nanotime_label2=Label(frame3,text="Nano Second(ns):",font=("Calibri", 11,"bold"),bg=bg_color)
    nanotime_label2.grid(row=3, column=10)
    nanotime_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    nanotime_entry2.grid(row=3, column=11, pady=5,padx=5)
   
    fix_3d=Label(frame3,text="PPS_3D_FIX:",font=("Calibri", 11,"bold"),bg=bg_color)
    fix_3d.grid(row=4, column=6)
    fix_3d=Entry(frame3,width=15,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    fix_3d.grid(column=7,row=4,pady=5,padx=5)
    
    leap=Label(frame3,text="PPS_LEAP:",font=("Calibri", 11,"bold"),bg=bg_color)
    leap.grid(row=4, column=8)
    leap=Entry(frame3,width=15,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    leap.grid(column=9,row=4,pady=5,padx=5)
    
    
    # ============================    ACQ ===========================================
    frame14=LabelFrame(parent_frame,text= f"  ACQ ({rt_name})  ",  # extra spacing in title gives a round feel
    bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame14.grid(row=2,column=3,padx=2,pady=2,sticky="nsew")
   
    acq1=Label(frame14,text="ACQ1",font=("Calibri", 11,"bold"),bg=bg_color)
    acq1.grid(row=0, column=0)
    acq1=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    acq1.grid(column=1,row=0,pady=2,padx=2)
   
    acq2=Label(frame14,text="ACQ-2",font=("Calibri", 11,"bold"),bg=bg_color)
    acq2.grid(row=0, column=2)
    acq2=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)      
    acq2.grid(column=3,row=0,pady=2,padx=2)
   
    acq3=Label(frame14,text="ACQ-3",font=("Calibri", 11,"bold"),bg=bg_color)
    acq3.grid(row=0, column=4)
    acq3=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    acq3.grid(column=5,row=0,pady=2,padx=2)
   
    acq4=Label(frame14,text="ACQ-4",font=("Calibri", 11,"bold"),bg=bg_color)
    acq4.grid(row=0, column=6)
    acq4=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    acq4.grid(column=7,row=0,pady=2,padx=2)
    
    port_conf=Label(frame14,text="ANT1",font=("Calibri", 11,"bold"),bg=bg_color)
    port_conf.grid(row=1, column=0)
    port_conf=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    port_conf.grid(column=1,row=1,pady=2,padx=2)
    
    port_conf1=Label(frame14,text="ANT2",font=("Calibri", 11,"bold"),bg=bg_color)
    port_conf1.grid(row=1, column=2)
    port_conf1=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    port_conf1.grid(column=3,row=1,pady=2,padx=2)
    
    port_conf2=Label(frame14,text="ANT3",font=("Calibri", 11,"bold"),bg=bg_color)
    port_conf2.grid(row=1, column=4)
    port_conf2=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    port_conf2.grid(column=5,row=1,pady=2,padx=2)
    
    port_conf3=Label(frame14,text="ANT4",font=("Calibri", 11,"bold"),bg=bg_color)
    port_conf3.grid(row=1, column=6)
    port_conf3=Entry(frame14,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    port_conf3.grid(column=7,row=1,pady=2,padx=2)
    
    # ===============   VECTOR DATA =============================================
    frame5=LabelFrame(parent_frame,text=f"  STATE VECTOR DATA({rt_name})   ",  # extra spacing in title gives a round feel
    bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame5.grid(row=2,column=0,padx=2,pady=2,sticky="nsew")
   
    Name=Label(frame5,text="  INSTANTIATE :",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg=bg_color)
    Name.grid(row=1, column=1)
    position_label = Label(frame5, text="X(m):",font=("Calibri", 11,"bold"),bg=bg_color)
    position_label.grid(row=1, column=3, sticky="W")
    velocity_label = Label(frame5, text="Vel_x(m/s):",font=("Calibri", 11,"bold"),bg=bg_color)
    velocity_label.grid(row=1, column=9, sticky="W")
    position_label1 = Label(frame5, text="Y(m):",font=("Calibri", 11,"bold"),bg=bg_color)
    position_label1.grid(row=1, column=5, sticky="W")
    velocity_label1 = Label(frame5, text="Vel_y(m/s):",font=("Calibri", 11,"bold"),bg=bg_color)
    velocity_label1.grid(row=1, column=11, sticky="W")
    position_label2 = Label(frame5, text="Z(m):",font=("Calibri", 11,"bold"),bg=bg_color)
    position_label2.grid(row=1, column=7, sticky="W")
    velocity_label2 = Label(frame5, text="Vel_z(m/s):",font=("Calibri", 11,"bold"),bg=bg_color)
    velocity_label2.grid(row=1, column=13, sticky="W")
   
    position_entry = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    position_entry.grid(row=1, column=4, padx=2)
    velocity_entry = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    velocity_entry.grid(row=1, column=10, padx=2)
    position_entry1 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    position_entry1.grid(row=1, column=6, padx=2)
    velocity_entry1 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    velocity_entry1.grid(row=1, column=12, padx=2)
    position_entry2 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    position_entry2.grid(row=1, column=8, padx=2)
    velocity_entry2 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    velocity_entry2.grid(row=1, column=14, padx=2)
   
    Name1=Label(frame5,text=" ESTIMATED    :",padx=2,pady=2,font=("Calibri", 11,"bold"),fg="blue",bg=bg_color)
    Name1.grid(row=2, column=1)
    position_label3 = Label(frame5, text="X(m):",font=("Calibri", 11,"bold"),bg=bg_color)
    position_label3.grid(row=2, column=3, sticky="W")
    velocity_label3 = Label(frame5, text="Vel_x(m/s):",font=("Calibri", 11,"bold"),bg=bg_color)
    velocity_label3.grid(row=2, column=9, sticky="W")
    position_label4 = Label(frame5, text="Y(m):",font=("Calibri", 11,"bold"),bg=bg_color)
    position_label4.grid(row=2, column=5, sticky="W")
    velocity_label4 = Label(frame5, text="Vel_y(m/s):",font=("Calibri", 11,"bold"),bg=bg_color)
    velocity_label4.grid(row=2, column=11, sticky="W")
    position_label5 = Label(frame5, text="Z(m):",font=("Calibri", 11,"bold"),bg=bg_color)
    position_label5.grid(row=2, column=7, sticky="W")
    velocity_label5 = Label(frame5, text="Vel_z(m/s):",font=("Calibri", 11,"bold"),bg=bg_color)
    velocity_label5.grid(row=2, column=13, sticky="W")
   
    position_entry3 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    position_entry3.grid(row=2, column=4, padx=2)
    velocity_entry3 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    velocity_entry3.grid(row=2, column=10, padx=2)
    position_entry4 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    position_entry4.grid(row=2, column=6, padx=2)
    velocity_entry4 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    velocity_entry4.grid(row=2, column=12, padx=2)
    position_entry5 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    position_entry5.grid(row=2, column=8, padx=2)
    velocity_entry5 = Entry(frame5, width=11, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="dark slate gray")
    velocity_entry5.grid(row=2, column=14, padx=2)
    
    
    # ======================= CHECKSUM ===============================================
    frame7=LabelFrame(parent_frame,text=f'CHECKSUM({rt_name}) ',
    bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame7.grid(row=0,column=1,padx=2,pady=2,sticky="nsew")
 
    csm1=Label(frame7,text="CHECKSUM 1",font=("Calibri", 11,"bold"),bg=bg_color)
    csm1.grid(row=3, column=0)
    csm1=Entry(frame7,width=15,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    csm1.grid(column=1,row=3,pady=2,padx=2)
    csm2=Label(frame7,text="CHECKSUM 2",font=("Calibri", 11,"bold"),bg=bg_color)
    csm2.grid(row=4, column=0)
    csm2=Entry(frame7,width=15,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    csm2.grid(column=1,row=4,pady=2,padx=2)
    
    
    # =========================== CLOCK AND DRIFT ================================
    frame9=LabelFrame(parent_frame,text=f'CLOCK and DRIFT ({rt_name})',bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame9.grid(row=1,column=1,padx=2,pady=2,sticky="nsew")
 
    cb=Label(frame9,text="Clock Bais",font=("Calibri", 11,"bold"),bg=bg_color)
    cb.grid(row=0, column=0)
    cb=Entry(frame9,width=10,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    cb.grid(column=1,row=0,pady=2,padx=2)
   
    isb=Label(frame9,text="Inter System Bais",font=("Calibri", 11,"bold"),bg=bg_color)
    isb.grid(row=1, column=0)
    isb=Entry(frame9,width=10,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    isb.grid(column=1,row=1,pady=2,padx=2)
   
    drift=Label(frame9,text="Drift",font=("Calibri", 11,"bold"),bg=bg_color)
    drift.grid(row=2, column=0)
    drift=Entry(frame9,width=10,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    drift.grid(column=1,row=2,pady=2,padx=2)
   
    InterSystemDrift=Label(frame9,text="Inter System Drift",font=("Calibri", 11,"bold"),bg=bg_color)
    InterSystemDrift.grid(row=3, column=0)
    isd=Entry(frame9,width=10,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    isd.grid(column=1,row=3,pady=2,padx=2)
    
     # ======================= PDOP AND NO OF SAT =====================================
    frame10=LabelFrame(parent_frame,text=f'PDOP and No of Sat({rt_name})',bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame10.grid(row=2,column=1,padx=2,pady=2,sticky="nsew")
 
    pdop=Label(frame10,text="PDOP",font=("Calibri", 11,"bold"),bg=bg_color)
    pdop.grid(row=3, column=0)
    pdop=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    pdop.grid(column=1,row=3,pady=2,padx=2)
    
    no_sat_trck=Label(frame10,text="No of SAT",font=("Calibri", 11,"bold"),bg=bg_color)
    no_sat_trck.grid(row=6, column=0)
    no_sat_trck=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    no_sat_trck.grid(column=1,row=6,pady=2,padx=2)
    
    # ================ LAST CMD ========================================================
    frame10=LabelFrame(parent_frame,text=f'LAST CMD({rt_name})',bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame10.grid(row=2,column=2,padx=2,pady=2,sticky="nsew")
 
    last_cmd_exe=Label(frame10,text="Last Cmd Exe",font=("Calibri", 11,"bold"),bg=bg_color)
    last_cmd_exe.grid(row=0, column=0)
    last_cmd_exe=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    last_cmd_exe.grid(column=1,row=0,pady=2,padx=2)
   
    last_reset_time=Label(frame10,text="Last reset time",font=("Calibri", 11,"bold"),bg=bg_color)
    last_reset_time.grid(row=1, column=0)
    last_reset_time=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    last_reset_time.grid(column=1,row=1,pady=2,padx=2)
   
    # ========================== TRACKING INFO ==========================
    frame8 = LabelFrame(parent_frame, text=f"TRACKING INFO ({rt_name})", bg=bg_color,
                    fg="dark red",
                    font=("Calibri", 13, "bold"),
                    relief="solid",
                    bd=2,
                    padx=2, pady=2)
    frame8.grid(row=4, column=0, padx=2, pady=2, sticky="nsew")
    
    channel = Label(frame8, text="Channel", font=("Calibri", 11, "bold"), fg="blue", bg=bg_color)
    channel.grid(row=4, column=1, padx=5, pady=5)
    
    # Channel labels
    for ch in range(1, 19):
        ch_label = Label(frame8, text=str(ch), padx=2, pady=2, font=("Calibri", 11, "bold"), 
                         fg="blue", bg=bg_color)
        ch_label.grid(row=4+ch, column=1)
    
    # SVID labels and entries
    svid = Label(frame8, width=5, text="SVID", font=("Calibri", 11, "bold"), fg="blue", bg=bg_color)
    svid.grid(row=4, column=2, padx=5, pady=5)
    
    svid_entries = []
    for ch in range(1, 19):
        entry = Entry(frame8, width=5, state="readonly", font=("Calibri", 11, "bold"))
        entry.grid(column=2, row=4+ch, pady=2, padx=2)
        svid_entries.append(entry)
    
    # CNDR labels and entries
    cndr = Label(frame8, width=5, text="CNDR", font=("Calibri", 11, "bold"), fg="blue", bg=bg_color)
    cndr.grid(row=4, column=3, padx=5, pady=5)
    
    cndr_entries = []
    for ch in range(1, 19):
        entry = Entry(frame8, width=5, state="readonly", font=("Calibri", 11, "bold"))
        entry.grid(column=3, row=4+ch, pady=2, padx=2)
        cndr_entries.append(entry)
    
     # All 16 bit names as per your request
    bit_names = ["ANT","TRK","DR","EPH","POS","URA","RIM","PR","INO","SBC","SBR","UR5"]
    
    # Bit labels
    for i, bit in enumerate(bit_names):
        Label(frame8, text=bit, font=("Calibri", 11, "bold"), fg="blue", bg=bg_color).grid(
            row=4, column=4+i, padx=5, pady=5)
    
    # Create Entry widgets for each channel and each bit
    bit_to_entrylist = {bit: [] for bit in bit_names}
    for ch in range(18):
        for i, bit in enumerate(bit_names):
            entry = Entry(frame8, width=4, state="readonly", font=("Calibri", 11, "bold"))
            entry.grid(row=5+ch, column=4+i, pady=2, padx=2)
            bit_to_entrylist[bit].append(entry)
    
    # IODE
    iode = Label(frame8, width=8, text="IODE", font=("Calibri", 11, "bold"), fg="blue", bg=bg_color)
    iode.grid(row=4, column=16, padx=5, pady=5)
    
    iode_entries = []
    for ch in range(1, 19):
        entry = Entry(frame8, width=8, state="readonly", font=("Calibri", 11, "bold"))
        entry.grid(column=16, row=4+ch, pady=2, padx=2)
        iode_entries.append(entry)
    
    # PR
    pr = Label(frame8, width=11, text="PR(cm)", font=("Calibri", 11, "bold"), fg="blue", bg=bg_color)
    pr.grid(row=4, column=17, padx=5, pady=5)
    
    pr_entries = []
    for ch in range(1, 19):
        entry = Entry(frame8, width=12, state="readonly", font=("Calibri", 11, "bold"))
        entry.grid(column=17, row=4+ch, pady=2, padx=2)
        pr_entries.append(entry)
    
    # DR
    dr = Label(frame8, width=11, text="DR(m/s)", font=("Calibri", 11, "bold"), fg="blue", bg=bg_color)
    dr.grid(row=4, column=18, padx=5, pady=5)
    
    dr_entries = []
    for ch in range(1, 19):
        entry = Entry(frame8, width=12, state="readonly", font=("Calibri", 11, "bold"))
        entry.grid(column=18, row=4+ch, pady=2, padx=2)
        dr_entries.append(entry)
    
    # ELEV
    elev = Label(frame8, width=11, text="ELEV(m/s)", font=("Calibri", 11, "bold"), fg="blue", bg=bg_color)
    elev.grid(row=4, column=19, padx=5, pady=5)
    
    elev_entries = []
    for ch in range(1, 19):
        entry = Entry(frame8, width=10, state="readonly", font=("Calibri", 11, "bold"))
        entry.grid(column=19, row=4+ch, pady=2, padx=2)
        elev_entries.append(entry)
    
    
    
   
    #  ========================= NAVIC ======================================
    frame12=LabelFrame(parent_frame,text=f'NAVIC({rt_name})',bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame12.grid(row=3,column=2,padx=2,pady=2,sticky="nsew")

    navic_msg_22_c=Label(frame12,text="NAVIC_MSG_22",font=("Calibri", 11,"bold"),bg=bg_color)
    navic_msg_22_c.grid(row=3, column=0)
    navic_msg_22_c=Entry(frame12,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    navic_msg_22_c.grid(column=1,row=3,pady=2,padx=2)
   
    navic_msg_cmd_c=Label(frame12,text="NAVIC_MSG_CMD_C",font=("Calibri", 11,"bold"),bg=bg_color)
    navic_msg_cmd_c.grid(row=4, column=0)
    navic_msg_cmd_c=Entry(frame12,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    navic_msg_cmd_c.grid(column=1,row=4,pady=2,padx=2)
    
    navic_cmd_var=Label(frame12,text="NAVIC CMD VAR",font=("Calibri", 11,"bold"),bg=bg_color)
    navic_cmd_var.grid(row=7, column=0)
    navic_cmd_var=Entry(frame12,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    navic_cmd_var.grid(column=1,row=7,pady=2,padx=2)

    
    # ============================  NRFFC and GRFFC CNT ============================== 
    frame12=LabelFrame(parent_frame,text=f'NRFFC and GRFFC CNT({rt_name})',bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame12.grid(row=3,column=3,padx=2,pady=2,sticky="nsew") 
   
    total_cmd_counter=Label(frame12,text="Total_cmd_c",font=("Calibri", 11,"bold"),bg=bg_color)
    total_cmd_counter.grid(row=0, column=0)
    total_cmd_counter=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    total_cmd_counter.grid(column=1,row=0,pady=2,padx=2)
    
    nrff_rst_counter1=Label(frame12,text="NRFFC_rst_c1",font=("Calibri", 11,"bold"),bg=bg_color)
    nrff_rst_counter1.grid(row=0, column=2)
    nrff_rst_counter1=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    nrff_rst_counter1.grid(column=3,row=0,pady=2,padx=2)
    
    nrff_rst_counter2=Label(frame12,text="NRFFC_rst_c2",font=("Calibri", 11,"bold"),bg=bg_color)
    nrff_rst_counter2.grid(row=0, column=4)
    nrff_rst_counter2=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    nrff_rst_counter2.grid(column=5,row=0,pady=2,padx=2)
    
    grff_rst_counter1=Label(frame12,text="GRFFC_rst_c1",font=("Calibri", 11,"bold"),bg=bg_color)
    grff_rst_counter1.grid(row=1, column=0)
    grff_rst_counter1=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    grff_rst_counter1.grid(column=1,row=1,pady=2,padx=2)
    
    grff_rst_counter2=Label(frame12,text="GRFFC_rst_c2",font=("Calibri", 11,"bold"),bg=bg_color)
    grff_rst_counter2.grid(row=1, column=2)
    grff_rst_counter2=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    grff_rst_counter2.grid(column=3,row=1,pady=2,padx=2)
    
    grff_rst_counter3=Label(frame12,text="GRFFC_rst_c3",font=("Calibri", 11,"bold"),bg=bg_color)
    grff_rst_counter3.grid(row=1, column=4)
    grff_rst_counter3=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    grff_rst_counter3.grid(column=5,row=1,pady=2,padx=2)
    
    grff_rst_counter4=Label(frame12,text="GRFFC_rst_c4",font=("Calibri", 11,"bold"),bg=bg_color)
    grff_rst_counter4.grid(row=2, column=0)
    grff_rst_counter4=Entry(frame12,width=6,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    grff_rst_counter4.grid(column=1,row=2,pady=2,padx=2)
    
    # ===================== MODE and PORT and ID's ====================================
    frame15=LabelFrame(parent_frame,text=f"MODE and PORT and ID's({rt_name})",bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame15.grid(row=3,column=0,padx=2,pady=2,sticky="nsew")
     
   
    TM=Label(frame15,text="TM",font=("Calibri", 11,"bold"),bg=bg_color)
    TM.grid(row=0, column=0)
    tm=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    tm.grid(column=1,row=0,pady=2,padx=2)
   
    SWDT=Label(frame15,text="SWDT",font=("Calibri", 11,"bold"),bg=bg_color)
    SWDT.grid(row=0, column=2)
    swdt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)   
    swdt.grid(column=3,row=0,pady=2,padx=2)
   
    HWDT=Label(frame15,text="HWDT",font=("Calibri", 11,"bold"),bg=bg_color)
    HWDT.grid(row=0, column=4)
    hwdt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    hwdt.grid(column=5,row=0,pady=2,padx=2)
   
    SBASEN=Label(frame15,text="SBASEN",font=("Calibri", 11,"bold"),bg=bg_color)
    SBASEN.grid(row=0, column=6)
    sbasen=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    sbasen.grid(column=7,row=0,pady=2,padx=2)
   
    SYS_MODE=Label(frame15,text="SYS_MODE",font=("Calibri", 11,"bold"),bg=bg_color)
    SYS_MODE.grid(row=0, column=8)
    sys_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    sys_mode.grid(column=9,row=0,pady=2,padx=2)
   
    REC_MODE=Label(frame15,text="REC_MODE",font=("Calibri", 11,"bold"),bg=bg_color)
    REC_MODE.grid(row=1, column=0)
    rec_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    rec_mode.grid(column=1,row=1,pady=2,padx=2)
   
    TIME_MODE=Label(frame15,text="TIME_MODE",font=("Calibri", 11,"bold"),bg=bg_color)
    TIME_MODE.grid(row=1, column=2)
    time_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    time_mode.grid(column=3,row=1,pady=2,padx=2)
     
    ALM_AV=Label(frame15,text="ALM_AV",font=("Calibri", 11,"bold"),bg=bg_color)
    ALM_AV.grid(row=1, column=4)
    alm_av=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    alm_av.grid(column=5,row=1,pady=2,padx=2)
   
    TIME_AV=Label(frame15,text="TIME_AV",font=("Calibri", 11,"bold"),bg=bg_color)
    TIME_AV.grid(row=1, column=6)
    time_av=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    time_av.grid(column=7,row=1,pady=2,padx=2)
   
    POS_MODE=Label(frame15,text="POS_MODE",font=("Calibri", 11,"bold"),bg=bg_color)
    POS_MODE.grid(row=1, column=8)
    pos_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    pos_mode.grid(column=9,row=1,pady=2,padx=2)
   
    POS_AV=Label(frame15,text="POS_AV",font=("Calibri", 11,"bold"),bg=bg_color)
    POS_AV.grid(row=2, column=0)
    pos_av=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    pos_av.grid(column=1,row=2,pady=2,padx=2)
  
    sol_mode=Label(frame15,text="Sol_mode",font=("Calibri", 11,"bold"),bg=bg_color)
    sol_mode.grid(row=2, column=2)
    sol_mode=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)   
    sol_mode.grid(column=3,row=2,pady=2,padx=2)
   
    sps_id=Label(frame15,text="SPS_ID",font=("Calibri", 11,"bold"),bg=bg_color)
    sps_id.grid(row=2, column=4)
    sps_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    sps_id.grid(column=5,row=2,pady=2,padx=2)
    
    sw_rst_id=Label(frame15,text="S/W RESET ID",font=("Calibri", 11,"bold"),bg=bg_color)
    sw_rst_id.grid(row=2, column=6)
    sw_rst_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    sw_rst_id.grid(column=7,row=2,pady=2,padx=2)
   
    leo_sat_id=Label(frame15,text="LEO SAT ID",font=("Calibri", 11,"bold"),bg=bg_color)
    leo_sat_id.grid(row=2, column=8)
    leo_sat_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    leo_sat_id.grid(column=9,row=2,pady=2,padx=2)
   
    rt_id=Label(frame15,text="RT_ID",font=("Calibri", 11,"bold"),bg=bg_color)
    rt_id.grid(row=3, column=0)
    rt_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    rt_id.grid(column=1,row=3,pady=2,padx=2)
    
    s_id=Label(frame15,text="S_ID",font=("Calibri", 11,"bold"),bg=bg_color)
    s_id.grid(row=3, column=2)
    s_id=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    s_id.grid(column=3,row=3,pady=2,padx=2)
    
    
    # ====================== RT ========================================
    frame15=LabelFrame(parent_frame,text=f"RT({rt_name})",bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame15.grid(row=3,column=1,padx=2,pady=2,sticky="nsew")
    
    cmd_based_rt=Label(frame15,text="CMD BASED RT",font=("Calibri", 11,"bold"),bg=bg_color)
    cmd_based_rt.grid(row=10, column=0)
    cmd_based_rt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    cmd_based_rt.grid(column=1,row=10,pady=2,padx=2)

    spu_cmd_c_rt=Label(frame15,text="SPU CMD C RT",font=("Calibri", 11,"bold"),bg=bg_color)
    spu_cmd_c_rt.grid(row=12, column=0)
    spu_cmd_c_rt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    spu_cmd_c_rt.grid(column=1,row=12,pady=2,padx=2)
   
    dual_cmd_c_rt=Label(frame15,text="DUAL CMD C RT",font=("Calibri", 11,"bold"),bg=bg_color)
    dual_cmd_c_rt.grid(row=13, column=0)
    dual_cmd_c_rt=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    dual_cmd_c_rt.grid(column=1,row=13,pady=2,padx=2)
    
    # ============================== GAGAN-SA4W31 =======================================
    frame15=LabelFrame(parent_frame,text=f"GAGAN-SA4W31({rt_name})",bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame15.grid(row=4,column=1,padx=2,pady=2,sticky="nsew")
   
    miss_ph=Label(frame15,text="MISS_PH",font=("Calibri", 11,"bold"),bg=bg_color)
    miss_ph.grid(row=1, column=0)
    miss_ph=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)   
    miss_ph.grid(column=1,row=1,pady=2,padx=2)
   
    fmem=Label(frame15,text="FMEM",font=("Calibri", 11,"bold"),bg=bg_color)
    fmem.grid(row=2, column=0)
    fmem=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    fmem.grid(column=1,row=2,pady=2,padx=2)
   
    cr_aid=Label(frame15,text="CR_AID",font=("Calibri", 11,"bold"),bg=bg_color)
    cr_aid.grid(row=3, column=0)
    cr_aid=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    cr_aid.grid(column=1,row=3,pady=2,padx=2)
   
    full_cntr=Label(frame15,text="FULL_CTRL",font=("Calibri", 11,"bold"),bg=bg_color)
    full_cntr.grid(row=4, column=0)
    full_cntr=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    full_cntr.grid(column=1,row=4,pady=2,padx=2)
   
    lig_1=Label(frame15,text="LIG_1",font=("Calibri", 11,"bold"),bg=bg_color)
    lig_1.grid(row=6, column=0)
    lig_1=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    lig_1.grid(column=1,row=6,pady=2,padx=2)
   
    lig_2=Label(frame15,text="LIG_2",font=("Calibri", 11,"bold"),bg=bg_color)
    lig_2.grid(row=7, column=0)
    lig_2=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    lig_2.grid(column=1,row=7,pady=2,padx=2)
   
    lig_3=Label(frame15,text="LIG_3",font=("Calibri", 11,"bold"),bg=bg_color)
    lig_3.grid(row=8, column=0)
    lig_3=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    lig_3.grid(column=1,row=8,pady=2,padx=2)
   
    lig_4=Label(frame15,text="LIG_4",font=("Calibri", 11,"bold"),bg=bg_color)
    lig_4.grid(row=9, column=0)
    lig_4=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    lig_4.grid(column=1,row=9,pady=2,padx=2)
   
    lin_1=Label(frame15,text="LIN_1",font=("Calibri", 11,"bold"),bg=bg_color)
    lin_1.grid(row=10, column=0)
    lin_1=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    lin_1.grid(column=1,row=10,pady=2,padx=2)
   
    lin_2=Label(frame15,text="LIN_2",font=("Calibri", 11,"bold"),bg=bg_color)
    lin_2.grid(row=11, column=0)
    lin_2=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    lin_2.grid(column=1,row=11,pady=2,padx=2)
   
    prime_ngc=Label(frame15,text="PRIME_NGC",font=("Calibri", 11,"bold"),bg=bg_color)
    prime_ngc.grid(row=12, column=0)
    prime_ngc=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    prime_ngc.grid(column=1,row=12,pady=2,padx=2)
    
    
    # =============================== GAGAN-SA4W32 ===================================
    frame15=LabelFrame(parent_frame,text=f"GAGAN-SA4W32({rt_name})",bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame15.grid(row=4,column=2,padx=2,pady=2,sticky="nsew")
   
    rng_l=Label(frame15,text="Rng L",font=("Calibri", 11,"bold"),bg=bg_color)
    rng_l.grid(row=0, column=0)
    rng_l=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    rng_l.grid(column=1,row=0,pady=2,padx=2)
   
    orbit_phase=Label(frame15,text="Orbit_phase",font=("Calibri", 11,"bold"),bg=bg_color)
    orbit_phase.grid(row=1, column=0)
    orbit_phase=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)   
    orbit_phase.grid(column=1,row=1,pady=2,padx=2)
   
    iono_c=Label(frame15,text="IONO cor",font=("Calibri", 11,"bold"),bg=bg_color)
    iono_c.grid(row=2, column=0)
    iono_c=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    iono_c.grid(column=1,row=2,pady=2,padx=2)
   
    iono_sm=Label(frame15,text="IONO sm",font=("Calibri", 11,"bold"),bg=bg_color)
    iono_sm.grid(row=3, column=0)
    iono_sm=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    iono_sm.grid(column=1,row=3,pady=2,padx=2)
   
    cr_smo=Label(frame15,text="CR_smo",font=("Calibri", 11,"bold"),bg=bg_color)
    cr_smo.grid(row=4, column=0)
    cr_smo=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    cr_smo.grid(column=1,row=4,pady=2,padx=2)
   
    vel_sm=Label(frame15,text="Vel_ms",font=("Calibri", 11,"bold"),bg=bg_color)
    vel_sm.grid(row=5, column=0)
    vel_sm=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    vel_sm.grid(column=1,row=5,pady=2,padx=2)
   
    raim=Label(frame15,text="RAIM",font=("Calibri", 11,"bold"),bg=bg_color)
    raim.grid(row=6, column=0)
    raim=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    raim.grid(column=1,row=6,pady=2,padx=2)
   
    pr_rej=Label(frame15,text="PR Rej",font=("Calibri", 11,"bold"),bg=bg_color)
    pr_rej.grid(row=7, column=0)
    pr_rej=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    pr_rej.grid(column=1,row=7,pady=2,padx=2)
   
    pr_bf_sync=Label(frame15,text="PR BF Sync",font=("Calibri", 11,"bold"),bg=bg_color)
    pr_bf_sync.grid(row=8, column=0)
    pr_bf_sync=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    pr_bf_sync.grid(column=1,row=8,pady=2,padx=2)
   
    cfg_loop=Label(frame15,text="Cfg_loop",font=("Calibri", 11,"bold"),bg=bg_color)
    cfg_loop.grid(row=9, column=0)
    cfg_loop=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    cfg_loop.grid(column=1,row=9,pady=2,padx=2)
   
    int_crd_tst=Label(frame15,text="Int crd Tst",font=("Calibri", 11,"bold"),bg=bg_color)
    int_crd_tst.grid(row=10, column=0)
    int_crd_tst=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    int_crd_tst.grid(column=1,row=10,pady=2,padx=2)
   
    elev_e=Label(frame15,text="Elev En",font=("Calibri", 11,"bold"),bg=bg_color)
    elev_e.grid(row=11, column=0)
    elev_e=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    elev_e.grid(column=1,row=11,pady=2,padx=2)
   
    rst_flag=Label(frame15,text="Rst_flag",font=("Calibri", 11,"bold"),bg=bg_color)
    rst_flag.grid(row=12, column=0)
    rst_flag=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    rst_flag.grid(column=1,row=12,pady=2,padx=2)
    
    odp_rst_sf=Label(frame15,text="ODP Rst SF",font=("Calibri", 11,"bold"),bg=bg_color)
    odp_rst_sf.grid(row=13, column=0)
    odp_rst_sf=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    odp_rst_sf.grid(column=1,row=13,pady=2,padx=2)
    
    cold_vis=Label(frame15,text="Cold Vis",font=("Calibri", 11,"bold"),bg=bg_color)
    cold_vis.grid(row=14, column=0)
    cold_vis=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    cold_vis.grid(column=1,row=14,pady=2,padx=2)
    
    nav_msg_e=Label(frame15,text="Nav Msg En",font=("Calibri", 11,"bold"),bg=bg_color)
    nav_msg_e.grid(row=15, column=0)
    nav_msg_e=Entry(frame15,width=12,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color)
    nav_msg_e.grid(column=1,row=15,pady=2,padx=2)
    
    # ====================== GAGAN-SA3W31MSB ==============================
    frame15=LabelFrame(parent_frame,text=f"GAGAN-SA3W31MSB({rt_name})",bg=bg_color,
    fg="dark red",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame15.grid(row=1,column=2,padx=2,pady=2,sticky="nsew")
   
    odp_est=Label(frame15,text="ODP_Est",font=("Calibri", 11,"bold"),bg=bg_color)
    odp_est.grid(row=0, column=0)
    odp_est=Entry(frame15,width=5,state="readonly",font=("Calibri", 11,"bold"),bg='light grey',fg="black")
    odp_est.grid(column=1,row=0,pady=2,padx=2)
   
    odp_en=Label(frame15,text="ODP_EN",font=("Calibri", 11,"bold"),bg=bg_color)
    odp_en.grid(row=1, column=0)
    odp_en=Entry(frame15,width=5,state="readonly",font=("Calibri", 11,"bold"),bg='light grey',fg="black")   
    odp_en.grid(column=1,row=1,pady=2,padx=2)
   
    phc_usg=Label(frame15,text="PHCUsg",font=("Calibri", 11,"bold"),bg=bg_color)
    phc_usg.grid(row=2, column=0)
    phc_usg=Entry(frame15,width=5,state="readonly",font=("Calibri", 11,"bold"),bg='light grey',fg="black")
    phc_usg.grid(column=1,row=2,pady=2,padx=2)
   
    phc_en=Label(frame15,text="PHC En",font=("Calibri", 11,"bold"),bg=bg_color)
    phc_en.grid(row=3, column=0)
    phc_en=Entry(frame15,width=5,state="readonly",font=("Calibri", 11,"bold"),bg='light grey',fg="black")
    phc_en.grid(column=1,row=3,pady=2,padx=2)
   
    eph_rt=Label(frame15,text="Eph RT",font=("Calibri", 11,"bold"),bg=bg_color)
    eph_rt.grid(row=0, column=2)
    eph_rt=Entry(frame15,width=5,state="readonly",font=("Calibri", 11,"bold"),bg='light grey',fg="black")
    eph_rt.grid(column=3,row=0,pady=2,padx=2)
   
    mnvon=Label(frame15,text="MNVON",font=("Calibri", 11,"bold"),bg=bg_color)
    mnvon.grid(row=1, column=2)
    mnvon=Entry(frame15,width=5,state="readonly",font=("Calibri", 11,"bold"),bg='light grey',fg="black")
    mnvon.grid(column=3,row=1,pady=2,padx=2)
   
    numsps=Label(frame15,text="NumSPS",font=("Calibri", 11,"bold"),bg=bg_color)
    numsps.grid(row=2, column=2)
    numsps=Entry(frame15,width=5,state="readonly",font=("Calibri", 11,"bold"),bg='light grey',fg="black")
    numsps.grid(column=3,row=2,pady=2,padx=2)
    
    
    # ========================== GRAPH ============================
    frame_cndr_plot = tk.LabelFrame(parent_frame, text=f"CNDR VS SVID PLOT({rt_name})",bg=bg_color,
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
    
    
    
   
    
    # Continue with other frames similarly...
    # Note: Due to length, I'm showing the pattern. You would continue creating all the widgets
    # for each RT similar to your original code but using the rt_name parameter
    
    # Store references to widgets
    if rt_name == "RT1":
        rt1_widgets.update({
            'update_entry': update_entry,'sw_rst_c': sw_rst_c,'hw_rst_c': hw_rst_c,'tsm_counter_entry': tsm_counter_entry,
            'week_entry': week_entry,'time_entry': time_entry,'nanotime_entry': nanotime_entry,
            'week_entry1': week_entry1,'time_entry1': time_entry1,'nanotime_entry1': nanotime_entry1,
            'week_entry2': week_entry2,'time_entry2': time_entry2,'nanotime_entry2': nanotime_entry2,
            'pdop':pdop,'no_sat_trck':no_sat_trck, 'csm1':csm1, 'csm2':csm2, 'fix_3d': fix_3d,'leap': leap,
            'acq1': acq1,'acq2': acq2,'acq3': acq3,'acq4': acq4,
            'port_conf':port_conf,'port_conf1':port_conf1, 'port_conf2':port_conf2, 'port_conf3':port_conf3,
            'position_entry':position_entry, 'position_entry1':position_entry1, 'position_entry2':position_entry2,
            'position_entry3':position_entry3,'position_entry4':position_entry4,'position_entry5':position_entry5,
            'velocity_entry':velocity_entry, 'velocity_entry1':velocity_entry1, 'velocity_entry2':velocity_entry2,
            'velocity_entry3':velocity_entry3,'velocity_entry4':velocity_entry4,  'velocity_entry5':velocity_entry5,
            'tm':tm, 'swdt':swdt, 'hwdt':hwdt,'sbasen':sbasen,'sys_mode':sys_mode, 'rec_mode':rec_mode,'time_mode':time_mode,
            'alm_av':alm_av,'time_av':time_av,'pos_mode':pos_mode,'pos_av':pos_av,'cb':cb,'isb':isb,
            'drift':drift,'isd':isd,'sw_rst_c':sw_rst_c,'hw_rst_c':hw_rst_c,'sw_rst_id':sw_rst_id,
            'sol_mode':sol_mode,'sps_id':sps_id, 'navic_msg_22_c':navic_msg_22_c,'navic_msg_cmd_c':navic_msg_cmd_c,
            'leo_sat_id':leo_sat_id,'odp_est':odp_est,'odp_en':odp_en,'phc_usg':phc_usg,
            'phc_en':phc_en,'eph_rt':eph_rt,'mnvon':mnvon,'numsps':numsps,'navic_cmd_var':navic_cmd_var,
            'rt_id':rt_id,'s_id':s_id,'last_cmd_exe':last_cmd_exe,'last_reset_time':last_reset_time,
            'dual_cmd_c_rt':dual_cmd_c_rt,'spu_cmd_c_rt':spu_cmd_c_rt,'cmd_based_rt':cmd_based_rt,
            'total_cmd_counter':total_cmd_counter,'nrff_rst_counter1':nrff_rst_counter1,'nrff_rst_counter2':nrff_rst_counter2,
            'grff_rst_counter1':grff_rst_counter1,'grff_rst_counter2':grff_rst_counter2,'grff_rst_counter3':grff_rst_counter3,'grff_rst_counter4':grff_rst_counter4,
            'miss_ph':miss_ph,'fmem':fmem,'cr_aid':cr_aid,'full_cntr':full_cntr,'s_id':s_id,'lig_1':lig_1,'lig_2':lig_2,'lig_3':lig_3,'lig_4':lig_1,
            'lin_1':lin_1,'lin_2':lin_2,'prime_ngc':prime_ngc,'rng_l':rng_l,'orbit_phase':orbit_phase,'iono_c':iono_c,'iono_sm':iono_sm,'cr_smo':cr_smo,
            'vel_sm':vel_sm,'raim':raim,'pr_rej':pr_rej,'pr_bf_sync':pr_bf_sync,'cfg_loop':cfg_loop,'int_crd_tst':int_crd_tst,'elev_e':elev_e,
            'rst_flag':rst_flag,'odp_rst_sf':odp_rst_sf,'cold_vis':cold_vis,'nav_msg_e':nav_msg_e,
            'svid_entries':svid_entries,'cndr_entries':cndr_entries,'iode_entries':iode_entries,'pr_entries':pr_entries,
            'dr_entries':dr_entries,'elev_entries':elev_entries,'bit_to_entrylist':bit_to_entrylist,
        
            
            
           
            
        })
    elif rt_name == "RT2":
        rt2_widgets.update({
           'update_entry': update_entry,'sw_rst_c': sw_rst_c,'hw_rst_c': hw_rst_c,'tsm_counter_entry': tsm_counter_entry,
            'week_entry': week_entry,'time_entry': time_entry,'nanotime_entry': nanotime_entry,
            'week_entry1': week_entry1,'time_entry1': time_entry1,'nanotime_entry1': nanotime_entry1,
            'week_entry2': week_entry2,'time_entry2': time_entry2,'nanotime_entry2': nanotime_entry2,
            'pdop':pdop,'no_sat_trck':no_sat_trck, 'csm1':csm1, 'csm2':csm2, 'fix_3d': fix_3d,'leap': leap,
            'acq1': acq1,'acq2': acq2,'acq3': acq3,'acq4': acq4,
            'port_conf':port_conf,'port_conf1':port_conf1, 'port_conf2':port_conf2, 'port_conf3':port_conf3,
            'position_entry':position_entry, 'position_entry1':position_entry1, 'position_entry2':position_entry2,
            'position_entry3':position_entry3,'position_entry4':position_entry4,'position_entry5':position_entry5,
            'velocity_entry':velocity_entry, 'velocity_entry1':velocity_entry1, 'velocity_entry2':velocity_entry2,
            'velocity_entry3':velocity_entry3,'velocity_entry4':velocity_entry4,  'velocity_entry5':velocity_entry5,
            'tm':tm, 'swdt':swdt, 'hwdt':hwdt,'sbasen':sbasen,'sys_mode':sys_mode, 'rec_mode':rec_mode,'time_mode':time_mode,
            'alm_av':alm_av,'time_av':time_av,'pos_mode':pos_mode,'pos_av':pos_av,'cb':cb,'isb':isb,
            'drift':drift,'isd':isd,'sw_rst_c':sw_rst_c,'hw_rst_c':hw_rst_c,'sw_rst_id':sw_rst_id,
            'sol_mode':sol_mode,'sps_id':sps_id, 'navic_msg_22_c':navic_msg_22_c,'navic_msg_cmd_c':navic_msg_cmd_c,
            'leo_sat_id':leo_sat_id,'odp_est':odp_est,'odp_en':odp_en,'phc_usg':phc_usg,
            'phc_en':phc_en,'eph_rt':eph_rt,'mnvon':mnvon,'numsps':numsps,'navic_cmd_var':navic_cmd_var,
            'rt_id':rt_id,'s_id':s_id,'last_cmd_exe':last_cmd_exe,'last_reset_time':last_reset_time,
             'dual_cmd_c_rt':dual_cmd_c_rt,'spu_cmd_c_rt':spu_cmd_c_rt,'cmd_based_rt':cmd_based_rt,
             'total_cmd_counter':total_cmd_counter,'nrff_rst_counter1':nrff_rst_counter1,'nrff_rst_counter2':nrff_rst_counter2,
            'grff_rst_counter1':grff_rst_counter1,'grff_rst_counter2':grff_rst_counter2,'grff_rst_counter3':grff_rst_counter3,'grff_rst_counter4':grff_rst_counter4,
             'miss_ph':miss_ph,'fmem':fmem,'cr_aid':cr_aid,'full_cntr':full_cntr,'s_id':s_id,'lig_1':lig_1,'lig_2':lig_2,'lig_3':lig_3,'lig_4':lig_1,
            'lin_1':lin_1,'lin_2':lin_2,'prime_ngc':prime_ngc,'rng_l':rng_l,'orbit_phase':orbit_phase,'iono_c':iono_c,'iono_sm':iono_sm,'cr_smo':cr_smo,
            'vel_sm':vel_sm,'raim':raim,'pr_rej':pr_rej,'pr_bf_sync':pr_bf_sync,'cfg_loop':cfg_loop,'int_crd_tst':int_crd_tst,'elev_e':elev_e,
            'rst_flag':rst_flag,'odp_rst_sf':odp_rst_sf,'cold_vis':cold_vis,'nav_msg_e':nav_msg_e,
            'svid_entries':svid_entries,'cndr_entries':cndr_entries,'iode_entries':iode_entries,'pr_entries':pr_entries,
            'dr_entries':dr_entries,'elev_entries':elev_entries,'bit_to_entrylist':bit_to_entrylist,
            
            
        })
    elif rt_name == "RT3":
        rt3_widgets.update({
           'update_entry': update_entry,'sw_rst_c': sw_rst_c,'hw_rst_c': hw_rst_c,'tsm_counter_entry': tsm_counter_entry,
            'week_entry': week_entry,'time_entry': time_entry,'nanotime_entry': nanotime_entry,
            'week_entry1': week_entry1,'time_entry1': time_entry1,'nanotime_entry1': nanotime_entry1,
            'week_entry2': week_entry2,'time_entry2': time_entry2,'nanotime_entry2': nanotime_entry2,
            'pdop':pdop,'no_sat_trck':no_sat_trck, 'csm1':csm1, 'csm2':csm2, 'fix_3d': fix_3d,'leap': leap,
            'acq1': acq1,'acq2': acq2,'acq3': acq3,'acq4': acq4,
            'port_conf':port_conf,'port_conf1':port_conf1, 'port_conf2':port_conf2, 'port_conf3':port_conf3,
            'position_entry':position_entry, 'position_entry1':position_entry1, 'position_entry2':position_entry2,
            'position_entry3':position_entry3,'position_entry4':position_entry4,'position_entry5':position_entry5,
            'velocity_entry':velocity_entry, 'velocity_entry1':velocity_entry1, 'velocity_entry2':velocity_entry2,
            'velocity_entry3':velocity_entry3,'velocity_entry4':velocity_entry4,  'velocity_entry5':velocity_entry5,
            'tm':tm, 'swdt':swdt, 'hwdt':hwdt,'sbasen':sbasen,'sys_mode':sys_mode, 'rec_mode':rec_mode,'time_mode':time_mode,
            'alm_av':alm_av,'time_av':time_av,'pos_mode':pos_mode,'pos_av':pos_av,'cb':cb,'isb':isb,
            'drift':drift,'isd':isd,'sw_rst_c':sw_rst_c,'hw_rst_c':hw_rst_c,'sw_rst_id':sw_rst_id,
            'sol_mode':sol_mode,'sps_id':sps_id, 'navic_msg_22_c':navic_msg_22_c,'navic_msg_cmd_c':navic_msg_cmd_c,
            'leo_sat_id':leo_sat_id,'odp_est':odp_est,'odp_en':odp_en,'phc_usg':phc_usg,
            'phc_en':phc_en,'eph_rt':eph_rt,'mnvon':mnvon,'numsps':numsps,'navic_cmd_var':navic_cmd_var,
            'rt_id':rt_id,'s_id':s_id,'last_cmd_exe':last_cmd_exe,'last_reset_time':last_reset_time,
             'dual_cmd_c_rt':dual_cmd_c_rt,'spu_cmd_c_rt':spu_cmd_c_rt,'cmd_based_rt':cmd_based_rt,
             'total_cmd_counter':total_cmd_counter,'nrff_rst_counter1':nrff_rst_counter1,'nrff_rst_counter2':nrff_rst_counter2,
            'grff_rst_counter1':grff_rst_counter1,'grff_rst_counter2':grff_rst_counter2,'grff_rst_counter3':grff_rst_counter3,'grff_rst_counter4':grff_rst_counter4,
             'miss_ph':miss_ph,'fmem':fmem,'cr_aid':cr_aid,'full_cntr':full_cntr,'s_id':s_id,'lig_1':lig_1,'lig_2':lig_2,'lig_3':lig_3,'lig_4':lig_1,
            'lin_1':lin_1,'lin_2':lin_2,'prime_ngc':prime_ngc,'rng_l':rng_l,'orbit_phase':orbit_phase,'iono_c':iono_c,'iono_sm':iono_sm,'cr_smo':cr_smo,
            'vel_sm':vel_sm,'raim':raim,'pr_rej':pr_rej,'pr_bf_sync':pr_bf_sync,'cfg_loop':cfg_loop,'int_crd_tst':int_crd_tst,'elev_e':elev_e,
            'rst_flag':rst_flag,'odp_rst_sf':odp_rst_sf,'cold_vis':cold_vis,'nav_msg_e':nav_msg_e,
            'svid_entries':svid_entries,'cndr_entries':cndr_entries,'iode_entries':iode_entries,'pr_entries':pr_entries,
            'dr_entries':dr_entries,'elev_entries':elev_entries,'bit_to_entrylist':bit_to_entrylist,
           
        })

def store_rt_widgets(rt_name):
    """Store widget references for each RT"""
    # This function would store all widget references for the RT
    # Implementation depends on how you create and name widgets
    pass

def update_project_name(project_name_var, header_label):
    input_name = project_name_var.get().strip()

    # Use "GAGANYAN" if empty or equal to GAGANYAN (case-insensitive)
    if not input_name or input_name.lower() == "gaganyaan":
        display_name = "GAGANYAAN"
    else:
        display_name = input_name.upper()

    header_label.config(text=f"SPS TELEMETRY AND COMMAND INTERFACE: {display_name}")

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
    clicked_bd.set("115200")
    drop_bd = OptionMenu(frame1, clicked_bd, *bds, command=connect_check)
    drop_bd.config(height=1,width=10,font=("Calibri", 12),bg="burlywood")
    drop_bd.grid(column=4, row=1, padx=2)
    
def update_coms():
    global clicked_com,drop_COM, frame1
    ports=serial.tools.list_ports.comports()
    coms=[com[0] for com in ports]
    coms.insert(0,"-")
    try:
        drop_COM.destroy()
    except:
        pass
    clicked_com=StringVar()
    clicked_com.set(coms[0])
    drop_COM=OptionMenu(frame1, clicked_com, *coms, command=connect_check)
    drop_COM.config(height=1,width=10,font=("Calibri", 12),bg="burlywood")
    drop_COM.grid(column=1,row=1,padx=2)
    connect_check(0)
   
def reverse_and_concatenate(hex_list, scale=1 ,is_signed=False):
    # Ensure the length of hex_list is valid for conversion
    if len(hex_list) in [1, 2, 3, 4, 8]:
        if len(hex_list) == 1:
            concatenated_hex = ''.join(hex_list)
            decimal_value = int(concatenated_hex, 16)
        elif len(hex_list) == 2:
            concatenated_hex = ''.join(hex_list)
            decimal_value = int(concatenated_hex, 16)
           
        elif len(hex_list) == 3:
            concatenated_hex = ''.join(hex_list)
            decimal_value = int(concatenated_hex, 16)
       
        elif len(hex_list) == 4:
            first_half = ''.join(hex_list[:2])
            second_half = ''.join(hex_list[2:])
            concatenated_hex = second_half + first_half
            decimal_value = int(concatenated_hex, 16)
 
        elif len(hex_list) == 8:
            first_half = ''.join(hex_list[:4])
            second_half = ''.join(hex_list[4:])
            reversed_first_half = first_half[6:8] + first_half[4:6] + first_half[2:4] + first_half[0:2]
            reversed_second_half = second_half[6:8] + second_half[4:6] + second_half[2:4] + second_half[0:2]
            concatenated_hex = reversed_first_half + reversed_second_half
            decimal_value = int(concatenated_hex, 16)
 
        # Handle signed values
        if is_signed:
            if decimal_value >= 0x80000000:
                decimal_value -= 0x100000000  # Adjust for signed value
 
        return decimal_value
 
    return None
 
def decode_channel_status_meaning(status_word):
    """
    Decodes a 16-bit channel status word according to the custom mapping:
    T   - Bits 0+1: Track/Bit Sync (00=A, 01=T, 10=N, 11=S)
    E   - Bit 2: Ephemeris Av
    P   - Bit 3: Used in Pos
    I   - Bit 4: Iono Correction Av
    S   - Bit 5: SBAS Correction Av
    P1  - Bit 6: PR Validity Reject
    H   - Bit 7: URA/Health
    A   - Bits 8+9: Antenna select (00=A1, 01=A2, 10=A3, 11=A4)
    SR  - Bit 10: SBAS Reject
    R   - Bit 11: RAIM Reject
    E1  - Bit 12: L1/L2 Ephem Indicator
    D   - Bit 14: DR Status (0=Y, 1=N)
    """
    # Track/Bit Sync decoding using bits 0 and 1
    sync_bits = (status_word & 0x0003)  # mask bits 0 and 1
    sync_map = {
        0b00: "A",  # Acquisition
        0b01: "T",  # Tracking
        0b10: "N",  # No Sync
        0b11: "S",  # Sync
    }

    # Antenna Select decoding using bits 8 and 9
    antenna_bits = (status_word  & 0x0300 ) >> 8  # mask bits 8 and 9
    antenna_map = {
        0b00: "1",
        0b01: "2",
        0b10: "3",
        0b11: "4",
    }
    
   # Extract individual bits
    bits = [(status_word >> i) & 1 for i in range(16)]
    
    #print(f"Sync_bit:{sync_bits}")
    #print(f"Sync_map:{sync_map}")
    #print(f"Ant_bit:{antenna_bits}")
    #print(f"Ant_map:{antenna_map}")

    return {
        "TRK": sync_map.get(sync_bits, "UK"),
        "EPH": "AVL" if bits[2]==0 else "NO", # if bit[2]==1 AVL else bit[2]==0 NAV
        "POS": "USE" if bits[3]==0 else "NO",
        "INO": "AVL" if bits[4]==0 else "NO",
        "SBC": "AVL" if bits[5]==0 else "NO",
        "PR": "Rej" if bits[6]==0 else "Pas",
        "URA": "Bad" if bits[7]==0 else "Gd",
        "ANT": antenna_map.get(antenna_bits, "UK"),
        "SBR": "Rej" if bits[10]==0 else "Pas",
        "RIM": "Rej" if bits[11]==0 else "Pas",
        "UR5": "NOK" if bits[12]==0 else "OK",
        "DR": "Av" if bits[14]==0 else "NAv",
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
        #widgets['csm1'].config(fg="dark green")
        #csm1.config(fg="dark green")
    else:
        checksum1 =  "Fail"
        #widgets['csm1'].config(fg="dark red")
        #csm1.config(fg="dark red")
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
    #print(f"Expected_cksm:{exepected_checksum}")
    #print(f"checksum2:{Checksum2}")
    
    if exepected_checksum == Checksum2:
        
        checksum2 = "Pass"
       # widgets['csm2'].config(fg="dark green")
        #csm2.config(fg="dark green")
    else:
        checksum2 =  "Fail"
        #csm2.config(fg="dark red")
       # widgets['csm2'].config(fg="dark red")
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
    
    

def send_general_command(data_str, cmd_type):
    global sa3_thread, sa3_running, sa4_thread, sa4_running

    if not (ser and ser.is_open):
        status_var.set("❌ Serial port not open.")
        return

    if cmd_type in ("SA3", "SA4"):
        filepath = file_entries[cmd_type].get()
        if not filepath or not os.path.exists(filepath):
            status_var.set(f"❌ Please select a valid file for {cmd_type} commands.")
            return

        if cmd_type == "SA3":
            if sa3_thread and sa3_thread.is_alive():
                status_var.set("❌ SA3 sending already running!")
                return
            sa3_running = True
            sa3_thread = threading.Thread(target=send_sax_from_file, args=(filepath, 0.064, cmd_type), daemon=True)
            sa3_thread.start()
            status_var.set("▶️ SA3 sending started.")
        else:  # SA4
            if sa4_thread and sa4_thread.is_alive():
                status_var.set("❌ SA4 sending already running!")
                return
            sa4_running = True
            sa4_thread = threading.Thread(target=send_sax_from_file, args=(filepath, 1.0, cmd_type), daemon=True)
            sa4_thread.start()
            status_var.set("▶️ SA4 sending started.")
        return

    # SA1 and SA2 manual send
    try:
        parts = data_str.strip().split()
        if len(parts) != 3:
            status_var.set("❌ Enter exactly 3 words (e.g. 0x0000 0x0004 0x0055)")
            return

        words = [int(word, 16) for word in parts]

        if cmd_type == "SA1":
            header = [0xAC, 0xCA, 0x1F, 0x01]
        elif cmd_type == "SA2":
            header = [0xAC, 0xCA, 0x1F, 0x02]
        else:
            status_var.set("❌ Unknown subaddress type!")
            return

        data_bytes = [b for word in words for b in word.to_bytes(2, byteorder='big')]
        full_packet = header + data_bytes

        ser.write(bytes(full_packet))
        sent_str = f"Manual {cmd_type} command sent: {[f'0x{b:02X}' for b in full_packet]}"
        status_var.set(f"✅ {sent_str}")
        print(sent_str)
        with open("(SA1-SA4)command_log.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | MANUAL {cmd_type} | {sent_str}\n")

    except ValueError:
        status_var.set("❌ Invalid hex format. Use e.g. 0x0000 0x0004 0x0055")
    except Exception as e:
        status_var.set(f"❌ Error sending manual command: {e}")

def send_sax_from_file(filepath, interval, cmd_type):
    global sa3_running, sa4_running

    try:
        with open(filepath, 'rb') as f:
            raw = f.read()

        try:
            as_text = raw.decode('ascii')
            hexstr = ''.join(c for c in as_text if c in '0123456789abcdefABCDEF')
            file_bytes = bytes.fromhex(hexstr)
        except Exception:
            file_bytes = raw

        if len(file_bytes) < 64:
            status_var.set(f"❌ File must contain at least 64 bytes of data for {cmd_type}.")
            if cmd_type == "SA3":
                sa3_running = False
            else:
                sa4_running = False
            return

        header = [0xAC, 0xCA, 0x1F, 0x03] if cmd_type == "SA3" else [0xAC, 0xCA, 0x1F, 0x04]
        num_blocks = len(file_bytes) // 64

        idx = 0

        while (sa3_running if cmd_type == "SA3" else sa4_running) and ser and ser.is_open:
            start = idx * 64
            end = start + 64
            if end > len(file_bytes):
                if cmd_type == "SA3":
                    sa3_running = False
                else:
                    sa4_running = False
                status_var.set(f"⏹️ {cmd_type} sending finished.")
                break

            chunk = file_bytes[start:end]
            packet = bytes(header) + chunk
            ser.write(packet)

            sent_str = f"{cmd_type} packet sent (block {idx+1}/{num_blocks}): {[f'0x{b:02X}' for b in packet]}"
            status_var.set(f"✅ {sent_str}")
            print(sent_str)
            with open("(SA1-SA4)command_log.txt", "a") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {cmd_type} | {sent_str}\n")

            idx += 1
            for _ in range(int(interval * 1000 / 10)):
                if not (sa3_running if cmd_type == "SA3" else sa4_running):
                    status_var.set(f"⏹️ {cmd_type} sending stopped.")
                    return
                cmdtime.sleep(0.01)

    except Exception as e:
        status_var.set(f"❌ Error in {cmd_type} send: {e}")
        if cmd_type == "SA3":
            sa3_running = False
        else:
            sa4_running = False
            
def stop_sa3():
    global sa3_running
    if sa3_running:
        sa3_running = False
        status_var.set("⏹️ Stopping SA3 sending...")

def stop_sa4():
    global sa4_running
    if sa4_running:
        sa4_running = False
        status_var.set("⏹️ Stopping SA4 sending...")
 
 
def on_bus_toggle(*args):
    try:
        if not (ser and ser.is_open):
            status_var.set("❌ Serial port not open.")
            return
        if bus_var.get() not in ["A", "B"]:
            return
        header = [0xAC, 0xCA, 0x1F, 0x0B]
        rt_address = 0x00
        bus_val = 0x78 if bus_var.get() == "A" else 0x77
        packet = header + [rt_address, bus_val]
        bus_name = "BUS A" if bus_val == 0x78 else "BUS B"
        ser.write(bytes(packet))
        sent_str = f"Packet for toggle: {[f'0x{b:02X}' for b in packet]} ({bus_name})"
        status_var.set(sent_str)
        with open("Buscmd.txt", "a") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | BUS_TOGGLE | {sent_str}\n")
    except Exception as e:
        status_var.set(f"❌ Error sending bus command (button): {e}")
            
def send_bus_command_button(cmd_value=None):
    """
    For preset bus command buttons: HEADER + RT Address (0x00) + Dataword
    """
    try:
        if not (ser and ser.is_open):
            status_var.set("❌ Serial port not open.")
            return
        rt_address = 0x00  # always 0x00 for buttons
        if cmd_value is not None:
            data_word = cmd_value
            cmd_name = [k for k, v in bus_commands if v == cmd_value][0]
        else:
            status_var.set("❌ Command value not provided.")
            return
        header = [0xAC, 0xCA, 0x1F, 0x0B]
        packet = header + [rt_address, data_word]
        ser.write(bytes(packet))
        sent_str = f"Sent (Button): {[f'0x{b:02X}' for b in packet]}  ({cmd_name}, RT=0x00, Data=0x{data_word:02X})"
        status_var.set(f"✅ {sent_str}")
        print(sent_str)
        with open("Buscmd.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | BUSCMD_BTN | {sent_str}\n")
    except Exception as e:
        status_var.set(f"❌ Error sending bus command (button): {e}")
 
def send_bus_command_entry():
    """
    For manual entry: HEADER + Entered Dataword + RT Address (0xCE)
    """
    try:
        if not (ser and ser.is_open):
            status_var.set("❌ Serial port not open.")
            return
        rt_address = 0xCE  # always 0xCE for entry/manual
        dataword_str = dataword_entry.get().strip()
        if dataword_str.lower().startswith("0x"):
            data_word = int(dataword_str, 16)
        else:
            data_word = int(dataword_str, 16) if all(c in "0123456789abcdefABCDEF" for c in dataword_str) else int(dataword_str)
        if not (0 <= data_word <= 0xFF):
            status_var.set("❌ Data word must be 1 byte (00-FF)")
            return
        header = [0xAC, 0xCA, 0x1F, 0x0B]
        packet = header + [data_word, rt_address]
        sent_str = f"Sent (Entry): {[f'0x{b:02X}' for b in packet]}  (Manual Data=0x{data_word:02X}, RT=0xCE)"
        ser.write(bytes(packet))
        status_var.set(f"✅ {sent_str}")
        print(sent_str)
        with open("Buscmd.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | BUSCMD_ENTRY | {sent_str}\n")
    except Exception as e:
        status_var.set(f"❌ Error sending bus command (entry): {e}")


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
     

def update_cndr_plot_func(svid_labels, cndr_values):
    colors = []
    for val in cndr_values:
        if 0 <= val < 20:
            colors.append("ORANGE")  # low range
        elif 20 <= val <= 40:
            colors.append("RED")   # Mid range
        elif 40 <= val <= 60:
            colors.append("BLUE")   # High range
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
        parent_frame.update_idletasks()  # make sure entries are updated

        CNDR_values = [
            float(cndr1.get() or 0), float(cndr2.get() or 0), float(cndr3.get() or 0), float(cndr4.get() or 0),
            float(cndr5.get() or 0), float(cndr6.get() or 0), float(cndr7.get() or 0), float(cndr8.get() or 0),
            float(cndr9.get() or 0), float(cndr10.get() or 0), float(cndr11.get() or 0), float(cndr12.get() or 0),
            float(cndr13.get() or 0), float(cndr14.get() or 0),float(cndr15.get() or 0), float(cndr16.get() or 0), 
            float(cndr17.get() or 0), float(cndr18.get() or 0),
        ]

        SVID_values = [
            svid1.get() or "CH1", svid2.get() or "CH2", svid3.get() or "CH3", svid4.get() or "CH4",
            svid5.get() or "CH5", svid6.get() or "CH6", svid7.get() or "CH7", svid8.get() or "CH8",
            svid9.get() or "CH9", svid10.get() or "CH10", svid11.get() or "CH11", svid12.get() or "CH12",
            svid13.get() or "CH13", svid14.get() or "CH14", svid15.get() or "CH15", svid16.get() or "CH16",
             svid17.get() or "CH17", svid18.get() or "CH18",
        ]

        update_cndr_plot_func(SVID_values, CNDR_values)

    except Exception as e:
        print("CNDR plot update error:", e)

def readSerial():
    global serialData, ser, hexDecodedData
    

    # Define headers for all RTs
    headers = {
        "RT1_A": ["ac", "ca", "1f", "0a"],  # 1200 bytes
        "RT1_B": ["ac", "ca", "1f", "0b"],  # 64 bytes
        "RT2_C": ["ac", "ca", "1f", "0c"],  # 1200 bytes
        "RT2_D": ["ac", "ca", "1f", "0d"],  # 64 bytes
        "RT3_E": ["ac", "ca", "1f", "0e"],  # 1200 bytes
        "RT3_F": ["ac", "ca", "1f", "0f"],  # 64 bytes
    }

    # Track header matching progress
    header_indices = {key: 0 for key in headers.keys()}

    try:
        while serialData:
            if ser.in_waiting > 0:
                byte = ser.read(1).hex()

                # Check all headers
                for header_name, header_bytes in headers.items():

                    # Matching next expected byte
                    if byte == header_bytes[header_indices[header_name]]:
                        header_indices[header_name] += 1

                        # Full header matched
                        if header_indices[header_name] == len(header_bytes):
                            print(f"\n{header_name} FOUND")

                            # Determine packet size
                            if header_name.endswith(("A", "C", "E")):
                                data_length = 1200
                            else:
                                data_length = 60

                            # Read full packet
                            payload = ser.read(data_length).hex()
                            hexDecodedData = ''.join(header_bytes) + payload

                            # ✅ Print full raw data
                            print(hexDecodedData.upper())
                            print()

                            # Determine RT group
                            if header_name.startswith("RT1"):
                                rt_name = "RT1"
                                #counter_value += 1
                            elif header_name.startswith("RT2"):
                                rt_name = "RT2"

                                #counter_value2 += 1
                            else:
                                rt_name = "RT3"
                                #counter_value3 += 1

                            # Push to queue
                            data_queue.put((rt_name, hexDecodedData))

                            # Reset header index
                            header_indices[header_name] = 0

                    else:
                        # Restart header search if mismatch
                        if byte == "ac":
                            header_indices[header_name] = 1
                        else:
                            header_indices[header_name] = 0

            time.sleep(0.001)

    except KeyboardInterrupt:
        print("Reading from serial port stopped")

       

 
def process_data():
    global base_name,filename
    try:
        while True:
            item = data_queue.get()
            if not item:
                continue
            rt_name, hexDecodedData = item
            
            # Process based on which RT the data belongs to
            if rt_name == "RT1":
                # Process RT1 data and update RT1 widgets
                process_rt_data(hexDecodedData, "RT1")
            elif rt_name == "RT2":
                # Process RT2 data and update RT2 widgets
                process_rt_data(hexDecodedData, "RT2")
            elif rt_name == "RT3":
                # Process RT3 data and update RT3 widgets
                process_rt_data(hexDecodedData, "RT3")
                
    except Exception as e:
        print(f"Error processing data: {e}")
    finally:
        ptime.sleep(0.001)

def process_rt_data(hexDecodedData, rt_name):
    """Process data for a specific RT and update its widgets"""
    try:
        # Detect header from first 4 bytes
        header = [hexDecodedData[i:i+2] for i in range(0, 8, 2)]

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
            #counter_var = counter_value
        elif rt_name == "RT2":
            widgets = rt2_widgets
            #counter_var = counter_value2
        elif rt_name == "RT3":
            widgets = rt3_widgets
            #counter_var = counter_value3
        else:
            print("Unknown RT Name")
            return

        # Current timestamp for file writes
        #current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Branch depending on header type
        if header_key.endswith(("A", "C", "E")):
            #header_length = 10
            #Raw_data = ' '.join([hexDecodedData[i:i+2]for i in range(header_length,len(hexDecodedData),2)])
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
            word20 = reverse_and_concatenate(word20_hex)
            flag = extract_word20_flags(word20)
            #print(flags)
           
 
 
           
            Bais_hex=hexDecodedData[220:228]
            ISB_hex = hexDecodedData[228:232]
            DRIFT_hex = hexDecodedData[232:240]
            ISD_hex=hexDecodedData[240:244]
            HW__SW_reset_counter_hex=hexDecodedData[244:248]
           
            word28_hex = hexDecodedData[248:252]   
            word28 = reverse_and_concatenate(word28_hex)
            flag1 = extract_word28LSB_flags(word28)
            #print(flags)
           
            
            Navic_msg_counter_hex=hexDecodedData[252:256]
            
            
            word30_hex=hexDecodedData[256:260]
            
            
            word31_hex = hexDecodedData[260:264]   
            word31 = reverse_and_concatenate(word31_hex)
            flag3 = extract_sps3word31LSB_flags(word31)
            
            
            
            
            csm2_hex=hexDecodedData[264:268]   
            Checksum2=reverse_and_concatenate(csm2_hex)
            SA4chechsum_calulation_covert_decimal(SYS_NanoSecond_hex,SYS_Second_hex,SYS_Weeknumber_hex,POS_X_hex,POS_Y_hex,POS_Z_hex,POS_Vx_hex,POS_Vy_hex,POS_Vz_hex,UpdateCounter_hex,PDOP_hex ,word20_hex ,Bais_hex ,ISB_hex ,DRIFT_hex ,ISD_hex ,HW__SW_reset_counter_hex,word28_hex,Navic_msg_counter_hex,word30_hex,word31_hex,Checksum2)
           
           
   
   
           
                # SVID values
            SVID_hex = [
                hexDecodedData[270:272],    # 1
                hexDecodedData[268:270],    # 2
                hexDecodedData[274:276],    # 3
                hexDecodedData[272:274],    # 4
                hexDecodedData[278:280],    # 5
                hexDecodedData[276:278],    # 6
                hexDecodedData[282:284],    # 7
                hexDecodedData[280:282],    # 8
                hexDecodedData[286:288],    # 9
                hexDecodedData[284:286],    # 10
                hexDecodedData[290:292],    # 11
                hexDecodedData[288:290],    # 12
                hexDecodedData[294:296],    # 13
                hexDecodedData[292:294],    # 14
                hexDecodedData[298:300],    # 15
                hexDecodedData[296:298],    # 16
                hexDecodedData[1166:1168],  # 17
                hexDecodedData[1164:1166]   # 18
            ]
            
            # IODE values
            IODE_hex = [
                hexDecodedData[302:304],    # 1
                hexDecodedData[300:302],    # 2
                hexDecodedData[306:308],    # 3
                hexDecodedData[304:306],    # 4
                hexDecodedData[310:312],    # 5
                hexDecodedData[308:310],    # 6
                hexDecodedData[314:316],    # 7
                hexDecodedData[312:314],    # 8
                hexDecodedData[318:320],    # 9
                hexDecodedData[316:318],    # 10
                hexDecodedData[322:324],    # 11
                hexDecodedData[320:322],    # 12
                hexDecodedData[326:328],    # 13
                hexDecodedData[324:326],    # 14
                hexDecodedData[330:332],    # 15
                hexDecodedData[328:330],    # 16
                hexDecodedData[1170:1172],  # 17
                hexDecodedData[1168:1170]   # 18
            ]
            
            # CNDR values
            CNDR_hex = [
                hexDecodedData[334:336],    # 1
                hexDecodedData[332:334],    # 2
                hexDecodedData[338:340],    # 3
                hexDecodedData[336:338],    # 4
                hexDecodedData[342:344],    # 5
                hexDecodedData[340:342],    # 6
                hexDecodedData[346:348],    # 7
                hexDecodedData[344:346],    # 8
                hexDecodedData[350:352],    # 9
                hexDecodedData[348:350],    # 10
                hexDecodedData[354:356],    # 11
                hexDecodedData[352:354],    # 12
                hexDecodedData[358:360],    # 13
                hexDecodedData[356:358],    # 14
                hexDecodedData[362:364],    # 15
                hexDecodedData[360:362],    # 16
                hexDecodedData[1174:1176],  # 17
                hexDecodedData[1172:1174]   # 18
            ]
           
            Last_cmd_ex_hex=hexDecodedData[364:372]
            Last_reset_time_hex = hexDecodedData[372:376]
            cmd_counter_hex = hexDecodedData[376:380]
            
           
            ACQ1_2_hex = hexDecodedData[380:384]
            ACQ3_4_hex = hexDecodedData[384:388]
            
           
            word31_hex = hexDecodedData[388:392]   # Update indices as needed
            word31 = reverse_and_concatenate(word31_hex)
            flags = extract_word31_flags(word31)
           
            word32_hex = hexDecodedData[392:396]   # Update indices as needed
            word32 = reverse_and_concatenate(word32_hex)
            flag2 = extract_sa4w32_flags(word32)
           
            # Channel Status
            CHANNEL_STATUS_hex = [
                hexDecodedData[396:400],   # 1
                hexDecodedData[400:404],   # 2
                hexDecodedData[404:408],   # 3
                hexDecodedData[408:412],   # 4
                hexDecodedData[412:416],   # 5
                hexDecodedData[416:420],   # 6
                hexDecodedData[420:424],   # 7
                hexDecodedData[424:428],   # 8
                hexDecodedData[428:432],   # 9
                hexDecodedData[432:436],   # 10
                hexDecodedData[436:440],   # 11
                hexDecodedData[440:444],   # 12
                hexDecodedData[444:448],   # 13
                hexDecodedData[448:452],   # 14
                hexDecodedData[452:456],   # 15
                hexDecodedData[456:460],   # 16
                hexDecodedData[1176:1180], # 17
                hexDecodedData[1180:1184]  # 18
            ]
            
            # PR values
            PR_hex = [
                hexDecodedData[524:532],   # 1
                hexDecodedData[532:540],   # 2
                hexDecodedData[540:548],   # 3
                hexDecodedData[548:556],   # 4
                hexDecodedData[556:564],   # 5
                hexDecodedData[564:572],   # 6
                hexDecodedData[572:580],   # 7
                hexDecodedData[580:588],   # 8
                hexDecodedData[588:596],   # 9
                hexDecodedData[596:604],   # 10
                hexDecodedData[604:612],   # 11
                hexDecodedData[612:620],   # 12
                hexDecodedData[620:628],   # 13
                hexDecodedData[628:636],   # 14
                hexDecodedData[636:644],   # 15
                hexDecodedData[644:652],   # 16
                hexDecodedData[1188:1196], # 17
                hexDecodedData[1196:1204]  # 18
            ]
            
            # DR values
            DR_hex = [
                hexDecodedData[652:660],   # 1
                hexDecodedData[660:668],   # 2
                hexDecodedData[668:676],   # 3
                hexDecodedData[676:684],   # 4
                hexDecodedData[684:692],   # 5
                hexDecodedData[692:700],   # 6
                hexDecodedData[700:708],   # 7
                hexDecodedData[708:716],   # 8
                hexDecodedData[716:724],   # 9
                hexDecodedData[724:732],   # 10
                hexDecodedData[732:740],   # 11
                hexDecodedData[740:748],   # 12
                hexDecodedData[748:756],   # 13
                hexDecodedData[756:764],   # 14
                hexDecodedData[764:772],   # 15
                hexDecodedData[772:780],   # 16
                hexDecodedData[1204:1212], # 17
                hexDecodedData[1212:1220]  # 18
            ]
           
            Dual_exe_cmd_c_hex = hexDecodedData[1186:1188]
            Spu_cmd_c_hex =hexDecodedData[1184:1186]
            Nrffc_counter1_hex = hexDecodedData[1244:1246]
            Nrffc_counter2_hex = hexDecodedData[1246:1248]
            Grffc_counter1_hex = hexDecodedData[1248:1250]
            Grffc_counter2_hex = hexDecodedData[1250:1252]
            Grffc_counter3_hex = hexDecodedData[1252:1254]
            Grffc_counter4_hex = hexDecodedData[1254:1256]
            
           
                # Elevation values
            Elev_hex = [
                hexDecodedData[1258:1260], # 1
                hexDecodedData[1256:1258], # 2
                hexDecodedData[1262:1264], # 3
                hexDecodedData[1260:1262], # 4
                hexDecodedData[1266:1268], # 5
                hexDecodedData[1264:1266], # 6
                hexDecodedData[1270:1272], # 7
                hexDecodedData[1268:1270], # 8
                hexDecodedData[1274:1276], # 9
                hexDecodedData[1272:1274], # 10
                hexDecodedData[1278:1280], # 11
                hexDecodedData[1276:1278], # 12
                hexDecodedData[1282:1284], # 13
                hexDecodedData[1280:1282], # 14
                hexDecodedData[1286:1288], # 15
                hexDecodedData[1284:1286], # 16
                hexDecodedData[1290:1292], # 17
                hexDecodedData[1288:1290]  # 18
            ]
           
           
            INS_x_hex = hexDecodedData[1292:1300]
            INS_y_hex = hexDecodedData[1300:1308]
            INS_z_hex = hexDecodedData[1308:1316]
            INS_vx_hex = hexDecodedData[1316:1324]
            INS_vy_hex = hexDecodedData[1324:1332]
            INS_vz_hex = hexDecodedData[1332:1340]
            
            fix_3D_hex = hexDecodedData[1804:1808]
            PPS_Nanosec_hex = hexDecodedData[1808:1816]
            PPS_Sec_hex = hexDecodedData[1816:1824]
            PPS_Week_hex = hexDecodedData[1824:1828]
            Leap_hex = hexDecodedData[1828:1832]
            
        
            # Convert hex to decimal and scale as needed
            SYS_Second=reverse_and_concatenate(SYS_Second_hex)
            SYS_NanoSecond=reverse_and_concatenate(SYS_NanoSecond_hex)
            SYS_WeekNumber=reverse_and_concatenate(SYS_Weeknumber_hex)
            TSM_update_counter=reverse_and_concatenate(Tsm_UpdateCounter_hex)
           
   
            Checksum1=reverse_and_concatenate(csm1_hex)
            chechsum_calulation_covert_decimal(SYN_NanoSecond_hex,SYN_Second_hex,SYN_Weeknumber_hex,Tsm_UpdateCounter_hex,Checksum1)
           
             
            INS_x = reverse_and_concatenate(INS_x_hex, is_signed=True)/100.0
            INS_y = reverse_and_concatenate(INS_y_hex, is_signed=True)/100.0
            INS_z = reverse_and_concatenate(INS_z_hex, is_signed=True)/100.0
            INS_vx = reverse_and_concatenate(INS_vx_hex, is_signed=True)/1000.0
            INS_vy = reverse_and_concatenate(INS_vy_hex, is_signed=True)/1000.0
            INS_vz = reverse_and_concatenate(INS_vz_hex, is_signed=True)/1000.0
            
           
            POS_x = reverse_and_concatenate(POS_X_hex, is_signed=True)/100.0
            POS_y = reverse_and_concatenate(POS_Y_hex, is_signed=True)/100.0
            POS_z = reverse_and_concatenate(POS_Z_hex, is_signed=True)/100.0
            POS_vx = reverse_and_concatenate(POS_Vx_hex, is_signed=True)/1000.0
            POS_vy = reverse_and_concatenate(POS_Vy_hex, is_signed=True)/1000.0
            POS_vz = reverse_and_concatenate(POS_Vz_hex, is_signed=True)/1000.0
           
           
           
            UpdateCounter=reverse_and_concatenate(UpdateCounter_hex)
            #print(f"\n UPDATE COUNTER:{UpdateCounter}")
            PDOP = reverse_and_concatenate(PDOP_hex, is_signed=True)/100.0
            word20 =  reverse_and_concatenate(word20_hex)
           
            Bais=reverse_and_concatenate(Bais_hex)
            ISB = reverse_and_concatenate(ISB_hex)
           
            DRIFT = reverse_and_concatenate(DRIFT_hex, is_signed=True)/100.0
            ISD=reverse_and_concatenate(ISD_hex)
           
           
            HW__SW_reset_counter=reverse_and_concatenate(HW__SW_reset_counter_hex)
            SW_reset_counter = (HW__SW_reset_counter >> 8) & 0X00FF
            HW_reset_counter = HW__SW_reset_counter & 0x00FF
            
            
            Navic_msg_counter=reverse_and_concatenate(Navic_msg_counter_hex)
            Navic_msg_22_counter =(Navic_msg_counter >> 8) & 0X00FF
            Navic_msg_counter = Navic_msg_counter & 0x00FF
            
            word30 = reverse_and_concatenate(word30_hex)
            Leo_sat_id_mil = (word30 >> 8) & 0X00FF
            No_of_Sat = word30  & 0x00FF
            Navic_cmd_var=  (word31 >> 8) & 0X00FF
            
           
           # Convert tracking values
            SVID_values = [reverse_and_concatenate(h) for h in SVID_hex]
            IODE_values = [reverse_and_concatenate(h) for h in IODE_hex]
            CNDR_values = [reverse_and_concatenate(h) for h in CNDR_hex]
            CHANNEL_STATUS = [reverse_and_concatenate(h) for h in CHANNEL_STATUS_hex]
            PR_values = [reverse_and_concatenate(h) for h in PR_hex]
            DR_values = [reverse_and_concatenate(h, is_signed=True)/1000.0 for h in DR_hex]
            Elev_values = [reverse_and_concatenate(h) for h in Elev_hex]
            
           
           
            Last_cmd_ex=reverse_and_concatenate(Last_cmd_ex_hex)
            Last_reset_time = reverse_and_concatenate(Last_reset_time_hex)
            
            cmd_counter = reverse_and_concatenate(cmd_counter_hex)
            Total_cmd_counter = cmd_counter  & 0X00FF
            Cmd_counter_based_rt = (cmd_counter >> 8)  & 0x00FF
            
            ACQ1_2 =  reverse_and_concatenate(ACQ1_2_hex)
            ACQ1 = (ACQ1_2 >> 8)  & 0x00FF
            ACQ2 = ACQ1_2 & 0X00FF
            
            ACQ3_4 =  reverse_and_concatenate(ACQ3_4_hex)
            
            ACQ3 = (ACQ3_4 >> 8)  & 0x00FF
            ACQ4 = ACQ3_4  & 0X00FF
           
           
           
            Dual_exe_cmd_c = reverse_and_concatenate(Dual_exe_cmd_c_hex)
            Spu_cmd_c = reverse_and_concatenate(Spu_cmd_c_hex)
            
            Nrffc_counter1 =  reverse_and_concatenate(Nrffc_counter1_hex)
            Nrffc_counter2 =  reverse_and_concatenate(Nrffc_counter2_hex)
            Grffc_counter1 =  reverse_and_concatenate(Grffc_counter1_hex)
            Grffc_counter2 =  reverse_and_concatenate(Grffc_counter2_hex)
            Grffc_counter3 =  reverse_and_concatenate(Grffc_counter3_hex)
            Grffc_counter4 =  reverse_and_concatenate(Grffc_counter4_hex)
           
          
           
            fix_3D = reverse_and_concatenate(fix_3D_hex)
            PPS_Nanosec = reverse_and_concatenate(PPS_Nanosec_hex)
            PPS_Sec = reverse_and_concatenate(PPS_Sec_hex)
            PPS_Week = reverse_and_concatenate(PPS_Week_hex)
            Leap = reverse_and_concatenate(Leap_hex)

            widgets['tsm_counter_entry'].config(state="normal")
            widgets['tsm_counter_entry'].delete(0, END)
            widgets['tsm_counter_entry'].insert(0, str(TSM_update_counter))
            widgets['tsm_counter_entry'].config(state="readonly")

            widgets['time_entry'].config(state="normal")
            widgets['time_entry'].delete(0, END)
            widgets['time_entry'].insert(0, str(SYS_Second))
            widgets['time_entry'].config(state="readonly")

            widgets['nanotime_entry'].config(state="normal")
            widgets['nanotime_entry'].delete(0, END)
            widgets['nanotime_entry'].insert(0, str(SYS_NanoSecond))
            widgets['nanotime_entry'].config(state="readonly")

            widgets['week_entry'].config(state="normal")
            widgets['week_entry'].delete(0, END)
            widgets['week_entry'].insert(0, str(SYS_WeekNumber))
            widgets['week_entry'].config(state="readonly")

            widgets['update_entry'].config(state="normal")
            widgets['update_entry'].delete(0, END)
            widgets['update_entry'].insert(0, str(UpdateCounter))
            widgets['update_entry'].config(state="readonly")
            
            widgets['time_entry2'].config(state="normal")
            widgets['time_entry2'].delete(0,END)
            widgets['time_entry2'].insert(0, str(PPS_Sec))
            widgets['time_entry2'].config(state="readonly")
            #set_colored_value(time_entry3,PPS_Sec)
    
            widgets['nanotime_entry2'].config(state="normal")
            widgets['nanotime_entry2'].delete(0,END)
            widgets['nanotime_entry2'].insert(0, str(PPS_Nanosec))
            widgets['nanotime_entry2'].config(state="readonly")
            #set_colored_value(nanotime_entry3,PPS_NanoSec)
    
            widgets['week_entry2'].config(state="normal")
            widgets['week_entry2'].delete(0,END)
            widgets['week_entry2'].insert(0, str(PPS_Week))
            widgets['week_entry2'].config(state="readonly")
            #set_colored_value(week_entry3,PPS_Week)
    
            widgets['fix_3d'].config(state="normal")
            widgets['fix_3d'].delete(0,END)
            widgets['fix_3d'].insert(0, f"{fix_3D}")
            widgets['fix_3d'].config(state="readonly")
            
            widgets['leap'].config(state="normal")
            widgets['leap'].delete(0,END)
            widgets['leap'].insert(0, f"{Leap}")
            widgets['leap'].config(state="readonly")

            widgets['csm1'].config(state="normal")
            widgets['csm1'].delete(0,END)
            widgets['csm1'].insert(0, f"{checksum1}")
            widgets['csm1'].config(state="readonly")

            widgets['csm2'].config(state="normal")
            widgets['csm2'].delete(0,END)
            widgets['csm2'].insert(0, f"{checksum2}")
            widgets['csm2'].config(state="readonly")
            
            widgets['position_entry'].config(state="normal")
            widgets['position_entry'].delete(0, END)
            widgets['position_entry'].insert(0, str(POS_x))
            widgets['position_entry'].config(state="readonly")
            
            widgets['position_entry1'].config(state="normal")
            widgets['position_entry1'].delete(0, END)
            widgets['position_entry1'].insert(0, str(POS_y))
            widgets['position_entry1'].config(state="readonly")
            
            widgets['position_entry2'].config(state="normal")
            widgets['position_entry2'].delete(0, END)
            widgets['position_entry2'].insert(0, str(POS_z))
            widgets['position_entry2'].config(state="readonly")

            widgets['velocity_entry'].config(state="normal")
            widgets['velocity_entry'].delete(0, END)
            widgets['velocity_entry'].insert(0, str(POS_vx))
            widgets['velocity_entry'].config(state="readonly")
            
            widgets['velocity_entry1'].config(state="normal")
            widgets['velocity_entry1'].delete(0, END)
            widgets['velocity_entry1'].insert(0, str(POS_vy))
            widgets['velocity_entry1'].config(state="readonly")
            
            widgets['velocity_entry2'].config(state="normal")
            widgets['velocity_entry2'].delete(0, END)
            widgets['velocity_entry2'].insert(0, str(POS_vz))
            widgets['velocity_entry2'].config(state="readonly")
            

            widgets['position_entry3'].config(state="normal")
            widgets['position_entry3'].delete(0, END)
            widgets['position_entry3'].insert(0, str(INS_x))
            widgets['position_entry3'].config(state="readonly")

            widgets['position_entry4'].config(state="normal")
            widgets['position_entry4'].delete(0, END)
            widgets['position_entry4'].insert(0, str(INS_y))
            widgets['position_entry4'].config(state="readonly")

            widgets['position_entry5'].config(state="normal")
            widgets['position_entry5'].delete(0, END)
            widgets['position_entry5'].insert(0, str(INS_z))
            widgets['position_entry5'].config(state="readonly")
            
            widgets['velocity_entry3'].config(state="normal")
            widgets['velocity_entry3'].delete(0, END)
            widgets['velocity_entry3'].insert(0, str(INS_vx))
            widgets['velocity_entry3'].config(state="readonly")
            
            widgets['velocity_entry4'].config(state="normal")
            widgets['velocity_entry4'].delete(0, END)
            widgets['velocity_entry4'].insert(0, str(INS_vy))
            widgets['velocity_entry4'].config(state="readonly")
            
            widgets['velocity_entry5'].config(state="normal")
            widgets['velocity_entry5'].delete(0, END)
            widgets['velocity_entry5'].insert(0, str(INS_vz))
            widgets['velocity_entry5'].config(state="readonly")
            
            widgets['pdop'].config(state="normal")
            widgets['pdop'].delete(0, END)
            widgets['pdop'].insert(0, f"{PDOP}")
            widgets['pdop'].config(state="readonly")
            
              
            widgets['tm'].config(state="normal")
            widgets['tm'].delete(0, END)
            widgets['tm'].insert(0, str(flag['Tm_sel']))
            widgets['tm'].config(state="readonly")
            
            
            widgets['swdt'].config(state="normal")
            widgets['swdt'].delete(0, END)
            widgets['swdt'].insert(0, str(flag["SWDT"]))
            widgets['swdt'].config(state="readonly")
            
            
            widgets['hwdt'].config(state="normal")
            widgets['hwdt'].delete(0, END)
            widgets['hwdt'].insert(0, str(flag["HWDT"]))
            widgets['hwdt'].config(state="readonly")
            
            
            widgets['sbasen'].config(state="normal")
            widgets['sbasen'].delete(0, END)
            widgets['sbasen'].insert(0, str(flag["SBASEN"]))
            widgets['sbasen'].config(state="readonly")
            
            widgets['sys_mode'].config(state="normal")
            widgets['sys_mode'].delete(0, END)
            widgets['sys_mode'].insert(0, str(flag["System_mode"]))
            widgets['sys_mode'].config(state="readonly")
            
            
            widgets['rec_mode'].config(state="normal")
            widgets['rec_mode'].delete(0, END)
            widgets['rec_mode'].insert(0, str(flag["Rec_Mode"]))
            widgets['rec_mode'].config(state="readonly")
            
             
            widgets['time_mode'].config(state="normal")
            widgets['time_mode'].delete(0, END)
            widgets['time_mode'].insert(0, str(flag["Time_Mode"]))
            widgets['time_mode'].config(state="readonly")
            
            widgets['alm_av'].config(state="normal")
            widgets['alm_av'].delete(0, END)
            widgets['alm_av'].insert(0, str(flag["Alm_Av"]))
            widgets['alm_av'].config(state="readonly")
            
            widgets['time_av'].config(state="normal")
            widgets['time_av'].delete(0, END)
            widgets['time_av'].insert(0, str(flag["Time_Av"]))
            widgets['time_av'].config(state="readonly")
            
            widgets['rec_mode'].config(state="normal")
            widgets['rec_mode'].delete(0, END)
            widgets['rec_mode'].insert(0, str(flag["Rec_Mode"]))
            widgets['rec_mode'].config(state="readonly")
            
             
            widgets['port_conf'].config(state="normal")
            widgets['port_conf'].delete(0, END)
            widgets['port_conf'].insert(0, flag1["Port_config"]["Antenna_1"])
            widgets['port_conf'].config(state="readonly")
            
            widgets['port_conf1'].config(state="normal")
            widgets['port_conf1'].delete(0, END)
            widgets['port_conf1'].insert(0, flag1["Port_config"]["Antenna_2"])
            widgets['port_conf1'].config(state="readonly")
            
            widgets['port_conf2'].config(state="normal")
            widgets['port_conf2'].delete(0, END)
            widgets['port_conf2'].insert(0, flag1["Port_config"]["Antenna_3"])
            widgets['port_conf2'].config(state="readonly")
            
            widgets['port_conf3'].config(state="normal")
            widgets['port_conf3'].delete(0, END)
            widgets['port_conf3'].insert(0, flag1["Port_config"]["Antenna_4"])
            widgets['port_conf3'].config(state="readonly")
            
            widgets['pos_mode'].config(state="normal")
            widgets['pos_mode'].delete(0, END)
            widgets['pos_mode'].insert(0, str(flag["Pose_Mode"]))
            widgets['pos_mode'].config(state="readonly")
            
            widgets['pos_av'].config(state="normal")
            widgets['pos_av'].delete(0, END)
            widgets['pos_av'].insert(0, str(flag["Pos_Av"]))
            widgets['pos_av'].config(state="readonly")
            
            widgets['cb'].config(state="normal")
            widgets['cb'].delete(0, END)
            widgets['cb'].insert(0, f"{Bais}")
            widgets['cb'].config(state="readonly")
            
            widgets['isb'].config(state="normal")
            widgets['isb'].delete(0, END)
            widgets['isb'].insert(0, f"{ISB}")
            widgets['isb'].config(state="readonly")
            
            widgets['drift'].config(state="normal")
            widgets['drift'].delete(0, END)
            widgets['drift'].insert(0, f"{DRIFT}")
            widgets['drift'].config(state="readonly")
            
            widgets['isd'].config(state="normal")
            widgets['isd'].delete(0, END)
            widgets['isd'].insert(0,f"{ISD}")
            widgets['isd'].config(state="readonly")
            
            widgets['sw_rst_c'].config(state="normal")
            widgets['sw_rst_c'].delete(0, END)
            widgets['sw_rst_c'].insert(0, f"{SW_reset_counter}")
            widgets['sw_rst_c'].config(state="readonly")
            
            widgets['hw_rst_c'].config(state="normal")
            widgets['hw_rst_c'].delete(0, END)
            widgets['hw_rst_c'].insert(0,f"{HW_reset_counter}")
            widgets['hw_rst_c'].config(state="readonly")
            
            widgets['no_sat_trck'].config(state="normal")
            widgets['no_sat_trck'].delete(0, END)
            widgets['no_sat_trck'].insert(0,f"{No_of_Sat}")
            widgets['no_sat_trck'].config(state="readonly")
            
            widgets['sol_mode'].config(state="normal")
            widgets['sol_mode'].delete(0, END)
            widgets['sol_mode'].insert(0,str(flag1["Sol_mode"]))
            widgets['sol_mode'].config(state="readonly")
            
            widgets['sps_id'].config(state="normal")
            widgets['sps_id'].delete(0, END)
            widgets['sps_id'].insert(0,str(flag1["SPS_ID"]))
            widgets['sps_id'].config(state="readonly")
            
            widgets['sw_rst_id'].config(state="normal")
            widgets['sw_rst_id'].delete(0, END)
            widgets['sw_rst_id'].insert(0,flag1["SW_Rst_ID"])
            widgets['sw_rst_id'].config(state="readonly")
            
            widgets['navic_msg_22_c'].config(state="normal")
            widgets['navic_msg_22_c'].delete(0, END)
            widgets['navic_msg_22_c'].insert(0,f"{Navic_msg_22_counter}")
            widgets['navic_msg_22_c'].config(state="readonly")
            
            widgets['navic_msg_cmd_c'].config(state="normal")
            widgets['navic_msg_cmd_c'].delete(0, END)
            widgets['navic_msg_cmd_c'].insert(0, f"{Navic_msg_counter}")
            widgets['navic_msg_cmd_c'].config(state="readonly")
            
            widgets['leo_sat_id'].config(state="normal")
            widgets['leo_sat_id'].delete(0, END)
            widgets['leo_sat_id'].insert(0,f"{Leo_sat_id_mil}")
            widgets['leo_sat_id'].config(state="readonly")
            
            widgets['odp_est'].config(state="normal")
            widgets['odp_est'].delete(0, END)
            widgets['odp_est'].insert(0,str(flag3["ODP_Est flag"]))
            widgets['odp_est'].config(state="readonly")
            
            widgets['odp_en'].config(state="normal")
            widgets['odp_en'].delete(0, END)
            widgets['odp_en'].insert(0,str(flag3["ODP_ENA"]))
            widgets['odp_en'].config(state="readonly")
            
            widgets['phc_usg'].config(state="normal")
            widgets['phc_usg'].delete(0, END)
            widgets['phc_usg'].insert(0,str(flag3["PHCUsage"]))
            widgets['phc_usg'].config(state="readonly")
            
            widgets['phc_en'].config(state="normal")
            widgets['phc_en'].delete(0, END)
            widgets['phc_en'].insert(0,str(flag3["PHCEn"]))
            widgets['phc_en'].config(state="readonly")
            
            widgets['eph_rt'].config(state="normal")
            widgets['eph_rt'].delete(0, END)
            widgets['eph_rt'].insert(0,str(flag3["Eph RT"]))
            widgets['eph_rt'].config(state="readonly")
            
            widgets['mnvon'].config(state="normal")
            widgets['mnvon'].delete(0, END)
            widgets['mnvon'].insert(0,str(flag3["MNVON"]))
            widgets['mnvon'].config(state="readonly")
            
            widgets['numsps'].config(state="normal")
            widgets['numsps'].delete(0, END)
            widgets['numsps'].insert(0,str(flag3["NUMSPS"]))
            widgets['numsps'].config(state="readonly")
            
            widgets['navic_cmd_var'].config(state="normal")
            widgets['navic_cmd_var'].delete(0, END)
            widgets['navic_cmd_var'].insert(0,f"{Navic_cmd_var}")
            widgets['navic_cmd_var'].config(state="readonly")
            
            
            widgets['rt_id'].config(state="normal")
            widgets['rt_id'].delete(0, END)
            widgets['rt_id'].insert(0,str(flags["RT_ID"]))
            widgets['rt_id'].config(state="readonly")
            
            widgets['s_id'].config(state="normal")
            widgets['s_id'].delete(0, END)
            widgets['s_id'].insert(0,str(flags["S_ID"]))
            widgets['s_id'].config(state="readonly")
            
            widgets['acq1'].config(state="normal")
            widgets['acq1'].delete(0, END)
            widgets['acq1'].insert(0,f"{ACQ1}")
            widgets['acq1'].config(state="readonly")
            
            widgets['acq2'].config(state="normal")
            widgets['acq2'].delete(0, END)
            widgets['acq2'].insert(0, f"{ACQ2}")
            widgets['acq2'].config(state="readonly")
            
            widgets['acq3'].config(state="normal")
            widgets['acq3'].delete(0, END)
            widgets['acq3'].insert(0,f"{ACQ3}")
            widgets['acq3'].config(state="readonly")
            
            widgets['acq4'].config(state="normal")
            widgets['acq4'].delete(0, END)
            widgets['acq4'].insert(0, f"{ACQ4}")
            widgets['acq4'].config(state="readonly")
            
            widgets['last_cmd_exe'].config(state="normal")
            widgets['last_cmd_exe'].delete(0, END)
            widgets['last_cmd_exe'].insert(0,f"{Last_cmd_ex}")
            widgets['last_cmd_exe'].config(state="readonly")
            
            widgets['last_reset_time'].config(state="normal")
            widgets['last_reset_time'].delete(0, END)
            widgets['last_reset_time'].insert(0,f"{Last_reset_time}")
            widgets['last_reset_time'].config(state="readonly")
            
            
            widgets['dual_cmd_c_rt'].config(state="normal")
            widgets['dual_cmd_c_rt'].delete(0, END)
            widgets['dual_cmd_c_rt'].insert(0, f"{Dual_exe_cmd_c}")
            widgets['dual_cmd_c_rt'].config(state="readonly")
            
            widgets['spu_cmd_c_rt'].config(state="normal")
            widgets['spu_cmd_c_rt'].delete(0, END)
            widgets['spu_cmd_c_rt'].insert(0, f"{Spu_cmd_c}")
            widgets['spu_cmd_c_rt'].config(state="readonly")
            
            widgets['cmd_based_rt'].config(state="normal")
            widgets['cmd_based_rt'].delete(0, END)
            widgets['cmd_based_rt'].insert(0,f"{Cmd_counter_based_rt}")
            widgets['cmd_based_rt'].config(state="readonly")
            
            widgets['nrff_rst_counter1'].config(state="normal")
            widgets['nrff_rst_counter1'].delete(0, END)
            widgets['nrff_rst_counter1'].insert(0, f"{Nrffc_counter1}")
            widgets['nrff_rst_counter1'].config(state="readonly")
            
            widgets['nrff_rst_counter2'].config(state="normal")
            widgets['nrff_rst_counter2'].delete(0, END)
            widgets['nrff_rst_counter2'].insert(0,f"{Nrffc_counter2}")
            widgets['nrff_rst_counter2'].config(state="readonly")
            
            widgets['grff_rst_counter1'].config(state="normal")
            widgets['grff_rst_counter1'].delete(0, END)
            widgets['grff_rst_counter1'].insert(0,f"{Grffc_counter1}")
            widgets['grff_rst_counter1'].config(state="readonly")
            
            
            widgets['grff_rst_counter2'].config(state="normal")
            widgets['grff_rst_counter2'].delete(0, END)
            widgets['grff_rst_counter2'].insert(0, f"{Grffc_counter2}")
            widgets['grff_rst_counter2'].config(state="readonly")
            
            widgets['grff_rst_counter3'].config(state="normal")
            widgets['grff_rst_counter3'].delete(0, END)
            widgets['grff_rst_counter3'].insert(0, f"{Grffc_counter3}")
            widgets['grff_rst_counter3'].config(state="readonly")
            
            widgets['grff_rst_counter4'].config(state="normal")
            widgets['grff_rst_counter4'].delete(0, END)
            widgets['grff_rst_counter4'].insert(0,f"{Grffc_counter4}")
            widgets['grff_rst_counter4'].config(state="readonly")
            
            widgets['total_cmd_counter'].config(state="normal")
            widgets['total_cmd_counter'].delete(0, END)
            widgets['total_cmd_counter'].insert(0,f"{Total_cmd_counter}")
            widgets['total_cmd_counter'].config(state="readonly")
            
            widgets['miss_ph'].config(state="normal")
            widgets['miss_ph'].delete(0, END)
            widgets['miss_ph'].insert(0,str(flags["Mission_Phase"]))
            widgets['miss_ph'].config(state="readonly")
            
            widgets['fmem'].config(state="normal")
            widgets['fmem'].delete(0, END)
            widgets['fmem'].insert(0,str(flags["Fmem"]))
            widgets['fmem'].config(state="readonly")
            
            widgets['cr_aid'].config(state="normal")
            widgets['cr_aid'].delete(0, END)
            widgets['cr_aid'].insert(0,str(flags["Cr_Aid"]))
            widgets['cr_aid'].config(state="readonly")
            
            widgets['full_cntr'].config(state="normal")
            widgets['full_cntr'].delete(0, END)
            widgets['full_cntr'].insert(0,str(flags["FLL_Cntr"]))
            widgets['full_cntr'].config(state="readonly")
            
            widgets['s_id'].config(state="normal")
            widgets['s_id'].delete(0, END)
            widgets['s_id'].insert(0,str(flags["S_ID"]))
            widgets['s_id'].config(state="readonly")
            
            widgets['lig_1'].config(state="normal")
            widgets['lig_1'].delete(0, END)
            widgets['lig_1'].insert(0,str(flags["LIG_1"]))
            widgets['lig_1'].config(state="readonly")
            
            widgets['lig_2'].config(state="normal")
            widgets['lig_2'].delete(0, END)
            widgets['lig_2'].insert(0,str(flags["LIG_2"]))
            widgets['lig_2'].config(state="readonly")
            
            widgets['lig_3'].config(state="normal")
            widgets['lig_3'].delete(0, END)
            widgets['lig_3'].insert(0,str(flags["LIG_3"]))
            widgets['lig_3'].config(state="readonly")
            
            widgets['lig_4'].config(state="normal")
            widgets['lig_4'].delete(0, END)
            widgets['lig_4'].insert(0,str(flags["LIG_4"]))
            widgets['lig_4'].config(state="readonly")
            
            widgets['lin_1'].config(state="normal")
            widgets['lin_1'].delete(0, END)
            widgets['lin_1'].insert(0,str(flags["LIN_1"]))
            widgets['lin_1'].config(state="readonly")
            
            widgets['lin_2'].config(state="normal")
            widgets['lin_2'].delete(0, END)
            widgets['lin_2'].insert(0,str(flags["LIN_2"]))
            widgets['lin_2'].config(state="readonly")
            
            widgets['prime_ngc'].config(state="normal")
            widgets['prime_ngc'].delete(0, END)
            widgets['prime_ngc'].insert(0,str(flags["Prime_NGC"]))
            widgets['prime_ngc'].config(state="readonly")
            
            widgets['rng_l'].config(state="normal")
            widgets['rng_l'].delete(0, END)
            widgets['rng_l'].insert(0,str(flag2["Rng L"]))
            widgets['rng_l'].config(state="readonly")
            
            widgets['orbit_phase'].config(state="normal")
            widgets['orbit_phase'].delete(0, END)
            widgets['orbit_phase'].insert(0,str(flag2["Orbit Phase"]))
            widgets['orbit_phase'].config(state="readonly")
            
            widgets['iono_c'].config(state="normal")
            widgets['iono_c'].delete(0, END)
            widgets['iono_c'].insert(0,str(flag2["Iono C"]))
            widgets['iono_c'].config(state="readonly")
            
            widgets['iono_sm'].config(state="normal")
            widgets['iono_sm'].delete(0, END)
            widgets['iono_sm'].insert(0,str(flag2["Iono Sm"]))
            widgets['iono_sm'].config(state="readonly")
            
            widgets['cr_smo'].config(state="normal")
            widgets['cr_smo'].delete(0, END)
            widgets['cr_smo'].insert(0,str(flag2["Cr Smo"]))
            widgets['cr_smo'].config(state="readonly")
            
            widgets['vel_sm'].config(state="normal")
            widgets['vel_sm'].delete(0, END)
            widgets['vel_sm'].insert(0,str(flag2["Vel sm"]))
            widgets['vel_sm'].config(state="readonly")
            
            widgets['raim'].config(state="normal")
            widgets['raim'].delete(0, END)
            widgets['raim'].insert(0,str(flag2["RAIM"]))
            widgets['raim'].config(state="readonly")
            
            widgets['pr_rej'].config(state="normal")
            widgets['pr_rej'].delete(0, END)
            widgets['pr_rej'].insert(0,str(flag2["PR Rej"]))
            widgets['pr_rej'].config(state="readonly")
            
            widgets['pr_bf_sync'].config(state="normal")
            widgets['pr_bf_sync'].delete(0, END)
            widgets['pr_bf_sync'].insert(0,str(flag2["Pr Bf Sync"]))
            widgets['pr_bf_sync'].config(state="readonly")
            
            widgets['cfg_loop'].config(state="normal")
            widgets['cfg_loop'].delete(0, END)
            widgets['cfg_loop'].insert(0,str(flag2["Cfg loop"]))
            widgets['cfg_loop'].config(state="readonly")
            
            widgets['int_crd_tst'].config(state="normal")
            widgets['int_crd_tst'].delete(0, END)
            widgets['int_crd_tst'].insert(0,str(flag2["int crd tst"]))
            widgets['int_crd_tst'].config(state="readonly")
            
            widgets['elev_e'].config(state="normal")
            widgets['elev_e'].delete(0, END)
            widgets['elev_e'].insert(0,str(flag2["Elev En"]))
            widgets['elev_e'].config(state="readonly")
            
            widgets['rst_flag'].config(state="normal")
            widgets['rst_flag'].delete(0, END)
            widgets['rst_flag'].insert(0,str(flag2["Rst Flag"]))
            widgets['rst_flag'].config(state="readonly")
            
            widgets['odp_rst_sf'].config(state="normal")
            widgets['odp_rst_sf'].delete(0, END)
            widgets['odp_rst_sf'].insert(0,str(flag2["ODP Rst Sp"]))
            widgets['odp_rst_sf'].config(state="readonly")
            
            widgets['cold_vis'].config(state="normal")
            widgets['cold_vis'].delete(0, END)
            widgets['cold_vis'].insert(0,str(flag2["Cold Vis"]))
            widgets['cold_vis'].config(state="readonly")
            
            widgets['nav_msg_e'].config(state="normal")
            widgets['nav_msg_e'].delete(0, END)
            widgets['nav_msg_e'].insert(0,str(flag2["Navic Msg En"]))
            widgets['nav_msg_e'].config(state="readonly")
            
            
            
              # Update SVID entries
            if 'svid_entries' in widgets and len(widgets['svid_entries']) == 18:
                for ch in range(18):
                    widgets['svid_entries'][ch].config(state="normal")
                    widgets['svid_entries'][ch].delete(0, END)
                    widgets['svid_entries'][ch].insert(0, str(SVID_values[ch]))
                    widgets['svid_entries'][ch].config(state="readonly")
            
            # Update CNDR entries
            if 'cndr_entries' in widgets and len(widgets['cndr_entries']) == 18:
                for ch in range(18):
                    widgets['cndr_entries'][ch].config(state="normal")
                    widgets['cndr_entries'][ch].delete(0, END)
                    widgets['cndr_entries'][ch].insert(0, str(CNDR_values[ch]))
                    widgets['cndr_entries'][ch].config(state="readonly")
                    
            refresh_cndr_plot()
            
            # Update IODE entries
            if 'iode_entries' in widgets and len(widgets['iode_entries']) == 18:
                for ch in range(18):
                    widgets['iode_entries'][ch].config(state="normal")
                    widgets['iode_entries'][ch].delete(0, END)
                    widgets['iode_entries'][ch].insert(0, str(IODE_values[ch]))
                    widgets['iode_entries'][ch].config(state="readonly")
            
            # Update PR entries
            if 'pr_entries' in widgets and len(widgets['pr_entries']) == 18:
                for ch in range(18):
                    widgets['pr_entries'][ch].config(state="normal")
                    widgets['pr_entries'][ch].delete(0, END)
                    widgets['pr_entries'][ch].insert(0, f"{PR_values[ch]}")
                    widgets['pr_entries'][ch].config(state="readonly")
            
            # Update DR entries
            if 'dr_entries' in widgets and len(widgets['dr_entries']) == 18:
                for ch in range(18):
                    widgets['dr_entries'][ch].config(state="normal")
                    widgets['dr_entries'][ch].delete(0, END)
                    widgets['dr_entries'][ch].insert(0, f"{DR_values[ch]:.3f}")
                    widgets['dr_entries'][ch].config(state="readonly")
            
            # Update ELEV entries
            if 'elev_entries' in widgets and len(widgets['elev_entries']) == 18:
                for ch in range(18):
                    widgets['elev_entries'][ch].config(state="normal")
                    widgets['elev_entries'][ch].delete(0, END)
                    widgets['elev_entries'][ch].insert(0, str(Elev_values[ch]))
                    widgets['elev_entries'][ch].config(state="readonly")
                    
              
               
            # Update bit flag entries
            if 'bit_to_entrylist' in widgets:
                # All 18 bit names as per your request
                bit_names = ["ANT","TRK","DR","EPH","POS","URA","RIM","PR","INO","SBC","SBR","UR5"]
                
                for idx, status_word in enumerate(CHANNEL_STATUS):
                    try:
                        status_meaning = decode_channel_status_meaning(status_word)
                    except Exception:
                        status_meaning = {}
                    
                    for bit in bit_names:
                        if idx < len(widgets['bit_to_entrylist'][bit]):
                            entry = widgets['bit_to_entrylist'][bit][idx]
                            entry.config(state="normal")
                            entry.delete(0, END)
                            entry.insert(0, status_meaning.get(bit, ""))
                            entry.config(state="readonly")
            
           
            


            # Write to files
        
        else:  # B/D/F branch
            # Extract fields
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

           
    except Exception as e:
        print(f"Error processing RT data for {rt_name}: {e}")


def replay_from_file():
    global replay_running, replay_filepath, replay_paused
    
    if replay_running:
        status_var.set("❌ Replay already running!")
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
    
    # Start replay in a separate thread
    replay_thread = threading.Thread(target=replay_thread_func, daemon=True)
    replay_thread.start()

def replay_thread_func():
    global replay_running, replay_paused, jump_target_sec, replay_filepath
    
    try:
        with open(replay_filepath, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            while replay_paused:
                time.sleep(0.1)
                if not replay_running:
                    return
            
            # Check for jump request
            if jump_target_sec is not None:
                # Find line with matching SYS_SEC
                target_found = False
                for i, l in enumerate(lines):
                    if f"SYS_SEC: {jump_target_sec}" in l:
                        # Skip to this line
                        lines = lines[i:]
                        target_found = True
                        break
                
                if target_found:
                    status_var.set(f"↗️ Jumped to SYS_SEC: {jump_target_sec}")
                else:
                    status_var.set(f"❌ SYS_SEC {jump_target_sec} not found in file")
                
                jump_target_sec = None
                continue
            
            # Process line and update displays based on header
            # This would parse the line and update the appropriate RT display
            
            # Simulate real-time playback
            time.sleep(0.1)
            
        replay_running = False
        status_var.set("⏹️ Replay finished")
        
    except Exception as e:
        status_var.set(f"❌ Replay error: {e}")
        replay_running = False

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
        btn_pause_resume.config(text="Resume ▶")
        status_var.set("⏸️ Replay paused")
    else:
        btn_pause_resume.config(text="Pause ⏸")
        status_var.set("▶️ Replay resumed")

def stop_replay():
    global replay_running
    
    if replay_running:
        replay_running = False
        status_var.set("⏹️ Replay stopped")
    else:
        status_var.set("❌ No replay running")

def connexion():
    global ser, serialData, thread, thread2, clicked_com, clicked_bd
    
    if serialData:
        serialData = False
        ser.close()
        connect_btn["text"] = "Connect"
        status_var.set("Disconnected")
    else:
        port = clicked_com.get()
        baud = clicked_bd.get()
        
        try:
            ser = serial.Serial(port, baud, timeout=1)
            serialData = True
            thread = threading.Thread(target=readSerial, daemon=True)
            thread.start()
            thread2 = threading.Thread(target=process_data, daemon=True)
            thread2.start()
            connect_btn["text"] = "Disconnect"
            status_var.set(f"Connected to {port} at {baud} baud")
        except Exception as e:
            status_var.set(f"Connection error: {e}")

# Start the application
if __name__ == "__main__":
    connect_menu_init()
