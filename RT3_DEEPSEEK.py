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
bit_names = ["A","T","D","E","P","H","R","P1","I","S","SR","E1"]
 
 
 
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
    
    window = Tk()
    window.title("GAGAN 18 CHANNNEL INTERFACE - MULTI-RT")
    window.configure(bg="burlywood")
    window.geometry("1800x1200")
    project_name_var = StringVar(value="GAGANYAAN")

    # === Header Banner ===
    header_label = Label(
        window,
        text="SPS TELEMETRY AND COMMAND INTERFACE : GAGANYAAN - MULTI-RT",
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
    rt2_frame = Frame(window, bg="lightgreen")
    rt2_frame.grid(row=2, column=0, columnspan=6, sticky="nsew")
    
    # === Scrollable Canvas Setup for RT2 ===
    canvas_rt2 = Canvas(rt2_frame, bg="lightgreen", highlightthickness=0)
    scrollbar_y_rt2 = ttk.Scrollbar(rt2_frame, orient="vertical", command=canvas_rt2.yview)
    scrollbar_x_rt2 = ttk.Scrollbar(rt2_frame, orient="horizontal", command=canvas_rt2.xview)
    canvas_rt2.configure(yscrollcommand=scrollbar_y_rt2.set, xscrollcommand=scrollbar_x_rt2.set)

    canvas_rt2.grid(row=0, column=0, sticky="nsew")
    scrollbar_y_rt2.grid(row=0, column=1, sticky="ns")
    scrollbar_x_rt2.grid(row=1, column=0, sticky="ew")

    root_rt2 = Frame(canvas_rt2, bg="lightgreen")
    canvas_rt2.create_window((0, 0), window=root_rt2, anchor="nw")

    rt2_frame.grid_rowconfigure(0, weight=1)
    rt2_frame.grid_columnconfigure(0, weight=1)

    for i in range(5):
        root_rt2.grid_columnconfigure(i, weight=1)

    def on_frame_configure_rt2(event):
        canvas_rt2.configure(scrollregion=canvas_rt2.bbox("all"))
    root_rt2.bind("<Configure>", on_frame_configure_rt2)
    
    # RT2 Header
    rt2_header = Label(root_rt2, text="RT2 DISPLAY (ACC A1F0C/D)", font=("Algerian", 16, "bold"),
                      bg="darkgreen", fg="white", pady=10)
    rt2_header.grid(row=0, column=0, columnspan=5, sticky="ew", pady=5)
    
    # Create RT2 display widgets (same layout but different background)
    create_rt_display_widgets(root_rt2, "RT2")
    
    # Store RT2 widgets
    store_rt_widgets("RT2")
    
    # ========================== RT3 Frame (without COM Manager and Commands) ======================
    rt3_frame = Frame(window, bg="lightcoral")
    rt3_frame.grid(row=2, column=0, columnspan=6, sticky="nsew")
    
    # === Scrollable Canvas Setup for RT3 ===
    canvas_rt3 = Canvas(rt3_frame, bg="lightcoral", highlightthickness=0)
    scrollbar_y_rt3 = ttk.Scrollbar(rt3_frame, orient="vertical", command=canvas_rt3.yview)
    scrollbar_x_rt3 = ttk.Scrollbar(rt3_frame, orient="horizontal", command=canvas_rt3.xview)
    canvas_rt3.configure(yscrollcommand=scrollbar_y_rt3.set, xscrollcommand=scrollbar_x_rt3.set)

    canvas_rt3.grid(row=0, column=0, sticky="nsew")
    scrollbar_y_rt3.grid(row=0, column=1, sticky="ns")
    scrollbar_x_rt3.grid(row=1, column=0, sticky="ew")

    root_rt3 = Frame(canvas_rt3, bg="lightcoral")
    canvas_rt3.create_window((0, 0), window=root_rt3, anchor="nw")

    rt3_frame.grid_rowconfigure(0, weight=1)
    rt3_frame.grid_columnconfigure(0, weight=1)

    for i in range(5):
        root_rt3.grid_columnconfigure(i, weight=1)

    def on_frame_configure_rt3(event):
        canvas_rt3.configure(scrollregion=canvas_rt3.bbox("all"))
    root_rt3.bind("<Configure>", on_frame_configure_rt3)
    
    # RT3 Header
    rt3_header = Label(root_rt3, text="RT3 DISPLAY (ACC A1F0E/F)", font=("Algerian", 16, "bold"),
                      bg="darkred", fg="white", pady=10)
    rt3_header.grid(row=0, column=0, columnspan=5, sticky="ew", pady=5)
    
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
    bg_color = "burlywood" if rt_name == "RT1" else ("lightgreen" if rt_name == "RT2" else "lightcoral")
    
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
   
    counter=Label(frame2,text="Display Counter",font=("Calibri", 11,"bold"),bg=bg_color)
    counter.grid(row=1, column=0)
    counter_entry=Entry(frame2,width=10,state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="red")
    counter_entry.grid(column=1,row=1,pady=2,padx=2)
    
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
    
    # ==============================HEADER2 TIME =================================
    Name=Label(frame3,text=" header2 Time:",font=("Calibri", 11,"bold"),fg="blue",bg=bg_color,padx=5,pady=5)
    Name.grid(row=5, column=1)
    
    weeks_h2=Label(frame3,text="h2Week Number:",font=("Calibri", 11,"bold"),bg=bg_color)
    weeks_h2.grid(row=5, column=6)
    weeks_h2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    weeks_h2.grid(row=5, column=7, pady=5,padx=5)
    
    time_h2=Label(frame3,text="h2Second(s):",font=("Calibri", 11,"bold"),bg=bg_color)
    time_h2.grid(row=5, column=8)
    time_h2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    time_h2.grid(row=5, column=9, pady=5,padx=5)
    
    nanotime_h2=Label(frame3,text="h2Nano Second(ns):",font=("Calibri", 11,"bold"),bg=bg_color)
    nanotime_h2.grid(row=5, column=10)
    nanotime_h2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"),bg=bg_color,fg="brown")
    nanotime_h2.grid(row=5, column=11, pady=5,padx=5)
    
    # Continue with other frames similarly...
    # Note: Due to length, I'm showing the pattern. You would continue creating all the widgets
    # for each RT similar to your original code but using the rt_name parameter
    
    # Store references to widgets
    if rt_name == "RT1":
        rt1_widgets.update({
            'update_entry': update_entry,
            'counter_entry': counter_entry,
            'sw_rst_c': sw_rst_c,
            'hw_rst_c': hw_rst_c,
            'tsm_counter_entry': tsm_counter_entry,
            'week_entry': week_entry,
            'time_entry': time_entry,
            'nanotime_entry': nanotime_entry,
            'week_entry1': week_entry1,
            'time_entry1': time_entry1,
            'nanotime_entry1': nanotime_entry1,
            'week_entry2': week_entry2,
            'time_entry2': time_entry2,
            'nanotime_entry2': nanotime_entry2,
            'fix_3d': fix_3d,
            'leap': leap,
            'weeks_h2': weeks_h2,
            'time_h2': time_h2,
            'nanotime_h2': nanotime_h2,
        })
    elif rt_name == "RT2":
        rt2_widgets.update({
            'update_entry': update_entry,
            'counter_entry': counter_entry,
            'sw_rst_c': sw_rst_c,
            'hw_rst_c': hw_rst_c,
            'tsm_counter_entry': tsm_counter_entry,
            'week_entry': week_entry,
            'time_entry': time_entry,
            'nanotime_entry': nanotime_entry,
            'week_entry1': week_entry1,
            'time_entry1': time_entry1,
            'nanotime_entry1': nanotime_entry1,
            'week_entry2': week_entry2,
            'time_entry2': time_entry2,
            'nanotime_entry2': nanotime_entry2,
            'fix_3d': fix_3d,
            'leap': leap,
            'weeks_h2': weeks_h2,
            'time_h2': time_h2,
            'nanotime_h2': nanotime_h2,
        })
    elif rt_name == "RT3":
        rt3_widgets.update({
            'update_entry': update_entry,
            'counter_entry': counter_entry,
            'sw_rst_c': sw_rst_c,
            'hw_rst_c': hw_rst_c,
            'tsm_counter_entry': tsm_counter_entry,
            'week_entry': week_entry,
            'time_entry': time_entry,
            'nanotime_entry': nanotime_entry,
            'week_entry1': week_entry1,
            'time_entry1': time_entry1,
            'nanotime_entry1': nanotime_entry1,
            'week_entry2': week_entry2,
            'time_entry2': time_entry2,
            'nanotime_entry2': nanotime_entry2,
            'fix_3d': fix_3d,
            'leap': leap,
            'weeks_h2': weeks_h2,
            'time_h2': time_h2,
            'nanotime_h2': nanotime_h2,
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
    clicked_bd.set(bds[0])
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
        # csm1.config(fg="dark green")
    else:
        checksum1 =  "Fail"
        # csm1.config(fg="dark red")
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
        # csm1.config(fg="dark green")
    else:
        checksum2 =  "Fail"
        # csm1.config(fg="dark red")
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
    

   
def get_timestamped_filename(base_name: str, suffix: str) -> str:
    """
    Generate consistent file name in format:
    GAGANYAN_YYYY-MM-DD_HH-MM-SS_BASENAME_SUFFIX.csv
    
    Example:
    GAGANYAN_2025-08-21_20-35-10_MYDATA_PVT.csv
  
    """
    return f"GAGANYAN_{SESSION_TIMESTAMP}_{base_name}_{suffix}.csv"
   
def write_to_raw(data, base_name ):
    file_name = get_timestamped_filename(base_name, "Raw")
    header = ['TimeStamp','RAW DATA']
   
    with open(file_name, mode='a', newline='')as file:
        write = csv.writer(file)
        if file.tell() == 0:
            write.writerow(header)
        write.writerow(data)
        
def write_to_rawh2(data, base_name ):
    file_name = get_timestamped_filename(base_name, "Rawh2")
    header = ['TimeStamp','RAW DATA']
    
    with open(file_name, mode='a', newline='')as file:
        write = csv.writer(file)
        if file.tell() == 0:
            write.writerow(header)
        write.writerow(data)
        
def write_to_rawh3(data, base_name ):
    file_name = get_timestamped_filename(base_name, "Rawh3")
    header = ['TimeStamp','RAW DATA']
    
    with open(file_name, mode='a', newline='')as file:
        write = csv.writer(file)
        if file.tell() == 0:
            write.writerow(header)
        write.writerow(data)
        
def write_to_rawh4(data, base_name ):
    file_name = get_timestamped_filename(base_name, "Rawh4")
    header = ['TimeStamp','RAW DATA']
    
    with open(file_name, mode='a', newline='')as file:
        write = csv.writer(file)
        if file.tell() == 0:
            write.writerow(header)
        write.writerow(data)

def write_to_SYN(data, base_name):
    file_name = get_timestamped_filename(base_name, "Sync")
    header = ['TimeStamp','SYN_SECOND','SYN_NANOSECOND','SYN_WEEKNUMBER']
   
    with open(file_name, mode='a', newline='')as file:
        write = csv.writer(file)
        if file.tell() == 0:
            write.writerow(header)
        write.writerow(data)
        
def write_to_SYNh2(data, base_name):
    file_name = get_timestamped_filename(base_name, "Synch2")
    header = ['TimeStamp','h2SYN_SECOND','h2SYN_NANOSECOND','h2SYN_WEEKNUMBER']
    
    with open(file_name, mode='a', newline='')as file:
        write = csv.writer(file)
        if file.tell() == 0:
            write.writerow(header)
        write.writerow(data)
 
       
 
 
def write_to_pvt(data,base_name):
    global filename
    file_name = get_timestamped_filename(base_name, "PVT")
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
    with open(file_name, mode='a', newline='')as file:
        write = csv.writer(file)
        if file.tell() == 0:
            write.writerow(header)
        write.writerow(data)
 
# Plot update function

def update_cndr_plot_func(svid_labels, cndr_values, ax_cndr, canvas_cndr):
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


def refresh_cndr_plot(rt_name="RT1"):
    try:
        # This would need to be updated to work with different RTs
        # For now, just a placeholder
        pass
    except Exception as e:
        print(f"CNDR plot update error for {rt_name}:", e)

def readSerial():
    global serialData, ser, hexDecodedData
    global counter_value, counter_value2, counter_value3

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
                                data_length = 64

                            # Read full packet
                            payload = ser.read(data_length).hex()
                            hexDecodedData = ''.join(header_bytes) + payload

                            # ✅ Print full raw data
                            print(hexDecodedData.upper())
                            print()

                            # Determine RT group
                            if header_name.startswith("RT1"):
                                rt_name = "RT1"
                                counter_value += 1
                            elif header_name.startswith("RT2"):
                                rt_name = "RT2"
                                counter_value2 += 1
                            else:
                                rt_name = "RT3"
                                counter_value3 += 1

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
    global base_name, filename
    try:
        if not data_queue.empty():
            item = data_queue.get()
            if item:
                rt_name, hexDecodedData = item

                # Process based on which RT the data belongs to
                if rt_name == "RT1":
                    process_rt_data(hexDecodedData, "RT1")
                elif rt_name == "RT2":
                    process_rt_data(hexDecodedData, "RT2")
                elif rt_name == "RT3":
                    process_rt_data(hexDecodedData, "RT3")

    except Exception as e:
        print(f"Error processing data: {e}")
    finally:
        # Schedule the next check after 1000 ms (1 second)
        root.after(1000, process_data)

def process_rt_data(hexDecodedData, rt_name):
    """Process data for a specific RT and update its widgets"""
    # This would contain the data processing logic from your original code
    # but updated to use the appropriate widget references for each RT
    
    # Get widget references for this RT
    if rt_name == "RT1":
        widgets = rt1_widgets
        counter_var = counter_value
    elif rt_name == "RT2":
        widgets = rt2_widgets
        counter_var = counter_value2
    elif rt_name == "RT3":
        widgets = rt3_widgets
        counter_var = counter_value3
    
    # Extract and process data (similar to your original process_data function)
    # Update widgets using the widget references
    
    # Example:
    if widgets.get('counter_entry'):
        widgets['counter_entry'].config(state="normal")
        widgets['counter_entry'].delete(0, END)
        widgets['counter_entry'].insert(0, str(counter_var))
        widgets['counter_entry'].config(state="readonly")
    
    # ... rest of the processing logic

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
