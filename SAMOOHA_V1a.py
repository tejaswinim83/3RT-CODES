# -*- coding: utf-8 -*-
"""
Created on Mon Aug 17 16:24:56 2026

@author: Adminservice
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 14:24:03 2026

@author: Adminservice
"""

# -*- coding: utf-8 -*-
"""
Created on Sat May 30 10:43:31 2026 

@author: Adminservice


"""

# -*- coding: utf-8 -*-
"""
Created on Fri May 22 15:29:39 2026

@author: Adminservice
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 16:12:52 2026

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Dec  9 09:15:25 2025

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 11:03:11 2025

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 09:35:03 2025

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 11:32:02 2025

@author: Admin
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 10:07:17 2025

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Sep 16 13:21:37 2025

@author: Adminservice
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Aug 21 13:55:41 2025

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 08:53:39 2025

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 09:09:07 2025

@author: Admin
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 14:10:26 2025

@author: Adminservice
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 14:46:55 2025

@author: Adminservice
"""

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
import time as pytime
import csv
from tkinter import Radiobutton, StringVar
from datetime import datetime
import os
import platform
import sys
import re
import bisect
from PIL import Image, ImageTk
import numpy as np

# Matplotlib Imports with Toolbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


# Global controls
replay_running = False
replay_paused = False
jump_target_sec = None
replay_filepath = None
latest_sys_second = 0
sys_second_lock = threading.Lock()
replay_thread = None  # ✅ Track replay thread for proper restart/stop

SESSION_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


serialData=False
ser=None
replay_data = []       # Stores [(SYS_Second, hex_data), ...]
replay_index = 0       # Current packet index
jump_pending = None    # Target value for jump request
jump_lock = threading.Lock()  # Thread-safe jump flag
process_data_thread = None  # Telemetry processor for replay mode


# ==================== GLOBAL STATE (Fixes Stop Button Issue) ====================
# ✅ These MUST be global so threads and functions can access/modify them
sa_active = {"SA1": False, "SA2": False, "SA3": False, "SA4": False,"SA5_9(ISL)":False,"SA10_11(ISR)":False,"SA12":False}
sa_stop_btns = {}  # ✅ Global dictionary to store button references
serial_write_lock = threading.Lock() # ✅ Prevents packet corruption during simultaneous sends

# ================= PRECISE FILE DATA =================

precise_data = []          # Stores complete precise rows
precise_times = []         # Stores only TOW values for fast binary search
precise_loaded = False
current_time_diff = 0.0    # holds the latest difference


display_name = "SAMOOHA"

# Plotting & Telemetry Registers
PLOT_REGISTRY = {}
GLOBAL_TELEMETRY_LOG = []
PLOTABLE_ENTRIES = []
MAX_PLOT_POINTS = 3600 # Caps points per plot to prevent memory leaks (~1 hour at 1 Hz)

_PLOT_UPDATE_THREAD = None
_PLOT_STOP_EVENT = threading.Event()

# Professional display names for telemetry entries
PARAM_NAME_MAP = {
    "time_entry": "SYNC Second(s)", "nanotime_entry": "SYNC Nano Second(ns)", "week_entry": "SYNC Week Number",
    "time_entry1": "SYS Second(s)", "nanotime_entry1": "SYS Nano Second(ns)", "week_entry1": "SYS Week Number",
    "time_entry3": "PPS Second(s)", "nanotime_entry3": "PPS Nano Second(ns)", "week_entry3": "PPS Week Number",
    "position_entry": "INST X(m)", "position_entry1": "INST Y(m)", "position_entry2": "INST Z(m)",
    "velocity_entry": "INST Vel_x(m/s)", "velocity_entry1": "INST Vel_y(m/s)", "velocity_entry2": "INST Vel_z(m/s)",
    "position_entry3": "ODP INT X(m)", "position_entry4": "ODP INT Y(m)", "position_entry5": "ODP INT Z(m)",
    "velocity_entry3": "ODP INT Vel_x(m/s)", "velocity_entry4": "ODP INT Vel_y(m/s)", "velocity_entry5": "ODP INT Vel_z(m/s)",
    "pdop": "PDOP", "cb": "Clock Bias", "icb": "Inter-System Bias", "drift": "Drift", "isd": "Inter-System Drift",
    "st_bias": "Steering Bias", "st_drift": "Steering Drift", "clk_crr": "Steering Clock", "U1": "U1", "U2": "U2",
    "swdt": "SWDT Reset Counter", "last_cmd_b1_b2": "Last Cmd B1_B2", "last_cmd_b3": "Last Cmd B3", "last_cmd_b4": "Last Cmd B4",
    "acq1_svid": "ACQ1 SVID", "mc": "Memory Count", "lrt": "Last Reset Time",
    "update_entry": "Update Counter", "fix_status": "PPS 3D Fix", "flag": "ODP Flag",
    "csm": "Checksum SA2", "csm1": "Checksum SA4",
    "tele_cmd_counter": "Tele CMD Counter", "upset_cmd_counter": "Upset CMD Counter",
    "sol": "Sol", "pos_e": "POS EST", "alm": "ALM", "time": "Time", "d2_3d": "Pos Mode", "pos": "POS",
    "ccsds": "Swap_mil_flag", "rand": "Rand_sts", "space_crf_id": "S_cft_id", "navic_cmd": "N_CMD",
    "odp": "ODP Status", "phase_center": "Phase Center Corr", "phase_center_sps": "Phase Cen for SPS",
    "port1": "PORT1", "port2": "PORT2",
    "tmillcond": "Illum Cond Val", "tmillcondlim": "Illum Cond Limit",
    "pre_chk_cntr": "Pre Check Counter", "post_chk_cntr": "Post Check Counter",
    "cond_pre": "Cond Pre Check", "cond_post": "Cond Post Check", "odp_prop": "ODP_PROP Used",
    "raw_data":"Raw_data","remote1_entry":"Remote read write1","remote2_entry":"Remote read write2","remote3_entry":"Remote read write3",
    "remote4_entry":"Remote read write4","remote5_entry":"Remote read write5","remote6_entry":"Remote read write6",
    "est_rec_clk_entry":"Est_Rec_Clk","est_rec_clk_bias_entry":"Est_Rec_Clk_Bias","LCOR_entry":"LCOR","str_crr_clk_entry":"Str_Crr_Clk",
     "diff_entry":"Precise Time_Diff","time_entry4":"Inst Pos Error(m)","nanotime_entry4":"Inst Vel Error(cm/s)",
    "odp_vel_err_entry":"ODP Vel Error(cm/s)","odp_pos_err_entry":"ODP Pos Error(m)",
    

}





data_queue = queue.Queue()
commands = {
    "playback-off": "0x0002", "playback-on": "0x0003",
    "storage-on": "0x0004", "storage-off": "0x0005",
    "sps-mvn-on": "0x0006", "sps-mvn-off": "0x0007",
    "Inter_card_mode=1": "0x0008", "Inter_card_mode=0": "0x0009",
    "System Model=1": "0x000A", "System Model=2": "0x000B", "System Model=3": "0x000C",
    "RaimChk1En=1": "0x000D", "RaimChk1Dis=0": "0x000E",
    "CarSmtEn=1": "0x000F", "CarSmtDis=0": "0x0010",
    "IonoCorrectionEn=1": "0x0011", "IonoCorrectionDis=0": "0x0012",
    "epheRetainEn=1": "0x0015", "epheRetainDis=0": "0x0016",
    "prRejectEn=1": "0x0017", "prRejectEn=0": "0x0018",
    "g_bl_TclillCondPreCheckEnable=1": "0x0019", "g_bl_TclillCondPreCheckDisable=0": "0x001A",
    "g_bl_SwapMilDisp=1": "0x001B", "g_bl_SwapMilDisp=0": "0x001C",
    "g_bl_TcLeoboundCheckEnable=1": "0x01D", "g_bl_TcLeoboundCheckDisable=0": "0x001E",
    "g_bl_TclillCondEnable=1": "0x001F", "g_bl_TclillCondDisable=0": "0x0020",
    "Use_Cmd_Intercard_delay=1": "0x0021", "Use_Cmd_Intercard_delay=0": "0x0022",
    "g_bl_TclillCondRegularizeEnable=1": "0x0023", "g_bl_TclillCondRegularizeDisable=0": "0x0024",
    "NavMsgEn=1": "0x0025", "NavMsgEn=0": "0x0026",
    "velocity-smoothing-E": "0x0027", "velocity-smoothing-D": "0x0028",
    "Remote_Write_En1=0x0f": "0x002A", "Remote_Read_En1=0x0f": "0x002B", "Remote_Write_En2=0x0f": "0x002C",
    "mission_phase=0": "0x0030", "mission_phase=1": "0x0031", 
    "clk_streeing_en=1": "0x0032","clk_streeing_dis=0": "0x0033", 
    "time_alignment_en=1": "0x0034", "time_alignment_dis=0": "0x0035",
    "conditional_loop_controls=0": "0x0035", "conditional_loop_controls=1": "0x0036",
    "iono smoothing En =1":"0x0038","iono smoothing Dis =0":"0x0039",
    "Intercard_Testing_mode=1": "0x003A", "Intercard_Testing_mode=0": "0x003B",
    "PR_Before_Sync_Enable=0": "0x003C", "PR_Before_Sync_Disable=1": "0x003D",
    "F_Mem_Conf_Err_Chk=0": "0x003E", "F_Mem_Conf_Err_Chk=1": "0x003F",
    "elevation logic D": "0x0040", "elevation logic E": "0x0041",
    "swdt flag En = 0": "0x0042", "swdt flag Dis = 1": "0x0043",
    "Orbit_phase=0,Reset_ODP_Soft=1": "0x0044", "Orbit_phase=1,Reset_ODP_Soft=1": "0x0045",
    "Range log=0": "0x0046", "Range log=1": "0x0047",
    "EnablePhc=0": "0x004C", "DisablePhc=1": "0x004D",
    "EnablePh_SPS=0": "0x004E", "DisablePh_SPS=1": "0x004F",
    "Reset_ODP_Soft=1": "0x0050", "odp En = 1": "0x0051", "odp Dis =0": "0x0052",
    "odp 10s E": "0x0053", "odp 10s D": "0x0054",
    "ODPinitiaizefilter(14)": "0x0055", "GLblOdpEopTc = True": "0x0056", "GLblOdpEopTc = False": "0x0057",
    "GlblOdpAntPhcTc = true": "0x0058", "GlblOdpAntPhcTc = flase": "0x0059",
    "GlblODPManEnabledTc =true": "0x005A", "GlblODPManDisabledTc =false": "0x005B",
    "GLenOdpMode = odpTest": "0x005C", "GLenOdpMode = odpEnabled": "0x005D",
    "GlenOdpMode = odpDisabled": "0x005E", 
    "Use_adaptive_acq_threshod_port1=1": "0x005F","Use_adaptive_acq_threshod_port1=0": "0x0060",
    "Use_adaptive_acq_threshod_port2=1": "0x0061", "Use_adaptive_acq_threshod_port2=0": "0x0062",
    "Use_adaptive_acq_threshod_port3=1": "0x0063","Use_adaptive_acq_threshod_port3=0": "0x0064",
    "Carrier_Aiding_value = 1": "0x0065","Carrier_Aiding_value =0": "0x0066",
    "Unconditional_doppler_aiding = 1,conditional_doppler_aiding=0": "0x0067",
    "Unconditional_doppler_aiding = 0,conditional_doppler_aiding=1": "0x0068",
    "Unconditional_doppler_aiding = 0,conditional_doppler_aiding=0": "0x0069",
    "Enable_EV_port_as_AEV_high_doppler_rate_addr=0,Enable_AEV_port_as_EV_high_sensitivity_addr=1": "0x006A",
    "Enable_EV_port_as_AEV_high_doppler_rate_addr=1,Enable_AEV_port_as_EV_high_sensitivity_addr=0": "0x006B",
    "Fll_Control_value=0":"0x006C","Fll_Control_value=1":"0x006D",
    "resetFlag=1,resetID=14":"0x006F",
    "Configure_Loops=0":"0x0070","Configure_Loops=1":"0x0071",
    "Enable_global_35ms_int_timer_port1_addr=0":"0x0072","Enable_global_35ms_int_timer_port1_addr=1":"0x0073",
    "Enable_global_64ms_int_timer_port1_addr=0":"0x0074","Enable_global_64ms_int_timer_port1_addr=1":"0x0075",
    "Enable_global_64ms_timer_port3_addr=0":"0x0076","Enable_global_64ms_timer_port1_addr=1":"0x0077",
    "Enable_global_15ms_timer_port3_addr=0":"0x0078","Enable_global_15ms_timer_port1_addr=1":"0x0079",
    #TYPE B
    "GEO_SPS-L1-Track Threshold Ev": "0x80B1", "GEO_SPS-L1-Track Threshold Aev": "0x81B1",
    "GEO_SPS-L1-ACQ Threshold Ev": "0x83B1", "GEO_SPS-L1-ACQ Threshold Aev": "0x84B1",
    "GEO_SPS-L1-ACQ Threshold Aev Navic": "0x85B1",
    "GEO_SPS-Carrier Smoothing Limit Value": "0x86B1","GEO_SPS-Carrier Smoothing Restart Value": "0x87B1",
    "Look_angle_flags(Polarity reversal)":"0x88B1","Remote Address 1":"0x89B1","Remote Address 2":"0x8AB1",
    "Remote Data 1":"0x8BB1","Remote Data 2":"0x8CB1","Remote Mask 1":"0x8DB1","Remote Mask 2":"0x8EB1",
    "GEO-SPS IONOSPHERE ALPHA FACTOR WORD":"0x90B1","GEO-SPS IONO Dense Height Word":"0x91B1",
    "DOP Limit":"0x93B1","MBYT Value":"0x94B1","DOP Limit1":"0x95B1","DOP Limit2":"0x96B1","PPS Count Check":"0x97B1",
    "Bit_sync_lower_bound_value":"0xA5","Margin_factor_acq_AEV_NAVIC":"0xA6","Margin_factor_acq_EV_GPS":"0xA7",
    "Height_limit_EV_AEV_switch_val":"0xA8","Bit_sync_lower_threshold_value_N_AVIC":"0xA9","Bit_sync_upper_threshold_value_N_AVIC":"0xAA",
    "Week Roll over Value":"0xAB","Wdt Time ValueReg":"0xAC","AntPortConf":"0xAD","Intercard_Del_Nav_Ports":"0xAE","Prog Hardware Delay":"0xB0",
    "Elevation Angle Threshold":"0xB1","QIB_Threshold":"0xB2","No_of_leapSeconds_GPS":"0xB4","Loop_BW_Value":"0xB5",
    "Ant_dig_combining_control":"0xB6","Tracking_counter_Val":"0xB7","FPGA_pll_order4_val":"0xB8","time_diff_PR_DR":"0xB9",
    "NavIC_Almanac_value":"0xBA","Almanac_restore_time":"0xBB","Intercard_Del_GPS_Port":"0xBD","Range_limit":"0xBE","DRange_limit":"0xBF",

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
def set_status_colored(entry, value):
    """Thread-safe update with existence check."""
    try:
        if not entry.winfo_exists():
            return

        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, str(value))

        val = str(value).lower()
        if "enabled" in val or "unlocked" in val or "on" in val or "GPS" in val or "GPS only" in val or "GPS" in val:
            entry.config(fg="dark green")
        elif "disabled" in val or "locked" in val or "off" in val:
            entry.config(fg="dark red")
        elif "GPS+NAVIC" in val:
            entry.config(fg="blue")
        elif "NavIC" in val or "NAVIC only" in val:
            entry.config(fg="orange")
        elif "GPS + NAVIC + SBAS" in val :
            entry.config(fg="purple")
        else:
            entry.config(fg="black")

        entry.config(state="readonly")
    except Exception:
        pass  # Widget already destroyed, ignore error

    entry.config(state="readonly")



def connect_menu_init():
    global root,output_text,END,NORMAL,Button,Label,Entry,LabelFrame,Frame,Tk,Canvas,OptionMenu
    global frame1,project_entry,port_label,refresh_btn,port_bd,file_bd,file_entry1,connect_btn,status_label,manual_data_entry,file_entry,jump_entry,btn_pause_resume
    global send_btn,drop_COM,drop_bd
    global frame2,update_entry,counter_entry,mc,tele_cmd_counter,upset_cmd_counter,mux_entry,tele_entries
    global frame3,time_entry,nanotime_entry,week_entry,time_entry1,nanotime_entry1,week_entry1,time_entry2,nanotime_entry2,week_entry2
    global fix_status,time_entry3,nanotime_entry3,week_entry3
    global frame5,position_entry,velocity_entry,position_entry1,velocity_entry1,position_entry2,velocity_entry2
    global frame4,sol,pos_e,alm,time,d2_3d, position,ccsds,rand,space_crf_id,navic_cmd
    global frame5,position_entry3,velocity_entry3,position_entry4,velocity_entry4,position_entry5,velocity_entry5
    global frame6,flag,flag1,frame_bus
    global diff_entry,time_entry4,nanotime_entry4,odp_pos_err_entry,odp_vel_err_entry
    global frame7,csm,csm1
    global frame8,channel,svid,iode,t,p,e,d,i,r,h,a,cndr,pr,dr
    global ch1,ch2,ch3,ch4,ch5,ch6,ch7,ch8,ch9,ch10,ch11,ch12,iode1,iode2,iode3,iode4,iode5,iode6,iode7,iode8,iode9,iode10,iode11,iode12,svid1,svid2,svid3,svid4,svid5
    global dr1,dr2,dr3,dr4,dr5,dr6,dr7,dr8,dr9,dr10,dr11,dr12,pr1,pr2,pr3,pr4,pr5,pr6,pr7,pr8,pr9,pr10,pr11,pr12,svid6,svid7,svid8,svid9,svid10,svid11,svid12
    global cndr1,cndr2,cndr3,cndr4,cndr5,cndr6,cndr7,cndr8,cndr9,cndr10,cndr11,cndr12,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,e1,e2,e3,e4,e5,e6,e7,e8,e9,e10,e11,e12
    global p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12,i1,i2,i3,i4,i5,i6,i7,i8,i9,i10,i11,i12
    global a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11,a12,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12
    global frame9,cb,icb,drift,isd,st_bias,st_drift,clk_crr,U1,U2,word32_entries,last_cmd_b1_b2,last_cmd_b3,last_cmd_b4,acq1_svid,port1,port2
    global frame10,pdop
    global frame11,swdt,lbl,entry,lrt,SI,iode,crs,odp,phase_center,phase_center_sps
    global remote1_entry,remote2_entry,remote3_entry,remote4_entry,remote5_entry,remote6_entry,est_rec_clk_entry,est_rec_clk_bias_entry,LCOR_entry,str_crr_clk_entry
    global frame13,btn
    global status_var,status_var1,bus_var,dataword_entry,dataword_entry1,gui_entry_dict,wdt_entries,word25_entries,odp_entries
    global frame14,lbl,entry,label,ttf,TTF
    global frame15,raw_data
    global frame_cndr_plot,ax_cndr,canvas_cndr,cmd_btn,btn_replay,display_name
    global tmillcond,tmillcondlim,cond_pre,cond_post,odp_prop,pre_chk_cntr,post_chk_cntr
    global sa8_w3_entry,sa8_w4_entry,sa8_w5_entry,sa8_w6_entry,sa8_w7_entry,sa8_w8_entry,sa8_w9_w10_entry,sa8_w11_w12_entry,sa8_w13_w14_entry,sa8_w15_w16_entry,sa8_w17_w18_entry
    global sa8_w19_w20_entry,sa8_w21_w22_entry,sa8_w23_w24_entry,sa8_w25_w26_entry,sa8_w27_w28_entry,sa8_w29_w30_entry,sa8_w31_w32_entry
    global sa9_w1_entry,sa9_w2_entry,sa9_w3_entry,sa9_w4_entry,sa9_w5_entry,sa9_w6_entry,sa9_w7_entry,sa9_w8_entry,sa9_w9_entry,sa9_w10_entry,sa9_w11_entry,sa9_w12_entry,sa9_w13_entry
    global sa9_w14_w15_entry,sa9_w16_w17_entry,sa9_w18_w19_entry,sa9_w20_w21_entry,sa9_w22_w23_entry,sa9_w24_w25_entry,sa9_w26_entry,sa9_w27_entry,sa9_w28_entry,sa9_w29_entry,sa9_w30_w31_entry,sa9_w32_entry
    global sa10_w1_entry,sa10_w2_entry,sa10_w3_entry,sa10_w4_entry,sa10_w5_entry,sa10_w6_entry,sa10_w7_entry,sa10_w8_entry,sa10_w9_w10_entry
    global sa10_w11_w12_entry,sa10_w13_w14_entry,sa10_w15_entry,sa10_w16_entry,sa10_w17_entry,sa10_w18_entry,sa10_w19_entry,sa10_w20_entry
    global sa10_w21_entry,sa10_w22_entry,sa10_w23_w24_entry,sa10_w25_w26_entry,sa10_w27_w28_entry,sa10_w29_w30_entry,sa10_w31_w32_entry
    global sa11_w1_w2_entry,sa11_w3_w4_entry,sa11_w5_w6_entry,sa11_w7_w8_entry,sa11_w9_w10_entry,sa11_w11_w12_entry,sa11_w13_w14_entry
    global sa11_w15_entry,sa11_w16_entry,sa11_w17_w18_entry,sa11_w19_entry,sa11_w20_entry,sa11_w21_entry,sa11_w22_entry,sa11_w23_entry
    global sa11_w24_entry,sa11_w25_w26_entry,sa11_w27_w28_entry,sa11_w29_entry,sa11_w30_w31_entry,sa11_w32_entry
    global sa12_w1_entry,sa12_w2_entry,sa12_w3_entry,sa12_w4_entry,sa12_w5_entry,sa12_w6_entry,sa12_w7_entry,sa12_w8_entry,sa12_w9_entry,sa12_w10_entry,sa12_w11_entry,sa12_w12_entry,sa12_w13_entry,sa12_w14_entry
    global sa12_w15_entry,sa12_w16_entry,sa12_w17_entry,sa12_w18_entry,sa12_w19_w20_entry,sa12_w21_w22_entry,sa12_w23_w24_entry,sa12_w25_w26_entry,sa12_w27_w28_entry,sa12_w29_w30_entry,sa12_w31_entry,sa12_w32_entry
    global sa13_w1_entry,sa13_w2_entry,sa13_w3_entry,sa13_w4_entry,sa13_w5_entry,sa13_w6_entry,sa13_w7_entry,sa13_w8_entry,sa13_w9_entry,sa13_w10_entry,sa13_w11_entry,sa13_w12_entry,sa13_w13_entry,sa13_w14_entry
    global sa13_w15_entry,sa13_w16_entry,sa13_w17_entry,sa13_w18_entry,sa13_w19_entry,sa13_w20_entry,sa13_w21_entry,sa13_w22_entry,sa13_w23_entry,sa13_w24_entry,sa13_w25_entry,sa13_w26_entry,sa13_w27_entry,sa13_w28_entry,sa13_w29_entry,sa13_w30_entry,sa13_w31_entry,sa13_w32_entry
    global sa14_w1_entry,sa14_w2_entry,sa14_w3_entry,sa14_w4_entry,sa14_w5_entry,sa14_w6_entry,sa14_w7_entry,sa14_w8_entry,sa14_w9_entry,sa14_w10_entry,sa14_w11_entry,sa14_w12_entry,sa14_w13_entry,sa14_w14_entry
    global sa14_w15_entry,sa14_w16_entry,sa14_w17_entry,sa14_w18_entry,sa14_w19_entry,sa14_w20_entry,sa14_w21_entry,sa14_w22_entry,sa14_w23_entry,sa14_w24_entry,sa14_w25_entry,sa14_w26_entry,sa14_w27_entry,sa14_w28_entry,sa14_w29_entry,sa14_w30_entry,sa14_w31_entry,sa14_w32_entry
    global sa15_w1_entry,sa15_w2_entry,sa15_w3_w4_entry,sa15_w5_w6_entry,sa15_w7_w8_entry,sa15_w9_w10_entry,sa15_w11_w12_entry,sa15_w13_w14_entry,sa15_w15_w16_entry,sa15_w17_w18_entry
    global sa15_w19_w20_entry,sa15_w21_w22_entry,sa15_w23_w24_entry,sa15_w25_w26_entry,sa15_w27_w28_entry,sa15_w29_w30_entry,sa15_w31_entry,sa15_w32_entry
    global sa16_w1_entry,sa16_w2_entry,sa16_w3_w4_entry,sa16_w5_entry,sa16_w6_entry,sa16_w7_entry,sa16_w8_w9_entry,sa16_w10_w11_entry,sa16_w12_w13_entry,sa16_w14_w15_entry,sa16_w16_w17_entry,sa16_w18_w19_entry,sa16_w20_w21_entry,sa16_w22_w23_entry
    global sa16_w24_w29_entry,sa16_w30_w31_entry,sa16_w32_entry
    global sa17_w1_entry,sa17_w2_entry,sa17_w3_entry,sa17_w4_entry,sa17_w5_entry,sa17_w6_entry,sa17_w7_entry,sa17_w8_entry,sa17_w9_entry,sa17_w10_entry,sa17_w11_entry,sa17_w12_entry,sa17_w13_entry,sa17_w14_entry
    global sa17_w15_entry,sa17_w16_entry,sa17_w17_entry,sa17_w18_entry,sa17_w19_entry,sa17_w20_entry,sa17_w21_entry,sa17_w22_entry,sa17_w23_entry,sa17_w24_entry,sa17_w25_entry,sa17_w26_w30_entry,sa17_w31_entry,sa17_w32_entry
    global sa18_w1_entry,sa18_w2_entry,sa18_w3_entry,sa18_w4_entry,sa18_w5_entry,sa18_w6_entry,sa18_w7_entry,sa18_w8_entry,sa18_w9_entry,sa18_w10_entry,sa18_w11_entry,sa18_w12_entry,sa18_w13_entry,sa18_w14_entry
    global sa18_w15_entry,sa18_w16_entry,sa18_w17_entry,sa18_w18_entry,sa18_w19_entry,sa18_w20_entry,sa18_w21_entry,sa18_w22_entry,sa18_w23_entry,sa18_w24_entry,sa18_w25_entry,sa18_w26_w30_entry,sa18_w31_entry,sa18_w32_entry
    global sa19_w1_entry,sa19_w2_entry,sa19_w3_entry,sa19_w4_entry,sa19_w5_entry,sa19_w6_entry,sa19_w7_entry,sa19_w8_entry,sa19_w9_entry,sa19_w10_entry,sa19_w11_entry,sa19_w12_entry,sa19_w13_entry,sa19_w14_entry
    global sa19_w15_entry,sa19_w16_entry,sa19_w17_entry,sa19_w18_entry,sa19_w19_entry,sa19_w20_entry,sa19_w21_entry,sa19_w22_entry,sa19_w23_entry,sa19_w24_entry,sa19_w25_entry,sa19_w26_entry,sa19_w27_entry,sa19_w28_entry,sa19_w29_entry,sa19_w30_entry,sa19_w31_entry,sa19_w32_entry
    global sa20_w1_entry,sa20_w2_entry,sa20_w3_entry,sa20_w4_entry,sa20_w5_entry,sa20_w6_entry,sa20_w7_entry,sa20_w8_entry,sa20_w9_entry,sa20_w10_entry,sa20_w11_entry,sa20_w12_entry,sa20_w13_entry,sa20_w14_entry
    global sa20_w15_entry,sa20_w16_entry,sa20_w17_entry,sa20_w18_entry,sa20_w19_entry,sa20_w20_entry,sa20_w21_entry,sa20_w22_entry,sa20_w23_entry,sa20_w24_entry,sa20_w25_entry,sa20_w26_entry,sa20_w27_entry,sa20_w28_entry,sa20_w29_entry,sa20_w30_entry,sa20_w31_entry,sa20_w32_entry
    global sa21_w1_entry,sa21_w2_entry,sa21_w3_entry,sa21_w4_entry,sa21_w5_entry,sa21_w6_entry,sa21_w7_entry,sa21_w8_entry,sa21_w9_entry,sa21_w10_entry,sa21_w11_entry,sa21_w12_entry,sa21_w13_entry,sa21_w14_entry
    global sa21_w15_entry,sa21_w16_entry,sa21_w17_entry,sa21_w18_entry,sa21_w19_entry,sa21_w20_entry,sa21_w21_entry,sa21_w22_entry,sa21_w23_entry,sa21_w24_entry,sa21_w25_entry,sa21_w26_entry,sa21_w27_entry,sa21_w28_entry,sa21_w29_entry,sa21_w30_entry,sa21_w31_entry,sa21_w32_entry
    global sa22_w1_entry,sa22_w2_entry,sa22_w3_entry,sa22_w4_entry,sa22_w5_entry,sa22_w6_entry,sa22_w7_entry,sa22_w8_entry,sa22_w9_entry,sa22_w10_entry,sa22_w11_entry,sa22_w12_entry,sa22_w13_entry,sa22_w14_entry
    global sa22_w15_entry,sa22_w16_entry,sa22_w17_entry,sa22_w18_entry,sa22_w19_entry,sa22_w20_entry,sa22_w21_entry,sa22_w22_entry,sa22_w23_entry,sa22_w24_entry,sa22_w25_entry,sa22_w26_entry,sa22_w27_entry,sa22_w28_entry,sa22_w29_entry,sa22_w30_entry,sa22_w31_entry,sa22_w32_entry
    global sa23_w1_entry,sa23_w2_entry,sa23_w3_entry,sa23_w4_entry,sa23_w5_entry,sa23_w6_entry,sa23_w7_entry,sa23_w8_entry,sa23_w9_entry,sa23_w10_entry,sa23_w11_entry,sa23_w12_entry,sa23_w13_entry,sa23_w14_entry
    global sa23_w15_entry,sa23_w16_entry,sa23_w17_entry,sa23_w18_entry,sa23_w19_entry,sa23_w20_entry,sa23_w21_entry,sa23_w22_entry,sa23_w23_entry,sa23_w24_entry,sa23_w25_entry,sa23_w26_entry,sa23_w27_entry,sa23_w28_entry,sa23_w29_entry,sa23_w30_entry,sa23_w31_entry,sa23_w32_entry
    global sa24_w1_entry,sa24_w2_entry,sa24_w3_entry,sa24_w4_entry,sa24_w5_entry,sa24_w6_entry,sa24_w7_entry,sa24_w8_entry,sa24_w9_entry,sa24_w10_entry,sa24_w11_entry,sa24_w12_entry,sa24_w13_entry,sa24_w14_entry
    global sa24_w15_entry,sa24_w16_entry,sa24_w17_entry,sa24_w18_entry,sa24_w19_entry,sa24_w20_entry,sa24_w21_entry,sa24_w22_entry,sa24_w23_entry,sa24_w24_entry,sa24_w25_entry,sa24_w26_entry,sa24_w27_entry,sa24_w28_entry,sa24_w29_entry,sa24_w30_entry,sa24_w31_entry,sa24_w32_entry
    global sa25_w1_entry,sa25_w2_entry,sa25_w3_entry,sa25_w4_entry,sa25_w5_entry,sa25_w6_entry,sa25_w7_entry,sa25_w8_entry,sa25_w9_entry,sa25_w10_entry,sa25_w11_entry,sa25_w12_entry,sa25_w13_entry,sa25_w14_entry
    global sa25_w15_entry,sa25_w16_entry,sa25_w17_entry,sa25_w18_entry,sa25_w19_entry,sa25_w20_entry,sa25_w21_entry,sa25_w22_entry,sa25_w23_entry,sa25_w24_entry,sa25_w25_entry,sa25_w26_entry,sa25_w27_entry,sa25_w28_entry,sa25_w29_entry,sa25_w30_entry,sa25_w31_entry,sa25_w32_entry
    global sa26_w1_entry,sa26_w2_entry,sa26_w3_entry,sa26_w4_entry,sa26_w5_entry,sa26_w6_entry,sa26_w7_entry,sa26_w8_entry,sa26_w9_entry,sa26_w10_entry,sa26_w11_entry,sa26_w12_entry,sa26_w13_entry,sa26_w14_entry
    global sa26_w15_entry,sa26_w16_entry,sa26_w17_entry,sa26_w18_entry,sa26_w19_entry,sa26_w20_entry,sa26_w21_entry,sa26_w22_entry,sa26_w23_entry,sa26_w24_entry,sa26_w25_entry,sa26_w26_entry,sa26_w27_entry,sa26_w28_entry,sa26_w29_entry,sa26_w30_entry,sa26_w31_entry,sa26_w32_entry
    global sa27_w1_entry,sa27_w2_entry,sa27_w3_entry,sa27_w4_entry,sa27_w5_entry,sa27_w6_entry,sa27_w7_entry,sa27_w8_entry,sa27_w9_entry,sa27_w10_entry,sa27_w11_entry,sa27_w12_entry,sa27_w13_entry,sa27_w14_entry
    global sa27_w15_entry,sa27_w16_entry,sa27_w17_entry,sa27_w18_entry,sa27_w19_entry,sa27_w20_entry,sa27_w21_entry,sa27_w22_entry,sa27_w23_entry,sa27_w24_entry,sa27_w25_entry,sa27_w26_entry,sa27_w27_entry,sa27_w28_entry,sa27_w29_entry,sa27_w30_entry,sa27_w31_entry,sa27_w32_entry


        
    window = Tk()
    window.title("SAMOOHA 12 CHANNNEL INTERFACE")
    window.configure(bg="lavender")
    window.geometry("1400x800")

    project_name_var = StringVar(value="SAMOOHA")

    # === Header with Different Left & Right Logos (PNG + Version Compatible) ===
    def get_resize_filter():
        """Auto-detects Pillow version for correct resize filter"""
        try:
            return Image.Resampling.LANCZOS
        except AttributeError:
            return Image.ANTIALIAS

    resize_filter = get_resize_filter()

    # Load Left Logo
    try:
        left_logo = Image.open("URSC Logonew.png").convert("RGBA")
        left_logo = left_logo.resize((150, 50), resize_filter)
        left_photo = ImageTk.PhotoImage(left_logo)
    except Exception as e:
        print(f"⚠️ Warning: Could not load logo_left.png. Error: {e}. Using placeholder.")
        left_photo = None

    # Load Right Logo
    try:
        right_logo = Image.open("isro_logo_new.png").convert("RGBA")
        right_logo = right_logo.resize((100, 50), resize_filter)
        right_photo = ImageTk.PhotoImage(right_logo)
    except Exception as e:
        print(f"⚠️ Warning: Could not load logo_right.png. Error: {e}. Using placeholder.")
        right_photo = None

    # Create header frame
    header_frame = Frame(window, bg="light blue")
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
    header_frame.grid_columnconfigure(1, weight=1)  # Allows center text to stretch naturally

    # Left Logo Label
    left_logo_lbl = Label(header_frame, image=left_photo, bg="light blue") if left_photo else Label(header_frame, width=3, bg="light blue")
    left_logo_lbl.grid(row=0, column=0, padx=(15, 5), pady=5)

    # Center Text
    header_text_label = Label(header_frame, text="SPS TELEMETRY AND TELECOMMAND INTERFACE: SAMOOHA",
                              font=("Algerian", 20, "bold"), bg="light blue", fg="dark blue")
    header_text_label.grid(row=0, column=1, padx=5, pady=5)

    # Right Logo Label
    right_logo_lbl = Label(header_frame, image=right_photo, bg="light blue") if right_photo else Label(header_frame, width=3, bg="light blue")
    right_logo_lbl.grid(row=0, column=2, padx=(5, 15), pady=5)

    # ✅ Prevent Python's garbage collector from deleting the images
    header_frame.logo_images = [left_photo, right_photo]

    # === Scrollable Canvas Setup ===
    canvas = Canvas(window, bg="lavender", highlightthickness=0)
    scrollbar_y = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
    scrollbar_x = ttk.Scrollbar(window, orient="horizontal", command=canvas.xview)
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    canvas.grid(row=1, column=0, sticky="nsew")
    scrollbar_y.grid(row=1, column=1, sticky="ns")
    scrollbar_x.grid(row=2, column=0, sticky="ew")

    root = Frame(canvas, bg="lavender")
    canvas.create_window((0, 0), window=root, anchor="nw")

    # Configure grid expansion
    window.grid_rowconfigure(1, weight=1)
    window.grid_columnconfigure(0, weight=1)
    
    header_frame.grid_columnconfigure(0, weight=10)
    header_frame.grid_columnconfigure(1, weight=1)
    header_frame.grid_columnconfigure(2, weight=10)

    # Allow root columns to expand
    for i in range(5):
        root.grid_columnconfigure(i, weight=1)

    # Update scroll region
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    root.bind("<Configure>", on_frame_configure)

    def update_project_name(*args):
        global display_name
        input_name = project_name_var.get().strip()

        # Use "SAMOOHA" if empty or equal to SAMOOHA (case-insensitive)
        if not input_name or input_name.lower() == "samooha":
            display_name = "SAMOOHA"
        else:
            display_name = input_name.upper()

        header_text_label.config(text=f"{display_name} TELEMETRY AND COMMAND INTERFACE")

    # Enable mouse wheel scrolling
    def bind_mousewheel(widget):
        system = platform.system()
        if system == 'Windows' or system == 'Darwin':
            widget.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        else:  # Linux
            widget.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            widget.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    bind_mousewheel(canvas)

    #  ======================= COM MANAGER ===============
    frame1 = LabelFrame(
    root,
    text="  COM MANAGER  ",  # extra spacing in title gives a round feel
    bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame1.grid(row=0,column=0,padx=1,pady=1,sticky="nsew")

    status_var1 = StringVar(value="port Status:")


    status_label = Label(
        frame1,
        textvariable=status_var1,
        anchor="w",
        font=("Calibri", 11,"bold"),bg="lavender",fg="BLUE",
        wraplength=700,  # Adjust as needed to fit frame width
        justify="left"
    )
    status_label.grid(row=2, column=0, columnspan=8, sticky="w", padx=5, pady=(0, 5))

    project_label = Label(frame1, text = "Project Name: ", font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    project_label.grid(column=0,row=0,pady=2,padx=2)
    project_entry = Entry(frame1, textvariable=project_name_var, font=("Calibri", 11,"bold"),bg="lavender",fg="purple", width=10, justify="center")
    project_entry.grid(row=0, column=1,pady=2,padx=2)
    project_name_var.trace_add("write", update_project_name)
    port_label = Label(frame1, text = "Available port[s]: ", font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    port_label.grid(column=0,row=1,pady=2,padx=2)
    refresh_btn=Button(frame1,text="Refresh",width=10,font=("Calibri", 11,"bold"),bg="lavender",fg="purple",command=update_coms)
    refresh_btn.grid(column=2,row=1,pady=2,padx=2)
    port_bd=Label(frame1,text="Baud Rate:",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    port_bd.grid(column=3,row=1,pady=2,padx=2)
    file_bd=Label(frame1,text="File:",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    file_bd.grid(column=5,row=1,pady=2,padx=2)
    file_entry1=Entry(frame1,width=10,font=("Calibri", 11,"bold"),bg="white",fg="purple")
    file_entry1.grid(column=6,row=1,pady=2,padx=2)
    connect_btn=Button(frame1,text="Connect",width=10,state="disabled",font=("Calibri", 11,"bold"),bg="lavender",fg="purple",command=connexion)
    connect_btn.grid(column=7,row=1,pady=2,padx=2)
    btn_replay = tk.Button(frame1, text="Replay", width=10, font=("Calibri", 11,"bold"),
                       bg="lavender", fg="purple", command=replay_from_file)
    btn_replay.grid(column=2, row=0, padx=2, pady=2)

    tk.Label(frame1, text="Jump to SYS_SEC:", font=("Calibri", 11,"bold"), bg="lavender").grid(column=3, row=0, padx=2, pady=2)

    jump_entry = tk.Entry(frame1, width=10)
    jump_entry.grid(column=4, row=0, padx=2, pady=2)

    btn_jump = tk.Button(frame1, text="Jump", width=10, font=("Calibri", 11,"bold"),bg="lavender",fg="purple", command=jump_to_sys_sec)
    btn_jump.grid(column=5, row=0, padx=2, pady=2)
    btn_pause_resume = tk.Button(frame1, text="Pause ⏸", width=10, font=("Calibri", 11,"bold"),
                                 bg="light yellow", fg="black", command=toggle_pause_resume)
    btn_pause_resume.grid(column=6, row=0, padx=2, pady=2)
    btn_stop_replay = tk.Button(frame1, text="Stop Replay", width=10, font=("Calibri", 11,"bold"),
                                bg="lavender", fg="red", command=stop_replay)
    btn_stop_replay.grid(column=7, row=0, padx=2, pady=2)
    # Pause/Resume toggle button


    btn_precise = tk.Button(frame1, text="Precise File", width=10, font=("Calibri", 12, "bold"),
                            bg="purple", fg="white", command=on_precise_file)
    btn_precise.grid(row=2, column=7, padx=2, pady=2)


       # ==================== COMMAND FRAME (SA1-SA4 Single Field Layout) ====================
    frame13 = LabelFrame(root, text="COMMANDS", bg="lavender", fg="purple", font=("Calibri", 13, "bold"), relief="solid", bd=2, padx=2, pady=2)
    frame13.grid(row=0, column=2, pady=2, padx=2, sticky="nsew")

    status_var = StringVar(value="CMD Status:")
    status_label = Label(frame1, textvariable=status_var, anchor="w", font=("Calibri",11,"bold"), bg="lavender", fg="BLUE", wraplength=700, justify="left")
    status_label.grid(row=3, column=0, columnspan=8, sticky="w", padx=5, pady=(0,5))
    
    

    
    sa_names = ["SA1","SA2","SA3","SA4","SA5_9(ISL)","SA10_11(ISR)","SA12"]
    for idx, sa in enumerate(sa_names, start=1):
        Label(frame13, text=f"{sa}:", font=("Calibri",11,"bold"), bg="lavender", fg="purple").grid(row=idx, column=0, padx=2, pady=2, sticky='e')

        ent = Entry(frame13, width=18, font=("Calibri",11,"bold"), bg="lavender", fg="purple")
        ent.grid(row=idx, column=1, padx=2, pady=2)

        # ✅ Set correct placeholder based on Sub-Address type
        if sa in ("SA1", "SA2"):
            ent.insert(0, "0x0000 0x0004 0x0055")
        elif sa in ("SA3", "SA4","SA12"):
            ent.insert(0, "64_byte_hex_data (128 chars)")
        elif sa in ("SA5_9(ISL)"):
            ent.insert(0, "320_byte_hex_data (640 chars)")
        else:
            ent.insert(0, "128_byte_hex_data (256 chars)")
  
            

        btn_send = Button(frame13, text=f"Send {sa}", width=7, font=("Calibri",11,"bold"), bg="lavender", fg="green",
                          state="disabled", command=lambda sn=sa, inp=ent: send_command(sn, inp.get()))
        btn_send.grid(row=idx, column=3, padx=2, pady=2)

        btn_browse = Button(frame13, text="Browse", width=7, font=("Calibri",12,"bold"), bg="purple", fg="white",
                            command=lambda e=ent, s=sa, b=btn_send: _browse_file(e, s, b))
        btn_browse.grid(row=idx, column=2, padx=2, pady=2)

        btn_stop = Button(frame13, text=f"Stop {sa}", width=6, font=("Calibri",11,"bold"), bg="lavender", fg="red", state="disabled",
                          command=lambda s=sa: stop_sa(s))
        btn_stop.grid(row=idx, column=4, padx=2, pady=2)

        ent.bind('<KeyRelease>', lambda event, btn=btn_send, e=ent: btn.config(state="normal" if e.get().strip() else "disabled"))
        sa_stop_btns[sa] = btn_stop
        cmd_btn = Button(frame13, text="CMD's List", font=("Calibri",11,"bold"), bg="dark blue", fg="white", command=open_popup).grid(row=1, column=5, padx=2, pady=2, sticky="ew")


    

    # ====== BUS COMMAND Section ====== # --- Show Toggle Packet Button ---
    frame_bus = LabelFrame(root, text="BUS COMMAND",bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame_bus.grid(row=1, column=2, padx=2, pady=2, sticky="nsew")

    bus_var = StringVar(value=" ")  # Start with no selection

 # Row 0: 4 Radio Buttons (BUS A, BUS B, INTR ISL, EXTR ISL)
    Radiobutton(frame_bus, text="BUS A", variable=bus_var, value="A", font=("Calibri", 12, "bold"), bg="lavender", fg="Blue").grid(row=0, column=0, padx=2, pady=2)
    Radiobutton(frame_bus, text="BUS B", variable=bus_var, value="B", font=("Calibri", 12, "bold"), bg="lavender", fg="Blue").grid(row=0, column=1, padx=2, pady=2)
    Radiobutton(frame_bus, text="INTR ISL", variable=bus_var, value="INTR_ISL", font=("Calibri", 12, "bold"), bg="lavender", fg="Blue").grid(row=0, column=2, padx=2, pady=2)
    Radiobutton(frame_bus, text="EXTR ISL", variable=bus_var, value="EXTR_ISL", font=("Calibri", 12, "bold"), bg="lavender", fg="Blue").grid(row=0, column=3, padx=2, pady=2)

    bus_var.trace_add('write', on_bus_toggle)
    
    for i, (cmd_name, cmd_val) in enumerate(bus_commands):
      btn = Button(frame_bus, text=cmd_name, width=11, font=("Calibri", 12,"bold"),bg="lavender",fg="dark green",command=lambda v=cmd_val: send_bus_command_button(v))
      btn.grid(row=3+i//4, column=i%4, padx=5, pady=5)
      bus_command_buttons[cmd_name] = btn

    #bus_var.trace_add('write', on_bus_toggle)

    Label(frame_bus, text="RT Add(Hex):",font=("Calibri", 12,"bold"),bg="lavender",fg="purple").grid(row=1, column=0, padx=5, pady=5)
    dataword_entry = Entry(frame_bus, width=6,font=("Calibri", 12,"bold"),bg="lavender",fg="BLUE")
    dataword_entry.grid(row=1, column=1,padx=2, pady=2)
    dataword_entry.insert(1, "00")  # default

    send_bus_manual = Button(frame_bus, text="RT Send", width=12,font=("Calibri", 12,"bold"),bg="green",fg="white",command=send_bus_command_entry)
    send_bus_manual.grid(row=1, column=2, padx=2, pady=2)
    
     #bus_var.trace_add('write', on_bus_toggle)

    Label(frame_bus, text="ISL Delay(Hex):",font=("Calibri", 12,"bold"),bg="lavender",fg="purple").grid(row=2, column=0, padx=5, pady=5)
    dataword_entry1 = Entry(frame_bus, width=6,font=("Calibri", 12,"bold"),bg="lavender",fg="BLUE")
    dataword_entry1.grid(row=2, column=1,padx=2, pady=2)
    dataword_entry1.insert(2, "00")  # default


    send_bus_manual_isl = Button(frame_bus, text="ISL Delay Send", width=12,font=("Calibri", 12,"bold"),bg="green",fg="white",command=send_bus_isl_delay_command_entry)
    send_bus_manual_isl.grid(row=2, column=2, padx=2, pady=2)

    # ====================  COUNTER ==================
    frame2=LabelFrame(root,text='COUNTERS & NO OF SAT TRK',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame2.grid(row=0,column=1,padx=2, pady=2,sticky="nsew")


    update_count=Label(frame2,text="Update Counter:",font=("Calibri", 11,"bold"),bg='lavender')
    update_count.grid(row=0, column=0)
    update_entry=Entry(frame2,width=12,state="readonly",font=("Calibri", 11,"bold"))
    update_entry.grid(column=1,row=0,padx=2, pady=2)

    '''counter=Label(frame2,text=" Display Counter:",font=("Calibri", 11,"bold"),bg='lavender')
    counter.grid(row=1, column=0)
    counter_entry=Entry(frame2,width=12,state="readonly",font=("Calibri", 11,"bold"))
    counter_entry.grid(column=1,row=1,padx=2, pady=2)'''

    memory_count=Label(frame2,text="Memory Count:",font=("Calibri", 11,"bold"),bg='lavender')
    memory_count.grid(row=2, column=0)
    mc=Entry(frame2,width=12,state="readonly",font=("Calibri", 11,"bold"))
    mc.grid(column=1,row=2,padx=2, pady=2)

    tele_cmd_counter=Label(frame2,text=" Tele CMD Counter:",font=("Calibri", 11,"bold"),bg='lavender')
    tele_cmd_counter.grid(row=3, column=0)
    tele_cmd_counter=Entry(frame2,width=12,state="readonly",font=("Calibri", 11,"bold"))
    tele_cmd_counter.grid(column=1,row=3,padx=2, pady=2)

    upset_cmd_counter=Label(frame2,text=" UPSET CMD Counter:",font=("Calibri", 11,"bold"),bg='lavender')
    upset_cmd_counter.grid(row=4, column=0)
    upset_cmd_counter=Entry(frame2,width=12,state="readonly",font=("Calibri", 11,"bold"))
    upset_cmd_counter.grid(column=1,row=4,padx=2, pady=2)

    labels = ["Interupt CMD Counter", "No Of Satellite"]
    tele_entries = {}

    for i, label_txt in enumerate(labels):
        lbl = tk.Label(frame2, text=label_txt + ":", font=("Calibri", 11,"bold"),bg='lavender')
        lbl.grid(row=i+5, column=0,padx=2, pady=2)

        entry = tk.Entry(frame2, width=12, state="readonly", font=("Calibri", 11,"bold"),bg='lavender')
        entry.grid(row=i+5, column=1, padx=2, pady=2)

        tele_entries[label_txt] = entry
    
    swdt=Label(frame2,text="SWDT Reset counter:",font=("Calibri", 11,"bold"),bg='lavender')
    swdt.grid(row=7, column=0)
    swdt=Entry(frame2,width=12,state="readonly",font=("Calibri", 11,"bold"))
    swdt.grid(column=1,row=7,padx=2, pady=2)

    labels = ["HWDT Reset Counter", "SWDT Reset ID"]
    word25_entries = {}

    for i, label_txt in enumerate(labels):
        lbl = tk.Label(frame2, text=label_txt + ":", font=("Calibri", 11,"bold"),bg='lavender')
        lbl.grid(row=i+8, column=0, sticky='w')

        entry = tk.Entry(frame2, width=12, state="readonly", font=("Calibri", 11,"bold"))
        entry.grid(row=i+8, column=1, padx=2, pady=2)

        word25_entries[label_txt] = entry



    # ===================== MULTIPLEXER =====================
    frame2=LabelFrame(root,text='MULTIPLEXER',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame2.grid(row=2,column=2,padx=2, pady=2,sticky="nsw")

    mux=Label(frame2,text="MUX:",font=("Calibri", 11,"bold"),bg='lavender')
    mux.grid(row=0, column=0)
    mux_entry=Entry(frame2,width=40,state="readonly",font=("Calibri", 11,"bold"))
    mux_entry.grid(column=1,row=0,padx=2, pady=2)

    #====================== TIME Availablity ==========================
    frame4=LabelFrame(root,text='TIME AV',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame4.grid(row=3,column=2,padx=2, pady=2,sticky="new")

    sol=Label(frame4,text="Sol:",font=("Calibri", 11,"bold"),bg='lavender')
    sol.grid(row=0, column=0)
    sol=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    sol.grid(column=1,row=0,padx=2, pady=2)

    pos_e=Label(frame4,text="POS EST:",font=("Calibri", 11,"bold"),bg='lavender')
    pos_e.grid(row=0, column=2)
    pos_e=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    pos_e.grid(column=3,row=0,padx=2, pady=2)

    alm=Label(frame4,text="ALM:",font=("Calibri", 11,"bold"),bg='lavender')
    alm.grid(row=0, column=4)
    alm=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    alm.grid(column=5,row=0,padx=2, pady=2)

    time=Label(frame4,text="Time:",font=("Calibri", 11,"bold"),bg='lavender')
    time.grid(row=0, column=6)
    time=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    time.grid(column=7,row=0,padx=2, pady=2)

    d2_3d=Label(frame4,text="Pos Mode:",font=("Calibri", 11,"bold"),bg='lavender')
    d2_3d.grid(row=1, column=0)
    d2_3d=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    d2_3d.grid(column=1,row=1,padx=2, pady=2)

    position=Label(frame4,text="POS:",font=("Calibri", 11,"bold"),bg='lavender')
    position.grid(row=1, column=2)
    position=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    position.grid(column=3,row=1,padx=2, pady=2)

    ccsds=Label(frame4,text="Swap_mil_flag:",font=("Calibri", 11,"bold"),bg='lavender')
    ccsds.grid(row=1, column=4)
    ccsds=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    ccsds.grid(column=5,row=1,padx=2, pady=2)

    rand=Label(frame4,text="Rand_sts:",font=("Calibri", 11,"bold"),bg='lavender')
    rand.grid(row=1, column=6)
    rand=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    rand.grid(column=7,row=1,padx=2, pady=2)

    space_crf_id=Label(frame4,text="S_cft_id:",font=("Calibri", 11,"bold"),bg='lavender')
    space_crf_id.grid(row=2, column=0)
    space_crf_id=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    space_crf_id.grid(column=1,row=2,padx=2, pady=2)

    navic_cmd=Label(frame4,text="N_CMD:",font=("Calibri", 11,"bold"),bg='lavender')
    navic_cmd.grid(row=2, column=2)
    navic_cmd=Entry(frame4,width=5,state="readonly",font=("Calibri", 11,"bold"))
    navic_cmd.grid(column=3,row=2,padx=2, pady=2)

    # ===================== VALIDATION FLAG ====================
    frame6=LabelFrame(root,text='ODP_FLAG',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame6.grid(row=2,column=1,padx=2, pady=2,sticky="nsew")

    validation=Label(frame6,text="ODP_FLAG:",font=("Calibri", 11,"bold"),bg='lavender')
    validation.grid(row=3, column=0)
    flag=Entry(frame6,width=20,state="readonly",font=("Calibri", 11,"bold"))
    flag.grid(column=1,row=3,padx=2, pady=2)
    
    validation1=Label(frame6,text="ODP_RUN_Mode:",font=("Calibri", 11,"bold"),bg='lavender')
    validation1.grid(row=4, column=0)
    flag1=Entry(frame6,width=20,state="readonly",font=("Calibri", 11,"bold"))
    flag1.grid(column=1,row=4,padx=2, pady=2)

    # ====================SYNC,SYSTEM,H2SYNC TIME ,PPS TIME =================
    frame3=LabelFrame(root,text="TIME",bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame3.grid(row=1,column=0,padx=2, pady=2,sticky="nsew")

    Name=Label(frame3,text=" SYNC Time:",font=("Calibri", 11,"bold"),bg='lavender',padx=2, pady=2)
    Name.grid(row=1, column=1)

    time_label=Label(frame3,text="Second:",font=("Calibri", 11,"bold"),bg='lavender')
    time_label.grid(row=1, column=6)
    time_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    time_entry.grid(row=1, column=7, padx=2, pady=2)

    nanotime_label=Label(frame3,text="Nano Second:",font=("Calibri", 11,"bold"),bg='lavender')
    nanotime_label.grid(row=1, column=8)
    nanotime_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    nanotime_entry.grid(row=1, column=9, padx=2, pady=2)

    weeks_label=Label(frame3,text="Week Number:",font=("Calibri", 11,"bold"),bg='lavender')
    weeks_label.grid(row=1, column=10)
    week_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    week_entry.grid(row=1, column=11, padx=2, pady=2)


    Name=Label(frame3,text=" SYS Time:",font=("Calibri", 11,"bold"),bg='lavender',padx=5,pady=5)
    Name.grid(row=2, column=1)

    time_label1=Label(frame3,text="Second:",font=("Calibri", 11,"bold"),bg='lavender')
    time_label1.grid(row=2, column=6)
    time_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    time_entry1.grid(row=2, column=7, padx=2, pady=2)

    nanotime_label1=Label(frame3,text="Nano Second:",font=("Calibri", 11,"bold"),bg='lavender')
    nanotime_label1.grid(row=2, column=8)
    nanotime_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    nanotime_entry1.grid(row=2, column=9, padx=2, pady=2)

    weeks_label1=Label(frame3,text="Week Number:",font=("Calibri", 11,"bold"),bg='lavender')
    weeks_label1.grid(row=2, column=10)
    week_entry1=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    week_entry1.grid(row=2, column=11, padx=2, pady=2)

    Name=Label(frame3,text=" PPS Time:",font=("Calibri", 11,"bold"),bg='lavender',padx=5,pady=5)
    Name.grid(row=3, column=1)

    time_label3=Label(frame3,text="PPS Sec:",font=("Calibri", 11,"bold"),bg='lavender')
    time_label3.grid(row=3, column=6)
    time_entry3=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    time_entry3.grid(row=3, column=7, padx=2, pady=2)

    nanotime_label3=Label(frame3,text="PPS Nano Sec:",font=("Calibri", 11,"bold"),bg='lavender')
    nanotime_label3.grid(row=3, column=8)
    nanotime_entry3=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    nanotime_entry3.grid(row=3, column=9, padx=2, pady=2)

    weeks_label3=Label(frame3,text="PPS Week No:",font=("Calibri", 11,"bold"),bg='lavender')
    weeks_label3.grid(row=3, column=10)
    week_entry3=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    week_entry3.grid(row=3, column=11, padx=2, pady=2)

    fix_status=Label(frame3,text="PPS 3D fix status:",font=("Calibri", 11,"bold"),bg='lavender')
    fix_status.grid(row=4, column=6)
    fix_status=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    fix_status.grid(row=4, column=7, padx=2, pady=2)
    
    Name=Label(frame3,text="Inst ERROR :",font=("Calibri", 11,"bold"),bg='lavender',padx=5,pady=5)
    Name.grid(row=5, column=1)
    
    Name=Label(frame3,text=" ODP ERROR :",font=("Calibri", 11,"bold"),bg='lavender',padx=5,pady=5)
    Name.grid(row=6, column=1)
    
     # Time difference display (updated continuously)
    diff_label = Label(frame3, text="Time Diff (s):", font=("Calibri", 11, "bold"),
                          bg="lavender", fg="purple")
    diff_label.grid(row=5, column=6,  sticky="e", padx=5, pady=2)
    diff_entry = Entry(frame3, width=15, font=("Calibri", 11, "bold"),
                          state="readonly", bg="white")
    diff_entry.grid(row=5, column=7,  sticky="w", padx=5, pady=2)

    time_label4=Label(frame3,text="Inst POS ERROR:",font=("Calibri", 11,"bold"),bg='lavender')
    time_label4.grid(row=5, column=8)
    time_entry4=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    time_entry4.grid(row=5, column=9, padx=2, pady=2)

    nanotime_label4=Label(frame3,text="Inst VEL ERROR:",font=("Calibri", 11,"bold"),bg='lavender')
    nanotime_label4.grid(row=5, column=10)
    nanotime_entry4=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    nanotime_entry4.grid(row=5, column=11, padx=2, pady=2)
    
    odp_pos_err=Label(frame3,text="ODP POS ERROR:",font=("Calibri", 11,"bold"),bg='lavender')
    odp_pos_err.grid(row=6, column=8)
    odp_pos_err_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    odp_pos_err_entry.grid(row=6, column=9, padx=2, pady=2)

    odp_vel_err=Label(frame3,text="ODP VEL ERROR:",font=("Calibri", 11,"bold"),bg='lavender')
    odp_vel_err.grid(row=6, column=10)
    odp_vel_err_entry=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    odp_vel_err_entry.grid(row=6, column=11, padx=2, pady=2)


    '''Name=Label(frame3,text=" Header2 Time:",font=("Calibri", 11,"bold"),bg='lavender',padx=5,pady=5)
    Name.grid(row=5, column=1)

    time_label2=Label(frame3,text="Header2 Sec:",font=("Calibri", 11,"bold"),bg='lavender')
    time_label2.grid(row=5, column=6)
    time_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    time_entry2.grid(row=5, column=7, padx=2, pady=2)

    nanotime_label2=Label(frame3,text="Header2 NS:",font=("Calibri", 11,"bold"),bg='lavender')
    nanotime_label2.grid(row=5, column=8)
    nanotime_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    nanotime_entry2.grid(row=5, column=9, padx=2, pady=2)

    weeks_label2=Label(frame3,text="Header2 WN:",font=("Calibri", 11,"bold"),bg='lavender')
    weeks_label2.grid(row=5, column=10)
    week_entry2=Entry(frame3,width=15, state="readonly",font=("Calibri", 11,"bold"))
    week_entry2.grid(row=5, column=11, padx=2, pady=2)'''




    # =================== VECTOR DATA X,Y,Z,VX,VY,VZ ==============
    frame5=LabelFrame(root,text="STATE VECTOR DATA",bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame5.grid(row=2,column=0,padx=2, pady=2,sticky="nsew")

    Name=Label(frame5,text="  INSTANTIATE :",font=("Calibri", 11,"bold"),bg='lavender',padx=5,pady=5)
    Name.grid(row=1, column=1)
    position_label = Label(frame5, text="X_DX:",font=("Calibri", 11,"bold"),bg='lavender')
    position_label.grid(row=1, column=3, sticky="W")
    velocity_label = Label(frame5, text="Vel_x:",font=("Calibri", 11,"bold"),bg='lavender')
    velocity_label.grid(row=1, column=9, sticky="W")
    position_label1 = Label(frame5, text="Y_DX:",font=("Calibri", 11,"bold"),bg='lavender')
    position_label1.grid(row=1, column=5, sticky="W")
    velocity_label1 = Label(frame5, text="Vel_y:",font=("Calibri", 11,"bold"),bg='lavender')
    velocity_label1.grid(row=1, column=11, sticky="W")
    position_label2 = Label(frame5, text="Z_DX:",font=("Calibri", 11,"bold"),bg='lavender')
    position_label2.grid(row=1, column=7, sticky="W")
    velocity_label2 = Label(frame5, text="Vel_z:",font=("Calibri", 11,"bold"),bg='lavender')
    velocity_label2.grid(row=1, column=13, sticky="W")

    position_entry = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    position_entry.grid(row=1, column=4,padx=2, pady=2)
    velocity_entry = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    velocity_entry.grid(row=1, column=10, padx=2, pady=2)
    position_entry1 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    position_entry1.grid(row=1, column=6, padx=2, pady=2)
    velocity_entry1 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    velocity_entry1.grid(row=1, column=12, padx=2, pady=2)
    position_entry2 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    position_entry2.grid(row=1, column=8, padx=2, pady=2)
    velocity_entry2 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    velocity_entry2.grid(row=1, column=14, padx=2, pady=2)

    Name1=Label(frame5,text="  ODP                    :",padx=2, pady=2,font=("Calibri", 11,"bold"),bg='lavender')
    Name1.grid(row=2, column=1)
    position_label3 = Label(frame5, text="X:",font=("Calibri", 11,"bold"),bg='lavender')
    position_label3.grid(row=2, column=3, sticky="W")
    velocity_label3 = Label(frame5, text="Vel_x:",font=("Calibri", 11,"bold"),bg='lavender')
    velocity_label3.grid(row=2, column=9, sticky="W")
    position_label4 = Label(frame5, text="Y:",font=("Calibri", 11,"bold"),bg='lavender')
    position_label4.grid(row=2, column=5, sticky="W")
    velocity_label4 = Label(frame5, text="Vel_y:",font=("Calibri", 11,"bold"),bg='lavender')
    velocity_label4.grid(row=2, column=11, sticky="W")
    position_label5 = Label(frame5, text="Z:",font=("Calibri", 11,"bold"),bg='lavender')
    position_label5.grid(row=2, column=7, sticky="W")
    velocity_label5 = Label(frame5, text="Vel_z:",font=("Calibri", 11,"bold"),bg='lavender')
    velocity_label5.grid(row=2, column=13, sticky="W")

    position_entry3 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    position_entry3.grid(row=2, column=4, padx=2, pady=2)
    velocity_entry3 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    velocity_entry3.grid(row=2, column=10, padx=2, pady=2)
    position_entry4 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    position_entry4.grid(row=2, column=6, padx=2, pady=2)
    velocity_entry4 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    velocity_entry4.grid(row=2, column=12, padx=2, pady=2)
    position_entry5 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    position_entry5.grid(row=2, column=8, padx=2, pady=2)
    velocity_entry5 = Entry(frame5, width=10, state="readonly",font=("Calibri", 11,"bold"))
    velocity_entry5.grid(row=2, column=14, padx=2, pady=2)

    # ====================== CHECKSUM  =============================
    frame7=LabelFrame(root,text='CHECKSUM ',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame7.grid(row=2,column=3,padx=2, pady=2,sticky="nsw")

    CSM=Label(frame7,text="Checksum SA2:",font=("Calibri", 11,"bold"),bg="lavender")
    CSM.grid(row=7, column=0)
    csm=Entry(frame7,width=12,state="readonly",font=("Calibri", 11,"bold"))
    csm.grid(column=1,row=7,padx=2, pady=2)

    CSM1=Label(frame7,text="Checksum SA3:",font=("Calibri", 11,"bold"),bg="lavender")
    CSM1.grid(row=8, column=0)
    csm1=Entry(frame7,width=12,state="readonly",font=("Calibri", 11,"bold"))
    csm1.grid(column=1,row=8,padx=2, pady=2)





    # ======================== CLOCK AND DRIFT====================

    frame9=LabelFrame(root,text='CLOCK & DRIFT',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame9.grid(row=1,column=1,padx=2, pady=2,sticky="nsew")

    clock_b=Label(frame9,text="Clock bias:",font=("Calibri", 11,"bold"),bg="lavender")
    clock_b.grid(row=3, column=0)
    cb=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    cb.grid(column=1,row=3,padx=2, pady=2)

    I_clock_b=Label(frame9,text="ISB:",font=("Calibri", 11,"bold"),bg="lavender")
    I_clock_b.grid(row=4, column=0)
    icb=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    icb.grid(column=1,row=4,padx=2, pady=2)

    drift=Label(frame9,text="Drift:",font=("Calibri", 11,"bold"),bg="lavender")
    drift.grid(row=5, column=0)
    drift=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    drift.grid(column=1,row=5,padx=2, pady=2)

    InterSystemDrift=Label(frame9,text="ISD:",font=("Calibri", 11,"bold"),bg='lavender')
    InterSystemDrift.grid(row=6, column=0)
    isd=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    isd.grid(column=1,row=6,padx=2, pady=2)

    st_bias=Label(frame9,text="St_Bias:",font=("Calibri", 11,"bold"),bg='lavender')
    st_bias.grid(row=7, column=0)
    st_bias=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    st_bias.grid(column=1,row=7,padx=2, pady=2)

    st_drift=Label(frame9,text="St_Drift:",font=("Calibri", 11,"bold"),bg="lavender")
    st_drift.grid(row=8, column=0)
    st_drift=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    st_drift.grid(column=1,row=8,padx=2, pady=2)

    clk_crr=Label(frame9,text="Clk_corr:",font=("Calibri", 11,"bold"),bg="lavender")
    clk_crr.grid(row=9, column=0)
    clk_crr=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    clk_crr.grid(column=1,row=9,padx=2, pady=2)

    U1=Label(frame9,text="U1:",font=("Calibri", 11,"bold"),bg="lavender")
    U1.grid(row=3, column=2)
    U1=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    U1.grid(column=3,row=3,padx=2, pady=2)

    U2=Label(frame9,text="U2:",font=("Calibri", 11,"bold"),bg="lavender")
    U2.grid(row=4, column=2)
    U2=Entry(frame9,width=8,state="readonly",font=("Calibri", 11,"bold"))
    U2.grid(column=3,row=4,padx=2, pady=2)

    labels = ["Str_Est","Str_En","Reset_C","Init"]
    word32_entries = {}

    for i, label_txt in enumerate(labels):
        lbl = tk.Label(frame9, text=label_txt + ":", font=("Calibri", 11,"bold"),bg='lavender')
        lbl.grid(row=i+5, column=2, sticky='w')

        entry = tk.Entry(frame9, width=8, state="readonly", font=("Calibri", 11,"bold"))
        entry.grid(row=i+5, column=3, padx=2, pady=2)

        word32_entries[label_txt] = entry

    #===============================LAST CMD EXE=======================

    frame9=LabelFrame(root,text='LAST_CMD_EXE',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame9.grid(row=3,column=3,padx=1,pady=1,sticky="nsw")

    last_cmd_b1_b2=Label(frame9,text="Last_cmd_b1_b2:",font=("Calibri", 11,"bold"),bg="lavender")
    last_cmd_b1_b2.grid(row=3, column=0)
    last_cmd_b1_b2=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    last_cmd_b1_b2.grid(column=1,row=3,padx=2, pady=2)

    last_cmd_b3=Label(frame9,text="Last_cmd_b3:",font=("Calibri", 11,"bold"),bg="lavender")
    last_cmd_b3.grid(row=4, column=0)
    last_cmd_b3=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    last_cmd_b3.grid(column=1,row=4,padx=2, pady=2)

    last_cmd_b4=Label(frame9,text="Last_cmd_b4:",font=("Calibri", 11,"bold"),bg='lavender')
    last_cmd_b4.grid(row=5, column=0)
    last_cmd_b4=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    last_cmd_b4.grid(column=1,row=5,padx=2, pady=2)

    acq1_svid=Label(frame9,text="ACQ1_SVID:",font=("Calibri", 11,"bold"),bg='lavender')
    acq1_svid.grid(row=6, column=0)
    acq1_svid=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    acq1_svid.grid(column=1,row=6,padx=2, pady=2)
    
    port1=Label(frame9,text="PORT1:",font=("Calibri", 11,"bold"),bg='lavender')
    port1.grid(row=7, column=0)
    port1=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    port1.grid(column=1,row=7,padx=2, pady=2)

    port2=Label(frame9,text="PORT2:",font=("Calibri", 11,"bold"),bg='lavender')
    port2.grid(row=8, column=0)
    port2=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    port2.grid(column=1,row=8,padx=2, pady=2)



     #===============================ODP PARAMETERS=======================

    frame9=LabelFrame(root,text='ODP PARAMETERS',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame9.grid(row=3,column=3,padx=1,pady=1,sticky="sw")

    odp_labels = [
        "No of I/P sat to odp",
        "No of sat est",
        "Filter Init reason",
        "Filter Init Flag",
        "KF Est Flag",
        "PPP Est Flag Unsing",
        "Ph_center En Flag"
    ]

    odp_entries = {}

    for i, label_txt in enumerate(odp_labels):
        lbl = tk.Label(frame9, text=label_txt + ":",font=("Calibri", 11,"bold"), bg='lavender')
        lbl.grid(row=i+1, column=0, sticky='w')

        entry = tk.Entry(frame9, width=12, state="readonly", font=("Calibri", 11,"bold"))
        entry.grid(row=i+1, column=1, padx=2, pady=2)

        odp_entries[label_txt] = entry

    tmillcond=Label(frame9,text="ill cond Val:",font=("Calibri", 11,"bold"),bg="lavender")
    tmillcond.grid(row=9, column=0)
    tmillcond=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    tmillcond.grid(column=1,row=9,padx=2, pady=2)

    tmillcondlim=Label(frame9,text="ill cond Limit:",font=("Calibri", 11,"bold"),bg="lavender")
    tmillcondlim.grid(row=10, column=0)
    tmillcondlim=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    tmillcondlim.grid(column=1,row=10,padx=2, pady=2)

    pre_chk_cntr=Label(frame9,text="Pre Check Counter:",font=("Calibri", 11,"bold"),bg='lavender')
    pre_chk_cntr.grid(row=11, column=0)
    pre_chk_cntr=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pre_chk_cntr.grid(column=1,row=11,padx=2, pady=2)

    post_chk_cntr=Label(frame9,text="Post Check Counter:",font=("Calibri", 11,"bold"),bg='lavender')
    post_chk_cntr.grid(row=12, column=0)
    post_chk_cntr=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    post_chk_cntr.grid(column=1,row=12,padx=2, pady=2)

    cond_pre=Label(frame9,text="Cond Pre check:",font=("Calibri", 11,"bold"),bg='lavender')
    cond_pre.grid(row=13, column=0)
    cond_pre=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    cond_pre.grid(column=1,row=13,padx=2, pady=2)

    cond_post=Label(frame9,text="Cond Post check:",font=("Calibri", 11,"bold"),bg='lavender')
    cond_post.grid(row=14, column=0)
    cond_post=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    cond_post.grid(column=1,row=14,padx=2, pady=2)

    odp_prop=Label(frame9,text="ODP_PROP_used:",font=("Calibri", 11,"bold"),bg='lavender')
    odp_prop.grid(row=15, column=0)
    odp_prop=Entry(frame9,width=12,state="readonly",font=("Calibri", 11,"bold"))
    odp_prop.grid(column=1,row=15,padx=2, pady=2)
    
    
    
     # ======================= LIST OF OTHER PARAMETERS ===============================================
    frame_list = LabelFrame(root, text='LIST OF OTHER PARAMETERS ',bg="lavender",
       fg="purple",
       font=("Calibri", 13, "bold"),
       relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
       bd=2,                    # border thickness
       padx=2, pady=2         # internal padding simulates rounded spacing
       )
    
    frame_list.grid(row=0, column=3, padx=2, pady=2,sticky="nsew")
    
    # Configure grid
    frame_list.grid_columnconfigure(0, weight=1)
    frame_list.grid_columnconfigure(1, weight=1)
    frame_list.grid_rowconfigure(0, weight=1)
    
    remote_btn = tk.Button(
        frame_list,
        text="Rem R/W",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_Remote_r_w_popup
    )
    remote_btn.grid(row=0, column=0, padx=10, pady=2)
    
    
    #===============================SUB ADDRESS8=======================

    frame11=LabelFrame(root,text='Remote R/W',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                   # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #SA8_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")

    remote1=Label(frame11,text="Rmt R/W 1:",font=("Calibri", 11,"bold"),bg='lavender')
    remote1.grid(row=0, column=0)
    remote1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    remote1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    remote2=Label(frame11,text="Rmt R/W 2:",font=("Calibri", 11,"bold"),bg='lavender')
    remote2.grid(row=1, column=0)
    remote2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    remote2_entry.grid(column=1,row=1,padx=2, pady=2)
    
    remote3=Label(frame11,text="Rmt R/W 3:",font=("Calibri", 11,"bold"),bg='lavender')
    remote3.grid(row=2, column=0)
    remote3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    remote3_entry.grid(column=1,row=2,padx=2, pady=2)
    
    remote4=Label(frame11,text="Rmt R/W 4:",font=("Calibri", 11,"bold"),bg='lavender')
    remote4.grid(row=3, column=0)
    remote4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    remote4_entry.grid(column=1,row=3,padx=2, pady=2)
    
    remote5=Label(frame11,text="Rmt R/W 5:",font=("Calibri", 11,"bold"),bg='lavender')
    remote5.grid(row=4, column=0)
    remote5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    remote5_entry.grid(column=1,row=4,padx=2, pady=2)
    
    remote6=Label(frame11,text="Rmt R/W 6:",font=("Calibri", 11,"bold"),bg='lavender')
    remote6.grid(row=5, column=0)
    remote6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    remote6_entry.grid(column=1,row=5,padx=2, pady=2)
    
    est_rec_clk = Label(frame11,text="Est_Rec_clk:",font=("Calibri", 11,"bold"),bg='lavender')
    est_rec_clk.grid(row=0, column=2)
    est_rec_clk_entry = Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    est_rec_clk_entry.grid(column=4,row=0,padx=2, pady=2)                                               
    
    est_rec_clk_bias = Label(frame11,text="Est_bias:",font=("Calibri", 11,"bold"),bg='lavender')
    est_rec_clk_bias.grid(row=1, column=2)
    est_rec_clk_bias_entry = Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    est_rec_clk_bias_entry.grid(column=4,row=1,padx=2, pady=2)

    LCOR = Label(frame11,text="LCOR:",font=("Calibri", 11,"bold"),bg='lavender')
    LCOR.grid(row=2, column=2)
    LCOR_entry = Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    LCOR_entry.grid(column=4,row=2,padx=2, pady=2)

    str_crr_clk = Label(frame11,text="Str_Crr_clk:",font=("Calibri", 11,"bold"),bg='lavender')
    str_crr_clk.grid(row=3, column=2)
    str_crr_clk_entry = Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    str_crr_clk_entry.grid(column=4,row=3,padx=2, pady=2)
    
    SA8_btn = tk.Button(
        frame_list,
        text="SA8",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA8_popup
    )
    SA8_btn.grid(row=0, column=1, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS8=======================

    frame11=LabelFrame(root,text='SA8',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,     
                  # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #SA8_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")

    sa8_w3=Label(frame11,text="SA8_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w3.grid(row=0, column=0)
    sa8_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w4=Label(frame11,text="SA8_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w4.grid(row=0, column=0)
    sa8_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w5=Label(frame11,text="SA8_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w5.grid(row=0, column=0)
    sa8_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w6=Label(frame11,text="SA8_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w6.grid(row=0, column=0)
    sa8_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w7=Label(frame11,text="SA8_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w7.grid(row=0, column=0)
    sa8_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w8=Label(frame11,text="SA8_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w8.grid(row=0, column=0)
    sa8_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w9_w10=Label(frame11,text="SA8_w9_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w9_w10.grid(row=0, column=0)
    sa8_w9_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w9_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w11_w12=Label(frame11,text="SA8_w11_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w11_w12.grid(row=0, column=0)
    sa8_w11_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w11_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w13_w14=Label(frame11,text="SA8_w13_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w13_w14.grid(row=0, column=0)
    sa8_w13_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w13_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w15_w16=Label(frame11,text="SA8_w15_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w15_w16.grid(row=0, column=0)
    sa8_w15_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w15_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w17_w18=Label(frame11,text="SA8_w17_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w17_w18.grid(row=0, column=0)
    sa8_w17_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w17_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w19_w20=Label(frame11,text="SA8_w19_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w19_w20.grid(row=0, column=0)
    sa8_w19_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w19_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w21_w22=Label(frame11,text="SA8_w21_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w21_w22.grid(row=0, column=0)
    sa8_w21_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w21_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w23_w24=Label(frame11,text="SA8_w23_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w23_w24.grid(row=0, column=0)
    sa8_w23_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w23_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w25_w26=Label(frame11,text="SA8_w25_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w25_w26.grid(row=0, column=0)
    sa8_w25_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w25_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w27_w28=Label(frame11,text="SA8_w27_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w27_w28.grid(row=0, column=0)
    sa8_w27_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w27_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w29_w30=Label(frame11,text="SA8_w29_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w29_w30.grid(row=0, column=0)
    sa8_w29_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w29_w30_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa8_w31_w32=Label(frame11,text="sA8_w31_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa8_w31_w32.grid(row=0, column=0)
    sa8_w31_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa8_w31_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    #=========================SA9=========================
    
    SA9_btn = tk.Button(
        frame_list,
        text="SA9",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA9_popup
    )
    SA9_btn.grid(row=0, column=2, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS8=======================

    frame11=LabelFrame(root,text='SA9',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #SA8_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa9_w1=Label(frame11,text="sa9_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w1.grid(row=0, column=0)
    sa9_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w2=Label(frame11,text="sa9_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w2.grid(row=0, column=0)
    sa9_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa9_w3=Label(frame11,text="sa9_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w3.grid(row=0, column=0)
    sa9_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w4=Label(frame11,text="sa9_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w4.grid(row=0, column=0)
    sa9_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w5=Label(frame11,text="sa9_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w5.grid(row=0, column=0)
    sa9_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w6=Label(frame11,text="sa9_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w6.grid(row=0, column=0)
    sa9_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w7=Label(frame11,text="sa9_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w7.grid(row=0, column=0)
    sa9_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w8=Label(frame11,text="sa9_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w8.grid(row=0, column=0)
    sa9_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w9=Label(frame11,text="SA8_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w9.grid(row=0, column=0)
    sa9_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w10=Label(frame11,text="sa9_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w10.grid(row=0, column=0)
    sa9_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w11=Label(frame11,text="sa9_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w11.grid(row=0, column=0)
    sa9_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w12=Label(frame11,text="sa9_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w12.grid(row=0, column=0)
    sa9_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w13=Label(frame11,text="sa9_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w13.grid(row=0, column=0)
    sa9_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    sa9_w14_w15=Label(frame11,text="sa9_w14_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w14_w15.grid(row=0, column=0)
    sa9_w14_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w14_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w16_w17=Label(frame11,text="sa9_w16_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w16_w17.grid(row=0, column=0)
    sa9_w16_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w16_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w18_w19=Label(frame11,text="sa9_w18_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w18_w19.grid(row=0, column=0)
    sa9_w18_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w18_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w20_w21=Label(frame11,text="sa9_w20_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w20_w21.grid(row=0, column=0)
    sa9_w20_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w20_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w22_w23=Label(frame11,text="sa9_w22_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w22_w23.grid(row=0, column=0)
    sa9_w22_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w22_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w24_w25=Label(frame11,text="sa9_w24_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w24_w25.grid(row=0, column=0)
    sa9_w24_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w24_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w26=Label(frame11,text="sa9_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w26.grid(row=0, column=0)
    sa9_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w27=Label(frame11,text="sa9_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w27.grid(row=0, column=0)
    sa9_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w28=Label(frame11,text="sa9_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w28.grid(row=0, column=0)
    sa9_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w29=Label(frame11,text="sa9_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w29.grid(row=0, column=0)
    sa9_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w30_w31=Label(frame11,text="sa9_w30_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w30_w31.grid(row=0, column=0)
    sa9_w30_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w30_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa9_w32=Label(frame11,text="sa9_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa9_w32.grid(row=0, column=0)
    sa9_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa9_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================SA10 ========================================
    
    SA10_btn = tk.Button(
        frame_list,
        text="SA10",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA10_popup
    )
    SA10_btn.grid(row=0, column=3, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS10=======================

    frame11=LabelFrame(root,text='SA10',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #SA10_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa10_w1=Label(frame11,text="sa10_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w1.grid(row=0, column=0)
    sa10_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w2=Label(frame11,text="sa10_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w2.grid(row=0, column=0)
    sa10_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa10_w3=Label(frame11,text="sa10_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w3.grid(row=0, column=0)
    sa10_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w4=Label(frame11,text="sa10_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w4.grid(row=0, column=0)
    sa10_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w5=Label(frame11,text="sa10_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w5.grid(row=0, column=0)
    sa10_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w6=Label(frame11,text="sa10_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w6.grid(row=0, column=0)
    sa10_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w7=Label(frame11,text="sa10_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w7.grid(row=0, column=0)
    sa10_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w8=Label(frame11,text="sa10_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w8.grid(row=0, column=0)
    sa10_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w9_w10=Label(frame11,text="SA8_w9_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w9_w10.grid(row=0, column=0)
    sa10_w9_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w9_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w11_w12=Label(frame11,text="sa10_w11_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w11_w12.grid(row=0, column=0)
    sa10_w11_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w11_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w13_w14=Label(frame11,text="sa10_w13_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w13_w14.grid(row=0, column=0)
    sa10_w13_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w13_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w15=Label(frame11,text="sa10_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w15.grid(row=0, column=0)
    sa10_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w16=Label(frame11,text="sa10_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w16.grid(row=0, column=0)
    sa10_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    sa10_w17=Label(frame11,text="sa10_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w17.grid(row=0, column=0)
    sa10_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w18=Label(frame11,text="sa10_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w18.grid(row=0, column=0)
    sa10_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w19=Label(frame11,text="sa10_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w19.grid(row=0, column=0)
    sa10_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w20=Label(frame11,text="sa10_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w20.grid(row=0, column=0)
    sa10_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w21=Label(frame11,text="sa10_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w21.grid(row=0, column=0)
    sa10_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w22=Label(frame11,text="sa10_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w22.grid(row=0, column=0)
    sa10_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w23_w24=Label(frame11,text="sa10_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w23_w24.grid(row=0, column=0)
    sa10_w23_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w23_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w25_w26=Label(frame11,text="sa10_w25_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w25_w26.grid(row=0, column=0)
    sa10_w25_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w25_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w27_w28=Label(frame11,text="sa10_w27_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w27_w28.grid(row=0, column=0)
    sa10_w27_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w27_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w29_w30=Label(frame11,text="sa10_w29_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w29_w30.grid(row=0, column=0)
    sa10_w29_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w29_w30_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa10_w31_w32=Label(frame11,text="sa10_w31_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa10_w31_w32.grid(row=0, column=0)
    sa10_w31_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa10_w31_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
      #==============================SA11 ========================================
    
    SA11_btn = tk.Button(
        frame_list,
        text="SA11",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA11_popup
    )
    SA11_btn.grid(row=0, column=4, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS11=======================

    frame11=LabelFrame(root,text='SA11',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #SA11_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa11_w1_w2=Label(frame11,text="sa11_w1_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w1_w2.grid(row=0, column=0)
    sa11_w1_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w1_w2_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w3_w4=Label(frame11,text="sa11_w3_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w3_w4.grid(row=0, column=0)
    sa11_w3_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w3_w4_entry.grid(column=1,row=0,padx=2, pady=2)

    sa11_w5_w6=Label(frame11,text="sa11_w5_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w5_w6.grid(row=0, column=0)
    sa11_w5_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w5_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w7_w8=Label(frame11,text="sa11_w7_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w7_w8.grid(row=0, column=0)
    sa11_w7_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w7_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w9_w10=Label(frame11,text="sa11_w9_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w9_w10.grid(row=0, column=0)
    sa11_w9_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w9_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w11_w12=Label(frame11,text="sa11_w11_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w11_w12.grid(row=0, column=0)
    sa11_w11_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w11_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w13_w14=Label(frame11,text="sa11_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w13_w14.grid(row=0, column=0)
    sa11_w13_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w13_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w15=Label(frame11,text="sa11_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w15.grid(row=0, column=0)
    sa11_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w16=Label(frame11,text="sa11_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w16.grid(row=0, column=0)
    sa11_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    sa11_w17_w18=Label(frame11,text="sa11_w17_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w17_w18.grid(row=0, column=0)
    sa11_w17_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w17_w18_entry.grid(column=1,row=0,padx=2, pady=2)

    
    sa11_w19=Label(frame11,text="sa11_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w19.grid(row=0, column=0)
    sa11_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w20=Label(frame11,text="sa11_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w20.grid(row=0, column=0)
    sa11_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w21=Label(frame11,text="sa11_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w21.grid(row=0, column=0)
    sa11_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w22=Label(frame11,text="sa11_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w22.grid(row=0, column=0)
    sa11_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w23=Label(frame11,text="sa11_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w23.grid(row=0, column=0)
    sa11_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w24=Label(frame11,text="sa11_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w24.grid(row=0, column=0)
    sa11_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w24_entry.grid(column=1,row=0,padx=2, pady=2)

    
    sa11_w25_w26=Label(frame11,text="sa11_w25_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w25_w26.grid(row=0, column=0)
    sa11_w25_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w25_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w27_w28=Label(frame11,text="sa11_w27_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w27_w28.grid(row=0, column=0)
    sa11_w27_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w27_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w29=Label(frame11,text="sa11_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w29.grid(row=0, column=0)
    sa11_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa11_w30_w31=Label(frame11,text="sa11_w30_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w30_w31.grid(row=0, column=0)
    sa11_w30_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w30_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
        
    sa11_w32=Label(frame11,text="sa11_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa11_w32.grid(row=0, column=0)
    sa11_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa11_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================SA12 ========================================
    
    SA12_btn = tk.Button(
        frame_list,
        text="SA12",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA12_popup
    )
    SA12_btn.grid(row=1, column=0, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS11=======================

    frame11=LabelFrame(root,text='SA12',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #SA12_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa12_w1=Label(frame11,text="sa12_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w1.grid(row=0, column=0)
    sa12_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w2 =Label(frame11,text="sa12_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w2.grid(row=0, column=0)
    sa12_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa12_w3 =Label(frame11,text="sa12_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w3.grid(row=0, column=0)
    sa12_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w4 =Label(frame11,text="sa12_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w4.grid(row=0, column=0)
    sa12_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w5 =Label(frame11,text="sa12_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w5.grid(row=0, column=0)
    sa12_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w6 =Label(frame11,text="sa12_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w6.grid(row=0, column=0)
    sa12_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w7 =Label(frame11,text="sa12_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w7.grid(row=0, column=0)
    sa12_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w8 =Label(frame11,text="sa12_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w8.grid(row=0, column=0)
    sa12_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w9 =Label(frame11,text="sa12_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w9.grid(row=0, column=0)
    sa12_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w10 =Label(frame11,text="sa12_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w10.grid(row=0, column=0)
    sa12_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w11 =Label(frame11,text="sa12_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w11.grid(row=0, column=0)
    sa12_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w12 =Label(frame11,text="sa12_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w12.grid(row=0, column=0)
    sa12_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w13 =Label(frame11,text="sa12_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w13.grid(row=0, column=0)
    sa12_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w14 =Label(frame11,text="sa12_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w14.grid(row=0, column=0)
    sa12_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w15 =Label(frame11,text="sa12_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w15.grid(row=0, column=0)
    sa12_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w16 =Label(frame11,text="sa12_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w16.grid(row=0, column=0)
    sa12_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w17 =Label(frame11,text="sa12_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w17.grid(row=0, column=0)
    sa12_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w18 =Label(frame11,text="sa12_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w18.grid(row=0, column=0)
    sa12_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w19_w20 =Label(frame11,text="sa12_w19_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w19_w20.grid(row=0, column=0)
    sa12_w19_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w19_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w21_w22 =Label(frame11,text="sa12_w21_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w21_w22.grid(row=0, column=0)
    sa12_w21_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w21_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w23_w24 =Label(frame11,text="sa12_w23_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w23_w24.grid(row=0, column=0)
    sa12_w23_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w23_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w25_w26 =Label(frame11,text="sa12_w25_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w25_w26.grid(row=0, column=0)
    sa12_w25_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w25_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w27_w28 =Label(frame11,text="sa12_w27_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w27_w28.grid(row=0, column=0)
    sa12_w27_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w27_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w29_w30 =Label(frame11,text="sa12_w29_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w29_w30.grid(row=0, column=0)
    sa12_w29_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w29_w30_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w31 =Label(frame11,text="sa12_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w31.grid(row=0, column=0)
    sa12_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa12_w32 =Label(frame11,text="sa12_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa12_w32.grid(row=0, column=0)
    sa12_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa12_w32_entry.grid(column=1,row=0,padx=2, pady=2)

    #==============================SA13 ========================================
    
    SA13_btn = tk.Button(
        frame_list,
        text="SA13",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA13_popup
    )
    SA13_btn.grid(row=1, column=1, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS11=======================

    frame11=LabelFrame(root,text='SA13',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa13_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa13_w1=Label(frame11,text="sa13_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w1.grid(row=0, column=0)
    sa13_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w2 =Label(frame11,text="sa13_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w2.grid(row=0, column=0)
    sa13_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa13_w3 =Label(frame11,text="sa13_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w3.grid(row=0, column=0)
    sa13_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w4 =Label(frame11,text="sa13_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w4.grid(row=0, column=0)
    sa13_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w5 =Label(frame11,text="sa13_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w5.grid(row=0, column=0)
    sa13_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w6 =Label(frame11,text="sa13_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w6.grid(row=0, column=0)
    sa13_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w7 =Label(frame11,text="sa13_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w7.grid(row=0, column=0)
    sa13_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w8 =Label(frame11,text="sa13_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w8.grid(row=0, column=0)
    sa13_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w9 =Label(frame11,text="sa13_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w9.grid(row=0, column=0)
    sa13_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w10 =Label(frame11,text="sa13_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w10.grid(row=0, column=0)
    sa13_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w11 =Label(frame11,text="sa13_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w11.grid(row=0, column=0)
    sa13_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w12 =Label(frame11,text="sa13_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w12.grid(row=0, column=0)
    sa13_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w13 =Label(frame11,text="sa13_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w13.grid(row=0, column=0)
    sa13_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w14 =Label(frame11,text="sa13_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w14.grid(row=0, column=0)
    sa13_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w15 =Label(frame11,text="sa13_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w15.grid(row=0, column=0)
    sa13_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w16 =Label(frame11,text="sa13_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w16.grid(row=0, column=0)
    sa13_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w17 =Label(frame11,text="sa13_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w17.grid(row=0, column=0)
    sa13_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w18 =Label(frame11,text="sa13_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w18.grid(row=0, column=0)
    sa13_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w19 =Label(frame11,text="sa13_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w19.grid(row=0, column=0)
    sa13_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w20 =Label(frame11,text="sa13_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w20.grid(row=0, column=0)
    sa13_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w21 =Label(frame11,text="sa13_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w21.grid(row=0, column=0)
    sa13_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w22 =Label(frame11,text="sa13_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w22.grid(row=0, column=0)
    sa13_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w23 =Label(frame11,text="sa13_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w23.grid(row=0, column=0)
    sa13_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w24 =Label(frame11,text="sa13_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w24.grid(row=0, column=0)
    sa13_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w25 =Label(frame11,text="sa13_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w25.grid(row=0, column=0)
    sa13_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w26 =Label(frame11,text="sa13_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w26.grid(row=0, column=0)
    sa13_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa13_w27 =Label(frame11,text="sa13_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w27.grid(row=0, column=0)
    sa13_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w28 =Label(frame11,text="sa13_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w28.grid(row=0, column=0)
    sa13_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w29 =Label(frame11,text="sa13_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w29.grid(row=0, column=0)
    sa13_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w30 =Label(frame11,text="sa13_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w30.grid(row=0, column=0)
    sa13_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa13_w31 =Label(frame11,text="sa13_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w31.grid(row=0, column=0)
    sa13_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa13_w32 =Label(frame11,text="sa13_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa13_w32.grid(row=0, column=0)
    sa13_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa13_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================SA14 ========================================
    
    SA14_btn = tk.Button(
        frame_list,
        text="SA14",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA14_popup
    )
    SA14_btn.grid(row=1, column=2, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS14=======================

    frame11=LabelFrame(root,text='SA14',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa14_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa14_w1=Label(frame11,text="sa14_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w1.grid(row=0, column=0)
    sa14_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w2 =Label(frame11,text="sa14_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w2.grid(row=0, column=0)
    sa14_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa14_w3 =Label(frame11,text="sa14_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w3.grid(row=0, column=0)
    sa14_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w4 =Label(frame11,text="sa14_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w4.grid(row=0, column=0)
    sa14_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w5 =Label(frame11,text="sa14_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w5.grid(row=0, column=0)
    sa14_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w6 =Label(frame11,text="sa14_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w6.grid(row=0, column=0)
    sa14_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w7 =Label(frame11,text="sa14_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w7.grid(row=0, column=0)
    sa14_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w8 =Label(frame11,text="sa14_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w8.grid(row=0, column=0)
    sa14_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w9 =Label(frame11,text="sa14_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w9.grid(row=0, column=0)
    sa14_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w10 =Label(frame11,text="sa14_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w10.grid(row=0, column=0)
    sa14_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w11 =Label(frame11,text="sa14_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w11.grid(row=0, column=0)
    sa14_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w12 =Label(frame11,text="sa14_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w12.grid(row=0, column=0)
    sa14_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w13 =Label(frame11,text="sa14_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w13.grid(row=0, column=0)
    sa14_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w14 =Label(frame11,text="sa14_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w14.grid(row=0, column=0)
    sa14_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w15 =Label(frame11,text="sa14_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w15.grid(row=0, column=0)
    sa14_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w16 =Label(frame11,text="sa14_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w16.grid(row=0, column=0)
    sa14_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w17 =Label(frame11,text="sa14_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w17.grid(row=0, column=0)
    sa14_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w18 =Label(frame11,text="sa14_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w18.grid(row=0, column=0)
    sa14_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w19 =Label(frame11,text="sa14_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w19.grid(row=0, column=0)
    sa14_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w20 =Label(frame11,text="sa14_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w20.grid(row=0, column=0)
    sa14_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w21 =Label(frame11,text="sa14_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w21.grid(row=0, column=0)
    sa14_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w22 =Label(frame11,text="sa14_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w22.grid(row=0, column=0)
    sa14_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w23 =Label(frame11,text="sa14_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w23.grid(row=0, column=0)
    sa14_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w24 =Label(frame11,text="sa14_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w24.grid(row=0, column=0)
    sa14_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w25 =Label(frame11,text="sa14_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w25.grid(row=0, column=0)
    sa14_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w26 =Label(frame11,text="sa14_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w26.grid(row=0, column=0)
    sa14_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa14_w27 =Label(frame11,text="sa14_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w27.grid(row=0, column=0)
    sa14_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w28 =Label(frame11,text="sa14_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w28.grid(row=0, column=0)
    sa14_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w29 =Label(frame11,text="sa14_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w29.grid(row=0, column=0)
    sa14_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w30 =Label(frame11,text="sa14_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w30.grid(row=0, column=0)
    sa14_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa14_w31 =Label(frame11,text="sa14_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w31.grid(row=0, column=0)
    sa14_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa14_w32 =Label(frame11,text="sa14_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa14_w32.grid(row=0, column=0)
    sa14_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa14_w32_entry.grid(column=1,row=0,padx=2, pady=2)


      #==============================SA15 ========================================
    
    SA15_btn = tk.Button(
        frame_list,
        text="SA15",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA15_popup
    )
    SA15_btn.grid(row=1, column=3, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS15=======================

    frame11=LabelFrame(root,text='SA15',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa15_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa15_w1=Label(frame11,text="sa15_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w1.grid(row=0, column=0)
    sa15_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w2 =Label(frame11,text="sa15_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w2.grid(row=0, column=0)
    sa15_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa15_w3_w4 =Label(frame11,text="sa15_w3_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w3_w4.grid(row=0, column=0)
    sa15_w3_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w3_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w5_w6 =Label(frame11,text="sa15_w5_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w5_w6.grid(row=0, column=0)
    sa15_w5_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w5_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w7_w8 =Label(frame11,text="sa15_w7_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w7_w8.grid(row=0, column=0)
    sa15_w7_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w7_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w9_w10 =Label(frame11,text="sa15_w9_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w9_w10.grid(row=0, column=0)
    sa15_w9_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w9_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w11_w12 =Label(frame11,text="sa15_w11_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w11_w12.grid(row=0, column=0)
    sa15_w11_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w11_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    sa15_w13_w14 =Label(frame11,text="sa15_w13_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w13_w14.grid(row=0, column=0)
    sa15_w13_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w13_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w15_w16 =Label(frame11,text="sa15_w15_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w15_w16.grid(row=0, column=0)
    sa15_w15_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w15_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w17_w18 =Label(frame11,text="sa15_w17_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w17_w18.grid(row=0, column=0)
    sa15_w17_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w17_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w19_w20 =Label(frame11,text="sa15_w9_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w19_w20.grid(row=0, column=0)
    sa15_w19_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w19_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w21_w22 =Label(frame11,text="sa15_w21_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w21_w22.grid(row=0, column=0)
    sa15_w21_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w21_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w23_w24 =Label(frame11,text="sa15_w23_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w23_w24.grid(row=0, column=0)
    sa15_w23_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w23_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w25_w26 =Label(frame11,text="sa15_w25_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w25_w26.grid(row=0, column=0)
    sa15_w25_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w25_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w27_w28 =Label(frame11,text="sa15_w27_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w27_w28.grid(row=0, column=0)
    sa15_w27_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w27_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w29_w30 =Label(frame11,text="sa15_w9_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w29_w30.grid(row=0, column=0)
    sa15_w29_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w29_w30_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w31 =Label(frame11,text="sa15_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w31.grid(row=0, column=0)
    sa15_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa15_w32 =Label(frame11,text="sa15_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa15_w32.grid(row=0, column=0)
    sa15_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa15_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    #==============================SA16 ========================================
    
    SA16_btn = tk.Button(
        frame_list,
        text="SA16",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA16_popup
    )
    SA16_btn.grid(row=1, column=4, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS15=======================

    frame11=LabelFrame(root,text='SA16',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa16_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa16_w1=Label(frame11,text="sa16_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w1.grid(row=0, column=0)
    sa16_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w2 =Label(frame11,text="sa16_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w2.grid(row=0, column=0)
    sa16_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa16_w3_w4 =Label(frame11,text="sa16_w3_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w3_w4.grid(row=0, column=0)
    sa16_w3_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w3_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w5 =Label(frame11,text="sa16_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w5.grid(row=0, column=0)
    sa16_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w6 =Label(frame11,text="sa16_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w6.grid(row=0, column=0)
    sa16_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w7 =Label(frame11,text="sa16_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w7.grid(row=0, column=0)
    sa16_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w8_w9 =Label(frame11,text="sa16_w8_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w8_w9.grid(row=0, column=0)
    sa16_w8_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w8_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    sa16_w10_w11 =Label(frame11,text="sa16_w10_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w10_w11.grid(row=0, column=0)
    sa16_w10_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w10_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w12_w13 =Label(frame11,text="sa16_w12_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w12_w13.grid(row=0, column=0)
    sa16_w12_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w12_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    sa16_w14_w15 =Label(frame11,text="sa16_w14_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w14_w15.grid(row=0, column=0)
    sa16_w14_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w14_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w16_w17 =Label(frame11,text="sa16_w16_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w16_w17.grid(row=0, column=0)
    sa16_w16_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w16_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w18_w19 =Label(frame11,text="sa16_w18_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w18_w19.grid(row=0, column=0)
    sa16_w18_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w18_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w20_w21 =Label(frame11,text="sa16_w9_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w20_w21.grid(row=0, column=0)
    sa16_w20_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w20_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w22_w23 =Label(frame11,text="sa16_w22_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w22_w23.grid(row=0, column=0)
    sa16_w22_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w22_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w24_w29 =Label(frame11,text="sa16_w24_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w24_w29.grid(row=0, column=0)
    sa16_w24_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w24_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa16_w30_w31 =Label(frame11,text="sa16_w30_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w30_w31.grid(row=0, column=0)
    sa16_w30_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w30_w31_entry.grid(column=1,row=0,padx=2, pady=2)

    sa16_w32 =Label(frame11,text="sa16_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa16_w32.grid(row=0, column=0)
    sa16_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa16_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================SA17 ========================================
    
    SA17_btn = tk.Button(
        frame_list,
        text="SA17",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_SA17_popup
    )
    SA17_btn.grid(row=2, column=0, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS14=======================

    frame11=LabelFrame(root,text='SA17',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa17_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa17_w1=Label(frame11,text="sa17_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w1.grid(row=0, column=0)
    sa17_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w2 =Label(frame11,text="sa17_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w2.grid(row=0, column=0)
    sa17_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa17_w3 =Label(frame11,text="sa17_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w3.grid(row=0, column=0)
    sa17_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w4 =Label(frame11,text="sa17_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w4.grid(row=0, column=0)
    sa17_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w5 =Label(frame11,text="sa17_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w5.grid(row=0, column=0)
    sa17_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w6 =Label(frame11,text="sa17_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w6.grid(row=0, column=0)
    sa17_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w7 =Label(frame11,text="sa17_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w7.grid(row=0, column=0)
    sa17_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w8 =Label(frame11,text="sa17_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w8.grid(row=0, column=0)
    sa17_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w9 =Label(frame11,text="sa17_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w9.grid(row=0, column=0)
    sa17_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w10 =Label(frame11,text="sa17_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w10.grid(row=0, column=0)
    sa17_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w11 =Label(frame11,text="sa17_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w11.grid(row=0, column=0)
    sa17_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w12 =Label(frame11,text="sa17_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w12.grid(row=0, column=0)
    sa17_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w13 =Label(frame11,text="sa17_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w13.grid(row=0, column=0)
    sa17_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w14 =Label(frame11,text="sa17_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w14.grid(row=0, column=0)
    sa17_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w15 =Label(frame11,text="sa17_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w15.grid(row=0, column=0)
    sa17_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w16 =Label(frame11,text="sa17_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w16.grid(row=0, column=0)
    sa17_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w17 =Label(frame11,text="sa17_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w17.grid(row=0, column=0)
    sa17_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w18 =Label(frame11,text="sa17_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w18.grid(row=0, column=0)
    sa17_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w19 =Label(frame11,text="sa17_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w19.grid(row=0, column=0)
    sa17_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w20 =Label(frame11,text="sa17_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w20.grid(row=0, column=0)
    sa17_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w21 =Label(frame11,text="sa17_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w21.grid(row=0, column=0)
    sa17_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w22 =Label(frame11,text="sa17_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w22.grid(row=0, column=0)
    sa17_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w23 =Label(frame11,text="sa17_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w23.grid(row=0, column=0)
    sa17_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w24 =Label(frame11,text="sa17_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w24.grid(row=0, column=0)
    sa17_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w25 =Label(frame11,text="sa17_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w25.grid(row=0, column=0)
    sa17_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w26_w30 =Label(frame11,text="sa17_w26_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w26_w30.grid(row=0, column=0)
    sa17_w26_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w26_w30_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa17_w27 =Label(frame11,text="sa17_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w27.grid(row=0, column=0)
    sa17_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w28 =Label(frame11,text="sa17_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w28.grid(row=0, column=0)
    sa17_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w29 =Label(frame11,text="sa17_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w29.grid(row=0, column=0)
    sa17_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w30 =Label(frame11,text="sa17_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w30.grid(row=0, column=0)
    sa17_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa17_w31 =Label(frame11,text="sa17_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w31.grid(row=0, column=0)
    sa17_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa17_w32 =Label(frame11,text="sa17_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa17_w32.grid(row=0, column=0)
    sa17_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa17_w32_entry.grid(column=1,row=0,padx=2, pady=2)

  
    #==============================sa18 ========================================
    
    sa18_btn = tk.Button(
        frame_list,
        text="SA18",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa18_popup
    )
    sa18_btn.grid(row=2, column=1, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS SA18=======================

    frame11=LabelFrame(root,text='SA18',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa18_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa18_w1=Label(frame11,text="sa18_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w1.grid(row=0, column=0)
    sa18_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w2 =Label(frame11,text="sa18_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w2.grid(row=0, column=0)
    sa18_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa18_w3 =Label(frame11,text="sa18_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w3.grid(row=0, column=0)
    sa18_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w4 =Label(frame11,text="sa18_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w4.grid(row=0, column=0)
    sa18_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w5 =Label(frame11,text="sa18_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w5.grid(row=0, column=0)
    sa18_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w6 =Label(frame11,text="sa18_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w6.grid(row=0, column=0)
    sa18_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w7 =Label(frame11,text="sa18_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w7.grid(row=0, column=0)
    sa18_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w8 =Label(frame11,text="sa18_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w8.grid(row=0, column=0)
    sa18_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w9 =Label(frame11,text="sa18_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w9.grid(row=0, column=0)
    sa18_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w10 =Label(frame11,text="sa18_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w10.grid(row=0, column=0)
    sa18_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w11 =Label(frame11,text="sa18_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w11.grid(row=0, column=0)
    sa18_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w12 =Label(frame11,text="sa18_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w12.grid(row=0, column=0)
    sa18_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w13 =Label(frame11,text="sa18_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w13.grid(row=0, column=0)
    sa18_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w14 =Label(frame11,text="sa18_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w14.grid(row=0, column=0)
    sa18_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w15 =Label(frame11,text="sa18_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w15.grid(row=0, column=0)
    sa18_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w16 =Label(frame11,text="sa18_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w16.grid(row=0, column=0)
    sa18_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w17 =Label(frame11,text="sa18_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w17.grid(row=0, column=0)
    sa18_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w18 =Label(frame11,text="sa18_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w18.grid(row=0, column=0)
    sa18_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w19 =Label(frame11,text="sa18_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w19.grid(row=0, column=0)
    sa18_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w20 =Label(frame11,text="sa18_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w20.grid(row=0, column=0)
    sa18_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w21 =Label(frame11,text="sa18_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w21.grid(row=0, column=0)
    sa18_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w22 =Label(frame11,text="sa18_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w22.grid(row=0, column=0)
    sa18_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w23 =Label(frame11,text="sa18_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w23.grid(row=0, column=0)
    sa18_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w24 =Label(frame11,text="sa18_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w24.grid(row=0, column=0)
    sa18_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w25 =Label(frame11,text="sa18_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w25.grid(row=0, column=0)
    sa18_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w26_w30 =Label(frame11,text="sa18_w26_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w26_w30.grid(row=0, column=0)
    sa18_w26_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w26_w30_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa18_w27 =Label(frame11,text="sa18_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w27.grid(row=0, column=0)
    sa18_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w28 =Label(frame11,text="sa18_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w28.grid(row=0, column=0)
    sa18_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w29 =Label(frame11,text="sa18_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w29.grid(row=0, column=0)
    sa18_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w30 =Label(frame11,text="sa18_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w30.grid(row=0, column=0)
    sa18_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa18_w31 =Label(frame11,text="sa18_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w31.grid(row=0, column=0)
    sa18_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa18_w32 =Label(frame11,text="sa18_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa18_w32.grid(row=0, column=0)
    sa18_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa18_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================sa19 ========================================
    
    sa19_btn = tk.Button(
        frame_list,
        text="SA19",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa19_popup
    )
    sa19_btn.grid(row=2, column=2, padx=10, pady=2,sticky="w")
    
     #===============================SUB ADDRESS 19=======================

    frame11=LabelFrame(root,text='sa19',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa19_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa19_w1=Label(frame11,text="sa19_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w1.grid(row=0, column=0)
    sa19_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w2 =Label(frame11,text="sa19_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w2.grid(row=0, column=0)
    sa19_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa19_w3 =Label(frame11,text="sa19_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w3.grid(row=0, column=0)
    sa19_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w4 =Label(frame11,text="sa19_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w4.grid(row=0, column=0)
    sa19_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w5 =Label(frame11,text="sa19_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w5.grid(row=0, column=0)
    sa19_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w6 =Label(frame11,text="sa19_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w6.grid(row=0, column=0)
    sa19_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w7 =Label(frame11,text="sa19_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w7.grid(row=0, column=0)
    sa19_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w8 =Label(frame11,text="sa19_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w8.grid(row=0, column=0)
    sa19_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w9 =Label(frame11,text="sa19_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w9.grid(row=0, column=0)
    sa19_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w10 =Label(frame11,text="sa19_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w10.grid(row=0, column=0)
    sa19_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w11 =Label(frame11,text="sa19_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w11.grid(row=0, column=0)
    sa19_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w12 =Label(frame11,text="sa19_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w12.grid(row=0, column=0)
    sa19_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w13 =Label(frame11,text="sa19_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w13.grid(row=0, column=0)
    sa19_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w14 =Label(frame11,text="sa19_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w14.grid(row=0, column=0)
    sa19_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w15 =Label(frame11,text="sa19_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w15.grid(row=0, column=0)
    sa19_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w16 =Label(frame11,text="sa19_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w16.grid(row=0, column=0)
    sa19_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w17 =Label(frame11,text="sa19_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w17.grid(row=0, column=0)
    sa19_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w18 =Label(frame11,text="sa19_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w18.grid(row=0, column=0)
    sa19_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w19 =Label(frame11,text="sa19_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w19.grid(row=0, column=0)
    sa19_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w20 =Label(frame11,text="sa19_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w20.grid(row=0, column=0)
    sa19_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w21 =Label(frame11,text="sa19_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w21.grid(row=0, column=0)
    sa19_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w22 =Label(frame11,text="sa19_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w22.grid(row=0, column=0)
    sa19_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w23 =Label(frame11,text="sa19_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w23.grid(row=0, column=0)
    sa19_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w24 =Label(frame11,text="sa19_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w24.grid(row=0, column=0)
    sa19_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w25 =Label(frame11,text="sa19_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w25.grid(row=0, column=0)
    sa19_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w26 =Label(frame11,text="sa19_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w26.grid(row=0, column=0)
    sa19_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa19_w27 =Label(frame11,text="sa19_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w27.grid(row=0, column=0)
    sa19_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w28 =Label(frame11,text="sa19_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w28.grid(row=0, column=0)
    sa19_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w29 =Label(frame11,text="sa19_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w29.grid(row=0, column=0)
    sa19_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w30 =Label(frame11,text="sa19_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w30.grid(row=0, column=0)
    sa19_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa19_w31 =Label(frame11,text="sa19_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w31.grid(row=0, column=0)
    sa19_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa19_w32 =Label(frame11,text="sa19_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa19_w32.grid(row=0, column=0)
    sa19_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa19_w32_entry.grid(column=1,row=0,padx=2, pady=2)
     #==============================sa20 ========================================
    
    sa20_btn = tk.Button(
        frame_list,
        text="SA20",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa20_popup
    )
    sa20_btn.grid(row=2, column=3, padx=10, pady=2,sticky="w")
     #===============================SUB ADDRESS 20=======================

    frame11=LabelFrame(root,text='sa20',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa20_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa20_w1=Label(frame11,text="sa20_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w1.grid(row=0, column=0)
    sa20_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w2 =Label(frame11,text="sa20_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w2.grid(row=0, column=0)
    sa20_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa20_w3 =Label(frame11,text="sa20_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w3.grid(row=0, column=0)
    sa20_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w4 =Label(frame11,text="sa20_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w4.grid(row=0, column=0)
    sa20_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w5 =Label(frame11,text="sa20_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w5.grid(row=0, column=0)
    sa20_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w6 =Label(frame11,text="sa20_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w6.grid(row=0, column=0)
    sa20_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w7 =Label(frame11,text="sa20_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w7.grid(row=0, column=0)
    sa20_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w8 =Label(frame11,text="sa20_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w8.grid(row=0, column=0)
    sa20_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w9 =Label(frame11,text="sa20_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w9.grid(row=0, column=0)
    sa20_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w10 =Label(frame11,text="sa20_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w10.grid(row=0, column=0)
    sa20_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w11 =Label(frame11,text="sa20_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w11.grid(row=0, column=0)
    sa20_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w12 =Label(frame11,text="sa20_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w12.grid(row=0, column=0)
    sa20_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w13 =Label(frame11,text="sa20_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w13.grid(row=0, column=0)
    sa20_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w14 =Label(frame11,text="sa20_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w14.grid(row=0, column=0)
    sa20_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w15 =Label(frame11,text="sa20_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w15.grid(row=0, column=0)
    sa20_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w16 =Label(frame11,text="sa20_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w16.grid(row=0, column=0)
    sa20_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w17 =Label(frame11,text="sa20_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w17.grid(row=0, column=0)
    sa20_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w18 =Label(frame11,text="sa20_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w18.grid(row=0, column=0)
    sa20_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w19 =Label(frame11,text="sa20_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w19.grid(row=0, column=0)
    sa20_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w20 =Label(frame11,text="sa20_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w20.grid(row=0, column=0)
    sa20_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w21 =Label(frame11,text="sa20_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w21.grid(row=0, column=0)
    sa20_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w22 =Label(frame11,text="sa20_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w22.grid(row=0, column=0)
    sa20_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w23 =Label(frame11,text="sa20_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w23.grid(row=0, column=0)
    sa20_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w24 =Label(frame11,text="sa20_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w24.grid(row=0, column=0)
    sa20_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w25 =Label(frame11,text="sa20_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w25.grid(row=0, column=0)
    sa20_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w26 =Label(frame11,text="sa20_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w26.grid(row=0, column=0)
    sa20_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa20_w27 =Label(frame11,text="sa20_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w27.grid(row=0, column=0)
    sa20_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w28 =Label(frame11,text="sa20_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w28.grid(row=0, column=0)
    sa20_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w29 =Label(frame11,text="sa20_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w29.grid(row=0, column=0)
    sa20_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w30 =Label(frame11,text="sa20_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w30.grid(row=0, column=0)
    sa20_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa20_w31 =Label(frame11,text="sa20_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w31.grid(row=0, column=0)
    sa20_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa20_w32 =Label(frame11,text="sa20_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa20_w32.grid(row=0, column=0)
    sa20_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa20_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
     #==============================sa21 ========================================
    
    sa21_btn = tk.Button(
        frame_list,
        text="SA21",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa21_popup
    )
    sa21_btn.grid(row=2, column=4, padx=10, pady=2,sticky="w")
     #===============================SUB ADDRESS 20=======================

    frame11=LabelFrame(root,text='sa21',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa21_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa21_w1=Label(frame11,text="sa21_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w1.grid(row=0, column=0)
    sa21_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w2 =Label(frame11,text="sa21_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w2.grid(row=0, column=0)
    sa21_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa21_w3 =Label(frame11,text="sa21_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w3.grid(row=0, column=0)
    sa21_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w4 =Label(frame11,text="sa21_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w4.grid(row=0, column=0)
    sa21_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w5 =Label(frame11,text="sa21_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w5.grid(row=0, column=0)
    sa21_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w6 =Label(frame11,text="sa21_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w6.grid(row=0, column=0)
    sa21_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w7 =Label(frame11,text="sa21_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w7.grid(row=0, column=0)
    sa21_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w8 =Label(frame11,text="sa21_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w8.grid(row=0, column=0)
    sa21_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w9 =Label(frame11,text="sa21_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w9.grid(row=0, column=0)
    sa21_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w10 =Label(frame11,text="sa21_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w10.grid(row=0, column=0)
    sa21_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w11 =Label(frame11,text="sa21_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w11.grid(row=0, column=0)
    sa21_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w12 =Label(frame11,text="sa21_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w12.grid(row=0, column=0)
    sa21_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w13 =Label(frame11,text="sa21_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w13.grid(row=0, column=0)
    sa21_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w14 =Label(frame11,text="sa21_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w14.grid(row=0, column=0)
    sa21_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w15 =Label(frame11,text="sa21_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w15.grid(row=0, column=0)
    sa21_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w16 =Label(frame11,text="sa21_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w16.grid(row=0, column=0)
    sa21_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w17 =Label(frame11,text="sa21_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w17.grid(row=0, column=0)
    sa21_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w18 =Label(frame11,text="sa21_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w18.grid(row=0, column=0)
    sa21_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w19 =Label(frame11,text="sa21_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w19.grid(row=0, column=0)
    sa21_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w20 =Label(frame11,text="sa21_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w20.grid(row=0, column=0)
    sa21_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w21 =Label(frame11,text="sa21_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w21.grid(row=0, column=0)
    sa21_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w22 =Label(frame11,text="sa21_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w22.grid(row=0, column=0)
    sa21_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w23 =Label(frame11,text="sa21_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w23.grid(row=0, column=0)
    sa21_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w24 =Label(frame11,text="sa21_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w24.grid(row=0, column=0)
    sa21_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w25 =Label(frame11,text="sa21_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w25.grid(row=0, column=0)
    sa21_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w26 =Label(frame11,text="sa21_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w26.grid(row=0, column=0)
    sa21_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa21_w27 =Label(frame11,text="sa21_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w27.grid(row=0, column=0)
    sa21_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w28 =Label(frame11,text="sa21_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w28.grid(row=0, column=0)
    sa21_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w29 =Label(frame11,text="sa21_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w29.grid(row=0, column=0)
    sa21_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w30 =Label(frame11,text="sa21_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w30.grid(row=0, column=0)
    sa21_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa21_w31 =Label(frame11,text="sa21_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w31.grid(row=0, column=0)
    sa21_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa21_w32 =Label(frame11,text="sa21_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa21_w32.grid(row=0, column=0)
    sa21_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa21_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================sa22 ========================================
    
    sa22_btn = tk.Button(
        frame_list,
        text="SA22",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa22_popup
    )
    sa22_btn.grid(row=3, column=0, padx=10, pady=2,sticky="w")
     #===============================SUB ADDRESS 20=======================

    frame11=LabelFrame(root,text='sa22',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa22_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa22_w1=Label(frame11,text="sa22_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w1.grid(row=0, column=0)
    sa22_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w2 =Label(frame11,text="sa22_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w2.grid(row=0, column=0)
    sa22_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa22_w3 =Label(frame11,text="sa22_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w3.grid(row=0, column=0)
    sa22_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w4 =Label(frame11,text="sa22_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w4.grid(row=0, column=0)
    sa22_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w5 =Label(frame11,text="sa22_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w5.grid(row=0, column=0)
    sa22_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w6 =Label(frame11,text="sa22_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w6.grid(row=0, column=0)
    sa22_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w7 =Label(frame11,text="sa22_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w7.grid(row=0, column=0)
    sa22_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w8 =Label(frame11,text="sa22_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w8.grid(row=0, column=0)
    sa22_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w9 =Label(frame11,text="sa22_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w9.grid(row=0, column=0)
    sa22_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w10 =Label(frame11,text="sa22_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w10.grid(row=0, column=0)
    sa22_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w11 =Label(frame11,text="sa22_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w11.grid(row=0, column=0)
    sa22_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w12 =Label(frame11,text="sa22_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w12.grid(row=0, column=0)
    sa22_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w13 =Label(frame11,text="sa22_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w13.grid(row=0, column=0)
    sa22_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w14 =Label(frame11,text="sa22_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w14.grid(row=0, column=0)
    sa22_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w15 =Label(frame11,text="sa22_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w15.grid(row=0, column=0)
    sa22_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w16 =Label(frame11,text="sa22_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w16.grid(row=0, column=0)
    sa22_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w17 =Label(frame11,text="sa22_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w17.grid(row=0, column=0)
    sa22_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w18 =Label(frame11,text="sa22_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w18.grid(row=0, column=0)
    sa22_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w19 =Label(frame11,text="sa22_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w19.grid(row=0, column=0)
    sa22_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w20 =Label(frame11,text="sa22_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w20.grid(row=0, column=0)
    sa22_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w21 =Label(frame11,text="sa22_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w21.grid(row=0, column=0)
    sa22_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w22 =Label(frame11,text="sa22_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w22.grid(row=0, column=0)
    sa22_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w23 =Label(frame11,text="sa22_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w23.grid(row=0, column=0)
    sa22_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w24 =Label(frame11,text="sa22_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w24.grid(row=0, column=0)
    sa22_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w25 =Label(frame11,text="sa22_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w25.grid(row=0, column=0)
    sa22_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w26 =Label(frame11,text="sa22_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w26.grid(row=0, column=0)
    sa22_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa22_w27 =Label(frame11,text="sa22_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w27.grid(row=0, column=0)
    sa22_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w28 =Label(frame11,text="sa22_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w28.grid(row=0, column=0)
    sa22_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w29 =Label(frame11,text="sa22_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w29.grid(row=0, column=0)
    sa22_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w30 =Label(frame11,text="sa22_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w30.grid(row=0, column=0)
    sa22_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa22_w31 =Label(frame11,text="sa22_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w31.grid(row=0, column=0)
    sa22_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa22_w32 =Label(frame11,text="sa22_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa22_w32.grid(row=0, column=0)
    sa22_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa22_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================sa23 ========================================
    
    sa23_btn = tk.Button(
        frame_list,
        text="SA23",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa23_popup
    )
    sa23_btn.grid(row=3, column=1, padx=10, pady=2,sticky="w")
     #===============================SUB ADDRESS 20=======================

    frame11=LabelFrame(root,text='sa23',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa23_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa23_w1=Label(frame11,text="sa23_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w1.grid(row=0, column=0)
    sa23_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w2 =Label(frame11,text="sa23_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w2.grid(row=0, column=0)
    sa23_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa23_w3 =Label(frame11,text="sa23_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w3.grid(row=0, column=0)
    sa23_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w4 =Label(frame11,text="sa23_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w4.grid(row=0, column=0)
    sa23_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w5 =Label(frame11,text="sa23_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w5.grid(row=0, column=0)
    sa23_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w6 =Label(frame11,text="sa23_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w6.grid(row=0, column=0)
    sa23_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w7 =Label(frame11,text="sa23_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w7.grid(row=0, column=0)
    sa23_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w8 =Label(frame11,text="sa23_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w8.grid(row=0, column=0)
    sa23_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w9 =Label(frame11,text="sa23_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w9.grid(row=0, column=0)
    sa23_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w10 =Label(frame11,text="sa23_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w10.grid(row=0, column=0)
    sa23_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w11 =Label(frame11,text="sa23_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w11.grid(row=0, column=0)
    sa23_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w12 =Label(frame11,text="sa23_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w12.grid(row=0, column=0)
    sa23_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w13 =Label(frame11,text="sa23_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w13.grid(row=0, column=0)
    sa23_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w14 =Label(frame11,text="sa23_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w14.grid(row=0, column=0)
    sa23_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w15 =Label(frame11,text="sa23_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w15.grid(row=0, column=0)
    sa23_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w16 =Label(frame11,text="sa23_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w16.grid(row=0, column=0)
    sa23_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w17 =Label(frame11,text="sa23_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w17.grid(row=0, column=0)
    sa23_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w18 =Label(frame11,text="sa23_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w18.grid(row=0, column=0)
    sa23_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w19 =Label(frame11,text="sa23_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w19.grid(row=0, column=0)
    sa23_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w20 =Label(frame11,text="sa23_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w20.grid(row=0, column=0)
    sa23_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w21 =Label(frame11,text="sa23_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w21.grid(row=0, column=0)
    sa23_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w22 =Label(frame11,text="sa23_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w22.grid(row=0, column=0)
    sa23_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w23 =Label(frame11,text="sa23_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w23.grid(row=0, column=0)
    sa23_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w24 =Label(frame11,text="sa23_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w24.grid(row=0, column=0)
    sa23_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w25 =Label(frame11,text="sa23_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w25.grid(row=0, column=0)
    sa23_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w26 =Label(frame11,text="sa23_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w26.grid(row=0, column=0)
    sa23_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa23_w27 =Label(frame11,text="sa23_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w27.grid(row=0, column=0)
    sa23_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w28 =Label(frame11,text="sa23_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w28.grid(row=0, column=0)
    sa23_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w29 =Label(frame11,text="sa23_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w29.grid(row=0, column=0)
    sa23_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w30 =Label(frame11,text="sa23_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w30.grid(row=0, column=0)
    sa23_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa23_w31 =Label(frame11,text="sa23_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w31.grid(row=0, column=0)
    sa23_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa23_w32 =Label(frame11,text="sa23_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa23_w32.grid(row=0, column=0)
    sa23_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa23_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================sa24 ========================================
    
    sa24_btn = tk.Button(
        frame_list,
        text="SA24",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa24_popup
    )
    sa24_btn.grid(row=3, column=2, padx=10, pady=2,sticky="w")
     #===============================SUB ADDRESS 20=======================

    frame11=LabelFrame(root,text='sa24',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa24_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa24_w1=Label(frame11,text="sa24_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w1.grid(row=0, column=0)
    sa24_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w2 =Label(frame11,text="sa24_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w2.grid(row=0, column=0)
    sa24_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa24_w3 =Label(frame11,text="sa24_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w3.grid(row=0, column=0)
    sa24_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w4 =Label(frame11,text="sa24_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w4.grid(row=0, column=0)
    sa24_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w5 =Label(frame11,text="sa24_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w5.grid(row=0, column=0)
    sa24_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w6 =Label(frame11,text="sa24_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w6.grid(row=0, column=0)
    sa24_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w7 =Label(frame11,text="sa24_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w7.grid(row=0, column=0)
    sa24_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w8 =Label(frame11,text="sa24_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w8.grid(row=0, column=0)
    sa24_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w9 =Label(frame11,text="sa24_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w9.grid(row=0, column=0)
    sa24_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w10 =Label(frame11,text="sa24_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w10.grid(row=0, column=0)
    sa24_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w11 =Label(frame11,text="sa24_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w11.grid(row=0, column=0)
    sa24_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w12 =Label(frame11,text="sa24_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w12.grid(row=0, column=0)
    sa24_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w13 =Label(frame11,text="sa24_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w13.grid(row=0, column=0)
    sa24_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w14 =Label(frame11,text="sa24_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w14.grid(row=0, column=0)
    sa24_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w15 =Label(frame11,text="sa24_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w15.grid(row=0, column=0)
    sa24_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w16 =Label(frame11,text="sa24_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w16.grid(row=0, column=0)
    sa24_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w17 =Label(frame11,text="sa24_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w17.grid(row=0, column=0)
    sa24_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w18 =Label(frame11,text="sa24_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w18.grid(row=0, column=0)
    sa24_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w19 =Label(frame11,text="sa24_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w19.grid(row=0, column=0)
    sa24_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w20 =Label(frame11,text="sa24_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w20.grid(row=0, column=0)
    sa24_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w21 =Label(frame11,text="sa24_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w21.grid(row=0, column=0)
    sa24_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w22 =Label(frame11,text="sa24_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w22.grid(row=0, column=0)
    sa24_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w23 =Label(frame11,text="sa24_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w23.grid(row=0, column=0)
    sa24_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w24 =Label(frame11,text="sa24_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w24.grid(row=0, column=0)
    sa24_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w25 =Label(frame11,text="sa24_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w25.grid(row=0, column=0)
    sa24_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w26 =Label(frame11,text="sa24_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w26.grid(row=0, column=0)
    sa24_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa24_w27 =Label(frame11,text="sa24_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w27.grid(row=0, column=0)
    sa24_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w28 =Label(frame11,text="sa24_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w28.grid(row=0, column=0)
    sa24_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w29 =Label(frame11,text="sa24_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w29.grid(row=0, column=0)
    sa24_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w30 =Label(frame11,text="sa24_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w30.grid(row=0, column=0)
    sa24_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa24_w31 =Label(frame11,text="sa24_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w31.grid(row=0, column=0)
    sa24_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa24_w32 =Label(frame11,text="sa24_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa24_w32.grid(row=0, column=0)
    sa24_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa24_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================sa25 ========================================
    
    sa25_btn = tk.Button(
        frame_list,
        text="SA25",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa25_popup
    )
    sa25_btn.grid(row=3, column=3, padx=10, pady=2,sticky="w")
     #===============================SUB ADDRESS 20=======================

    frame11=LabelFrame(root,text='sa25',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa25_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa25_w1=Label(frame11,text="sa25_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w1.grid(row=0, column=0)
    sa25_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w2 =Label(frame11,text="sa25_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w2.grid(row=0, column=0)
    sa25_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa25_w3 =Label(frame11,text="sa25_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w3.grid(row=0, column=0)
    sa25_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w4 =Label(frame11,text="sa25_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w4.grid(row=0, column=0)
    sa25_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w5 =Label(frame11,text="sa25_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w5.grid(row=0, column=0)
    sa25_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w6 =Label(frame11,text="sa25_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w6.grid(row=0, column=0)
    sa25_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w7 =Label(frame11,text="sa25_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w7.grid(row=0, column=0)
    sa25_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w8 =Label(frame11,text="sa25_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w8.grid(row=0, column=0)
    sa25_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w9 =Label(frame11,text="sa25_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w9.grid(row=0, column=0)
    sa25_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w10 =Label(frame11,text="sa25_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w10.grid(row=0, column=0)
    sa25_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w11 =Label(frame11,text="sa25_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w11.grid(row=0, column=0)
    sa25_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w12 =Label(frame11,text="sa25_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w12.grid(row=0, column=0)
    sa25_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w13 =Label(frame11,text="sa25_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w13.grid(row=0, column=0)
    sa25_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w14 =Label(frame11,text="sa25_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w14.grid(row=0, column=0)
    sa25_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w15 =Label(frame11,text="sa25_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w15.grid(row=0, column=0)
    sa25_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w16 =Label(frame11,text="sa25_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w16.grid(row=0, column=0)
    sa25_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w17 =Label(frame11,text="sa25_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w17.grid(row=0, column=0)
    sa25_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w18 =Label(frame11,text="sa25_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w18.grid(row=0, column=0)
    sa25_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w19 =Label(frame11,text="sa25_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w19.grid(row=0, column=0)
    sa25_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w20 =Label(frame11,text="sa25_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w20.grid(row=0, column=0)
    sa25_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w21 =Label(frame11,text="sa25_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w21.grid(row=0, column=0)
    sa25_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w22 =Label(frame11,text="sa25_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w22.grid(row=0, column=0)
    sa25_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w23 =Label(frame11,text="sa25_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w23.grid(row=0, column=0)
    sa25_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w24 =Label(frame11,text="sa25_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w24.grid(row=0, column=0)
    sa25_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w25 =Label(frame11,text="sa25_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w25.grid(row=0, column=0)
    sa25_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w26 =Label(frame11,text="sa25_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w26.grid(row=0, column=0)
    sa25_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa25_w27 =Label(frame11,text="sa25_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w27.grid(row=0, column=0)
    sa25_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w28 =Label(frame11,text="sa25_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w28.grid(row=0, column=0)
    sa25_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w29 =Label(frame11,text="sa25_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w29.grid(row=0, column=0)
    sa25_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w30 =Label(frame11,text="sa25_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w30.grid(row=0, column=0)
    sa25_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa25_w31 =Label(frame11,text="sa25_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w31.grid(row=0, column=0)
    sa25_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa25_w32 =Label(frame11,text="sa25_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa25_w32.grid(row=0, column=0)
    sa25_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa25_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================sa26 ========================================
    
    sa26_btn = tk.Button(
        frame_list,
        text="SA26",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa26_popup
    )
    sa26_btn.grid(row=3, column=4, padx=10, pady=2,sticky="w")
     #===============================SUB ADDRESS 20=======================

    frame11=LabelFrame(root,text='sa26',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa26_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa26_w1=Label(frame11,text="sa26_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w1.grid(row=0, column=0)
    sa26_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w2 =Label(frame11,text="sa26_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w2.grid(row=0, column=0)
    sa26_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa26_w3 =Label(frame11,text="sa26_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w3.grid(row=0, column=0)
    sa26_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w4 =Label(frame11,text="sa26_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w4.grid(row=0, column=0)
    sa26_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w5 =Label(frame11,text="sa26_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w5.grid(row=0, column=0)
    sa26_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w6 =Label(frame11,text="sa26_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w6.grid(row=0, column=0)
    sa26_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w7 =Label(frame11,text="sa26_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w7.grid(row=0, column=0)
    sa26_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w8 =Label(frame11,text="sa26_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w8.grid(row=0, column=0)
    sa26_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w9 =Label(frame11,text="sa26_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w9.grid(row=0, column=0)
    sa26_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w10 =Label(frame11,text="sa26_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w10.grid(row=0, column=0)
    sa26_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w11 =Label(frame11,text="sa26_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w11.grid(row=0, column=0)
    sa26_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w12 =Label(frame11,text="sa26_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w12.grid(row=0, column=0)
    sa26_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w13 =Label(frame11,text="sa26_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w13.grid(row=0, column=0)
    sa26_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w14 =Label(frame11,text="sa26_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w14.grid(row=0, column=0)
    sa26_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w15 =Label(frame11,text="sa26_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w15.grid(row=0, column=0)
    sa26_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w16 =Label(frame11,text="sa26_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w16.grid(row=0, column=0)
    sa26_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w17 =Label(frame11,text="sa26_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w17.grid(row=0, column=0)
    sa26_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w18 =Label(frame11,text="sa26_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w18.grid(row=0, column=0)
    sa26_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w19 =Label(frame11,text="sa26_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w19.grid(row=0, column=0)
    sa26_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w20 =Label(frame11,text="sa26_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w20.grid(row=0, column=0)
    sa26_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w21 =Label(frame11,text="sa26_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w21.grid(row=0, column=0)
    sa26_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w22 =Label(frame11,text="sa26_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w22.grid(row=0, column=0)
    sa26_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w23 =Label(frame11,text="sa26_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w23.grid(row=0, column=0)
    sa26_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w24 =Label(frame11,text="sa26_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w24.grid(row=0, column=0)
    sa26_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w25 =Label(frame11,text="sa26_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w25.grid(row=0, column=0)
    sa26_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w26 =Label(frame11,text="sa26_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w26.grid(row=0, column=0)
    sa26_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa26_w27 =Label(frame11,text="sa26_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w27.grid(row=0, column=0)
    sa26_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w28 =Label(frame11,text="sa26_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w28.grid(row=0, column=0)
    sa26_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w29 =Label(frame11,text="sa26_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w29.grid(row=0, column=0)
    sa26_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w30 =Label(frame11,text="sa26_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w30.grid(row=0, column=0)
    sa26_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa26_w31 =Label(frame11,text="sa26_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w31.grid(row=0, column=0)
    sa26_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa26_w32 =Label(frame11,text="sa26_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa26_w32.grid(row=0, column=0)
    sa26_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa26_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    #==============================sa27 ========================================
    
    sa27_btn = tk.Button(
        frame_list,
        text="SA27",
        font=("Calibri", 12, "bold"),
        bg="dark blue",
        fg="white",
        width=8,
        command= open_sa27_popup
    )
    sa27_btn.grid(row=4, column=0, padx=10, pady=2,sticky="w")
     #===============================SUB ADDRESS 20=======================

    frame11=LabelFrame(root,text='sa27',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    
    #sa27_btn.grid(row=0, column=4, padx=2, pady=2, sticky="nsew")
    
    sa27_w1=Label(frame11,text="sa27_w1:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w1.grid(row=0, column=0)
    sa27_w1_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w1_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w2 =Label(frame11,text="sa27_w2:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w2.grid(row=0, column=0)
    sa27_w2_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w2_entry.grid(column=1,row=0,padx=2, pady=2)

    sa27_w3 =Label(frame11,text="sa27_w3:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w3.grid(row=0, column=0)
    sa27_w3_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w3_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w4 =Label(frame11,text="sa27_w4:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w4.grid(row=0, column=0)
    sa27_w4_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w4_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w5 =Label(frame11,text="sa27_w5:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w5.grid(row=0, column=0)
    sa27_w5_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w5_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w6 =Label(frame11,text="sa27_w6:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w6.grid(row=0, column=0)
    sa27_w6_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w6_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w7 =Label(frame11,text="sa27_w7:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w7.grid(row=0, column=0)
    sa27_w7_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w7_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w8 =Label(frame11,text="sa27_w8:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w8.grid(row=0, column=0)
    sa27_w8_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w8_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w9 =Label(frame11,text="sa27_w9:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w9.grid(row=0, column=0)
    sa27_w9_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w9_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w10 =Label(frame11,text="sa27_w10:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w10.grid(row=0, column=0)
    sa27_w10_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w10_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w11 =Label(frame11,text="sa27_w11:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w11.grid(row=0, column=0)
    sa27_w11_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w11_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w12 =Label(frame11,text="sa27_w12:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w12.grid(row=0, column=0)
    sa27_w12_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w12_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w13 =Label(frame11,text="sa27_w13:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w13.grid(row=0, column=0)
    sa27_w13_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w13_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w14 =Label(frame11,text="sa27_w14:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w14.grid(row=0, column=0)
    sa27_w14_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w14_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w15 =Label(frame11,text="sa27_w15:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w15.grid(row=0, column=0)
    sa27_w15_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w15_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w16 =Label(frame11,text="sa27_w16:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w16.grid(row=0, column=0)
    sa27_w16_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w16_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w17 =Label(frame11,text="sa27_w17:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w17.grid(row=0, column=0)
    sa27_w17_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w17_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w18 =Label(frame11,text="sa27_w18:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w18.grid(row=0, column=0)
    sa27_w18_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w18_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w19 =Label(frame11,text="sa27_w19:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w19.grid(row=0, column=0)
    sa27_w19_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w19_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w20 =Label(frame11,text="sa27_w20:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w20.grid(row=0, column=0)
    sa27_w20_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w20_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w21 =Label(frame11,text="sa27_w21:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w21.grid(row=0, column=0)
    sa27_w21_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w21_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w22 =Label(frame11,text="sa27_w22:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w22.grid(row=0, column=0)
    sa27_w22_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w22_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w23 =Label(frame11,text="sa27_w23:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w23.grid(row=0, column=0)
    sa27_w23_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w23_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w24 =Label(frame11,text="sa27_w24:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w24.grid(row=0, column=0)
    sa27_w24_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w24_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w25 =Label(frame11,text="sa27_w25:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w25.grid(row=0, column=0)
    sa27_w25_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w25_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w26 =Label(frame11,text="sa27_w26:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w26.grid(row=0, column=0)
    sa27_w26_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w26_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    sa27_w27 =Label(frame11,text="sa27_w27:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w27.grid(row=0, column=0)
    sa27_w27_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w27_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w28 =Label(frame11,text="sa27_w28:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w28.grid(row=0, column=0)
    sa27_w28_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w28_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w29 =Label(frame11,text="sa27_w29:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w29.grid(row=0, column=0)
    sa27_w29_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w29_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w30 =Label(frame11,text="sa27_w30:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w30.grid(row=0, column=0)
    sa27_w30_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w30_entry.grid(column=1,row=0,padx=2, pady=2) 
    
    sa27_w31 =Label(frame11,text="sa27_w31:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w31.grid(row=0, column=0)
    sa27_w31_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w31_entry.grid(column=1,row=0,padx=2, pady=2)
    
    sa27_w32 =Label(frame11,text="sa27_w32:",font=("Calibri", 11,"bold"),bg='lavender')
    sa27_w32.grid(row=0, column=0)
    sa27_w32_entry=Entry(frame11,width=10,state="readonly",font=("Calibri", 11,"bold"))
    sa27_w32_entry.grid(column=1,row=0,padx=2, pady=2)
    
    
    
    # ======================== PDOP ==========================

    frame10=LabelFrame(root,text='PDOP',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame10.grid(row=2,column=2,padx=2, pady=2,sticky="nse")

    pdop=Label(frame10,text="PDOP:",font=("Calibri", 11,"bold"),bg='lavender')
    pdop.grid(row=3, column=0)
    pdop=Entry(frame10,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pdop.grid(column=1,row=3,padx=2, pady=2)




    

 

    # ========================= SYS MODE AND WDT STATUS ===============================================
    frame14 = LabelFrame(root, text='SYS MODE &  WDT STS',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame14.grid(row=3, column=1, padx=2, pady=2, sticky="nsew")

    labels = [
    "Range log Type","Eph Retain En","Iono Smoothing", "INONO Enable", "GP2015 Lock", "RFFC5071 Lock", "Nav 1A",
    "Velocity Smoothing", "GPS2015 Ant2 Lock", "RAIM", "Carrier Smoothing",
    "System Mode", "Time Aligned To","Time Init From",
    ]

    gui_entry_dict = {}

    for i, label_text in enumerate(labels):
        label = Label(frame14, text=label_text+ ":",font=("Calibri", 11,"bold"), bg="lavender")
        label.grid(row=i, column=0, sticky="w", padx=5, pady=2)

        entry = Entry(frame14, width=12, state="readonly",font=("Calibri", 11,"bold"))
        entry.grid(row=i, column=1, padx=5, pady=2)
        gui_entry_dict[label_text] = entry
    #===========================================================================
    wdt_labels = [
        "Valid 1553 CMD CTR",
        "TM Selection",
        "SW Line/WDT Status",
        "HW WDT Status",
        "SPS1 S/W WDT STATUS",
        "SPS Software Status"
    ]

    wdt_entries = {}

    for i, label_txt in enumerate(wdt_labels):
        lbl = tk.Label(frame14, text=label_txt + ":",font=("Calibri", 11,"bold"), bg='lavender')
        lbl.grid(row=i+16, column=0, sticky='w')

        entry = tk.Entry(frame14, width=12, state="readonly", font=("Calibri", 11,"bold"))
        entry.grid(row=i+16, column=1, padx=2, pady=2)

        wdt_entries[label_txt] = entry

    # =========================== TRACKING INFO ======================

    frame8=LabelFrame(root,text="TRACKING INFO",bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame8.grid(row=3,column=0,padx=2, pady=2,sticky="new")

    channel=Label(frame8,text="Channel",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    channel.grid(row=4,column=1,padx=10,pady=10)

    ch1=Label(frame8,text="1",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch1.grid(row=5, column=1)
    ch2=Label(frame8,text="2",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch2.grid(column=1,row=6,pady=2,padx=2)
    ch3=Label(frame8,text="3",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch3.grid(column=1,row=7,pady=2,padx=2)
    ch4=Label(frame8,text="4",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch4.grid(column=1,row=8,pady=2,padx=2)
    ch5=Label(frame8,text="5",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch5.grid(column=1,row=9,pady=2,padx=2)
    ch6=Label(frame8,text="6",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch6.grid(column=1,row=10,pady=2,padx=2)
    ch7=Label(frame8,text="7",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch7.grid(column=1,row=11,pady=2,padx=2)
    ch8=Label(frame8,text="8",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch8.grid(column=1,row=12,pady=2,padx=2)
    ch9=Label(frame8,text="9",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch9.grid(column=1,row=13,pady=2,padx=2)
    ch10=Label(frame8,text="10",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch10.grid(column=1,row=14,pady=2,padx=2)
    ch11=Label(frame8,text="11",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch11.grid(column=1,row=15,pady=2,padx=2)
    ch12=Label(frame8,text="12",padx=5,pady=5,font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    ch12.grid(column=1,row=16,pady=2,padx=2)

    svid=Label(frame8,width=6,text="SVID",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    svid.grid(row=4,column=2,padx=10,pady=10)

    svid1=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid1.grid(column=2,row=5,pady=2,padx=2)
    svid2=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid2.grid(column=2,row=6,pady=2,padx=2)
    svid3=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid3.grid(column=2,row=7,pady=2,padx=2)
    svid4=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid4.grid(column=2,row=8,pady=2,padx=2)
    svid5=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid5.grid(column=2,row=9,pady=2,padx=2)
    svid6=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid6.grid(column=2,row=10,pady=2,padx=2)
    svid7=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid7.grid(column=2,row=11,pady=2,padx=2)
    svid8=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid8.grid(column=2,row=12,pady=2,padx=2)
    svid9=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid9.grid(column=2,row=13,pady=2,padx=2)
    svid10=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid10.grid(column=2,row=14,pady=2,padx=2)
    svid11=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid11.grid(column=2,row=15,pady=2,padx=2)
    svid12=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    svid12.grid(column=2,row=16,pady=2,padx=2)

    cndr=Label(frame8,width=6,text="CNDR",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    cndr.grid(row=4,column=3,padx=10,pady=10)

    cndr1=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr1.grid(column=3,row=5,pady=2,padx=2)
    cndr2=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr2.grid(column=3,row=6,pady=2,padx=2)
    cndr3=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr3.grid(column=3,row=7,pady=2,padx=2)
    cndr4=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr4.grid(column=3,row=8,pady=2,padx=2)
    cndr5=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr5.grid(column=3,row=9,pady=2,padx=2)
    cndr6=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr6.grid(column=3,row=10,pady=2,padx=2)
    cndr7=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr7.grid(column=3,row=11,pady=2,padx=2)
    cndr8=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr8.grid(column=3,row=12,pady=2,padx=2)
    cndr9=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr9.grid(column=3,row=13,pady=2,padx=2)
    cndr10=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr10.grid(column=3,row=14,pady=2,padx=2)
    cndr11=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr11.grid(column=3,row=15,pady=2,padx=2)
    cndr12=Entry(frame8,width=6,state="readonly",font=("Calibri", 11,"bold"))
    cndr12.grid(column=3,row=16,pady=2,padx=2)

    t=Label(frame8,text="T",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    t.grid(row=4,column=4,padx=5,pady=5)

    t1=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t1.grid(column=4,row=5,pady=2,padx=2)
    t2=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t2.grid(column=4,row=6,pady=2,padx=2)
    t3=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t3.grid(column=4,row=7,pady=2,padx=2)
    t4=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t4.grid(column=4,row=8,pady=2,padx=2)
    t5=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t5.grid(column=4,row=9,pady=2,padx=2)
    t6=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t6.grid(column=4,row=10,pady=2,padx=2)
    t7=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t7.grid(column=4,row=11,pady=2,padx=2)
    t8=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t8.grid(column=4,row=12,pady=2,padx=2)
    t9=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t9.grid(column=4,row=13,pady=2,padx=2)
    t10=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t10.grid(column=4,row=14,pady=2,padx=2)
    t11=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t11.grid(column=4,row=15,pady=2,padx=2)
    t12=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    t12.grid(column=4,row=16,pady=2,padx=2)


    p=Label(frame8,text="P",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    p.grid(row=4,column=5,padx=5,pady=5)

    p1=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p1.grid(column=5,row=5,pady=2,padx=2)
    p2=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p2.grid(column=5,row=6,pady=2,padx=2)
    p3=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p3.grid(column=5,row=7,pady=2,padx=2)
    p4=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p4.grid(column=5,row=8,pady=2,padx=2)
    p5=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p5.grid(column=5,row=9,pady=2,padx=2)
    p6=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p6.grid(column=5,row=10,pady=2,padx=2)
    p7=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p7.grid(column=5,row=11,pady=2,padx=2)
    p8=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p8.grid(column=5,row=12,pady=2,padx=2)
    p9=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p9.grid(column=5,row=13,pady=2,padx=2)
    p10=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p10.grid(column=5,row=14,pady=2,padx=2)
    p11=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p11.grid(column=5,row=15,pady=2,padx=2)
    p12=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    p12.grid(column=5,row=16,pady=2,padx=2)


    e=Label(frame8,text="E",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    e.grid(row=4,column=6,padx=5,pady=5)

    e1=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e1.grid(column=6,row=5,pady=2,padx=2)
    e2=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e2.grid(column=6,row=6,pady=2,padx=2)
    e3=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e3.grid(column=6,row=7,pady=2,padx=2)
    e4=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e4.grid(column=6,row=8,pady=2,padx=2)
    e5=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e5.grid(column=6,row=9,pady=2,padx=2)
    e6=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e6.grid(column=6,row=10,pady=2,padx=2)
    e7=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e7.grid(column=6,row=11,pady=2,padx=2)
    e8=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e8.grid(column=6,row=12,pady=2,padx=2)
    e9=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e9.grid(column=6,row=13,pady=2,padx=2)
    e10=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e10.grid(column=6,row=14,pady=2,padx=2)
    e11=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e11.grid(column=6,row=15,pady=2,padx=2)
    e12=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    e12.grid(column=6,row=16,pady=2,padx=2)

    d=Label(frame8,text="D",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    d.grid(row=4,column=7,padx=5,pady=5)

    d1=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d1.grid(column=7,row=5,pady=2,padx=2)
    d2=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d2.grid(column=7,row=6,pady=2,padx=2)

    d3=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d3.grid(column=7,row=7,pady=2,padx=2)
    d4=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d4.grid(column=7,row=8,pady=2,padx=2)
    d5=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d5.grid(column=7,row=9,pady=2,padx=2)
    d6=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d6.grid(column=7,row=10,pady=2,padx=2)
    d7=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d7.grid(column=7,row=11,pady=2,padx=2)
    d8=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d8.grid(column=7,row=12,pady=2,padx=2)
    d9=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d9.grid(column=7,row=13,pady=2,padx=2)
    d10=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d10.grid(column=7,row=14,pady=2,padx=2)
    d11=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d11.grid(column=7,row=15,pady=2,padx=2)

    d12=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    d12.grid(column=7,row=16,pady=2,padx=2)


    i=Label(frame8,text="I",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    i.grid(row=4,column=8,padx=5,pady=5)

    i1=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i1.grid(column=8,row=5,pady=2,padx=2)
    i2=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i2.grid(column=8,row=6,pady=2,padx=2)
    i3=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i3.grid(column=8,row=7,pady=2,padx=2)
    i4=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i4.grid(column=8,row=8,pady=2,padx=2)
    i5=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i5.grid(column=8,row=9,pady=2,padx=2)
    i6=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i6.grid(column=8,row=10,pady=2,padx=2)
    i7=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i7.grid(column=8,row=11,pady=2,padx=2)
    i8=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i8.grid(column=8,row=12,pady=2,padx=2)
    i9=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i9.grid(column=8,row=13,pady=2,padx=2)
    i10=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i10.grid(column=8,row=14,pady=2,padx=2)
    i11=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i11.grid(column=8,row=15,pady=2,padx=2)
    i12=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    i12.grid(column=8,row=16,pady=2,padx=2)


    r=Label(frame8,text="R",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    r.grid(row=4,column=9,padx=5,pady=5)

    r1=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r1.grid(column=9,row=5,pady=2,padx=2)
    r2=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r2.grid(column=9,row=6,pady=2,padx=2)
    r3=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r3.grid(column=9,row=7,pady=2,padx=2)
    r4=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r4.grid(column=9,row=8,pady=2,padx=2)
    r5=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r5.grid(column=9,row=9,pady=2,padx=2)
    r6=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r6.grid(column=9,row=10,pady=2,padx=2)
    r7=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r7.grid(column=9,row=11,pady=2,padx=2)
    r8=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r8.grid(column=9,row=12,pady=2,padx=2)
    r9=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r9.grid(column=9,row=13,pady=2,padx=2)
    r10=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r10.grid(column=9,row=14,pady=2,padx=2)
    r11=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r11.grid(column=9,row=15,pady=2,padx=2)
    r12=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    r12.grid(column=9,row=16,pady=2,padx=2)


    h=Label(frame8,text="H",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    h.grid(row=4,column=10,padx=5,pady=5)

    h1=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h1.grid(column=10,row=5,pady=2,padx=2)
    h2=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h2.grid(column=10,row=6,pady=2,padx=2)
    h3=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h3.grid(column=10,row=7,pady=2,padx=2)
    h4=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h4.grid(column=10,row=8,pady=2,padx=2)
    h5=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h5.grid(column=10,row=9,pady=2,padx=2)
    h6=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h6.grid(column=10,row=10,pady=2,padx=2)
    h7=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h7.grid(column=10,row=11,pady=2,padx=2)
    h8=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h8.grid(column=10,row=12,pady=2,padx=2)
    h9=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h9.grid(column=10,row=13,pady=2,padx=2)
    h10=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h10.grid(column=10,row=14,pady=2,padx=2)
    h11=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h11.grid(column=10,row=15,pady=2,padx=2)
    h12=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    h12.grid(column=10,row=16,pady=2,padx=2)

    a=Label(frame8,text="A",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    a.grid(row=4,column=11,padx=5,pady=5)

    a1=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a1.grid(column=11,row=5,pady=2,padx=2)
    a2=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a2.grid(column=11,row=6,pady=2,padx=2)
    a3=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a3.grid(column=11,row=7,pady=2,padx=2)
    a4=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a4.grid(column=11,row=8,pady=2,padx=2)
    a5=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a5.grid(column=11,row=9,pady=2,padx=2)
    a6=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a6.grid(column=11,row=10,pady=2,padx=2)
    a7=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a7.grid(column=11,row=11,pady=2,padx=2)
    a8=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a8.grid(column=11,row=12,pady=2,padx=2)
    a9=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a9.grid(column=11,row=13,pady=2,padx=2)
    a10=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a10.grid(column=11,row=14,pady=2,padx=2)
    a11=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a11.grid(column=11,row=15,pady=2,padx=2)
    a12=Entry(frame8,width=2,state="readonly",font=("Calibri", 11,"bold"))
    a12.grid(column=11,row=16,pady=2,padx=2)

    iode=Label(frame8,width=12,text="IODE",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    iode.grid(row=4,column=12,padx=10,pady=10)

    iode1=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode1.grid(column=12,row=5,pady=2,padx=2)
    iode2=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode2.grid(column=12,row=6,pady=2,padx=2)
    iode3=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode3.grid(column=12,row=7,pady=2,padx=2)
    iode4=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode4.grid(column=12,row=8,pady=2,padx=2)
    iode5=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode5.grid(column=12,row=9,pady=2,padx=2)
    iode6=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode6.grid(column=12,row=10,pady=2,padx=2)
    iode7=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode7.grid(column=12,row=11,pady=2,padx=2)
    iode8=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode8.grid(column=12,row=12,pady=2,padx=2)
    iode9=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode9.grid(column=12,row=13,pady=2,padx=2)
    iode10=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode10.grid(column=12,row=14,pady=2,padx=2)
    iode11=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode11.grid(column=12,row=15,pady=2,padx=2)
    iode12=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode12.grid(column=12,row=16,pady=2,padx=2)

    pr=Label(frame8,width=12,text="PR(cm)",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    pr.grid(row=4,column=13,padx=10,pady=10)

    pr1=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr1.grid(column=13,row=5,pady=2,padx=2)
    pr2=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr2.grid(column=13,row=6,pady=2,padx=2)
    pr3=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr3.grid(column=13,row=7,pady=2,padx=2)
    pr4=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr4.grid(column=13,row=8,pady=2,padx=2)
    pr5=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr5.grid(column=13,row=9,pady=2,padx=2)
    pr6=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr6.grid(column=13,row=10,pady=2,padx=2)
    pr7=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr7.grid(column=13,row=11,pady=2,padx=2)
    pr8=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr8.grid(column=13,row=12,pady=2,padx=2)
    pr9=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr9.grid(column=13,row=13,pady=2,padx=2)
    pr10=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr10.grid(column=13,row=14,pady=2,padx=2)
    pr11=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr11.grid(column=13,row=15,pady=2,padx=2)
    pr12=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    pr12.grid(column=13,row=16,pady=2,padx=2)


    dr=Label(frame8,width=12,text="DR(m/s)",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    dr.grid(row=4,column=14,padx=10,pady=10)

    dr1=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr1.grid(column=14,row=5,pady=2,padx=2)
    dr2=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr2.grid(column=14,row=6,pady=2,padx=2)
    dr3=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr3.grid(column=14,row=7,pady=2,padx=2)
    dr4=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr4.grid(column=14,row=8,pady=2,padx=2)
    dr5=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr5.grid(column=14,row=9,pady=2,padx=2)
    dr6=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr6.grid(column=14,row=10,pady=2,padx=2)
    dr7=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr7.grid(column=14,row=11,pady=2,padx=2)
    dr8=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr8.grid(column=14,row=12,pady=2,padx=2)
    dr9=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr9.grid(column=14,row=13,pady=2,padx=2)
    dr10=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr10.grid(column=14,row=14,pady=2,padx=2)
    dr11=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr11.grid(column=14,row=15,pady=2,padx=2)
    dr12=Entry(frame8,width=12,state="readonly",font=("Calibri", 11,"bold"))
    dr12.grid(column=14,row=16,pady=2,padx=2)
    



    #======================================++++++++++++++
    frame11=LabelFrame(root,text='TABLE',bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame11.grid(row=1,column=3,pady=2,padx=2,sticky="nsW")

    Last_Reset_Time=Label(frame11,text="Last_Reset_Time:",font=("Calibri", 11,"bold"),bg='lavender')
    Last_Reset_Time.grid(row=1, column=0)
    lrt=Entry(frame11,width=12,state="readonly",font=("Calibri", 11,"bold"))
    lrt.grid(column=1,row=1,pady=2,padx=2)

    SVID_IODE=Label(frame11,text="SVID:",font=("Calibri", 11,"bold"),bg='lavender')
    SVID_IODE.grid(row=2, column=0)
    SI=Entry(frame11,width=12,state="readonly",font=("Calibri", 11,"bold"))
    SI.grid(column=1,row=2,pady=2,padx=2)

    iode=Label(frame11,text="IODE:",font=("Calibri", 11,"bold"),bg='lavender')
    iode.grid(row=3, column=0)
    iode=Entry(frame11,width=12,state="readonly",font=("Calibri", 11,"bold"))
    iode.grid(column=1,row=3,pady=2,padx=2)

    CRS=Label(frame11,text="CRS:",font=("Calibri", 11,"bold"),bg='lavender')
    CRS.grid(row=4, column=0)
    crs=Entry(frame11,width=12,state="readonly",font=("Calibri", 11,"bold"))
    crs.grid(column=1,row=4,pady=2,padx=2)

    odp=Label(frame11,text="ODP status:",font=("Calibri", 11,"bold"),bg='lavender')
    odp.grid(row=5, column=0)
    odp=Entry(frame11,width=12,state="readonly",font=("Calibri", 11,"bold"))
    odp.grid(column=1,row=5,pady=2,padx=2)

    phase_center=Label(frame11,text="Phase_center_Corr:",font=("Calibri", 11,"bold"),bg='lavender')
    phase_center.grid(row=6, column=0)
    phase_center=Entry(frame11,width=12,state="readonly",font=("Calibri", 11,"bold"))
    phase_center.grid(column=1,row=6,pady=2,padx=2)

    phase_center_sps=Label(frame11,text="Phase cen for SPS:",font=("Calibri", 11,"bold"),bg='lavender')
    phase_center_sps.grid(row=7, column=0)
    phase_center_sps=Entry(frame11,width=12,state="readonly",font=("Calibri", 11,"bold"))
    phase_center_sps.grid(column=1,row=7,pady=2,padx=2)

     # ===========================SA29 RAW INFO ======================

    frame15=LabelFrame(root,text="SA29_RAW_DATA",bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame15.grid(row=3,column=0,padx=2, pady=2,sticky="sew")

    raw=Label(frame15,text="HEX_DATA:",font=("Calibri", 11,"bold"),bg="lavender",fg="purple")
    raw.grid(row=0,column=0,padx=10,pady=10)
    raw_data=Entry(frame15,width=70,state="readonly",font=("Calibri", 15,"bold"))
    raw_data.grid(column=1,row=0,pady=2,padx=2)







    # ==================== TTF ====================================
    '''frame12 = LabelFrame(root, text="TTF",bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )
    frame12.grid(row=3, column=3, padx=2, pady=2, sticky="new")

    TTF=Label(frame12,text="TTF:",font=("Calibri", 11,"bold"),bg='lavender')
    TTF.grid(row=0, column=0)
    ttf=Entry(frame12,width=20,state="readonly",font=("Calibri", 11,"bold"))
    ttf.grid(column=1,row=0,padx=2, pady=2)

    def reset_ttf():
        global TTF
        TTF = None
        ttf.config(text="TTF: --")
        print("TTF has been reset.")

    reset_ttf_button = Button(frame12, text="Reset TTF", command=reset_ttf, bg="lavender", font=("Arial", 9))
    reset_ttf_button.grid(row=0, column=2, padx=5, pady=2, sticky="w")'''

    # ========================== GRAPH ============================
    frame_cndr_plot = tk.LabelFrame(root, text="CNDR VS SVID PLOT",bg="lavender",
    fg="purple",
    font=("Calibri", 13, "bold"),
    relief="solid",         # makes edges visible(solid,ridge,raised,groove,sunken,flat)
    bd=2,                    # border thickness
    padx=2, pady=2         # internal padding simulates rounded spacing
    )

    frame_cndr_plot.grid(row=3, column=2, padx=2, pady=2, sticky="sew")



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

    # === Footer Section inside scrollable area ===
    separator = Frame(window, bg="black", height=2)
    separator.grid(row=99, column=0, columnspan=40, sticky="ew", pady=(10, 0))

    footer_label = Label(
        window,
        text=f"copyright@2026, Flight Dynamics Navigation Group/URSC/ISRO | Version 1.0 | {display_name} UI",
        font=("Segoe UI", 12, "bold"),
        bg="purple",
        fg="white",
        pady=2
    )
    footer_label.grid(row=100, column=0, columnspan=20, sticky="nsew")


    
    root.grid_rowconfigure(0, weight=2)
    root.grid_rowconfigure(1, weight=2)
    root.grid_rowconfigure(2, weight=2)
    root.grid_rowconfigure(3, weight=2)
    root.grid_columnconfigure(0,weight=2)
    root.grid_columnconfigure(1,weight=2)
    root.grid_columnconfigure(2,weight=2)
    root.grid_columnconfigure(3,weight=2)
    baud_select()
    update_coms()
    bind_all_params_to_plots()
    canvas.create_window((0, 0), window=root, anchor="nw")
    root.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
    # ✅ CORRECT BINDING: Use toplevel to get the Tk window, not the Frame
    root.winfo_toplevel().protocol("WM_DELETE_WINDOW", close_window)
    root.mainloop()
    

# ==================== THREAD-SAFE HELPERS ====================
def safe_status(msg):
    """Updates status bar safely from background threads"""
    try:
        # Uses global status_var defined in connect_menu_init
        root.after(0, status_var.set, msg)
    except: pass

def log_cmd(msg):
    """Writes to your exact command log file format"""
    try:
        with open("(SA1-SA12)(ISL and ISR)Command_logg.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n")
    except: pass

def format_hex_bytes(data):
    """Converts bytes to ['0xAC', ...] format"""
    return [f'0x{b:02X}' for b in data]

def safe_serial_write(data):
    """Thread-safe write: prevents interleaving if multiple SAs send at once"""
    with serial_write_lock:
        if ser and ser.is_open:
            ser.write(data)

# ==================== MAIN COMMAND DISPATCHER ====================
def send_command(sa, inp_text):
    """Routes manual input based on SA type"""
    inp_text = inp_text.strip().strip('"\'').strip()

    if not inp_text:
        safe_status(f"❌ {sa}: Enter hex data or browse a file.")
        return
    if not (ser and ser.is_open):
        safe_status("❌ Serial port not open. Connect first.")
        return
    if sa_active.get(sa, False):
        safe_status(f"❌ {sa} already running! Click STOP first.")
        return

    # File vs Manual routing
    filepath = os.path.normpath(inp_text)
    if os.path.isfile(filepath):
        threading.Thread(target=_run_file, args=(sa, filepath), daemon=True).start()
    else:
        # Manual input routing
        if sa in ("SA1", "SA2"):
            _run_manual(sa1_2=sa, txt=inp_text)
        elif sa in ("SA3", "SA4","SA12"):
            _run_manual_sa3_4_12(sa, inp_text)
         # Manual input routing
        elif sa in ("SA5_9(ISL)"):
            _run_manual_sa5_9(sa, inp_text)
        else :
            _run_manual_sa10_11(sa, inp_text)
       


# ==================== MANUAL SEND LOGIC (SA1 & SA2: 3 Data Words) ====================
def _run_manual(sa1_2, txt):
    try:
        parts = txt.split()
        if len(parts) != 3:
            safe_status(f"❌ {sa1_2}: Enter exactly 3 data words (e.g., 0x0000 0x0004 0x0055)")
            return

        words = [int(p, 16) for p in parts]
        hdr_map = {"SA1": 0x01, "SA2": 0x02}
        hdr = [0xAC, 0xCA, 0x1F, hdr_map.get(sa1_2, 0x02)]

        pkt = hdr + [b for w in words for b in w.to_bytes(2, 'big')]
        hex_pkt = format_hex_bytes(pkt)

        safe_serial_write(bytes(pkt))
        safe_status(f"✅ Manual {sa1_2} command sent: {hex_pkt}")
        log_cmd(f"MANUAL {sa1_2} | {hex_pkt}")

    except ValueError:
        safe_status("❌ Invalid hex format. Use e.g., 0x0000 0x0004 0x0055")
    except Exception as e:
        safe_status(f"❌ Error sending manual command: {e}")

# ==================== MANUAL SEND LOGIC (SA3 & SA4: Exactly 64 Bytes) ====================
def _run_manual_sa3_4_12(sa, txt):
    try:
        # Strip all non-hex characters (spaces, 0x, etc.)
        hex_str = re.sub(r'[^0-9a-fA-F]', '', txt)

        # 64 bytes = 128 hex characters
        if len(hex_str) != 128:
            safe_status(f"❌ {sa}: Input must be exactly 64 bytes (128 continuous hex characters). Got {len(hex_str)} chars.")
            return

        payload = bytes.fromhex(hex_str)
        hdr_map = {"SA3": 0x03, "SA4": 0x04,"SA12": 0X07}
        hdr = [0xAC, 0xCA, 0x1F, hdr_map.get(sa, 0x03)]

        pkt = hdr + list(payload)
        hex_pkt = format_hex_bytes(pkt)

        safe_serial_write(bytes(pkt))
        safe_status(f"✅ Manual {sa} command sent: {hex_pkt}")
        log_cmd(f"MANUAL {sa} | {hex_pkt}")

    except ValueError:
        safe_status("❌ Invalid hex format. Ensure input is exactly 128 continuous hex digits (64 bytes).")
    except Exception as e:
        safe_status(f"❌ Error sending manual command: {e}")
# ==================== MANUAL SEND LOGIC (SA5_9: Exactly 64 Bytes) ====================
def _run_manual_sa5_9(sa, txt):
    try:
        # Strip all non-hex characters (spaces, 0x, etc.)
        hex_str = re.sub(r'[^0-9a-fA-F]', '', txt)

        # 320 bytes = 640 hex characters
        if len(hex_str) != 640:
            safe_status(f"❌ {sa}: Input must be exactly 64 bytes (128 continuous hex characters). Got {len(hex_str)} chars.")
            return

        payload = bytes.fromhex(hex_str)
        hdr_map = {"SA5_9(ISL)": 0X05}
        hdr = [0xAC, 0xCA, 0x1F, hdr_map.get(sa, 0x05)]

        pkt = hdr + list(payload)
        hex_pkt = format_hex_bytes(pkt)

        safe_serial_write(bytes(pkt))
        safe_status(f"✅ Manual {sa} command sent: {hex_pkt}")
        log_cmd(f"MANUAL {sa} | {hex_pkt}")

    except ValueError:
        safe_status("❌ Invalid hex format. Ensure input is exactly 640 continuous hex digits (320 bytes).")
    except Exception as e:
        safe_status(f"❌ Error sending manual command: {e}")
# ==================== MANUAL SEND LOGIC (SA10_11(ISR): Exactly 64 Bytes) ====================
def _run_manual_sa10_11(sa, txt):
    try:
        # Strip all non-hex characters (spaces, 0x, etc.)
        hex_str = re.sub(r'[^0-9a-fA-F]', '', txt)

        # 128 bytes = 256 hex characters
        if len(hex_str) != 256:
            safe_status(f"❌ {sa}: Input must be exactly 64 bytes (128 continuous hex characters). Got {len(hex_str)} chars.")
            return

        payload = bytes.fromhex(hex_str)
        hdr_map = {"SA10_11(ISR)": 0X06}
        hdr = [0xAC, 0xCA, 0x1F, hdr_map.get(sa, 0x06)]

        pkt = hdr + list(payload)
        hex_pkt = format_hex_bytes(pkt)

        safe_serial_write(bytes(pkt))
        safe_status(f"✅ Manual {sa} command sent: {hex_pkt}")
        log_cmd(f"MANUAL {sa} | {hex_pkt}")

    except ValueError:
        safe_status("❌ Invalid hex format. Ensure input is exactly 256 continuous hex digits (128 bytes).")
    except Exception as e:
        safe_status(f"❌ Error sending manual command: {e}")



# ==================== FILE SEND LOGIC ====================
def _run_file(sa, fpath):
    """Handles state for all file operations"""
    if not sa_active.get(sa):
        sa_active[sa] = True
    btn = sa_stop_btns.get(sa)
    if btn:
        try: btn.config(state="normal")
        except: pass

    try:
        if sa == "SA1": _sa1_sync(fpath)

        elif sa == "SA2": _sa2_imm(fpath)
        elif sa == "SA3": _sa3_cont(fpath, 0.064)
        elif sa == "SA4": _sa4_cont(fpath, 1.0)
        elif sa == "SA5_9(ISL)": _sa5_9_cont(fpath, 1.0)
        elif sa == "SA10_11(ISR)": _sa10_11_cont(fpath, 1.0)
        elif sa == "SA12": _sa12_cont(fpath, 1.0)
        
        else: safe_status(f"❌ Unknown SA: {sa}")
    except Exception as e:
        safe_status(f"❌ {sa} File Error: {e}")
    finally:
        sa_active[sa] = False
        if btn:
            try: btn.config(state="disabled")
            except: pass

def _sa1_sync(fpath):
    try:
        # 1. Read & clean file content
        raw_text = open(fpath, 'r', errors='ignore').read()
        cleaned = re.sub(r'#.*$', '', raw_text, flags=re.MULTILINE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = cleaned.replace('0x', '').replace('0X', '')
        tokens = [t for t in cleaned.split() if t]

        # Validate minimum structure
        if len(tokens) < 4:
            safe_status("❌ SA1 File: Invalid format. Expected: TARGET_SEC HEX1 HEX2 HEX3")
            return

        # Parse into packets: (target_time, [word1, word2, word3])
        pkts = []
        for i in range(0, len(tokens) - 2, 4):
            try:
                target = int(tokens[i])
                words = [tokens[i+1], tokens[i+2], tokens[i+3]]
                pkts.append((target, words))
            except ValueError:
                continue  # Skip malformed lines safely

        safe_status(f"📋 SA1: Loaded {len(pkts)} time-synced commands.")

        # 2. Execute with YOUR EXACT LOGIC
        for target, words in pkts:
            if not sa_active.get("SA1"):
                break

            # Continuous polling loop for synchronization
            while sa_active.get("SA1"):
                with sys_second_lock:
                    current_sec = latest_sys_second

                if current_sec == target:
                    # ✅ 1. IF SYS_SEC MATCHED -> SEND COMMAND
                    try:
                        pkt = [0xAC, 0xCA, 0x1F, 0x01] + [b for w in words for b in int(w, 16).to_bytes(2, 'big')]
                        hex_pkt = format_hex_bytes(pkt)
                        safe_serial_write(bytes(pkt))
                        safe_status(f"✅ SA1 at SYS_SEC={target}: {hex_pkt}")
                        log_cmd(f"SA1 | Executed at SYS_SEC={target}: {hex_pkt}")
                    except Exception as e:
                        safe_status(f"❌ SA1: Packet build error at {target}: {e}")
                    break  # ✅ Command sent, exit wait loop & go to next file line

                elif current_sec > target:
                    # ✅ 3. IF SYS_SEC IS GREATER -> SKIP AND SEARCH IN NEXT
                    safe_status(f"⏩ SA1: Skipped target {target} (current SYS_SEC={current_sec})")
                    break  # ✅ Missed it, exit wait loop & go to next file line

                else:
                    # ✅ 2. IF SYS_SEC IS LESS -> WAIT UNTIL MATCH COMES
                    cmdtime.sleep(0.05)  # Poll every 50ms to keep CPU low & responsive

        if sa_active.get("SA1"):
            safe_status("✅ SA1: All commands processed!")
    except Exception as e:
        safe_status(f"❌ SA1 File Error: {e}")



# ==================== SA2: IMMEDIATE FILE ====================
def _sa2_imm(fpath):
    try:
        tokens = re.findall(r'[0-9a-fA-F]+', open(fpath, 'r', errors='ignore').read())
        if len(tokens) % 3 != 0:
            safe_status("❌ SA2 File: Format: HEX1 HEX2 HEX3 (must be multiple of 3)")
            return

        pkts = [tokens[i:i+3] for i in range(0, len(tokens), 3)]
        safe_status(f"📋 SA2: Sending {len(pkts)} commands...")

        for i, words in enumerate(pkts):
            if not sa_active.get("SA2"): break

            pkt = [0xAC, 0xCA, 0x1F, 0x02] + [b for w in words for b in int(w,16).to_bytes(2,'big')]
            hex_pkt = format_hex_bytes(pkt)
            safe_serial_write(bytes(pkt))
            safe_status(f"✅ SA2: {hex_pkt}")
            log_cmd(f"SA2 | SA2 command {i+1}/{len(pkts)}: {hex_pkt}")
            cmdtime.sleep(0.01)

        if sa_active.get("SA2"): safe_status("✅ SA2: All commands sent")
    except Exception as e:
        safe_status(f"❌ SA2 File Error: {e}")

# ==================== SA3: CONTINUOUS 64MS ====================
def _sa3_cont(fpath, interval):
    try:
        with open(fpath, 'rb') as f: raw = f.read()
        try:
            # Try reading as ASCII hex first
            file_bytes = bytes.fromhex(''.join(c for c in raw.decode('ascii') if c in '0123456789abcdefABCDEF'))
        except:
            # Fallback to raw binary
            file_bytes = raw

        if len(file_bytes) < 64:
            safe_status("❌ SA3: File must contain at least 64 bytes of data.")
            return

        header = [0xAC, 0xCA, 0x1F, 0x03]
        num_blocks = len(file_bytes) // 64
        idx = 0

        while sa_active.get("SA3") and ser and ser.is_open:
            start = idx * 64
            end = start + 64
            if end > len(file_bytes):
                if sa_active.get("SA3"): safe_status("⏹️ SA3 sending finished.")
                break

            chunk = file_bytes[start:end]
            packet = bytes(header) + chunk
            hex_pkt = format_hex_bytes(packet)

            safe_serial_write(packet)
            safe_status(f"✅ SA3 packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")
            log_cmd(f"SA3 | SA3 packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")

            idx += 1
            cmdtime.sleep(interval) # 0.064s

        if sa_active.get("SA3"): safe_status("⏹️ SA3 finished")
    except Exception as e:
        safe_status(f"❌ Error in SA3 send: {e}")
        sa_active["SA3"] = False

# ==================== SA4: CONTINUOUS 1s ====================
def _sa4_cont(fpath, interval):
    try:
        with open(fpath, 'rb') as f: raw = f.read()
        try:
            file_bytes = bytes.fromhex(''.join(c for c in raw.decode('ascii') if c in '0123456789abcdefABCDEF'))
        except:
            file_bytes = raw

        if len(file_bytes) < 64:
            safe_status("❌ SA4: File must contain at least 64 bytes of data.")
            return

        header = [0xAC, 0xCA, 0x1F, 0x04]
        num_blocks = len(file_bytes) // 64
        idx = 0

        while sa_active.get("SA4") and ser and ser.is_open:
            start = idx * 64
            end = start + 64
            if end > len(file_bytes):
                if sa_active.get("SA4"): safe_status("⏹️ SA4 sending finished.")
                break

            chunk = file_bytes[start:end]
            packet = bytes(header) + chunk
            hex_pkt = format_hex_bytes(packet)

            safe_serial_write(packet)
            safe_status(f"✅ SA4 packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")
            log_cmd(f"SA4 | SA4 packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")

            idx += 1
            cmdtime.sleep(interval) # 1.0s

        if sa_active.get("SA4"): safe_status("⏹️ SA4 finished")
    except Exception as e:
        safe_status(f"❌ Error in SA4 send: {e}")
        sa_active["SA4"] = False


# ==================== SA5_9: CONTINUOUS 1s ====================
def _sa5_9_cont(fpath, interval):
    try:
        with open(fpath, 'rb') as f: raw = f.read()
        try:
            file_bytes = bytes.fromhex(''.join(c for c in raw.decode('ascii') if c in '0123456789abcdefABCDEF'))
        except:
            file_bytes = raw

        if len(file_bytes) < 320:
            safe_status("❌ SA5_9(ISL): File must contain at least 320 bytes of data.")
            return

        header = [0xAC, 0xCA, 0x1F, 0x05]
        num_blocks = len(file_bytes) // 320
        idx = 0

        while sa_active.get("SA5_9(ISL)") and ser and ser.is_open:
            start = idx * 320
            end = start + 320
            if end > len(file_bytes):
                if sa_active.get("SA5_9(ISL)"): safe_status("⏹️ ISL(SA5_9) sending finished.")
                break

            chunk = file_bytes[start:end]
            packet = bytes(header) + chunk
            hex_pkt = format_hex_bytes(packet)

            safe_serial_write(packet)
            safe_status(f"✅ ISL(SA5_9) packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")
            log_cmd(f"ISL(SA5_9) | ISL(SA5_9) packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")

            idx += 1
            cmdtime.sleep(interval) # 1.0s

        if sa_active.get("SA5_9(ISL)"): safe_status("⏹️ ISL(SA5_9) finished")
    except Exception as e:
        safe_status(f"❌ Error in ISL send: {e}")
        sa_active["SA5_9(ISL)"] = False
# ==================== ISR: CONTINUOUS 1s ====================
def _sa10_11_cont(fpath, interval):
    try:
        with open(fpath, 'rb') as f: raw = f.read()
        try:
            file_bytes = bytes.fromhex(''.join(c for c in raw.decode('ascii') if c in '0123456789abcdefABCDEF'))
        except:
            file_bytes = raw

        if len(file_bytes) < 128:
            safe_status("❌ SA10_11(ISR): File must contain at least 128 bytes of data.")
            return

        header = [0xAC, 0xCA, 0x1F, 0x06]
        num_blocks = len(file_bytes) // 128
        idx = 0

        while sa_active.get("SA10_11(ISR)") and ser and ser.is_open:
            start = idx * 128
            end = start + 128
            if end > len(file_bytes):
                if sa_active.get("SA10_11(ISR)"): safe_status("⏹️ ISR(SA10_11) sending finished.")
                break

            chunk = file_bytes[start:end]
            packet = bytes(header) + chunk
            hex_pkt = format_hex_bytes(packet)

            safe_serial_write(packet)
            safe_status(f"✅ ISR(SA10_11) packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")
            log_cmd(f"ISR(SA10_11) | ISR(SA10_11) packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")

            idx += 1
            cmdtime.sleep(interval) # 1.0s

        if sa_active.get("SA10_11(ISR)"): safe_status("⏹️ ISR(SA10_11) finished")
    except Exception as e:
        safe_status(f"❌ Error in ISL send: {e}")
        sa_active["SA10_11(ISR)"] = False
        
def _sa12_cont(fpath, interval):
    try:
        with open(fpath, 'rb') as f: raw = f.read()
        try:
            file_bytes = bytes.fromhex(''.join(c for c in raw.decode('ascii') if c in '0123456789abcdefABCDEF'))
        except:
            file_bytes = raw

        if len(file_bytes) < 64:
            safe_status("❌ SA12: File must contain at least 64 bytes of data.")
            return

        header = [0xAC, 0xCA, 0x1F, 0x07]
        num_blocks = len(file_bytes) // 64
        idx = 0

        while sa_active.get("SA12") and ser and ser.is_open:
            start = idx * 64
            end = start + 64
            if end > len(file_bytes):
                if sa_active.get("SA12"): safe_status("⏹️ SA4 sending finished.")
                break

            chunk = file_bytes[start:end]
            packet = bytes(header) + chunk
            hex_pkt = format_hex_bytes(packet)

            safe_serial_write(packet)
            safe_status(f"✅ SA12 packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")
            log_cmd(f"SA12 | SA12 packet sent (block {idx+1}/{num_blocks}): {hex_pkt}")

            idx += 1
            cmdtime.sleep(interval) # 1.0s

        if sa_active.get("SA12"): safe_status("⏹️ SA12 finished")
    except Exception as e:
        safe_status(f"❌ Error in SA12 send: {e}")
        sa_active["SA12"] = False
# ==================== STOP & BROWSE HELPERS ====================

def stop_sa(sa):
    if sa_active.get(sa):
        sa_active[sa] = False
        safe_status(f"⏹️ Stopping {sa} sending...")
    # ✅ FIX: Access global sa_stop_btns directly
    btn = sa_stop_btns.get(sa)
    if btn:
        try: btn.config(state="disabled")
        except: pass

def _browse_file(ent, sa_name, btn_send_ref):
    filepath = filedialog.askopenfilename(title=f"Select {sa_name} File", filetypes=[("All Files","*.*")])
    if filepath:
        ent.delete(0, tk.END)
        ent.insert(0, filepath)

        # ✅ Explicitly enable Send button (fixes disabled bug)
        btn_send_ref.config(state="normal")

        '''try:
            with open(filepath, 'r', errors='ignore') as f:
                file_data = f.read()
                print("======================")
                print(file_data)
        except Exception as e:
            print(f"❌ Could not read file: {e}")'''


def parse_plot_value(val):
    """Safely converts GUI text to a float for plotting. Returns None if unparseable."""
    if val is None:
        return None
    val = str(val).strip().lower()
    if val in ("disabled", "off", "locked", "2d","no fix", "unknown ekf level","fail", "n", "r","b","no sol, 0","UN","NA"):
        return 0.0
    if val in ("enabled","gps + navic + sbas", "on", "unlocked", "3d fix", "3d", "pass", "y", "p","t","g","a","estimated, 1"):
        return 1.0
    if val in ("instantaneous, 2","gps + navic"):
        return 2.0
    if val in ("propagated, 3","2d fix","navic only"):
        return 3.0
    if val in ("gps + sbas"):
        return 4.0
    if val in ("gps only"):
        return 5.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_gui_update(widget, value):
    def _apply():
        try:
            if not widget.winfo_exists():
                return
            widget.config(state="normal")
            widget.delete(0, tk.END)
            widget.insert(0, str(value))
            widget.config(state="readonly")

            val_str = str(value).upper().strip()
            if val_str in ['Y', 'A', 'T', 'ENABLED', 'P', 'G', 'LOCKED', '3D FIX', '3D', 'PASS', 'OFF']:
                widget.config(fg='green')
            elif val_str in ['N', 'I', 'NA', 'R', 'B', 'DISABLED', 'UNLOCKED', '2D FIX', '2D', 'FAIL', 'ON']:
                widget.config(fg='red')
            elif val_str in ['UN', 'UNAVAIL']:
                widget.config(fg='orange')
            else:
                try:
                    num = float(value)
                    if num < 0: widget.config(fg='red')
                    elif num == 0: widget.config(fg='orange')
                    elif num <= 50: widget.config(fg='blue')
                    elif num <= 70: widget.config(fg='green')
                    else: widget.config(fg='black')
                except ValueError:
                    widget.config(fg='black')
        except Exception:
            pass

    try:
        root.after(0, _apply)
    except Exception:
        pass

def connect_check(args):
    global clicked_bd, clicked_com
    if "-" in clicked_com.get() or "-" in clicked_bd.get():
        connect_btn["state"] = "disabled"
    else:
        connect_btn["state"] = "active"

def baud_select():
    global clicked_bd, drop_bd, frame1
    clicked_bd = StringVar()
    bds = ["---", "300", "600", "1200", "2400", "4800", "9600", "14400", "19200", "28800", "38400", "56000", "57600", "115200", "128000", "256000"]
    clicked_bd.set("115200")
    drop_bd = OptionMenu(frame1, clicked_bd, *bds, command=connect_check)
    drop_bd.config(height=1, width=10, font=("Calibri", 11, "bold"), bg="lavender", fg="purple")
    drop_bd.grid(column=4, row=1, padx=2, pady=2)

    
def update_coms():
    global clicked_com, drop_COM, frame1
    ports = serial.tools.list_ports.comports()
    coms = [com[0] for com in ports]
    coms.insert(0, "---")
    try:
        drop_COM.destroy()
    except Exception:
        pass
    clicked_com = StringVar()
    clicked_com.set(coms[0])
    drop_COM = OptionMenu(frame1, clicked_com, *coms, command=connect_check)
    drop_COM.config(height=1, width=10, font=("Calibri", 11, "bold"), bg="lavender", fg="purple")
    drop_COM.grid(column=1, row=1, padx=2, pady=2)
    connect_check(0)

def on_precise_file():
    global precise_data, precise_times, precise_loaded
    filepath = filedialog.askopenfilename(
        title="Select Precise CSV File",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not filepath:
        return
    try:
        precise_data = []
        precise_times = []
        precise_loaded = False
        with open(filepath, 'r', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                status_var1.set("❌ Precise file header not found")
                return

            required_columns = [
                "decimal tow(s)", "v1_veh_x_pos(m)", "v1_veh_y_pos(m)", "v1_veh_z_pos(m)",
                "v1_veh_x_vel(m/s)", "v1_veh_y_vel(m/s)", "v1_veh_z_vel(m/s)",
                "v1_veh_x_acc(m/s²)", "v1_veh_y_acc(m/s²)", "v1_veh_z_acc(m/s²)"
            ]
            missing_columns = [col for col in required_columns if col not in reader.fieldnames]
            if missing_columns:
                status_var1.set("❌ Missing columns: " + ", ".join(missing_columns))
                return

            for row in reader:
                try:
                    tow = float(row["decimal tow(s)"])
                    precise_data.append({
                        "tow": tow,
                        "px": float(row["v1_veh_x_pos(m)"]),
                        "py": float(row["v1_veh_y_pos(m)"]),
                        "pz": float(row["v1_veh_z_pos(m)"]),
                        "vx": float(row["v1_veh_x_vel(m/s)"]),
                        "vy": float(row["v1_veh_y_vel(m/s)"]),
                        "vz": float(row["v1_veh_z_vel(m/s)"]),
                        "ax": float(row["v1_veh_x_acc(m/s²)"]),
                        "ay": float(row["v1_veh_y_acc(m/s²)"]),
                        "az": float(row["v1_veh_z_acc(m/s²)"])
                    })
                except Exception:
                    continue

        if not precise_data:
            status_var1.set("❌ No valid precise data found")
            return

        precise_data.sort(key=lambda x: x["tow"])
        precise_times = [row["tow"] for row in precise_data]
        precise_loaded = True
        status_var1.set(f"✅ Loaded {len(precise_data)} precise records")
    except Exception as e:
        precise_loaded = False
        status_var1.set(f"❌ Precise file error: {e}")

def reverse_and_concatenate(hex_list, scale=1, is_signed=False):
    if len(hex_list) in [1, 2, 3, 4, 8]:
        if len(hex_list) in [1, 2, 3]:
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

        if is_signed and decimal_value >= 0x80000000:
            decimal_value -= 0x100000000
        return decimal_value
    return None

def convert_to_decimal(hex_str):
    reversed_hex = ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])
    return int(reversed_hex, 16)


'''def reverse_and_concatenate(hex_list, scale=1 ,is_signed=False):
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

def check_and_store_TTF(EST_x, EST_y, EST_z, SYN_Second, SYN_NanoSecond, SYN_Weeknumber, UpdateCounter):
    global TTF
    if TTF is None:
        if all(val != 0 for val in [EST_x, EST_y, EST_z, SYN_Second, SYN_NanoSecond, SYN_Weeknumber]):
            TTF = UpdateCounter
            print(f"TTF stored: {TTF}")'''

def chechsum_calulation_covert_decimal(NanoSecond_hex, Second_hex, Weeknumber_hex, CHECKSUM):
    global checksum
    NanoSecond_part1 = convert_to_decimal(NanoSecond_hex[:4])
    NanoSecond_part2 = convert_to_decimal(NanoSecond_hex[4:])
    Second_part1 = convert_to_decimal(Second_hex[:4])
    Second_part2 = convert_to_decimal(Second_hex[4:])
    Week = convert_to_decimal(Weeknumber_hex)
    total = NanoSecond_part1 + NanoSecond_part2 + Second_part1 + Second_part2 + Week
    exepected_checksum = (0 - total) & 0xFFFF

    if exepected_checksum == CHECKSUM:
        checksum = "Pass"
        csm.config(fg="dark green")
    else:
        checksum = "Fail"
        csm.config(fg="dark red")
    return checksum

def SA4chechsum_calulation_covert_decimal(SYS_NanoSecond_hex, SYS_Second_hex, SYS_Weeknumber_hex, INST_x_hex, INST_y_hex, INST_z_hex, INST_vx_hex, INST_vy_hex, INST_vz_hex, UpdateCounter_hex, Est_x_hex, Est_y_hex, Est_z_hex, Est_vx_hex, Est_vy_hex, Est_vz_hex, validation_flag_hex, CHECKSUM1):
    global checksum1
    SYS_NanoSecond_part1 = convert_to_decimal(SYS_NanoSecond_hex[:4])
    SYS_NanoSecond_part2 = convert_to_decimal(SYS_NanoSecond_hex[4:])
    SYS_Second_part1 = convert_to_decimal(SYS_Second_hex[:4])
    SYS_Second_part2 = convert_to_decimal(SYS_Second_hex[4:])
    SYS_Weeknumber = convert_to_decimal(SYS_Weeknumber_hex)
    SPS_x_part1 = convert_to_decimal(INST_x_hex[:4])
    SPS_x_part2 = convert_to_decimal(INST_x_hex[4:])
    SPS_y_part1 = convert_to_decimal(INST_y_hex[:4])
    SPS_y_part2 = convert_to_decimal(INST_y_hex[4:])
    SPS_z_part1 = convert_to_decimal(INST_z_hex[:4])
    SPS_z_part2 = convert_to_decimal(INST_z_hex[4:])
    SPS_vx_part1 = convert_to_decimal(INST_vx_hex[:4])
    SPS_vx_part2 = convert_to_decimal(INST_vx_hex[4:])
    SPS_vy_part1 = convert_to_decimal(INST_vy_hex[:4])
    SPS_vy_part2 = convert_to_decimal(INST_vy_hex[4:])
    SPS_vz_part1 = convert_to_decimal(INST_vz_hex[:4])
    SPS_vz_part2 = convert_to_decimal(INST_vz_hex[4:])
    UpdateCounter_part = convert_to_decimal(UpdateCounter_hex)
    INT_x_part1 = convert_to_decimal(Est_x_hex[:4])
    INT_x_part2 = convert_to_decimal(Est_x_hex[4:])
    INT_y_part1 = convert_to_decimal(Est_y_hex[:4])
    INT_y_part2 = convert_to_decimal(Est_y_hex[4:])
    INT_z_part1 = convert_to_decimal(Est_z_hex[:4])
    INT_z_part2 = convert_to_decimal(Est_z_hex[4:])
    INT_vx_part1 = convert_to_decimal(Est_vx_hex[:4])
    INT_vx_part2 = convert_to_decimal(Est_vx_hex[4:])
    INT_vy_part1 = convert_to_decimal(Est_vy_hex[:4])
    INT_vy_part2 = convert_to_decimal(Est_vy_hex[4:])
    INT_vz_part1 = convert_to_decimal(Est_vz_hex[:4])
    INT_vz_part2 = convert_to_decimal(Est_vz_hex[4:])
    Validation_part = convert_to_decimal(validation_flag_hex)

    total = (SYS_NanoSecond_part1 + SYS_NanoSecond_part2 + SYS_Second_part1 + SYS_Second_part2 + SYS_Weeknumber +
             SPS_x_part1 + SPS_x_part2 + SPS_y_part1 + SPS_y_part2 + SPS_z_part1 + SPS_z_part2 +
             SPS_vx_part1 + SPS_vx_part2 + SPS_vy_part1 + SPS_vy_part2 + SPS_vz_part1 + SPS_vz_part2 +
             UpdateCounter_part + INT_x_part1 + INT_x_part2 + INT_y_part1 + INT_y_part2 + INT_z_part1 +
             INT_z_part2 + INT_vx_part1 + INT_vx_part2 + INT_vy_part1 + INT_vy_part2 + INT_vz_part1 +
             INT_vz_part2 + Validation_part)

    exepected_checksum = (0 - total) & 0xFFFF
    if exepected_checksum == CHECKSUM1:
        checksum1 = "Pass"
        csm1.config(fg="dark green")
    else:
        checksum1 = "Fail"
        csm1.config(fg="dark red")
    return checksum1



def open_Remote_r_w_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA8 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # Remote R/W frame
    # ---------------------------------------------------------
    remote_frame = LabelFrame(
        popup,
        text="RM R/W",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    remote_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    remote_frame.grid_columnconfigure(1, weight=1)
    remote_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    # Remote R/W variables
    # ---------------------------------------------------------
    remote_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(6):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            remote_frame,
            text=f"Remote R/W {i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            remote_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        remote_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_remote_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                remote1_entry.get(),
                remote2_entry.get(),
                remote3_entry.get(),
                remote4_entry.get(),
                remote5_entry.get(),
                remote6_entry.get()
            ]

            # Update popup
            for entry, value in zip(remote_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_remote_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("Remote R/W popup update error:", e)

            try:
                popup.after(1000, update_remote_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_remote_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    

def open_SA8_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA8 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA8 frame
    # ---------------------------------------------------------
    SA8_frame = LabelFrame(
        popup,
        text="SA8",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA8_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA8_frame.grid_columnconfigure(1, weight=1)
    SA8_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA8 variables
    # ---------------------------------------------------------
    SA8_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(18):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA8_frame,
            text=f"SA8_W{(i+2) + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA8_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA8_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_remote_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                sa8_w3_entry.get(),
                sa8_w4_entry.get(),
                sa8_w5_entry.get(),
                sa8_w6_entry.get(),
                sa8_w7_entry.get(),
                sa8_w8_entry.get(),
                sa8_w9_w10_entry.get(),
                sa8_w11_w12_entry.get(),
                sa8_w13_w14_entry.get(),
                sa8_w15_w16_entry.get(),
                sa8_w17_w18_entry.get(),
                sa8_w19_w20_entry.get(),
                sa8_w21_w22_entry.get(),
                sa8_w23_w24_entry.get(),
                sa8_w25_w26_entry.get(),
                sa8_w27_w28_entry.get(),
                sa8_w29_w30_entry.get(),
                sa8_w31_w32_entry.get(),
                
                
            ]

            # Update popup
            for entry, value in zip(SA8_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_remote_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA8 popup update error:", e)

            try:
                popup.after(1000, update_remote_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_remote_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()

def open_SA9_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA9 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA9_frame = LabelFrame(
        popup,
        text="SA9",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA9_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA9_frame.grid_columnconfigure(1, weight=1)
    SA9_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA8 variables
    # ---------------------------------------------------------
    SA9_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(25):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA9_frame,
            text=f"SA9_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA9_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA9_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_remote_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                sa9_w1_entry.get(),
                sa9_w2_entry.get(),
                sa9_w3_entry.get(),
                sa9_w4_entry.get(),
                sa9_w5_entry.get(),
                sa9_w6_entry.get(),
                sa9_w7_entry.get(),
                sa9_w8_entry.get(),
                sa9_w9_entry.get(),
                sa9_w10_entry.get(),
                sa9_w11_entry.get(),
                sa9_w12_entry.get(),
                sa9_w13_entry.get(),
                sa9_w14_w15_entry.get(),
                sa9_w16_w17_entry.get(),
                sa9_w18_w19_entry.get(),
                sa9_w20_w21_entry.get(),
                sa9_w22_w23_entry.get(),
                sa9_w24_w25_entry.get(),
                sa9_w26_entry.get(),
                sa9_w27_entry.get(),
                sa9_w28_entry.get(),
                sa9_w29_entry.get(),
                sa9_w30_w31_entry.get(),
                sa9_w32_entry.get(),
                
                
            ]

            # Update popup
            for entry, value in zip(SA9_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_remote_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA9 popup update error:", e)

            try:
                popup.after(1000, update_remote_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_remote_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    
def open_SA10_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA10 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA10_frame = LabelFrame(
        popup,
        text="SA10",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA10_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA10_frame.grid_columnconfigure(1, weight=1)
    SA10_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA8 variables
    # ---------------------------------------------------------
    SA10_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(23):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA10_frame,
            text=f"SA10_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA10_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA10_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa10_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                sa10_w1_entry.get(),
                sa10_w2_entry.get(),
                sa10_w3_entry.get(),
                sa10_w4_entry.get(),
                sa10_w5_entry.get(),
                sa10_w6_entry.get(),
                sa10_w7_entry.get(),
                sa10_w8_entry.get(),
                sa10_w9_w10_entry.get(),
                sa10_w11_w12_entry.get(),
                sa10_w13_w14_entry.get(),
                sa10_w15_entry.get(),
                sa10_w16_entry.get(),
                sa10_w17_entry.get(),
                sa10_w18_entry.get(),
                sa10_w19_entry.get(),
                sa10_w20_entry.get(),
                sa10_w21_entry.get(),
                sa10_w22_entry.get(),
                sa10_w23_w24_entry.get(),
                sa10_w25_w26_entry.get(),
                sa10_w27_w28_entry.get(),
                sa10_w29_w30_entry.get(),
                sa10_w31_w32_entry.get()
                
                
            ]

            # Update popup
            for entry, value in zip(SA10_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa10_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA10 popup update error:", e)

            try:
                popup.after(1000, update_sa10_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa10_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()

def open_SA11_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA11 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA11_frame = LabelFrame(
        popup,
        text="SA11",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA11_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA11_frame.grid_columnconfigure(1, weight=1)
    SA11_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA11 variables
    # ---------------------------------------------------------
    SA11_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(21):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA11_frame,
            text=f"SA11_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA11_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA11_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa11_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                sa11_w1_w2_entry.get(),
                sa11_w3_w4_entry.get(),
                sa11_w5_w6_entry.get(),
                sa11_w7_w8_entry.get(),
                sa11_w9_w10_entry.get(),
                sa11_w11_w12_entry.get(),
                sa11_w13_w14_entry.get(),
                sa11_w15_entry.get(),
                sa11_w16_entry.get(),
                sa11_w17_w18_entry.get(),
                sa11_w19_entry.get(),
                sa11_w20_entry.get(),
                sa11_w21_entry.get(),
                sa11_w22_entry.get(),
                sa11_w23_entry.get(),
                sa11_w24_entry.get(),
                sa11_w25_w26_entry.get(),
                sa11_w27_w28_entry.get(),
                sa11_w29_entry.get(),
                sa11_w30_w31_entry.get(),
                sa11_w32_entry.get()

                
                
            ]

            # Update popup
            for entry, value in zip(SA11_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa11_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA11 popup update error:", e)

            try:
                popup.after(1000, update_sa11_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa11_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    
def open_SA12_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA12 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA12_frame = LabelFrame(
        popup,
        text="SA12",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA12_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA12_frame.grid_columnconfigure(1, weight=1)
    SA12_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA11 variables
    # ---------------------------------------------------------
    SA12_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(26):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA12_frame,
            text=f"SA12_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA12_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA12_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa12_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                sa12_w1_entry.get(),
                sa12_w2_entry.get(),
                sa12_w3_entry.get(),
                sa12_w4_entry.get(),
                sa12_w5_entry.get(),
                sa12_w6_entry.get(),
                sa12_w7_entry.get(),
                sa12_w8_entry.get(),
                sa12_w9_entry.get(),
                sa12_w10_entry.get(),
                sa12_w11_entry.get(),
                sa12_w12_entry.get(),
                sa12_w13_entry.get(),
                sa12_w14_entry.get(),
                sa12_w15_entry.get(),
                sa12_w16_entry.get(),
                sa12_w17_entry.get(),
                sa12_w18_entry.get(),
                sa12_w19_w20_entry.get(),
                sa12_w21_w22_entry.get(),
                sa12_w23_w24_entry.get(),
                sa12_w25_w26_entry.get(),
                sa12_w27_w28_entry.get(),
                sa12_w29_w30_entry.get(),
                sa12_w31_entry.get(),
                sa12_w32_entry.get()


                
                
            ]

            # Update popup
            for entry, value in zip(SA12_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa12_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA12 popup update error:", e)

            try:
                popup.after(1000, update_sa12_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa12_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    
def open_SA13_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA13 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA13_frame = LabelFrame(
        popup,
        text="SA13",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA13_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA13_frame.grid_columnconfigure(1, weight=1)
    SA13_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA13 variables
    # ---------------------------------------------------------
    SA13_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA13_frame,
            text=f"SA13_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA13_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA13_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa13_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa13_w1_entry.get(),
                    sa13_w2_entry.get(),
                    sa13_w3_entry.get(),
                    sa13_w4_entry.get(),
                    sa13_w5_entry.get(),
                    sa13_w6_entry.get(),
                    sa13_w7_entry.get(),
                    sa13_w8_entry.get(),
                    sa13_w9_entry.get(),
                    sa13_w10_entry.get(),
                    sa13_w11_entry.get(),
                    sa13_w12_entry.get(),
                    sa13_w13_entry.get(),
                    sa13_w14_entry.get(),
                    sa13_w15_entry.get(),
                    sa13_w16_entry.get(),
                    sa13_w17_entry.get(),
                    sa13_w18_entry.get(),
                    sa13_w19_entry.get(),
                    sa13_w20_entry.get(),
                    sa13_w21_entry.get(),
                    sa13_w22_entry.get(),
                    sa13_w23_entry.get(),
                    sa13_w24_entry.get(),
                    sa13_w25_entry.get(),
                    sa13_w26_entry.get(),
                    sa13_w27_entry.get(),
                    sa13_w28_entry.get(),
                    sa13_w29_entry.get(),
                    sa13_w30_entry.get(),
                    sa13_w31_entry.get(),
                    sa13_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(SA13_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa13_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA12 popup update error:", e)

            try:
                popup.after(1000, update_sa13_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa13_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    
def open_SA14_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA14 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA14_frame = LabelFrame(
        popup,
        text="SA14",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA14_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA14_frame.grid_columnconfigure(1, weight=1)
    SA14_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA14 variables
    # ---------------------------------------------------------
    SA14_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA14_frame,
            text=f"SA14_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA14_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA14_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa14_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa14_w1_entry.get(),
                    sa14_w2_entry.get(),
                    sa14_w3_entry.get(),
                    sa14_w4_entry.get(),
                    sa14_w5_entry.get(),
                    sa14_w6_entry.get(),
                    sa14_w7_entry.get(),
                    sa14_w8_entry.get(),
                    sa14_w9_entry.get(),
                    sa14_w10_entry.get(),
                    sa14_w11_entry.get(),
                    sa14_w12_entry.get(),
                    sa14_w13_entry.get(),
                    sa14_w14_entry.get(),
                    sa14_w15_entry.get(),
                    sa14_w16_entry.get(),
                    sa14_w17_entry.get(),
                    sa14_w18_entry.get(),
                    sa14_w19_entry.get(),
                    sa14_w20_entry.get(),
                    sa14_w21_entry.get(),
                    sa14_w22_entry.get(),
                    sa14_w23_entry.get(),
                    sa14_w24_entry.get(),
                    sa14_w25_entry.get(),
                    sa14_w26_entry.get(),
                    sa14_w27_entry.get(),
                    sa14_w28_entry.get(),
                    sa14_w29_entry.get(),
                    sa14_w30_entry.get(),
                    sa14_w31_entry.get(),
                    sa14_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(SA14_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa14_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA14 popup update error:", e)

            try:
                popup.after(1000, update_sa14_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa14_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    
def open_SA15_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA15 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA15_frame = LabelFrame(
        popup,
        text="SA15",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA15_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA15_frame.grid_columnconfigure(1, weight=1)
    SA15_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA14 variables
    # ---------------------------------------------------------
    SA15_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(18):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA15_frame,
            text=f"SA15_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA15_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA15_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa15_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa15_w1_entry.get(),
                    sa15_w2_entry.get(),
                    sa15_w3_w4_entry.get(),
                    sa15_w5_w6_entry.get(),
                    sa15_w7_w8_entry.get(),
                    sa15_w9_w10_entry.get(),
                    sa15_w11_w12_entry.get(),
                    sa15_w13_w14_entry.get(),
                    sa15_w15_w16_entry.get(),
                    sa15_w17_w18_entry.get(),
                    sa15_w19_w20_entry.get(),
                    sa15_w21_w22_entry.get(),
                    sa15_w23_w24_entry.get(),
                    sa15_w25_w26_entry.get(),
                    sa15_w27_w28_entry.get(),
                    sa15_w29_w30_entry.get(),
                    sa15_w31_entry.get(),
                    sa15_w32_entry.get(),

                
                
            ]

            # Update popup
            for entry, value in zip(SA15_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa15_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA15 popup update error:", e)

            try:
                popup.after(1000, update_sa15_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa15_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    
def open_SA16_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA16 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA16_frame = LabelFrame(
        popup,
        text="SA16",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA16_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA16_frame.grid_columnconfigure(1, weight=1)
    SA16_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA16 variables
    # ---------------------------------------------------------
    SA16_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(17):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA16_frame,
            text=f"SA16_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA16_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA16_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa16_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    
                    sa16_w1_entry.get(),
                    sa16_w2_entry.get(),
                    sa16_w3_w4_entry.get(),
                    sa16_w5_entry.get(),
                    sa16_w6_entry.get(),
                    sa16_w7_entry.get(),
                    sa16_w8_w9_entry.get(),
                    sa16_w10_w11_entry.get(),
                    sa16_w12_w13_entry.get(),
                    sa16_w14_w15_entry.get(),
                    sa16_w16_w17_entry.get(),
                    sa16_w18_w19_entry.get(),
                    sa16_w20_w21_entry.get(),
                    sa16_w22_w23_entry.get(),
                    sa16_w24_w29_entry.get(),
                    sa16_w30_w31_entry.get(),
                    sa16_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(SA16_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa16_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA16 popup update error:", e)

            try:
                popup.after(1000, update_sa16_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa16_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
def open_SA17_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("SA17 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    SA17_frame = LabelFrame(
        popup,
        text="SA17",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    SA17_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    SA17_frame.grid_columnconfigure(1, weight=1)
    SA17_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #SA17 variables
    # ---------------------------------------------------------
    SA17_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(28):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            SA17_frame,
            text=f"SA17_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            SA17_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        SA17_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_SA17_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                     sa17_w1_entry.get(),
                   sa17_w2_entry.get(),
                   sa17_w3_entry.get(),
                   sa17_w4_entry.get(),
                   sa17_w5_entry.get(),
                   sa17_w6_entry.get(),
                   sa17_w7_entry.get(),
                   sa17_w8_entry.get(),
                   sa17_w9_entry.get(),
                   sa17_w10_entry.get(),
                   sa17_w11_entry.get(),
                   sa17_w12_entry.get(),
                   sa17_w13_entry.get(),
                   sa17_w14_entry.get(),
                   sa17_w15_entry.get(),
                   sa17_w16_entry.get(),
                   sa17_w17_entry.get(),
                   sa17_w18_entry.get(),
                   sa17_w19_entry.get(),
                   sa17_w20_entry.get(),
                   sa17_w21_entry.get(),
                   sa17_w22_entry.get(),
                   sa17_w23_entry.get(),
                   sa17_w24_entry.get(),
                   sa17_w25_entry.get(),
                   sa17_w26_w30_entry.get(),
                   sa17_w31_entry.get(),
                   sa17_w32_entry.get()
                    

                
                
            ]

            # Update popup
            for entry, value in zip(SA17_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_SA17_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA17 popup update error:", e)

            try:
                popup.after(1000, update_SA17_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_SA17_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    
def open_sa18_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa18 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa18_frame = LabelFrame(
        popup,
        text="sa18",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa18_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa18_frame.grid_columnconfigure(1, weight=1)
    sa18_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa18 variables
    # ---------------------------------------------------------
    sa18_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(28):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa18_frame,
            text=f"sa18_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa18_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa18_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa18_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa18_w1_entry.get(),
                   sa18_w2_entry.get(),
                   sa18_w3_entry.get(),
                   sa18_w4_entry.get(),
                   sa18_w5_entry.get(),
                   sa18_w6_entry.get(),
                   sa18_w7_entry.get(),
                   sa18_w8_entry.get(),
                   sa18_w9_entry.get(),
                   sa18_w10_entry.get(),
                   sa18_w11_entry.get(),
                   sa18_w12_entry.get(),
                   sa18_w13_entry.get(),
                   sa18_w14_entry.get(),
                   sa18_w15_entry.get(),
                   sa18_w16_entry.get(),
                   sa18_w17_entry.get(),
                   sa18_w18_entry.get(),
                   sa18_w19_entry.get(),
                   sa18_w20_entry.get(),
                   sa18_w21_entry.get(),
                   sa18_w22_entry.get(),
                   sa18_w23_entry.get(),
                   sa18_w24_entry.get(),
                   sa18_w25_entry.get(),
                   sa18_w26_w30_entry.get(),
                   sa18_w31_entry.get(),
                   sa18_w32_entry.get()
                    

                
                
            ]

            # Update popup
            for entry, value in zip(sa18_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa18_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("sa18 popup update error:", e)

            try:
                popup.after(1000, update_sa18_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa18_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()

def open_sa19_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa19 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa19_frame = LabelFrame(
        popup,
        text="sa19",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa19_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa19_frame.grid_columnconfigure(1, weight=1)
    sa19_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa19 variables
    # ---------------------------------------------------------
    sa19_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa19_frame,
            text=f"sa19_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa19_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa19_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa19_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa19_w1_entry.get(),
                    sa19_w2_entry.get(),
                    sa19_w3_entry.get(),
                    sa19_w4_entry.get(),
                    sa19_w5_entry.get(),
                    sa19_w6_entry.get(),
                    sa19_w7_entry.get(),
                    sa19_w8_entry.get(),
                    sa19_w9_entry.get(),
                    sa19_w10_entry.get(),
                    sa19_w11_entry.get(),
                    sa19_w12_entry.get(),
                    sa19_w13_entry.get(),
                    sa19_w14_entry.get(),
                    sa19_w15_entry.get(),
                    sa19_w16_entry.get(),
                    sa19_w17_entry.get(),
                    sa19_w18_entry.get(),
                    sa19_w19_entry.get(),
                    sa19_w20_entry.get(),
                    sa19_w21_entry.get(),
                    sa19_w22_entry.get(),
                    sa19_w23_entry.get(),
                    sa19_w24_entry.get(),
                    sa19_w25_entry.get(),
                    sa19_w26_entry.get(),
                    sa19_w27_entry.get(),
                    sa19_w28_entry.get(),
                    sa19_w29_entry.get(),
                    sa19_w30_entry.get(),
                    sa19_w31_entry.get(),
                    sa19_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa19_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa19_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA19 popup update error:", e)

            try:
                popup.after(1000, update_sa19_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa19_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
    
def open_sa20_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa20 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa20_frame = LabelFrame(
        popup,
        text="sa20",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa20_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa20_frame.grid_columnconfigure(1, weight=1)
    sa20_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa20 variables
    # ---------------------------------------------------------
    sa20_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa20_frame,
            text=f"sa20_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa20_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa20_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa20_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa20_w1_entry.get(),
                    sa20_w2_entry.get(),
                    sa20_w3_entry.get(),
                    sa20_w4_entry.get(),
                    sa20_w5_entry.get(),
                    sa20_w6_entry.get(),
                    sa20_w7_entry.get(),
                    sa20_w8_entry.get(),
                    sa20_w9_entry.get(),
                    sa20_w10_entry.get(),
                    sa20_w11_entry.get(),
                    sa20_w12_entry.get(),
                    sa20_w13_entry.get(),
                    sa20_w14_entry.get(),
                    sa20_w15_entry.get(),
                    sa20_w16_entry.get(),
                    sa20_w17_entry.get(),
                    sa20_w18_entry.get(),
                    sa20_w19_entry.get(),
                    sa20_w20_entry.get(),
                    sa20_w21_entry.get(),
                    sa20_w22_entry.get(),
                    sa20_w23_entry.get(),
                    sa20_w24_entry.get(),
                    sa20_w25_entry.get(),
                    sa20_w26_entry.get(),
                    sa20_w27_entry.get(),
                    sa20_w28_entry.get(),
                    sa20_w29_entry.get(),
                    sa20_w30_entry.get(),
                    sa20_w31_entry.get(),
                    sa20_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa20_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa20_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA20 popup update error:", e)

            try:
                popup.after(1000, update_sa20_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa20_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
def open_sa21_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa21 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa21_frame = LabelFrame(
        popup,
        text="sa21",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa21_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa21_frame.grid_columnconfigure(1, weight=1)
    sa21_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa21 variables
    # ---------------------------------------------------------
    sa21_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa21_frame,
            text=f"sa21_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa21_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa21_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa21_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa21_w1_entry.get(),
                    sa21_w2_entry.get(),
                    sa21_w3_entry.get(),
                    sa21_w4_entry.get(),
                    sa21_w5_entry.get(),
                    sa21_w6_entry.get(),
                    sa21_w7_entry.get(),
                    sa21_w8_entry.get(),
                    sa21_w9_entry.get(),
                    sa21_w10_entry.get(),
                    sa21_w11_entry.get(),
                    sa21_w12_entry.get(),
                    sa21_w13_entry.get(),
                    sa21_w14_entry.get(),
                    sa21_w15_entry.get(),
                    sa21_w16_entry.get(),
                    sa21_w17_entry.get(),
                    sa21_w18_entry.get(),
                    sa21_w19_entry.get(),
                    sa21_w20_entry.get(),
                    sa21_w21_entry.get(),
                    sa21_w22_entry.get(),
                    sa21_w23_entry.get(),
                    sa21_w24_entry.get(),
                    sa21_w25_entry.get(),
                    sa21_w26_entry.get(),
                    sa21_w27_entry.get(),
                    sa21_w28_entry.get(),
                    sa21_w29_entry.get(),
                    sa21_w30_entry.get(),
                    sa21_w31_entry.get(),
                    sa21_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa21_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa21_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA21 popup update error:", e)

            try:
                popup.after(1000, update_sa21_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa21_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
        
def open_sa22_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa22 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa22_frame = LabelFrame(
        popup,
        text="sa22",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa22_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa22_frame.grid_columnconfigure(1, weight=1)
    sa22_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa22 variables
    # ---------------------------------------------------------
    sa22_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa22_frame,
            text=f"sa22_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa22_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa22_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa22_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa22_w1_entry.get(),
                    sa22_w2_entry.get(),
                    sa22_w3_entry.get(),
                    sa22_w4_entry.get(),
                    sa22_w5_entry.get(),
                    sa22_w6_entry.get(),
                    sa22_w7_entry.get(),
                    sa22_w8_entry.get(),
                    sa22_w9_entry.get(),
                    sa22_w10_entry.get(),
                    sa22_w11_entry.get(),
                    sa22_w12_entry.get(),
                    sa22_w13_entry.get(),
                    sa22_w14_entry.get(),
                    sa22_w15_entry.get(),
                    sa22_w16_entry.get(),
                    sa22_w17_entry.get(),
                    sa22_w18_entry.get(),
                    sa22_w19_entry.get(),
                    sa22_w20_entry.get(),
                    sa22_w21_entry.get(),
                    sa22_w22_entry.get(),
                    sa22_w23_entry.get(),
                    sa22_w24_entry.get(),
                    sa22_w25_entry.get(),
                    sa22_w26_entry.get(),
                    sa22_w27_entry.get(),
                    sa22_w28_entry.get(),
                    sa22_w29_entry.get(),
                    sa22_w30_entry.get(),
                    sa22_w31_entry.get(),
                    sa22_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa22_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa22_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA22 popup update error:", e)

            try:
                popup.after(1000, update_sa22_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa22_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
        
def open_sa23_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa23 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa23_frame = LabelFrame(
        popup,
        text="sa23",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa23_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa23_frame.grid_columnconfigure(1, weight=1)
    sa23_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa23 variables
    # ---------------------------------------------------------
    sa23_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa23_frame,
            text=f"sa23_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa23_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa23_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa23_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa23_w1_entry.get(),
                    sa23_w2_entry.get(),
                    sa23_w3_entry.get(),
                    sa23_w4_entry.get(),
                    sa23_w5_entry.get(),
                    sa23_w6_entry.get(),
                    sa23_w7_entry.get(),
                    sa23_w8_entry.get(),
                    sa23_w9_entry.get(),
                    sa23_w10_entry.get(),
                    sa23_w11_entry.get(),
                    sa23_w12_entry.get(),
                    sa23_w13_entry.get(),
                    sa23_w14_entry.get(),
                    sa23_w15_entry.get(),
                    sa23_w16_entry.get(),
                    sa23_w17_entry.get(),
                    sa23_w18_entry.get(),
                    sa23_w19_entry.get(),
                    sa23_w20_entry.get(),
                    sa23_w21_entry.get(),
                    sa23_w22_entry.get(),
                    sa23_w23_entry.get(),
                    sa23_w24_entry.get(),
                    sa23_w25_entry.get(),
                    sa23_w26_entry.get(),
                    sa23_w27_entry.get(),
                    sa23_w28_entry.get(),
                    sa23_w29_entry.get(),
                    sa23_w30_entry.get(),
                    sa23_w31_entry.get(),
                    sa23_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa23_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa23_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA23 popup update error:", e)

            try:
                popup.after(1000, update_sa23_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa23_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
        
def open_sa24_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa24 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa24_frame = LabelFrame(
        popup,
        text="sa24",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa24_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa24_frame.grid_columnconfigure(1, weight=1)
    sa24_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa24 variables
    # ---------------------------------------------------------
    sa24_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa24_frame,
            text=f"sa24_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa24_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa24_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa24_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa24_w1_entry.get(),
                    sa24_w2_entry.get(),
                    sa24_w3_entry.get(),
                    sa24_w4_entry.get(),
                    sa24_w5_entry.get(),
                    sa24_w6_entry.get(),
                    sa24_w7_entry.get(),
                    sa24_w8_entry.get(),
                    sa24_w9_entry.get(),
                    sa24_w10_entry.get(),
                    sa24_w11_entry.get(),
                    sa24_w12_entry.get(),
                    sa24_w13_entry.get(),
                    sa24_w14_entry.get(),
                    sa24_w15_entry.get(),
                    sa24_w16_entry.get(),
                    sa24_w17_entry.get(),
                    sa24_w18_entry.get(),
                    sa24_w19_entry.get(),
                    sa24_w20_entry.get(),
                    sa24_w21_entry.get(),
                    sa24_w22_entry.get(),
                    sa24_w23_entry.get(),
                    sa24_w24_entry.get(),
                    sa24_w25_entry.get(),
                    sa24_w26_entry.get(),
                    sa24_w27_entry.get(),
                    sa24_w28_entry.get(),
                    sa24_w29_entry.get(),
                    sa24_w30_entry.get(),
                    sa24_w31_entry.get(),
                    sa24_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa24_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa24_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA24 popup update error:", e)

            try:
                popup.after(1000, update_sa24_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa24_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
        
    
def open_sa25_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa25 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa25_frame = LabelFrame(
        popup,
        text="sa25",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa25_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa25_frame.grid_columnconfigure(1, weight=1)
    sa25_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa25 variables
    # ---------------------------------------------------------
    sa25_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa25_frame,
            text=f"sa25_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa25_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa25_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa25_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa25_w1_entry.get(),
                    sa25_w2_entry.get(),
                    sa25_w3_entry.get(),
                    sa25_w4_entry.get(),
                    sa25_w5_entry.get(),
                    sa25_w6_entry.get(),
                    sa25_w7_entry.get(),
                    sa25_w8_entry.get(),
                    sa25_w9_entry.get(),
                    sa25_w10_entry.get(),
                    sa25_w11_entry.get(),
                    sa25_w12_entry.get(),
                    sa25_w13_entry.get(),
                    sa25_w14_entry.get(),
                    sa25_w15_entry.get(),
                    sa25_w16_entry.get(),
                    sa25_w17_entry.get(),
                    sa25_w18_entry.get(),
                    sa25_w19_entry.get(),
                    sa25_w20_entry.get(),
                    sa25_w21_entry.get(),
                    sa25_w22_entry.get(),
                    sa25_w23_entry.get(),
                    sa25_w24_entry.get(),
                    sa25_w25_entry.get(),
                    sa25_w26_entry.get(),
                    sa25_w27_entry.get(),
                    sa25_w28_entry.get(),
                    sa25_w29_entry.get(),
                    sa25_w30_entry.get(),
                    sa25_w31_entry.get(),
                    sa25_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa25_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa25_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA25 popup update error:", e)

            try:
                popup.after(1000, update_sa25_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa25_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
        
    
def open_sa26_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa26 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa26_frame = LabelFrame(
        popup,
        text="sa26",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa26_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa26_frame.grid_columnconfigure(1, weight=1)
    sa26_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa26 variables
    # ---------------------------------------------------------
    sa26_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa26_frame,
            text=f"sa26_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa26_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa26_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa26_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa26_w1_entry.get(),
                    sa26_w2_entry.get(),
                    sa26_w3_entry.get(),
                    sa26_w4_entry.get(),
                    sa26_w5_entry.get(),
                    sa26_w6_entry.get(),
                    sa26_w7_entry.get(),
                    sa26_w8_entry.get(),
                    sa26_w9_entry.get(),
                    sa26_w10_entry.get(),
                    sa26_w11_entry.get(),
                    sa26_w12_entry.get(),
                    sa26_w13_entry.get(),
                    sa26_w14_entry.get(),
                    sa26_w15_entry.get(),
                    sa26_w16_entry.get(),
                    sa26_w17_entry.get(),
                    sa26_w18_entry.get(),
                    sa26_w19_entry.get(),
                    sa26_w20_entry.get(),
                    sa26_w21_entry.get(),
                    sa26_w22_entry.get(),
                    sa26_w23_entry.get(),
                    sa26_w24_entry.get(),
                    sa26_w25_entry.get(),
                    sa26_w26_entry.get(),
                    sa26_w27_entry.get(),
                    sa26_w28_entry.get(),
                    sa26_w29_entry.get(),
                    sa26_w30_entry.get(),
                    sa26_w31_entry.get(),
                    sa26_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa26_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa26_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA26 popup update error:", e)

            try:
                popup.after(1000, update_sa26_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa26_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
        
    
def open_sa27_popup():
    """Open SA8 popup showing Remote R/W values and update every 1 second."""

    popup = tk.Toplevel(root)
    popup.title("sa27 Parameters")
    popup.geometry("600x300")
    popup.configure(bg="lavender")

    # ---------------------------------------------------------
    # SA9 frame
    # ---------------------------------------------------------
    sa27_frame = LabelFrame(
        popup,
        text="sa27",
        bg="lavender",
        fg="purple",
        font=("Calibri", 13, "bold"),
        relief="solid",
        bd=2,
        padx=10,
        pady=10
    )
    sa27_frame.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="nsew"
    )

    # Allow popup/frame expansion
    popup.grid_columnconfigure(0, weight=1)
    popup.grid_rowconfigure(0, weight=1)

    sa27_frame.grid_columnconfigure(1, weight=1)
    sa27_frame.grid_columnconfigure(3, weight=1)

    # ---------------------------------------------------------
    #sa27 variables
    # ---------------------------------------------------------
    sa27_popup_entries = []

    # ---------------------------------------------------------
    # Create 6 Remote R/W entries ONLY ONCE
    # ---------------------------------------------------------
    for i in range(32):

        row = i // 2
        col = (i % 2) * 2

        label = Label(
            sa27_frame,
            text=f"sa27_W{i + 1}:",
            bg="lavender",
            fg="purple",
            font=("Calibri", 11, "bold")
        )

        label.grid(
            row=row,
            column=col,
            padx=8,
            pady=8,
            sticky="e"
        )

        entry = Entry(
            sa27_frame,
            width=15,
            font=("Calibri", 11, "bold"),
            justify="center",
            state="readonly"
        )

        entry.grid(
            row=row,
            column=col + 1,
            padx=8,
            pady=8,
            sticky="w"
        )

        sa27_popup_entries.append(entry)

    # ---------------------------------------------------------
    # Function to safely update readonly Entry
    # ---------------------------------------------------------
    def set_popup_entry(entry, value):

        try:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.insert(0, str(value))
            entry.config(state="readonly")
        except tk.TclError:
            pass

    # ---------------------------------------------------------
    # Update values every 1 second
    # ---------------------------------------------------------
    def update_sa27_values():

        try:

            # Check whether popup still exists
            if not popup.winfo_exists():
                return

            # Read CURRENT values from main GUI entries
            values = [
                    sa27_w1_entry.get(),
                    sa27_w2_entry.get(),
                    sa27_w3_entry.get(),
                    sa27_w4_entry.get(),
                    sa27_w5_entry.get(),
                    sa27_w6_entry.get(),
                    sa27_w7_entry.get(),
                    sa27_w8_entry.get(),
                    sa27_w9_entry.get(),
                    sa27_w10_entry.get(),
                    sa27_w11_entry.get(),
                    sa27_w12_entry.get(),
                    sa27_w13_entry.get(),
                    sa27_w14_entry.get(),
                    sa27_w15_entry.get(),
                    sa27_w16_entry.get(),
                    sa27_w17_entry.get(),
                    sa27_w18_entry.get(),
                    sa27_w19_entry.get(),
                    sa27_w20_entry.get(),
                    sa27_w21_entry.get(),
                    sa27_w22_entry.get(),
                    sa27_w23_entry.get(),
                    sa27_w24_entry.get(),
                    sa27_w25_entry.get(),
                    sa27_w26_entry.get(),
                    sa27_w27_entry.get(),
                    sa27_w28_entry.get(),
                    sa27_w29_entry.get(),
                    sa27_w30_entry.get(),
                    sa27_w31_entry.get(),
                    sa27_w32_entry.get(),


                
                
            ]

            # Update popup
            for entry, value in zip(sa27_popup_entries, values):
                set_popup_entry(entry, value)

            # Schedule next update
            popup.after(1000, update_sa27_values)

        except tk.TclError:
            # Popup/root was destroyed
            return

        except Exception as e:
            print("SA27 popup update error:", e)

            try:
                popup.after(1000, update_sa27_values)
            except tk.TclError:
                pass

    # ---------------------------------------------------------
    # Start first update immediately
    # ---------------------------------------------------------
    update_sa27_values()

    # Keep popup on top
    popup.lift()
    popup.focus_force()
        
def decode_validation_flag(validation_flag):

    # Convert to integer if needed
    if isinstance(validation_flag, str):
        validation_flag = int(validation_flag, 16)
    elif isinstance(validation_flag, tuple):
        validation_flag = (validation_flag[0] << 8) | validation_flag[1]
    elif not isinstance(validation_flag, int):
        raise ValueError("Input must be int, hex string, or (MSB, LSB) tuple")

    #raw_flag = validation_flag
    B1_B0 = validation_flag & 0x03
    B3_B2 = (validation_flag >> 2) & 0x03

    # Decode EKF level/orbit status
    if B1_B0 == 0b00:
        orbit_status = "NO SOL, 0"
    elif B1_B0 == 0b01:
        orbit_status = "ESTIMATED, 1"
    elif B1_B0 == 0b10:
        orbit_status = "INSTANTANEOUS, 2"
    elif B1_B0 == 0b11:
        orbit_status = "PROPAGATED, 3"
    else:
        orbit_status = "Unknown EKF level"

    # ODP run mode
    #odp_run_mode = B3_B2
     # Decode odp_run_mode status
    if B3_B2 == 0b00:
        odp_run_mode = "ODP Test Mode, 0"
    elif B3_B2 == 0b01:
        odp_run_mode = "ODP Disable Mode, 1"
    elif B3_B2 == 0b10:
        odp_run_mode = "ODP Enable Mode, 2"
    elif B3_B2 == 0b11:
        odp_run_mode = "NIL, 3"
    else:
        odp_run_mode = "Unknown ODP RUN MODE"

    # EKF level (same as B1_B0)
    #ekf_level = B1_B0

    # OD&P state vectors usability
    #odp_vectors_usable = B1_B0 in [0b01, 0b11]

    return orbit_status,odp_run_mode

    '''return {
        'odp': orbit_status,
        'val': format(B1_B0, '02b'),
        #'ODP_run_mode': odp_run_mode,
        #'EKF_level': ekf_level,
        #'ODP_vectors_usable': odp_vectors_usable,
        #'B3_B2_bin': format(B3_B2, '02b'),
        #'raw_flag': raw_flag
    }'''

def Multiplexing(word31):
    """
    Decodes the multiplexed Word #31 and returns a clean output string.
    Also stores decoded values in global 'decoded_data' dictionary.

    Args:
        word31 (int, hex str, or (MSB, LSB) tuple)

    Returns:
        str: A formatted output like:
             - "MUX: 0 : 1200"
             - "MUX: 11 : NavIC Cmd=45, GPS_alm_chk=12"
             - "MUX: 12 : P2E=2, ALM_usel=17, ALM_col=6"
    """
    global decoded_data

    # Convert input to 16-bit integer
    if isinstance(word31, str):
        word31 = int(word31, 16)
    elif isinstance(word31, tuple):
        word31 = (word31[0] << 8) | word31[1]
    elif not isinstance(word31, int):
        raise ValueError("Input must be int, hex string, or (MSB, LSB) tuple")

    mux_sel = (word31 >> 12) & 0xF  # Bits B15–B12
    data = word31 & 0xFFF           # Bits B11–B0

    decoded_data = {'Selector': mux_sel}

    # Define per selector
    if mux_sel == 0:
        decoded_data['Acq threshold'] = data
        return f"MUX: {mux_sel} : {data}  (Acq threshold)"
    elif mux_sel == 1:
        decoded_data['Trk threshold'] = data
        return f"MUX: {mux_sel} : {data}  (Trk threshold)"
    elif mux_sel == 2:
        decoded_data['Search reg 12 bits [b31-b24]'] = data
        return f"MUX: {mux_sel} : {data}  (Write SVID Search)"
    elif mux_sel == 3:
        decoded_data['Search reg 12 bits [b23-b12]'] = data
        return f"MUX: {mux_sel} : {data}  (Write SVID Search)"
    elif mux_sel == 4:
        decoded_data['SW Version'] = data
        return f"MUX: {mux_sel} : {data} (Dummy)"
    elif mux_sel == 5:
        decoded_data['uialm_cpy-cnt'] = data
        return f"MUX: {mux_sel} : {data} (Dummy)"
    elif mux_sel == 6:
        decoded_data['Search reg 8 bits [b11-b0]'] = data & 0xFF
        return f"MUX: {mux_sel} : {data & 0xFF} (Write SVID Search)"
    elif mux_sel == 7:
        decoded_data['alm_av_flag 16'] = data
        return f"MUX: {mux_sel} : {data} (Alm flag AV)"
    elif mux_sel == 8:
        decoded_data['alm+ctr_24'] = data
        return f"MUX: {mux_sel} : {data} (Alm availablity ctrl)"
    elif mux_sel == 9:
        decoded_data['CCSDS Spacecraft ID'] = data
        return f"MUX: {mux_sel} : {data}  (S/C ID)"
    elif mux_sel == 10:
        decoded_data['Elevation angle Threshold'] = data
        return f"MUX: {mux_sel} : {data} (Elev Threshold)"
    elif mux_sel == 11:
        navic_cmd = data & 0x7F
        gps_chk = (data >> 7) & 0x1F
        decoded_data['NavIC Cmd sat'] = navic_cmd
        decoded_data['Stored GPS alm_ucAlm_num_chk'] = gps_chk
        return f"MUX: {mux_sel} : NavIC Cmd={navic_cmd}, GPS_alm_chk={gps_chk}"
    elif mux_sel == 12:
        p2e = (data >> 10) & 0x03
        alm_usel = (data >> 5) & 0x1F
        alm_col = data & 0x1F
        decoded_data['P2E_3bits'] = p2e
        decoded_data['GPS_ALM_usel'] = alm_usel
        decoded_data['GPS_ALM_collected'] = alm_col
        return f"MUX: {mux_sel} : P2E={p2e}, ALM_usel={alm_usel}, ALM_col={alm_col}"
    else:
        decoded_data['Reserved/Unknown'] = data
        return f"MUX: {mux_sel} : {data} (Reserved)"


def decode_wdt_status_word(status_word):
    """
    Decodes the 16-bit WDT status and command counter word.

    Args:
        status_word (int, str, or tuple): A 16-bit unsigned int, hex string, or (high_byte, low_byte)

    Returns:
        dict: Decoded fields with descriptive labels.
    """
    if isinstance(status_word, str):
        status_word = int(status_word, 16)
    elif isinstance(status_word, tuple):
        status_word = (status_word[0] << 8) | status_word[1]
    elif not isinstance(status_word, int):
        raise ValueError("Input must be int, hex string, or (high_byte, low_byte) tuple")

    result = {}

    # Bits B15–B10: 6-bit Valid 1553 Command Counter
    result["Valid 1553 CMD CTR"] = (status_word >> 10) & 0x3F

    # Bit B9: TM selection
    result["TM Selection"] = "TM2" if (status_word >> 9) & 1 else "TM1"

    # Bit B8: SW line/SW WDT status
    b8 = (status_word >> 8) & 1
    result["SW Line/WDT Status"] = (
        "Disabled" if b8
        else "Enabled "
    )

    # Bit B7: HW WDT status
    result["HW WDT Status"] = "Disabled" if (status_word >> 7) & 1 else "Enabled"

    # Bit B6: MNV ON/OFF
    result["MNV Status"] = "ON" if (status_word >> 6) & 1 else "OFF"
    
    # Bit B5: SPS1 S/W WDT STATUS
    result["SPS1 S/W WDT STATUS"] = "Disabled" if (status_word >> 5) & 1 else "Enabled"

    # Bit B4: SPS Software Status
    result["SPS Software Status"] = "EEPROM Mode" if (status_word >> 4) & 1 else "PROM Mode"

    return result


def decode_system_mode_status(system_flag):
    """
    Decodes the 16-bit system mode and status flag.
    """
    if isinstance(system_flag, str):
        system_flag = int(system_flag, 16)
    elif isinstance(system_flag, tuple):
        system_flag = (system_flag[0] << 8) | system_flag[1]
    elif not isinstance(system_flag, int):
        raise ValueError("Input should be an integer, hex string, or tuple")

    flags = {
        "Range log Type": "Smooth Range" if (system_flag >> 15) & 1 else "Raw Range",
        "Eph Retain En": "Enabled" if (system_flag >> 14) & 1 else "Disabled",
        "Iono Smoothing": "Enabled" if (system_flag >> 13) & 1 else "Disabled",
        "INONO Enable": "Enabled" if (system_flag >> 12) & 1 else "Disabled",
        "GP2015 Lock": "Locked" if (system_flag >> 11) & 1 else "Unlocked",
        "RFFC5071 Lock": "Locked" if (system_flag >> 10) & 1 else "Unlocked",
        "Nav 1A": "Enabled" if (system_flag >> 9) & 1 else "Disabled",
        "Velocity Smoothing": "Enabled" if (system_flag >> 8) & 1 else "Disabled",
        "GPS2015 Ant2 Lock": "Locked" if (system_flag >> 7) & 1 else "Unlocked",
        "RAIM": "Enabled" if (system_flag >> 6) & 1 else "Disabled",
        "Carrier Smoothing": "Enabled" if (system_flag >> 5) & 1 else "Disabled",
    }

    # System Mode (B4–B2)
    system_mode_val = (system_flag >> 2) & 0b111
    system_mode_map = {
        0b001: "GPS + NAVIC",
        #0b010: "GPS + NAVIC",
        0b011: "NAVIC only",
        0b100: "GPS ",
        #0b101: "GPS only"
    }
    flags["System Mode"] = system_mode_map.get(system_mode_val, f"Unknown ({system_mode_val:03b})")

    # Time alignment system (B1)
    flags["Time Aligned To"] = "NavIC" if (system_flag >> 1) & 1 else "GPS"
     # Time Initialize system (B1)
    flags["Time Init From"] = "NavIC" if (system_flag >> 0) &  1 else "GPS"
    #print(flags["Time Init From"])

    return flags

def decode_word25(word25):
    """
    Decodes HWDT Reset Counter, SWDT Reset ID, and PB Storage Mode from a 16-bit word.

    Args:
        word25 (int, str, or tuple): 16-bit word (int), hex string, or (MSB, LSB) tuple.

    Returns:
        dict: Decoded values
    """
    if isinstance(word25, str):
        word25 = int(word25, 16)
    elif isinstance(word25, tuple):
        word25 = (word25[0] << 8) | word25[1]
    elif not isinstance(word25, int):
        raise ValueError("Input must be int, hex string, or (MSB, LSB) tuple")

    result = {}
    result["HWDT Reset Counter"] = (word25 >> 8) & 0xFF
    result["SWDT Reset ID"] = word25 & 0x0F
    '''pb_storage_mode_code = (word25 >> 4) & 0x0F

    pb_storage_mode_map = {
        1: "1s", 2: "2s", 5: "5s", 10: "10s"
    }
    result["PB Storage Mode"] = pb_storage_mode_map.get(pb_storage_mode_code, f"Unknown ({pb_storage_mode_code})")'''
    return result

def decode_sa9word32(word32):
    """
    Decodes HWDT Reset Counter, SWDT Reset ID, and PB Storage Mode from a 16-bit word.

    Args:
        word25 (int, str, or tuple): 16-bit word (int), hex string, or (MSB, LSB) tuple.

    Returns:
        dict: Decoded values
    """
    if isinstance(word32, str):
        word32 = int(word32, 16)
    elif isinstance(word32, tuple):
        word32 = (word32[0] << 8) | word32[1]
    elif not isinstance(word32, int):
        raise ValueError("Input must be int, hex string, or (MSB, LSB) tuple")

    result = {}
    result["Str_Est"] = word32 & 0x3
    result["Str_En"] = "Enabled" if (word32 >> 2) & 0x1 else "Disabled"
    result["Reset_C"] = (word32 >> 3) & 0x7
    result["Init"] = "Enabled" if (word32 >> 6) & 0x1 else "Disabled"

    return result

def odp_parameter(word1):
   
    if isinstance(word1, str):
        word1 = int(word1, 16)
    elif isinstance(word1, tuple):
        word1 = (word1[0] << 8) | word1[1]
    elif not isinstance(word1, int):
        raise ValueError("Input must be int, hex string, or (MSB, LSB) tuple")

    odp_par = {
   "No of I/P sat to odp" :(word1 & 0xF000) >> 12,
   "No of sat est" :(word1 & 0x0F00) >> 8,
   "Filter Init reason" :(word1 & 0x00F0) >> 4,
   "Filter Init Flag" :"Enabled" if (word1 >> 3) & 1 else "Disabled",
   "KF Est Flag" :"Enabled" if (word1 >> 2) & 1 else "Disabled",
   "PPP Est Flag Unsing" :"Enabled" if (word1 >> 1) & 1 else "Disabled",
   "Ph_center En Flag" :"Enabled" if word1  & 1 else "Disabled",

    }
    return odp_par

def decode_word15(word15):
    """
    Decodes Telecommand interrupt counter and number of satellites tracked from a 16-bit word.

    Args:
        word15 (int, str, or tuple): 16-bit unsigned int, hex string, or (MSB, LSB) tuple

    Returns:
        dict: Decoded values
    """
    if isinstance(word15, str):
        word15 = int(word15, 16)
    elif isinstance(word15, tuple):
        word15 = (word15[0] << 8) | word15[1]
    elif not isinstance(word15, int):
        raise ValueError("Input must be int, hex string, or (MSB, LSB) tuple")

    result = {}
    result["Interupt CMD Counter"] = (word15 >> 5) & 0x7FF  # 11 bits: B15-B5
    result["No Of Satellite"] = word15 & 0x1F           # 5 bits: B4-B0
    return result



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






def on_bus_toggle(*args):
    """
    Handles toggling between BUS A (0x78), BUS B (0x77), INTR ISL (0x7A), and EXTR ISL (0x7B).
    Packet format: [0xAC, 0xCA, 0x1F, 0x0B, RT_Address (0x00), Bus_Value]
    """
    try:
        if not (ser and ser.is_open):
            status_var.set("❌ Serial port not open.")
            return

        bus_map = {
            "A": (0x78, "BUS A"),
            "B": (0x77, "BUS B"),
            "INTR_ISL": (0x7A, "INTR ISL"),
            "EXTR_ISL": (0x7B, "EXTR ISL")
        }

        selected = bus_var.get()
        if selected not in bus_map:
            return

        bus_val, bus_name = bus_map[selected]
        header = [0xAC, 0xCA, 0x1F, 0x0B]
        rt_address = 0x00
        packet = header + [rt_address, bus_val]

        ser.write(bytes(packet))
        sent_str = f"Packet for toggle: {[f'0x{b:02X}' for b in packet]} ({bus_name})"
        status_var.set(sent_str)
        print(sent_str)
        with open("Buscmd.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | BUS_TOGGLE | {sent_str}\n")
    except Exception as e:
        status_var.set(f"❌ Error sending bus command (toggle): {e}")


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
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | RT_CMD_ENTRY | {sent_str}\n")
    except Exception as e:
        status_var.set(f"❌ Error sending bus command (entry): {e}")
    

def send_bus_isl_delay_command_entry():
    """
    For manual entry: HEADER + Entered Dataword + ISL Delay Address (0x7B)
    """
    try:
        if not (ser and ser.is_open):
            status_var.set("❌ Serial port not open.")
            return
        isl_delay_address = 0x7B  # always 0x7B for entry/manual
        dataword_str = dataword_entry1.get().strip()
        if dataword_str.lower().startswith("0x"):
            data_word = int(dataword_str, 16)
        else:
            data_word = int(dataword_str, 16) if all(c in "0123456789abcdefABCDEF" for c in dataword_str) else int(dataword_str)
        if not (0 <= data_word <= 0xFF):
            status_var.set("❌ Data word must be 1 byte (00-FF)")
            return
        header = [0xAC, 0xCA, 0x1F, 0x0B]
        packet = header + [data_word, isl_delay_address]
        sent_str = f"Sent (Entry): {[f'0x{b:02X}' for b in packet]}  (Manual Data=0x{data_word:02X}, ISL Delay=0x7B)"
        ser.write(bytes(packet))
        status_var.set(f"✅ {sent_str}")
        print(sent_str)
        with open("Buscmd.txt", "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ISL_Delay_CMD_ENTRY | {sent_str}\n")
    except Exception as e:
        status_var.set(f"❌ Error sending bus command (entry): {e}")


def get_timestamped_filename(base_name: str, suffix: str) -> str:
    """
    Generate consistent file name in format:
    SAMOOHA_YYYY-MM-DD_HH-MM-SS_BASENAME_SUFFIX.csv

    Example:
    SAMOOHA_2025-08-21_20-35-10_MYDATA_PVT.csv

    """
    global display_name
    return f"{display_name}_{SESSION_TIMESTAMP}_{base_name}_{suffix}.csv"
# =========================
# RAW DATA WITH HEADER LOGGING
# =========================
def write_to_raw_withheader1(data, base_name):
    file_name = get_timestamped_filename(base_name, "Raw1_withheader")
    header = ['TimeStamp','RAW DATA']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)

def write_to_raw_withheader2(data, base_name):
    file_name = get_timestamped_filename(base_name, "Raw2_withheader")
    header = ['TimeStamp','RAW DATA']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_raw_withheader3(data, base_name):
    file_name = get_timestamped_filename(base_name, "Raw3_withheader")
    header = ['TimeStamp','RAW DATA']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_raw_withheader4(data, base_name):
    file_name = get_timestamped_filename(base_name, "Raw4_withheader")
    header = ['TimeStamp','RAW DATA']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)


# =========================
# RAW DATA LOGGING
# =========================
def write_to_raw(data, base_name):
    file_name = get_timestamped_filename(base_name, "Raw")
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def write_to_rawh2(data, base_name):
    file_name = get_timestamped_filename(base_name, "Rawh2")
    header = ['TimeStamp','RAW DATA']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_rawh3(data, base_name):
    file_name = get_timestamped_filename(base_name, "Rawh3")
    header = ['TimeStamp','RAW DATA']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)

def write_to_rawh4(data, base_name):
    file_name = get_timestamped_filename(base_name, "Rawh4")
    header = ['TimeStamp','RAW DATA']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)


# =========================
# SYNC DATA LOGGING
# =========================
'''def write_to_SYN(data, base_name):
    file_name = get_timestamped_filename(base_name, "Sync")
    header = ['TimeStamp','SYN_SECOND','SYN_NANOSECOND','SYN_WEEKNUMBER']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)'''

def write_to_SYNh2(data, base_name):
    file_name = get_timestamped_filename(base_name, "Sync_Time")
    header = ['TimeStamp','h2SYN_SECOND','h2SYN_NANOSECOND','h2SYN_WEEKNUMBER']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA1_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA1_File")
    header = ['TimeStamp','SA1']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)

def write_to_SA3_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA3_File")
    header = ['TimeStamp','SA3']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)

def write_to_SA4_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA4_File")
    header = ['TimeStamp','SA4']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
        
def write_to_SA4_FILE_data(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA4_data_extr")
    header = ['TimeStamp','SA4_data_extr']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA5_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA5_File")
    header = ['TimeStamp','SA5']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA6_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA6_File")
    header = ['TimeStamp','SA6']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA7_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA7_File")
    header = ['TimeStamp','SA7']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA8_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA8_File")
    header = ['TimeStamp','SA8']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA9_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA9_File")
    header = ['TimeStamp','SA9']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA10_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA10_File")
    header = ['TimeStamp','SA10']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA11_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA11_File")
    header = ['TimeStamp','SA11']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA12_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA12_File")
    header = ['TimeStamp','SA12']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA13_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA13_File")
    header = ['TimeStamp','SA13']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA14_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA14_File")
    header = ['TimeStamp','SA14']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA15_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA15_File")
    header = ['TimeStamp','SA15']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA16_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA16_File")
    header = ['TimeStamp','SA16']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA17_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA17_File")
    header = ['TimeStamp','SA17']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
def write_to_SA18_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA18_File")
    header = ['TimeStamp','SA18']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
        
def write_to_SA28_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA28_File")
    header = ['TimeStamp','SA28']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)

def write_to_SA29_FILE(data, base_name):
    file_name = get_timestamped_filename(base_name, "SA29_File")
    header = ['TimeStamp','SA29']
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:   # write header only once
            writer.writerow(header)
        writer.writerow(data)
        
# =========================
# MAIN PVT DATA LOGGING
# =========================
# =========================
# MAIN PVT DATA LOGGING
# =========================
def write_to_csv(data, base_name):
    file_name = get_timestamped_filename(base_name, "PVT")

    header = [
        'TimeStamp','SYS_Second','SYS_NanoSecond','SYS_WeekNumber',
        'PPS Sec','PPS NS','PPS WN','PPS 3D Fix',
        'INST_X','INST_Y','INST_Z','INST_VX','INST_VY','INST_VZ',
        'EST_X','EST_Y','EST_Z','EST_VX','EST_VY','EST_VZ',
        'UpdateCounter','Memory count','SPU cmd Counter','Upset cmd Counter',
        'Checksum SA2','Checksum SA4','Validation Flag','PDOP',
        'Clock bias','InterSystem bias','Drift','Inter System Drift','Steering Bias','Steering Drift','Streening Clock','U1','U2',
        'Last_cmd_B1_B2','Last_cmd_B3','Last_cmd_B4','ACQ1_SVID',
        'SWDT Reset Counter',
        'Remote1 R/W','Remote2 R/W','Remote3 R/W','Remote4 R/W','Remote5 R/W','Remote6 R/W',
        'SA8_W3','SA8_W4','SA8_W5','SA8_W6','SA8_W7','SA8_W8','SA8_W9_W10',' SA8_W11_W12','SA8_W13_W14','SA8_W15_W16','SA8_W17_W18','SA8_W19_W20','SA8_W21_W22','SA8_W23_W24','SA8_W25_W26','SA8_W27_W28','SA8_W29_W30','SA8_W31_W32',
        'SA9_W1','SA9_W2','SA9_W3',' SA9_W4','SA9_W5',' SA9_W6','SA9_W7','SA9_W8',' SA9_W9','SA9_W10',' SA9_W11',' SA9_W12','SA9_W13','SA9_W14_W15','SA9_W16_W17',' SA9_W18_W19','SA9_W20_W21','SA9_W22_W23','SA9_W24_W25','SA9_W26',' SA9_W27','SA9_W28',' SA9_W29','SA9_W30_W31','SA9_W32',
        'SA10_W1','SA10_W2','SA10_W3','SA10_W4','SA10_W5','SA10_W6','SA10_W7','SA10_W8','SA10_W9_W10','SA10_W11_W12',' SA10_W13_W14','SA10_W15',' SA10_W16','SA10_W17','SA10_W18','SA10_W19','SA10_W20','SA10_W21','SA10_W22','SA10_W23_W24','SA10_W25_W26','SA10_W27_W28','SA10_W29_W30','SA10_W31_W32',
        'SA11_W1_W2','SA11_W3_W4','SA11_W5_W6','SA11_W7_W8','SA11_W9_W10','SA11_W11_W12','SA11_W13_W14','SA11_W15','SA11_W16','SA11_W17_W18','SA11_W19','SA11_W20','SA11_W21','SA11_W22','SA11_W23','SA11_W24','SA11_W25_W26','SA11_W27_W28','SA11_W29','SA11_W30_W31','SA11_W32',
        'SA12_W1','SA12_W2','SA12_W3','SA12_W4','SA12_W5','SA12_W6','SA12_W7','SA12_W8','SA12_W9','SA12_W10','SA12_W11','SA12_W12','SA12_W13','SA12_W14','SA12_W15','SA12_W16','SA12_W17','SA12_W18','SA12_W19_W20','SA12_W21_W22','SA12_W23_W24','SA12_W25_W26','SA12_W27_W28','SA12_W29_W30','SA12_W31','SA12_W32',
        'SA13_W1','SA13_W2','SA13_W3','SA13_W4','SA13_W5','SA13_W6','SA13_W7','SA13_W8','SA13_W9','SA13_W10','SA13_W11','SA13_W12','SA13_W13','SA13_W14','SA13_W15',
        'SA13_W16','SA13_W17','SA13_W18','SA13_W19','SA13_W20','SA13_W21','SA13_W22','SA13_W23','SA13_W24','SA13_W25','SA13_W26','SA13_W27','SA13_W28','SA13_W29','SA13_W30','SA13_W31','SA13_W32',
        'SA14_W1','SA14_W2','SA14_W3','SA14_W4','SA14_W5','SA14_W6','SA14_W7','SA14_W8','SA14_W9','SA14_W10','SA14_W11','SA14_W12','SA14_W13','SA14_W14','SA14_W15',
        'SA14_W16','SA14_W17','SA14_W18','SA14_W19','SA14_W20','SA14_W21','SA14_W22','SA14_W23','SA14_W24','SA14_W25','SA14_W26','SA14_W27','SA14_W28','SA14_W29','SA14_W30','SA14_W31','SA14_W32',
        'SA15_W1','SA15_W2','SA15_W3_W4','SA15_W5_W6','SA15_W7_W8','SA15_W9_W10','SA15_W11_W12','SA15_W13_W14','SA15_W15_W16','SA15_W17_W18','SA15_W19_W20','SA15_W21_W22','SA15_W23_W24','SA15_W25_W26','SA15_W27_W28','SA15_W29_W30','SA15_W31','SA15_W32',
        'SA16_W1','SA16_W2','SA16_W3_W4','SA16_W5','SA16_W6','SA16_W7','SA16_W8_W9','SA16_W10_W11','SA16_W12_W13','SA16_W14_W15','SA16_W16_W17','SA16_W18_W19','SA16_W20_W21','SA16_W22_W23','SA16_W24_W29','SA16_W30_W31','SA16_W32',
        'SA17_W1','SA17_W2','SA17_W3','SA17_W4','SA17_W5','SA17_W6','SA17_W7','SA17_W8','SA17_W9','SA17_W10','SA17_W11','SA17_W12','SA17_W13','SA17_W14','SA17_W15',
        'SA17_W16','SA17_W17','SA17_W18','SA17_W19','SA17_W20','SA17_W21','SA17_W22','SA17_W23','SA17_W24','SA17_W25','SA17_W26_W30','SA17_W31','SA17_W32',
        'SA18_W1','SA18_W2','SA18_W3','SA18_W4','SA18_W5','SA18_W6','SA18_W7','SA18_W8','SA18_W9','SA18_W10','SA18_W11','SA18_W12','SA18_W13','SA18_W14','SA18_W15',
        'SA18_W16','SA18_W17','SA18_W18','SA18_W19','SA18_W20','SA18_W21','SA18_W22','SA18_W23','SA18_W24','SA18_W25','SA18_W26_W30','SA18_W31','SA18_W32',
        'SA19_W1','SA19_W2','SA19_W3','SA19_W4','SA19_W5','SA19_W6','SA19_W7','SA19_W8','SA19_W9','SA19_W10','SA19_W11','SA19_W12','SA19_W13','SA19_W14','SA19_W15',
        'SA19_W16','SA19_W17','SA19_W18','SA19_W19','SA19_W20','SA19_W21','SA19_W22','SA19_W23','SA19_W24','SA19_W25','SA19_W26','SA19_W27','SA19_W28','SA19_W29','SA19_W30','SA19_W31','SA19_W32',
        'SA20_W1','SA20_W2','SA20_W3','SA20_W4','SA20_W5','SA20_W6','SA20_W7','SA20_W8','SA20_W9','SA20_W10','SA20_W11','SA20_W12','SA20_W13','SA20_W14','SA20_W15',
        'SA20_W16','SA20_W17','SA20_W18','SA20_W19','SA20_W20','SA20_W21','SA20_W22','SA20_W23','SA20_W24','SA20_W25','SA20_W26','SA20_W27','SA20_W28','SA20_W29','SA20_W30','SA20_W31','SA20_W32',
        'SA21_W1','SA21_W2','SA21_W3','SA21_W4','SA21_W5','SA21_W6','SA21_W7','SA21_W8','SA21_W9','SA21_W10','SA21_W11','SA21_W12','SA21_W13','SA21_W14','SA21_W15',
        'SA21_W16','SA21_W17','SA21_W18','SA21_W19','SA21_W20','SA21_W21','SA21_W22','SA21_W23','SA21_W24','SA21_W25','SA21_W26','SA21_W27','SA21_W28','SA21_W29','SA21_W30','SA21_W31','SA21_W32',
        'SA22_W1','SA22_W2','SA22_W3','SA22_W4','SA22_W5','SA22_W6','SA22_W7','SA22_W8','SA22_W9','SA22_W10','SA22_W11','SA22_W12','SA22_W13','SA22_W14','SA22_W15',
        'SA22_W16','SA22_W17','SA22_W18','SA22_W19','SA22_W20','SA22_W21','SA22_W22','SA22_W23','SA22_W24','SA22_W25','SA22_W26','SA22_W27','SA22_W28','SA22_W29','SA22_W30','SA22_W31','SA22_W32',
        'SA23_W1','SA23_W2','SA23_W3','SA23_W4','SA23_W5','SA23_W6','SA23_W7','SA23_W8','SA23_W9','SA23_W10','SA23_W11','SA23_W12','SA23_W13','SA23_W14','SA23_W15',
        'SA23_W16','SA23_W17','SA23_W18','SA23_W19','SA23_W20','SA23_W21','SA23_W22','SA23_W23','SA23_W24','SA23_W25','SA23_W26','SA23_W27','SA23_W28','SA23_W29','SA23_W30','SA23_W31','SA23_W32',
        'SA24_W1','SA24_W2','SA24_W3','SA24_W4','SA24_W5','SA24_W6','SA24_W7','SA24_W8','SA24_W9','SA24_W10','SA24_W11','SA24_W12','SA24_W13','SA24_W14','SA24_W15',
        'SA24_W16','SA24_W17','SA24_W18','SA24_W19','SA24_W20','SA24_W21','SA24_W22','SA24_W23','SA24_W24','SA24_W25','SA24_W26','SA24_W27','SA24_W28','SA24_W29','SA24_W30','SA24_W31','SA24_W32',
        'SA25_W1','SA25_W2','SA25_W3','SA25_W4','SA25_W5','SA25_W6','SA25_W7','SA25_W8','SA25_W9','SA25_W10','SA25_W11','SA25_W12','SA25_W13','SA25_W14','SA25_W15',
        'SA25_W16','SA25_W17','SA25_W18','SA25_W19','SA25_W20','SA25_W21','SA25_W22','SA25_W23','SA25_W24','SA25_W25','SA25_W26','SA25_W27','SA25_W28','SA25_W29','SA25_W30','SA25_W31','SA25_W32',
        'SA26_W1','SA26_W2','SA26_W3','SA26_W4','SA26_W5','SA26_W6','SA26_W7','SA26_W8','SA26_W9','SA26_W10','SA26_W11','SA26_W12','SA26_W13','SA26_W14','SA26_W15',
        'SA26_W16','SA26_W17','SA26_W18','SA26_W19','SA26_W20','SA26_W21','SA26_W22','SA26_W23','SA26_W24','SA26_W25','SA26_W26','SA26_W27','SA26_W28','SA26_W29','SA26_W30','SA26_W31','SA26_W32',
        'SA27_W1','SA27_W2','SA27_W3','SA27_W4','SA27_W5','SA27_W6','SA27_W7','SA27_W8','SA27_W9','SA27_W10','SA27_W11','SA27_W12','SA27_W13','SA27_W14','SA27_W15',
        'SA27_W16','SA27_W17','SA27_W18','SA27_W19','SA27_W20','SA27_W21','SA27_W22','SA27_W23','SA27_W24','SA27_W25','SA27_W26','SA27_W27','SA27_W28','SA27_W29','SA27_W30','SA27_W31','SA27_W32',


        'Str_Est','Str_En','Reset_C','Initialization',
        'HWDT Reset Counter','SWDT Reset ID',
        #'PB Storage Mode',
        'Tele CMD Counter','No Of Satellite','Valid 1553 Command Counter',
        'TM Selection','SW Line/WDT Status','HW WDT Status','MNV Status','SPS1 S/W WDT STATUS',
        'SPS Software Status','Iono Smoothing','INONO Enable','GP2015 Lock',
        'RFFC5071 Lock','Nav 1A','Velocity Smoothing','GPS2015 Ant2 Lock',
        'RAIM','Carrier Smoothing','System Mode','Time Aligned To','Last_reset_time',
        'SVID','IODE','CRS','MUX','ODP Status','Phase center correction',
        'Phase center correction SPS','PORT1','PORT2','SOL','POS_E','ALM','TIME',
        'Pos Mode','POS','CCSDS','Randomzier','Spacecraft_id','Navic_cmd',
         'No of I/P sat to odp','No of sat est','Filter Init reason','Filter Init Flag',
        'KF Est Flag','PPP Est Flag Unsing','Ph_center En Flag',
        'TM_Ill_cond','TM_Ill_cond_lim','Cond_pre','Cond_post','odp_prop_use','Precise_Time_Diff',"Inst Delta X","Inst Delta Y","Inst Delta Z","Inst Delta VX","Inst Delta VY","Inst Delta VZ",'Inst Pos Error'  ,"Inst Vel Error",
        "ODP Delta X","ODP Delta Y","ODP Delta Z","ODP Delta VX","ODP Delta VY","ODP Delta VZ","Odp Pos Error","Odp Vel Error",


        # CH1 → CH12 details
        'CH1','SVID1','CNDR1','T','P','E','D','I','R','H','A','IODE1','Pr(cm)1','Dr(m/s)1',
        'CH2','SVID2','CNDR2','T','P','E','D','I','R','H','A','IODE2','Pr(cm)2','Dr(m/s)2',
        'CH3','SVID3','CNDR3','T','P','E','D','I','R','H','A','IODE3','Pr(cm)3','Dr(m/s)3',
        'CH4','SVID4','CNDR4','T','P','E','D','I','R','H','A','IODE4','Pr(cm)4','Dr(m/s)4',
        'CH5','SVID5','CNDR5','T','P','E','D','I','R','H','A','IODE5','Pr(cm)5','Dr(m/s)5',
        'CH6','SVID6','CNDR6','T','P','E','D','I','R','H','A','IODE6','Pr(cm)6','Dr(m/s)6',
        'CH7','SVID7','CNDR7','T','P','E','D','I','R','H','A','IODE7','Pr(cm)7','Dr(m/s)7',
        'CH8','SVID8','CNDR8','T','P','E','D','I','R','H','A','IODE8','Pr(cm)8','Dr(m/s)8',
        'CH9','SVID9','CNDR9','T','P','E','D','I','R','H','A','IODE9','Pr(cm)9','Dr(m/s)9',
        'CH10','SVID10','CNDR10','T','P','E','D','I','R','H','A','IODE10','Pr(cm)10','Dr(m/s)10',
        'CH11','SVID11','CNDR11','T','P','E','D','I','R','H','A','IODE11','Pr(cm)11','Dr(m/s)11',
        'CH12','SVID12','CNDR12','T','P','E','D','I','R','H','A','IODE12','Pr(cm)12','Dr(m/s)12'
    ]

    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(header)  # write header once
        writer.writerow(data)
# Plot update function

def update_cndr_plot_func(svid_labels, cndr_values):
    colors = []
    for val in cndr_values:
        if 30 <= val < 40:
            colors.append("orange")  # Mid range
        elif 40 <= val <= 60:
            colors.append("blue")   # High range
        else:
            colors.append("lightgray")  # Other values
    ax_cndr.clear()
    ax_cndr.set_title("CNDR Values")
    ax_cndr.set_xlabel("SVIDs")
    ax_cndr.set_ylabel("CNDR Values")
    ax_cndr.set_ylim(0, 60)
    ax_cndr.set_yticks([0, 10, 20, 30, 35, 40, 45, 50, 60])

    ax_cndr.bar(range(1, 13), cndr_values, color=colors,edgecolor='black')
    ax_cndr.set_xticks(range(1, 13))
    ax_cndr.set_xticklabels(svid_labels, rotation=45)

    canvas_cndr.draw_idle()


def refresh_cndr_plot():
    try:
        cndr_vals = [float(eval(f"cndr{i}").get() or 0) for i in range(1, 13)]
        svid_labs = [eval(f"svid{i}").get() or f"CH{i}" for i in range(1, 13)]
        update_cndr_plot_func(svid_labs, cndr_vals)
    except Exception:
        pass

def readSerial():
    global serialData, ser, data_queue
    import collections

    HEADER_INFO = {
        "header1": (["ac", "ca", "1f", "0a"], 2046),
        "header2": (["ac", "ca", "1f", "0b"], 60),
        "header3": (["ac", "ca", "1f", "05"], 320),
        "header4": (["ac", "ca", "1f", "0d"], 2046),
    }

    State = collections.namedtuple("State", ["match_index", "buffer", "collecting", "target_len"])
    state = {k: State(0, bytearray(), False, len(v[0]) + v[1]) for k, v in HEADER_INFO.items()}

    try:
        while serialData and (ser and ser.is_open):
            if ser.in_waiting > 0:
                b = ser.read(1)
                if not b: continue
                b_hex = b.hex()

                for header_name, (header_seq, payload_len) in HEADER_INFO.items():
                    idx, buf, collecting, target_len = state[header_name]
                    if collecting:
                        buf += b
                        if len(buf) >= target_len:
                            data_queue.put((header_name, buf.hex().upper()))
                            state[header_name] = State(0, bytearray(), False, target_len)
                        else:
                            state[header_name] = State(idx, buf, True, target_len)
                        continue

                    if b_hex == header_seq[idx]:
                        idx += 1
                        if idx == len(header_seq):
                            hdr_bytes = bytes.fromhex(''.join(header_seq))
                            state[header_name] = State(idx, bytearray(hdr_bytes), True, target_len)
                        else:
                            state[header_name] = State(idx, bytearray(), False, target_len)
                    else:
                        state[header_name] = State(1 if b_hex == header_seq[0] else 0, bytearray(), False, target_len)
            else:
                pytime.sleep(0.01)
    except Exception:
        pass



def process_data():
    global base_name, filename, SYS_Second,SYS_NanoSecond, replay_running, serialData
    global diff_entry, current_time_diff, precise_loaded, precise_data,precise_times
    try:
        while True:
            try:
                item = data_queue.get(timeout=0.5)
            except queue.Empty:
                # Only exit if NOT live AND NOT replaying
                if not serialData and not replay_running:
                    break
                continue

            if not item or len(item) < 2:
                continue

            data_type, hexDecodedData = item
            if data_type == "header1":
                header_length = 10
                Raw_data = ' '.join([hexDecodedData[i:i+2]for i in range(header_length,len(hexDecodedData),2)])
                #formatted_data = ''.join([hexDecodedData[i:i+2]for i in range(0,len(without_header),2)])
                #=================SUBADDRESS 2 STRAT====================
                '''SA1_MIL = hexDecodedData[0:8]
                SA3_MIL = hexDecodedData[140:268]
                SA4_MIL = hexDecodedData[268:396]
                SA5_MIL = hexDecodedData[396:524]
                SA6_MIL = hexDecodedData[524:648]
                SA7_MIL = hexDecodedData[652:780]
                SA8_MIL = hexDecodedData[780:908]
                SA9_MIL = hexDecodedData[908:1036]
                SA10_MIL = hexDecodedData[1036:1164]
                SA11_MIL = hexDecodedData[1164:1292]
                SA12_MIL = hexDecodedData[1292:1420]
                SA13_MIL = hexDecodedData[1420:1548]
                SA14_MIL = hexDecodedData[1548:1676]
                SA15_MIL = hexDecodedData[1676:1804]
                SA16_MIL = hexDecodedData[1804:1932]
                SA17_MIL = hexDecodedData[1932:2060]
                SA18_MIL = hexDecodedData[2060:2188]
                SA28_MIL = hexDecodedData[2444:2468]
                SA29_MIL = hexDecodedData[2468:2524]'''
                SYN_NanoSecond_hex=hexDecodedData[12:20] #SA2W1-W2
                #print(f"SYN_NanoSecond_hex:{SYN_NanoSecond_hex}")
                SYN_Second_hex=hexDecodedData[20:28] #SA2W3-W4
                SYN_Weeknumber_hex=hexDecodedData[28:32] #SA2W5
                CHECKSUM_hex = hexDecodedData[32:36] #SA2W6

                #=====================SUBADDRESS 3 START=================
                SYS_NanoSecond_hex=hexDecodedData[140:148]#SA3W1-W2
                #print(f"\nSYS_NanoSecond_hex:{SYS_NanoSecond_hex}")
                SYS_Second_hex=hexDecodedData[148:156]#SA3W3-W4
                SYS_Weeknumber_hex=hexDecodedData[156:160]#SA3W5
                #print(SYS_Weeknumber_hex)
                Inst_x_hex = hexDecodedData[160:168] #SA3W6-W7
                #print(SPS_x)
                Inst_y_hex = hexDecodedData[168:176] #SA3W8-W9
                #print(SPS_y)
                Inst_z_hex = hexDecodedData[176:184] #SA3W10-W11
                #print(SPS_z)
                Inst_vx_hex = hexDecodedData[184:192] #SA3W12-W13
                #print(SPS_vx)
                Inst_vy_hex = hexDecodedData[192:200] #SA3W14-W15
                #print(SPS_vy)
                Inst_vz_hex = hexDecodedData[200:208] #SA3W16-W17
                #print(SPS_vz)

                UpdateCounter_hex=hexDecodedData[208:212] # SA3W18
                #print(UpdateCounter_hex)

                Est_x_hex = hexDecodedData[212:220] #SA3W19-W20
                #print(INT_x_hex)
                Est_y_hex  = hexDecodedData[220:228] #SA3W21-W22
                #print(INT_y_hex)
                Est_z_hex  = hexDecodedData[228:236] #SA3W23-W24
                #print(INT_z_hex)
                Est_vx_hex  = hexDecodedData[236:244] #SA3W25-W26
                #print(INT_vx_hex)
                Est_vy_hex  = hexDecodedData[244:252] #SA3W27-W28
                #print(INT_vy_hex)
                Est_vz_hex  = hexDecodedData[252:260] #SA3W29-W30
                

                validation_flag_hex=hexDecodedData[260:264] #SA3W31
                #print(validation_flag_hex)
                validation_flag=reverse_and_concatenate(validation_flag_hex)
                #print(f"\nvalidation flag:{validation_flag}")
                ODP_FLAG,odp_run_mode =decode_validation_flag(validation_flag)



                CHECKSUM1_hex = hexDecodedData[264:268] #SA3W32
                #print(f"CHECKSUM1_hex:{CHECKSUM1_hex}")

                #========================SUBADRESS 4 START==================
                SVID1_hex = hexDecodedData[400:402] #SA4W1-W2
                SVID2_hex = hexDecodedData[402:404] #SA4W3-W4
                SVID3_hex = hexDecodedData[396:398] #SA4W5-W6
                SVID4_hex = hexDecodedData[398:400] #SA4W7-W8
                SVID5_hex = hexDecodedData[408:410] #SA4W9-W10
                SVID6_hex = hexDecodedData[410:412] #SA4W11-W12
                SVID7_hex = hexDecodedData[404:406] #SA4W13-W14
                SVID8_hex = hexDecodedData[406:408] #SA4W15-W16

                #Delta SV1
                DR1_hex = hexDecodedData[332:340] #SA4W17-W18
                DR2_hex = hexDecodedData[340:348] #SA4W19-W20
                DR3_hex = hexDecodedData[348:356] #SA4W21-W22
                DR4_hex = hexDecodedData[356:364] #SA4W23-W24
                DR5_hex = hexDecodedData[364:372] #SA4W25-W26
                DR6_hex = hexDecodedData[372:380] #SA4W27-W28
                DR7_hex = hexDecodedData[380:388] #SA4W29-W30
                DR8_hex = hexDecodedData[388:396] #SA4W31-W32

                CLOCKBIAS_hex = hexDecodedData[428:436] #SA4
                PDOP_hex = hexDecodedData[436:440]

                system_flag_hex = hexDecodedData[448:452] #
                system_flag = reverse_and_concatenate(system_flag_hex)
                #print(system_flag)

                decoded_flags = decode_system_mode_status(system_flag)

                # Example: Update GUI entry widgets
                for label, value in decoded_flags.items():
                    entry = gui_entry_dict.get(label)
                    if entry:
                        entry.config(state="normal")
                        entry.delete(0, END)
                        entry.insert(0, value)
                        entry.config(state="readonly")
                        set_status_colored(entry, value)   # ✅ instead of manual insert

                

                Last_cmd_excuted_byte4_hex = hexDecodedData[478:480]
                Last_cmd_excuted_byte3_hex = hexDecodedData[490:492]
                Last_cmd_excuted_byte1_2_hex = hexDecodedData[480:484]

                wdt_status_hex = hexDecodedData[484:488]
                wdt_status = reverse_and_concatenate(wdt_status_hex)

                decoded_wdt = decode_wdt_status_word(wdt_status)

                for label, value in decoded_wdt.items():
                    entry = wdt_entries.get(label)
                    if entry:
                        entry.config(state="normal")
                        entry.delete(0, tk.END)
                        entry.insert(0, value)
                        entry.config(state="readonly")
                        set_status_colored(entry, value)

                ACQ1_SVID_hex = hexDecodedData[488:490]
                SWDT_RST_COUNTER_hex = hexDecodedData[476:478]

                word25_hex = hexDecodedData[492:496]  # Word#25
                word25 = reverse_and_concatenate(word25_hex)
                decoded25 = decode_word25(word25)

                for label, value in decoded25.items():
                    entry = word25_entries.get(label)
                    if entry:
                        entry.config(state="normal")
                        entry.delete(0, tk.END)
                        entry.insert(0, str(value))
                        entry.config(state="readonly")

                word32_hex = hexDecodedData[1032:1036]  # Word#25
                word32 = reverse_and_concatenate(word32_hex)
                decoded32 = decode_sa9word32(word32)


                for label, value in decoded32.items():
                    entry = word32_entries.get(label)
                    if entry:
                        entry.config(state="normal")
                        entry.delete(0, tk.END)
                        entry.insert(0, str(value))
                        entry.config(state="readonly")
                        set_status_colored(entry, value)   # ✅ instead of manual insert


                MC_hex = hexDecodedData[496:500]

                sa5w22_hex = hexDecodedData[484:488]
                sa5w22 = reverse_and_concatenate(sa5w22_hex)
                ODP_prop_used = (sa5w22 & 0x0008) >> 3

                LAST_RESET_TIME_hex = hexDecodedData[504:508]
                sa5w27_hex = hexDecodedData[504:508]
                sa5w27 = reverse_and_concatenate(sa5w27_hex)

                ill_cnd_val = (sa5w27 & 0xFFF8) >> 3

                INTER_SYSTEM_BIAS_hex = hexDecodedData[456:460]
                sa5w15_hex = hexDecodedData[456:460]
                sa5w15 = reverse_and_concatenate(sa5w15_hex)
                ill_cnd_Limit = (sa5w15 &0xFFC0) >> 6

                post_cntr = ((sa5w27 & 0x0007)<<6) |(sa5w15 & 0x003f)


                sa5w28_hex = hexDecodedData[508:512]  # Adjust index as per actual layout

                # Convert to integer
                sa5w28 = reverse_and_concatenate(sa5w28_hex)

                cond_pre_check = (sa5w28 &0x1000)>>12
                cond_post_check = (sa5w28 & 0x2000)>>13

                sa5w29_hex= hexDecodedData[512:516]  # Adjust index if needed



                # Convert to int
                sa5w29 = reverse_and_concatenate(sa5w29_hex)
                pre_cntr = (sa5w29 & 0xf000)>>12




                INTER_SYSTEM_Drift_hex = hexDecodedData[520:524]

                IODE_hex = hexDecodedData[524:526]
                SVID_hex = hexDecodedData[526:528]
                CRS_hex = hexDecodedData[528:532]

                DRIFT_LSB_hex = hexDecodedData[684:688]
                #print(f"Drift_lsb:{DRIFT_LSB_hex}")
                DRIFT_MSB_hex = hexDecodedData[704:708]
                #print(f"Drift_msb:{DRIFT_MSB_hex}")


                DRIFT_MSB_LSB_HEX = DRIFT_MSB_hex + DRIFT_LSB_hex
                #print(f"drift hex:{DRIFT_MSB_LSB_HEX}")
                DRIFT = reverse_and_concatenate(DRIFT_MSB_LSB_HEX, is_signed=True)/1000.0
                #print(f"drift:{DRIFT}")



                
                word15_hex = hexDecodedData[708:712]
                word15=reverse_and_concatenate(word15_hex)
                decoded_cmd = decode_word15(word15)

                # When you decode:
                for label, value in decoded_cmd.items():
                    entry = tele_entries[label]
                    entry.config(state="normal")
                    entry.delete(0, END)
                    entry.insert(0, value)
                    entry.config(state="readonly")
                    set_status_colored(entry, value)

                TELE_CMD_COUNTER_hex = hexDecodedData[744:746]
                UPSET_COUNTER_hex = hexDecodedData[746:748]


                SVID9_hex = hexDecodedData[688:690]
                SVID10_hex = hexDecodedData[690:692]
                SVID11_hex = hexDecodedData[748:750]
                SVID12_hex = hexDecodedData[750:752]

                CNDR1_hex = hexDecodedData[464:466]
                CNDR2_hex = hexDecodedData[466:468]
                CNDR3_hex = hexDecodedData[460:462]
                CNDR4_hex = hexDecodedData[462:464]
                CNDR5_hex = hexDecodedData[472:474]
                CNDR6_hex = hexDecodedData[474:476]
                CNDR7_hex = hexDecodedData[468:470]
                CNDR8_hex = hexDecodedData[470:472]
                CNDR9_hex = hexDecodedData[700:702]
                CNDR10_hex = hexDecodedData[702:704]
                CNDR11_hex = hexDecodedData[760:762]
                CNDR12_hex = hexDecodedData[762:764]

                IODE1_hex = hexDecodedData[416:418]
                IODE2_hex = hexDecodedData[418:420]
                IODE3_hex = hexDecodedData[412:414]
                IODE4_hex = hexDecodedData[414:416]
                IODE5_hex = hexDecodedData[424:426]
                IODE6_hex = hexDecodedData[426:428]
                IODE7_hex = hexDecodedData[420:422]
                IODE8_hex = hexDecodedData[422:424]
                IODE9_hex = hexDecodedData[696:698]
                IODE10_hex = hexDecodedData[698:700]
                IODE11_hex = hexDecodedData[756:758]
                IODE12_hex = hexDecodedData[758:760]

                PR1_hex = hexDecodedData[268:276]
                PR2_hex = hexDecodedData[276:284]
                PR3_hex = hexDecodedData[284:292]
                PR4_hex = hexDecodedData[292:300]
                PR5_hex = hexDecodedData[300:308]
                PR6_hex = hexDecodedData[308:316]
                PR7_hex = hexDecodedData[316:324]
                PR8_hex = hexDecodedData[324:332]
                PR9_hex = hexDecodedData[652:660]
                PR10_hex = hexDecodedData[660:668]
                PR11_hex = hexDecodedData[712:720]
                PR12_hex = hexDecodedData[720:728]

                DR9_hex = hexDecodedData[668:676]
                DR10_hex = hexDecodedData[676:684]
                DR11_hex = hexDecodedData[728:736]
                DR12_hex = hexDecodedData[736:744]
                
                Remote_Read_Write1_hex = hexDecodedData[632:636]
                Remote_Read_Write2_hex = hexDecodedData[636:640]
                Remote_Read_Write3_hex = hexDecodedData[640:644]
                Remote_Read_Write4_hex = hexDecodedData[644:648]
                Remote_Read_Write5_hex = hexDecodedData[780:784]
                Remote_Read_Write6_hex = hexDecodedData[784:788]
                
                sbas_fast_crr = hexDecodedData[776:780]  # Adjust index if needed

                # Convert to int
                word32_int = reverse_and_concatenate(sbas_fast_crr)
                # Decode Additional Bits
                #elev_flag = 'Disabled' if ((word32_int >> 12) & 0x1) == 0 else 'Enabled'
                ccsds_flag = 'Enabled' if ((word32_int >> 15) & 0x1) == 1 else 'Disabled'
                randomizer_flag = 'on' if ((word32_int >> 14) & 0x1) == 1 else 'off'
                #pr_mode_flag = 'old' if ((word32_int >> 13) & 0x1) == 1 else 'new'
                
                
                #===============SA8 ============================#
                
                SA8W3_hex = hexDecodedData[788:792]
                SA8W3 = reverse_and_concatenate(SA8W3_hex)
        
                SA8W4_hex = hexDecodedData[792:796]
                SA8W4 = reverse_and_concatenate(SA8W4_hex)
                
                SA8W5_hex = hexDecodedData[796:800]
                SA8W5 = reverse_and_concatenate(SA8W5_hex)
        
                SA8W6_hex = hexDecodedData[800:804]
                SA8W6 = reverse_and_concatenate(SA8W6_hex)
                
                SA8W7_hex = hexDecodedData[804:808]
                SA8W7 = reverse_and_concatenate(SA8W7_hex)
        
                SA8W8_hex = hexDecodedData[808:812]
                SA8W8 = reverse_and_concatenate(SA8W8_hex)
                
                SA8W9_W10_hex = hexDecodedData[812:820]
                SA8W9_W10 = reverse_and_concatenate(SA8W9_W10_hex)
        
                SA8W11_W12_hex = hexDecodedData[820:828]
                SA8W11_W12 = reverse_and_concatenate(SA8W11_W12_hex)
                
                SA8W13_W14_hex = hexDecodedData[828:836]
                SA8W13_W14 = reverse_and_concatenate(SA8W13_W14_hex)
        
                SA8W15_W16_hex = hexDecodedData[836:844]
                SA8W15_W16 = reverse_and_concatenate(SA8W15_W16_hex)
                
                SA8W17_W18_hex = hexDecodedData[844:852]
                SA8W17_W18 = reverse_and_concatenate(SA8W17_W18_hex)
        
                SA8W19_W20_hex = hexDecodedData[852:860]
                SA8W19_W20 = reverse_and_concatenate(SA8W19_W20_hex)
                
                SA8W21_W22_hex = hexDecodedData[860:868]
                SA8W21_W22 = reverse_and_concatenate(SA8W21_W22_hex)
        
                SA8W23_W24_hex = hexDecodedData[868:876]
                SA8W23_W24 = reverse_and_concatenate(SA8W23_W24_hex)
                
                SA8W25_W26_hex = hexDecodedData[876:884]
                SA8W25_W26 = reverse_and_concatenate(SA8W25_W26_hex)
        
                SA8W27_W28_hex = hexDecodedData[884:892]
                SA8W27_W28 = reverse_and_concatenate(SA8W27_W28_hex)
                
                SA8W29_W30_hex = hexDecodedData[892:900]
                SA8W29_W30 = reverse_and_concatenate(SA8W29_W30_hex)
        
                SA8W31_W32_hex = hexDecodedData[900:908]
                SA8W31_W32 = reverse_and_concatenate(SA8W31_W32_hex)
                
                #===============SA9 ============================#
                SA9W1_hex = hexDecodedData[908:912]
                SA9W1 = reverse_and_concatenate(SA9W1_hex)
        
                SA9W2_hex = hexDecodedData[912:916]
                SA9W2 = reverse_and_concatenate(SA9W2_hex)
                
                SA9W3_hex = hexDecodedData[916:920]
                SA9W3 = reverse_and_concatenate(SA9W3_hex)
        
                SA9W4_hex = hexDecodedData[920:924]
                SA9W4 = reverse_and_concatenate(SA9W4_hex)
                
                SA9W5_hex = hexDecodedData[924:928]
                SA9W5 = reverse_and_concatenate(SA9W5_hex)
        
                SA9W6_hex = hexDecodedData[928:932]
                SA9W6 = reverse_and_concatenate(SA9W6_hex)
                
                SA9W7_hex = hexDecodedData[932:936]
                SA9W7 = reverse_and_concatenate(SA9W7_hex)
        
                SA9W8_hex = hexDecodedData[936:940]
                SA9W8 = reverse_and_concatenate(SA9W8_hex)
                
                SA9W9_hex = hexDecodedData[940:944]
                SA9W9 = reverse_and_concatenate(SA9W9_hex)
        
                SA9W10_hex = hexDecodedData[944:948]
                SA9W10 = reverse_and_concatenate(SA9W10_hex)
                
                SA9W11_hex = hexDecodedData[948:952]
                SA9W11 = reverse_and_concatenate(SA9W11_hex)
        
                SA9W12_hex = hexDecodedData[952:956]
                SA9W12 = reverse_and_concatenate(SA9W12_hex)
                
                SA9W13_hex = hexDecodedData[956:960]
                SA9W13 = reverse_and_concatenate(SA9W13_hex)
                
                SA9W14_W15_hex = hexDecodedData[960:968]
                SA9W14_W15 = reverse_and_concatenate(SA9W14_W15_hex)
        
                SA9W16_W17_hex = hexDecodedData[968:976]
                SA9W16_W17 = reverse_and_concatenate(SA9W16_W17_hex)
                
                SA9W18_W19_hex = hexDecodedData[976:984]
                SA9W18_W19 = reverse_and_concatenate(SA9W18_W19_hex)
        
                SA9W20_W21_hex = hexDecodedData[984:992]
                SA9W20_W21 = reverse_and_concatenate(SA9W20_W21_hex)
                
                SA9W22_W23_hex = hexDecodedData[992:1000]
                SA9W22_W23 = reverse_and_concatenate(SA9W22_W23_hex)
        
                SA9W24_W25_hex = hexDecodedData[1000:1008]
                SA9W24_W25 = reverse_and_concatenate(SA9W24_W25_hex)
                
                SA9W26_hex = hexDecodedData[1008:1012]
                SA9W26 = reverse_and_concatenate(SA9W26_hex)
                
                SA9W27_hex = hexDecodedData[1012:1016]
                SA9W27 = reverse_and_concatenate(SA9W27_hex)
        
                SA9W28_hex = hexDecodedData[1016:1020]
                SA9W28 = reverse_and_concatenate(SA9W28_hex)
                
                SA9W29_hex = hexDecodedData[1020:1024]
                SA9W29 = reverse_and_concatenate(SA9W29_hex)
                
                SA9W30_W31_hex = hexDecodedData[1024:1032]
                SA9W30_W31 = reverse_and_concatenate(SA9W30_W31_hex)
        
                SA9W32_hex = hexDecodedData[1032:1036]
                SA9W32 = reverse_and_concatenate(SA9W32_hex)
                
                #===============SA10 ============================#
                SA10W1_hex = hexDecodedData[1036:1040]
                SA10W1 = reverse_and_concatenate(SA10W1_hex)
        
                SA10W2_hex = hexDecodedData[1040:1044]
                SA10W2 = reverse_and_concatenate(SA10W2_hex)
                
                SA10W3_hex = hexDecodedData[1044:1048]
                SA10W3 = reverse_and_concatenate(SA10W3_hex)
        
                SA10W4_hex = hexDecodedData[1048:1052]
                SA10W4 = reverse_and_concatenate(SA10W4_hex)
                
                SA10W5_hex = hexDecodedData[1052:1056]
                SA10W5 = reverse_and_concatenate(SA10W5_hex)
        
                SA10W6_hex = hexDecodedData[1056:1060]
                SA10W6 = reverse_and_concatenate(SA10W6_hex)
                
                SA10W7_hex = hexDecodedData[1060:1064]
                SA10W7 = reverse_and_concatenate(SA10W7_hex)
        
                SA10W8_hex = hexDecodedData[1064:1068]
                SA10W8 = reverse_and_concatenate(SA10W8_hex)
                
                SA10W9_W10_hex = hexDecodedData[1068:1076]
                SA10W9_W10 = reverse_and_concatenate(SA10W9_W10_hex)
        
                SA10W11_W12_hex = hexDecodedData[1076:1084]
                SA10W11_W12 = reverse_and_concatenate(SA10W11_W12_hex)
        
                SA10W13_W14_hex = hexDecodedData[1084:1092]
                SA10W13_W14 = reverse_and_concatenate(SA10W13_W14_hex)

                SA10W15_hex = hexDecodedData[1092:1096]
                SA10W15 = reverse_and_concatenate(SA10W15_hex)
        
                SA10W16_hex = hexDecodedData[1096:1100]
                SA10W16 = reverse_and_concatenate(SA10W16_hex)
                
                SA10W17_hex = hexDecodedData[1100:1104]
                SA10W17 = reverse_and_concatenate(SA10W17_hex)
                
                SA10W18_hex = hexDecodedData[1104:1108]
                SA10W18 = reverse_and_concatenate(SA10W18_hex)
                
                SA10W19_hex = hexDecodedData[1108:1112]
                SA10W19 = reverse_and_concatenate(SA10W19_hex)
                
                SA10W20_hex = hexDecodedData[1112:1116]
                SA10W20 = reverse_and_concatenate(SA10W20_hex)
                
                SA10W21_hex = hexDecodedData[1116:1120]
                SA10W21 = reverse_and_concatenate(SA10W21_hex)
                
                SA10W22_hex = hexDecodedData[1120:1124]
                SA10W22 = reverse_and_concatenate(SA10W22_hex)
                
                SA10W23_W24_hex = hexDecodedData[1124:1132]
                SA10W23_W24 = reverse_and_concatenate(SA10W23_W24_hex)
                
                SA10W25_W26_hex = hexDecodedData[1132:1140]
                SA10W25_W26 = reverse_and_concatenate(SA10W25_W26_hex)
                
                SA10W27_W28_hex = hexDecodedData[1140:1148]
                SA10W27_W28 = reverse_and_concatenate(SA10W27_W28_hex)
                
                SA10W29_W30_hex = hexDecodedData[1148:1156]
                SA10W29_W30 = reverse_and_concatenate(SA10W29_W30_hex)
                
                SA10W31_W32_hex = hexDecodedData[1156:1164]
                SA10W31_W32 = reverse_and_concatenate(SA10W31_W32_hex)
                
                 #===============SA11 ============================#
                SA11W1_W2_hex = hexDecodedData[1164:1172]
                SA11W1_W2 = reverse_and_concatenate(SA11W1_W2_hex)
        
                SA11W3_W4_hex = hexDecodedData[1172:1180]
                SA11W3_W4 = reverse_and_concatenate(SA11W3_W4_hex)
                
                SA11W5_W6_hex = hexDecodedData[1180:1188]
                SA11W5_W6 = reverse_and_concatenate(SA11W5_W6_hex)
        
                SA11W7_W8_hex = hexDecodedData[1188:1196]
                SA11W7_W8 = reverse_and_concatenate(SA11W7_W8_hex)
                
                SA11W9_W10_hex = hexDecodedData[1196:1204]
                SA11W9_W10 = reverse_and_concatenate(SA11W9_W10_hex)
        
                SA11W11_W12_hex = hexDecodedData[1204:1212]
                SA11W11_W12 = reverse_and_concatenate(SA11W11_W12_hex)
                
                SA11W13_W14_hex = hexDecodedData[1212:1220]
                SA11W13_W14 = reverse_and_concatenate(SA11W13_W14_hex)
        

                SA11W15_hex = hexDecodedData[1220:1224]
                SA11W15 = reverse_and_concatenate(SA11W15_hex)
        
                SA11W16_hex = hexDecodedData[1224:1228]
                SA11W16 = reverse_and_concatenate(SA11W16_hex)
                
                SA11W17_W18_hex = hexDecodedData[1228:1236]
                SA11W17_W18 = reverse_and_concatenate(SA11W17_W18_hex)
                
                SA11W19_hex = hexDecodedData[1236:1240]
                SA11W19 = reverse_and_concatenate(SA11W19_hex)
                
                SA11W20_hex = hexDecodedData[1240:1244]
                SA11W20 = reverse_and_concatenate(SA11W20_hex)
                
                SA11W21_hex = hexDecodedData[1244:1248]
                SA11W21 = reverse_and_concatenate(SA11W21_hex)
                
                SA11W22_hex = hexDecodedData[1248:1252]
                SA11W22 = reverse_and_concatenate(SA11W22_hex)
                
                SA11W23_hex = hexDecodedData[1252:1256]
                SA11W23 = reverse_and_concatenate(SA11W23_hex)
                
                SA11W24_hex = hexDecodedData[1256:1260]
                SA11W24 = reverse_and_concatenate(SA11W24_hex)
                
                SA11W25_W26_hex = hexDecodedData[1260:1268]
                SA11W25_W26 = reverse_and_concatenate(SA11W25_W26_hex)
                
                SA11W27_W28_hex = hexDecodedData[1268:1276]
                SA11W27_W28 = reverse_and_concatenate(SA11W27_W28_hex)
                
                SA11W29_hex = hexDecodedData[1276:1280]
                SA11W29 = reverse_and_concatenate(SA11W29_hex)
                
                SA11W30_W31_hex = hexDecodedData[1280:1288]
                SA11W30_W31 = reverse_and_concatenate(SA11W30_W31_hex)
                
                SA11W32_hex = hexDecodedData[1288:1292]
                SA11W32 = reverse_and_concatenate(SA11W32_hex)
                
                #===============SA12 ============================#
                SA12W1_hex = hexDecodedData[1292:1296]
                SA12W1 = reverse_and_concatenate(SA12W1_hex)
        
                SA12W2_hex = hexDecodedData[1296:1300]
                SA12W2 = reverse_and_concatenate(SA12W2_hex)
                
                SA12W3_hex = hexDecodedData[1300:1304]
                SA12W3 = reverse_and_concatenate(SA12W3_hex)
        
                SA12W4_hex = hexDecodedData[1304:1308]
                SA12W4 = reverse_and_concatenate(SA12W4_hex)
                
                SA12W5_hex = hexDecodedData[1308:1312]
                SA12W5 = reverse_and_concatenate(SA12W5_hex)
        
                SA12W6_hex = hexDecodedData[1312:1316]
                SA12W6 = reverse_and_concatenate(SA12W6_hex)
                
                SA12W7_hex = hexDecodedData[1316:1320]
                SA12W7 = reverse_and_concatenate(SA12W7_hex)
                
                SA12W8_hex = hexDecodedData[1320:1324]
                SA12W8 = reverse_and_concatenate(SA12W8_hex)
        
                SA12W9_hex = hexDecodedData[1324:1328]
                SA12W9 = reverse_and_concatenate(SA12W9_hex)
                
                SA12W10_hex = hexDecodedData[1328:1332]
                SA12W10 = reverse_and_concatenate(SA12W10_hex)
        
                SA12W11_hex = hexDecodedData[1332:1336]
                SA12W11 = reverse_and_concatenate(SA12W11_hex)
                
                SA12W12_hex = hexDecodedData[1336:1340]
                SA12W12 = reverse_and_concatenate(SA12W12_hex)
        
                SA12W13_hex = hexDecodedData[1340:1344]
                SA12W13 = reverse_and_concatenate(SA12W13_hex)
                
                SA12W14_hex = hexDecodedData[1344:1348]
                SA12W14 = reverse_and_concatenate(SA12W14_hex)
                
                SA12W15_hex = hexDecodedData[1348:1352]
                SA12W15 = reverse_and_concatenate(SA12W15_hex)
        
                SA12W16_hex = hexDecodedData[1352:1356]
                SA12W16 = reverse_and_concatenate(SA12W16_hex)
                
                SA12W17_hex = hexDecodedData[1356:1360]
                SA12W17 = reverse_and_concatenate(SA12W17_hex)
                
                SA12W18_hex = hexDecodedData[1360:1364]
                SA12W18 = reverse_and_concatenate(SA12W18_hex)
                
                SA12W19_W20_hex = hexDecodedData[1364:1372]
                SA12W19_W20 = reverse_and_concatenate(SA12W19_W20_hex)
                
                SA12W21_W22_hex = hexDecodedData[1372:1380]
                SA12W21_W22 = reverse_and_concatenate(SA12W21_W22_hex)
                
                SA12W23_W24_hex = hexDecodedData[1380:1388]
                SA12W23_W24 = reverse_and_concatenate(SA12W23_W24_hex)
                
                SA12W25_W26_hex = hexDecodedData[1388:1396]
                SA12W25_W26 = reverse_and_concatenate(SA12W25_W26_hex)
                
                SA12W27_W28_hex = hexDecodedData[1396:1404]
                SA12W27_W28 = reverse_and_concatenate(SA12W27_W28_hex)
                
                SA12W29_W30_hex = hexDecodedData[1404:1412]
                SA12W29_W30 = reverse_and_concatenate(SA12W29_W30_hex)
                
                SA12W31_hex = hexDecodedData[1412:1416]
                SA12W31 = reverse_and_concatenate(SA12W31_hex)
                
                SA12W32_hex = hexDecodedData[1416:1420]
                SA12W32 = reverse_and_concatenate(SA12W32_hex)
                
                
                #===============SA13 ============================#
                SA13W1_hex = hexDecodedData[1420:1424]
                SA13W1 = reverse_and_concatenate(SA13W1_hex)
        
                SA13W2_hex = hexDecodedData[1424:1428]
                SA13W2 = reverse_and_concatenate(SA13W2_hex)
                
                SA13W3_hex = hexDecodedData[1428:1432]
                SA13W3 = reverse_and_concatenate(SA13W3_hex)
        
                SA13W4_hex = hexDecodedData[1432:1436]
                SA13W4 = reverse_and_concatenate(SA13W4_hex)
                
                SA13W5_hex = hexDecodedData[1436:1440]
                SA13W5 = reverse_and_concatenate(SA13W5_hex)
        
                SA13W6_hex = hexDecodedData[1440:1444]
                SA13W6 = reverse_and_concatenate(SA13W6_hex)
                
                SA13W7_hex = hexDecodedData[1444:1448]
                SA13W7 = reverse_and_concatenate(SA13W7_hex)
                
                SA13W8_hex = hexDecodedData[1448:1452]
                SA13W8 = reverse_and_concatenate(SA13W8_hex)
        
                SA13W9_hex = hexDecodedData[1452:1456]
                SA13W9 = reverse_and_concatenate(SA13W9_hex)
                
                SA13W10_hex = hexDecodedData[1456:1460]
                SA13W10 = reverse_and_concatenate(SA13W10_hex)
        
                SA13W11_hex = hexDecodedData[1460:1464]
                SA13W11 = reverse_and_concatenate(SA13W11_hex)
                
                SA13W12_hex = hexDecodedData[1464:1468]
                SA13W12 = reverse_and_concatenate(SA13W12_hex)
        
                SA13W13_hex = hexDecodedData[1468:1472]
                SA13W13 = reverse_and_concatenate(SA13W13_hex)
                
                SA13W14_hex = hexDecodedData[1472:1476]
                SA13W14 = reverse_and_concatenate(SA13W14_hex)
                
                SA13W15_hex = hexDecodedData[1476:1480]
                SA13W15 = reverse_and_concatenate(SA13W15_hex)
        
                SA13W16_hex = hexDecodedData[1480:1484]
                SA13W16 = reverse_and_concatenate(SA13W16_hex)
                
                SA13W17_hex = hexDecodedData[1484:1488]
                SA13W17 = reverse_and_concatenate(SA13W17_hex)
                
                SA13W18_hex = hexDecodedData[1488:1492]
                SA13W18 = reverse_and_concatenate(SA13W18_hex)
                
                SA13W19_hex = hexDecodedData[1492:1496]
                SA13W19 = reverse_and_concatenate(SA13W19_hex)
                
                SA13W20_hex = hexDecodedData[1496:1500]
                SA13W20 = reverse_and_concatenate(SA13W20_hex)
        
                SA13W21_hex = hexDecodedData[1500:1504]
                SA13W21 = reverse_and_concatenate(SA13W21_hex)
                
                SA13W22_hex = hexDecodedData[1504:1508]
                SA13W22 = reverse_and_concatenate(SA13W22_hex)
        
                SA13W23_hex = hexDecodedData[1508:1512]
                SA13W23 = reverse_and_concatenate(SA13W23_hex)
                
                SA13W24_hex = hexDecodedData[1512:1516]
                SA13W24 = reverse_and_concatenate(SA13W24_hex)
                
                SA13W25_hex = hexDecodedData[1516:1520]
                SA13W25 = reverse_and_concatenate(SA13W25_hex)
        
                SA13W26_hex = hexDecodedData[1520:1524]
                SA13W26 = reverse_and_concatenate(SA13W26_hex)
                
                SA13W27_hex = hexDecodedData[1524:1528]
                SA13W27 = reverse_and_concatenate(SA13W27_hex)
                
                SA13W28_hex = hexDecodedData[1528:1532]
                SA13W28 = reverse_and_concatenate(SA13W28_hex)
                
                SA13W29_hex = hexDecodedData[1532:1536]
                SA13W29 = reverse_and_concatenate(SA13W29_hex)
                
                SA13W30_hex = hexDecodedData[1536:1540]
                SA13W30 = reverse_and_concatenate(SA13W30_hex)
        
                SA13W31_hex = hexDecodedData[1540:1544]
                SA13W31 = reverse_and_concatenate(SA13W31_hex)
                
                SA13W32_hex = hexDecodedData[1544:1548]
                SA13W32 = reverse_and_concatenate(SA13W32_hex)
                
                #===============SA14 ============================#
                SA14W1_hex = hexDecodedData[1548:1552]
                SA14W1 = reverse_and_concatenate(SA14W1_hex)
        
                SA14W2_hex = hexDecodedData[1552:1556]
                SA14W2 = reverse_and_concatenate(SA14W2_hex)
                
                SA14W3_hex = hexDecodedData[1556:1560]
                SA14W3 = reverse_and_concatenate(SA14W3_hex)
        
                SA14W4_hex = hexDecodedData[1560:1564]
                SA14W4 = reverse_and_concatenate(SA14W4_hex)
                
                SA14W5_hex = hexDecodedData[1564:1568]
                SA14W5 = reverse_and_concatenate(SA14W5_hex)
        
                SA14W6_hex = hexDecodedData[1568:1572]
                SA14W6 = reverse_and_concatenate(SA14W6_hex)
                
                SA14W7_hex = hexDecodedData[1572:1576]
                SA14W7 = reverse_and_concatenate(SA14W7_hex)
                
                SA14W8_hex = hexDecodedData[1576:1580]
                SA14W8 = reverse_and_concatenate(SA14W8_hex)
        
                SA14W9_hex = hexDecodedData[1580:1584]
                SA14W9 = reverse_and_concatenate(SA14W9_hex)
                
                SA14W10_hex = hexDecodedData[1584:1588]
                SA14W10 = reverse_and_concatenate(SA14W10_hex)
        
                SA14W11_hex = hexDecodedData[1588:1592]
                SA14W11 = reverse_and_concatenate(SA14W11_hex)
                
                SA14W12_hex = hexDecodedData[1592:1596]
                SA14W12 = reverse_and_concatenate(SA14W12_hex)
        
                SA14W13_hex = hexDecodedData[1596:1600]
                SA14W13 = reverse_and_concatenate(SA14W13_hex)
                
                SA14W14_hex = hexDecodedData[1600:1604]
                SA14W14 = reverse_and_concatenate(SA14W14_hex)
                
                SA14W15_hex = hexDecodedData[1604:1608]
                SA14W15 = reverse_and_concatenate(SA14W15_hex)
        
                SA14W16_hex = hexDecodedData[1608:1612]
                SA14W16 = reverse_and_concatenate(SA14W16_hex)
                
                SA14W17_hex = hexDecodedData[1612:1616]
                SA14W17 = reverse_and_concatenate(SA14W17_hex)
                
                SA14W18_hex = hexDecodedData[1616:1620]
                SA14W18 = reverse_and_concatenate(SA14W18_hex)
                
                SA14W19_hex = hexDecodedData[1620:1624]
                SA14W19 = reverse_and_concatenate(SA14W19_hex)
                
                SA14W20_hex = hexDecodedData[1624:1628]
                SA14W20 = reverse_and_concatenate(SA14W20_hex)
        
                SA14W21_hex = hexDecodedData[1628:1632]
                SA14W21 = reverse_and_concatenate(SA14W21_hex)
                
                SA14W22_hex = hexDecodedData[1632:1636]
                SA14W22 = reverse_and_concatenate(SA14W22_hex)
        
                SA14W23_hex = hexDecodedData[1636:1640]
                SA14W23 = reverse_and_concatenate(SA14W23_hex)
                
                SA14W24_hex = hexDecodedData[1640:1644]
                SA14W24 = reverse_and_concatenate(SA14W24_hex)
                
                SA14W25_hex = hexDecodedData[1644:1648]
                SA14W25 = reverse_and_concatenate(SA14W25_hex)
        
                SA14W26_hex = hexDecodedData[1648:1652]
                SA14W26 = reverse_and_concatenate(SA14W26_hex)
                
                SA14W27_hex = hexDecodedData[1652:1656]
                SA14W27 = reverse_and_concatenate(SA14W27_hex)
                
                SA14W28_hex = hexDecodedData[1656:1660]
                SA14W28 = reverse_and_concatenate(SA14W28_hex)
                
                SA14W29_hex = hexDecodedData[1660:1664]
                SA14W29 = reverse_and_concatenate(SA14W29_hex)
                
                SA14W30_hex = hexDecodedData[1664:1668]
                SA14W30 = reverse_and_concatenate(SA14W30_hex)
        
                SA14W31_hex = hexDecodedData[1668:1672]
                SA14W31 = reverse_and_concatenate(SA14W31_hex)
                
                SA14W32_hex = hexDecodedData[1672:1676]
                SA14W32 = reverse_and_concatenate(SA14W32_hex)
                
                #===============SA15 ============================#
                SA15W1_hex = hexDecodedData[1676:1680]
                SA15W1 = reverse_and_concatenate(SA15W1_hex)
        
                SA15W2_hex = hexDecodedData[1680:1684]
                SA15W2 = reverse_and_concatenate(SA15W2_hex)
                
                SA15W3_W4_hex = hexDecodedData[1684:1692]
                SA15W3_W4 = reverse_and_concatenate(SA15W3_W4_hex)
        
                SA15W5_W6_hex = hexDecodedData[1692:1700]
                SA15W5_W6 = reverse_and_concatenate(SA15W5_W6_hex)
                
                SA15W7_W8_hex = hexDecodedData[1700:1708]
                SA15W7_W8 = reverse_and_concatenate(SA15W7_W8_hex)
        
                SA15W9_W10_hex = hexDecodedData[1708:1716]
                SA15W9_W10 = reverse_and_concatenate(SA15W9_W10_hex)
                
                SA15W11_W12_hex = hexDecodedData[1716:1724]
                SA15W11_W12 = reverse_and_concatenate(SA15W11_W12_hex)
                
                SA15W13_W14_hex = hexDecodedData[1724:1732]
                SA15W13_W14 = reverse_and_concatenate(SA15W13_W14_hex)
        
                SA15W15_W16_hex = hexDecodedData[1732:1740]
                SA15W15_W16 = reverse_and_concatenate(SA15W15_W16_hex)
                
                SA15W17_W18_hex = hexDecodedData[1740:1748]
                SA15W17_W18 = reverse_and_concatenate(SA15W17_W18_hex)
        
                SA15W19_W20_hex = hexDecodedData[1748:1756]
                SA15W19_W20 = reverse_and_concatenate(SA15W19_W20_hex)
                
                SA15W21_W22_hex = hexDecodedData[1756:1764]
                SA15W21_W22 = reverse_and_concatenate(SA15W21_W22_hex)
                
                SA15W23_W24_hex = hexDecodedData[1764:1772]
                SA15W23_W24 = reverse_and_concatenate(SA15W23_W24_hex)
        
                SA15W25_W26_hex = hexDecodedData[1772:1780]
                SA15W25_W26 = reverse_and_concatenate(SA15W25_W26_hex)
                
                SA15W27_W28_hex = hexDecodedData[1780:1788]
                SA15W27_W28 = reverse_and_concatenate(SA15W27_W28_hex)
        
                SA15W29_W30_hex = hexDecodedData[1788:1796]
                SA15W29_W30 = reverse_and_concatenate(SA15W29_W30_hex)
                
                SA15W31_hex = hexDecodedData[1796:1800]
                SA15W31 = reverse_and_concatenate(SA15W31_hex)
                
                SA15W32_hex = hexDecodedData[1800:1804]
                SA15W32 = reverse_and_concatenate(SA15W32_hex)
                
                #===============SA16 ============================#
                SA16W1_hex = hexDecodedData[1804:1808]
                SA16W1 = reverse_and_concatenate(SA16W1_hex)
        
                SA16W2_hex = hexDecodedData[1808:1812]
                SA16W2 = reverse_and_concatenate(SA16W2_hex)
                
                SA16W3_W4_hex = hexDecodedData[1812:1820]
                SA16W3_W4 = reverse_and_concatenate(SA16W3_W4_hex)
        
                SA16W5_hex = hexDecodedData[1820:1824]
                SA16W5 = reverse_and_concatenate(SA16W5_hex)
                
                SA16W6_hex = hexDecodedData[1824:1828]
                SA16W6 = reverse_and_concatenate(SA16W6_hex)
                
                SA16W7_hex = hexDecodedData[1828:1832]
                SA16W7 = reverse_and_concatenate(SA16W7_hex)
                
                SA16W8_W9_hex = hexDecodedData[1832:1840]
                SA16W8_W9 = reverse_and_concatenate(SA16W8_W9_hex)
        
                SA16W10_W11_hex = hexDecodedData[1840:1848]
                SA16W10_W11 = reverse_and_concatenate(SA16W10_W11_hex)
                
                SA16W12_W13_hex = hexDecodedData[1848:1856]
                SA16W12_W13 = reverse_and_concatenate(SA16W12_W13_hex)
        
                SA16W14_W15_hex = hexDecodedData[1856:1864]
                SA16W14_W15 = reverse_and_concatenate(SA16W14_W15_hex)
                
                SA16W16_W17_hex = hexDecodedData[1864:1872]
                SA16W16_W17 = reverse_and_concatenate(SA16W16_W17_hex)
        
                SA16W18_W19_hex = hexDecodedData[1872:1880]
                SA16W18_W19 = reverse_and_concatenate(SA16W18_W19_hex)
                
                SA16W20_W21_hex = hexDecodedData[1880:1888]
                SA16W20_W21 = reverse_and_concatenate(SA16W20_W21_hex)
        
                SA16W22_W23_hex = hexDecodedData[1888:1896]
                SA16W22_W23 = reverse_and_concatenate(SA16W22_W23_hex)
                
                SA16W24_W29_hex = hexDecodedData[1896:1920]
                #SA16W24_W29 = reverse_and_concatenate(SA16W24_W29_hex)
        
                SA16W30_W31_hex = hexDecodedData[1920:1928]
                SA16W30_W31 = reverse_and_concatenate(SA16W30_W31_hex)
                
                SA16W32_hex = hexDecodedData[1928:1932]
                SA16W32 = reverse_and_concatenate(SA16W32_hex)
                
                 #===============SA17 ============================#
                SA17W1_hex = hexDecodedData[1932:1936]
                SA17W1 = reverse_and_concatenate(SA17W1_hex)
        
                SA17W2_hex = hexDecodedData[1936:1940]
                SA17W2 = reverse_and_concatenate(SA17W2_hex)
                
                SA17W3_hex = hexDecodedData[1940:1944]
                SA17W3 = reverse_and_concatenate(SA17W3_hex)
        
                SA17W4_hex = hexDecodedData[1944:1948]
                SA17W4 = reverse_and_concatenate(SA17W4_hex)
                
                SA17W5_hex = hexDecodedData[1948:1952]
                SA17W5 = reverse_and_concatenate(SA17W5_hex)
        
                SA17W6_hex = hexDecodedData[1952:1956]
                SA17W6 = reverse_and_concatenate(SA17W6_hex)
                
                SA17W7_hex = hexDecodedData[1956:1960]
                SA17W7 = reverse_and_concatenate(SA17W7_hex)
                
                SA17W8_hex = hexDecodedData[1960:1964]
                SA17W8 = reverse_and_concatenate(SA17W8_hex)
        
                SA17W9_hex = hexDecodedData[1964:1968]
                SA17W9 = reverse_and_concatenate(SA17W9_hex)
                
                SA17W10_hex = hexDecodedData[1968:1972]
                SA17W10 = reverse_and_concatenate(SA17W10_hex)
        
                SA17W11_hex = hexDecodedData[1972:1976]
                SA17W11 = reverse_and_concatenate(SA17W11_hex)
                
                SA17W12_hex = hexDecodedData[1976:1980]
                SA17W12 = reverse_and_concatenate(SA17W12_hex)
        
                SA17W13_hex = hexDecodedData[1980:1984]
                SA17W13 = reverse_and_concatenate(SA17W13_hex)
                
                SA17W14_hex = hexDecodedData[1984:1988]
                SA17W14 = reverse_and_concatenate(SA17W14_hex)
                
                SA17W15_hex = hexDecodedData[1988:1992]
                SA17W15 = reverse_and_concatenate(SA17W15_hex)
        
                SA17W16_hex = hexDecodedData[1992:1996]
                SA17W16 = reverse_and_concatenate(SA17W16_hex)
                
                SA17W17_hex = hexDecodedData[1996:2000]
                SA17W17 = reverse_and_concatenate(SA17W17_hex)
                
                SA17W18_hex = hexDecodedData[2000:2004]
                SA17W18 = reverse_and_concatenate(SA17W18_hex)
                
                SA17W19_hex = hexDecodedData[2004:2008]
                SA17W19 = reverse_and_concatenate(SA17W19_hex)
                
                SA17W20_hex = hexDecodedData[2008:2012]
                SA17W20 = reverse_and_concatenate(SA17W20_hex)
        
                SA17W21_hex = hexDecodedData[2012:2016]
                SA17W21 = reverse_and_concatenate(SA17W21_hex)
                
                SA17W22_hex = hexDecodedData[2016:2020]
                SA17W22 = reverse_and_concatenate(SA17W22_hex)
        
                SA17W23_hex = hexDecodedData[2020:2024]
                SA17W23 = reverse_and_concatenate(SA17W23_hex)
                
                SA17W24_hex = hexDecodedData[2024:2028]
                SA17W24 = reverse_and_concatenate(SA17W24_hex)
                
                SA17W25_hex = hexDecodedData[2028:2032]
                SA17W25 = reverse_and_concatenate(SA17W25_hex)
        
                SA17W26_w30_hex = hexDecodedData[2032:2052]
                #SA17W26_W30 = reverse_and_concatenate(SA17W26_w30_hex)
        
                SA17W31_hex = hexDecodedData[2052:2056]
                SA17W31 = reverse_and_concatenate(SA17W31_hex)
                
                SA17W32_hex = hexDecodedData[2056:2060]
                SA17W32 = reverse_and_concatenate(SA17W32_hex)
                
                #===============SA17 ============================#
                SA18W1_hex = hexDecodedData[2060:2064]
                SA18W1 = reverse_and_concatenate(SA18W1_hex)
        
                SA18W2_hex = hexDecodedData[2064:2068]
                SA18W2 = reverse_and_concatenate(SA18W2_hex)
                
                SA18W3_hex = hexDecodedData[2068:2072]
                SA18W3 = reverse_and_concatenate(SA18W3_hex)
        
                SA18W4_hex = hexDecodedData[2072:2076]
                SA18W4 = reverse_and_concatenate(SA18W4_hex)
                
                SA18W5_hex = hexDecodedData[2076:2080]
                SA18W5 = reverse_and_concatenate(SA18W5_hex)
        
                SA18W6_hex = hexDecodedData[2080:2084]
                SA18W6 = reverse_and_concatenate(SA18W6_hex)
                
                SA18W7_hex = hexDecodedData[2084:2088]
                SA18W7 = reverse_and_concatenate(SA18W7_hex)
                
                SA18W8_hex = hexDecodedData[2088:2092]
                SA18W8 = reverse_and_concatenate(SA18W8_hex)
        
                SA18W9_hex = hexDecodedData[2092:2096]
                SA18W9 = reverse_and_concatenate(SA18W9_hex)
                
                SA18W10_hex = hexDecodedData[2096:2100]
                SA18W10 = reverse_and_concatenate(SA18W10_hex)
        
                SA18W11_hex = hexDecodedData[2100:2104]
                SA18W11 = reverse_and_concatenate(SA18W11_hex)
                
                SA18W12_hex = hexDecodedData[2104:2108]
                SA18W12 = reverse_and_concatenate(SA18W12_hex)
        
                SA18W13_hex = hexDecodedData[2108:2112]
                SA18W13 = reverse_and_concatenate(SA18W13_hex)
                
                SA18W14_hex = hexDecodedData[2112:2116]
                SA18W14 = reverse_and_concatenate(SA18W14_hex)
                
                SA18W15_hex = hexDecodedData[2116:2120]
                SA18W15 = reverse_and_concatenate(SA18W15_hex)
        
                SA18W16_hex = hexDecodedData[2120:2124]
                SA18W16 = reverse_and_concatenate(SA18W16_hex)
                
                SA18W17_hex = hexDecodedData[2124:2128]
                SA18W17 = reverse_and_concatenate(SA18W17_hex)
                
                SA18W18_hex = hexDecodedData[2128:2132]
                SA18W18 = reverse_and_concatenate(SA18W18_hex)
                
                SA18W19_hex = hexDecodedData[2132:2136]
                SA18W19 = reverse_and_concatenate(SA18W19_hex)
                
                SA18W20_hex = hexDecodedData[2136:2140]
                SA18W20 = reverse_and_concatenate(SA18W20_hex)
        
                SA18W21_hex = hexDecodedData[2140:2144]
                SA18W21 = reverse_and_concatenate(SA18W21_hex)
                
                SA18W22_hex = hexDecodedData[2144:2148]
                SA18W22 = reverse_and_concatenate(SA18W22_hex)
        
                SA18W23_hex = hexDecodedData[2148:2152]
                SA18W23 = reverse_and_concatenate(SA18W23_hex)
                
                SA18W24_hex = hexDecodedData[2152:2156]
                SA18W24 = reverse_and_concatenate(SA18W24_hex)
                
                SA18W25_hex = hexDecodedData[2156:2160]
                SA18W25 = reverse_and_concatenate(SA18W25_hex)
        
                SA18W26_w30_hex = hexDecodedData[2160:2180]
                #SA18W26_W30 = reverse_and_concatenate(SA18W26_w30_hex)
        
                SA18W31_hex = hexDecodedData[2180:2184]
                SA18W31 = reverse_and_concatenate(SA18W31_hex)
                
                SA18W32_hex = hexDecodedData[2184:2188]
                SA18W32 = reverse_and_concatenate(SA18W32_hex)
                
            
                
                #===============SA19 ============================#
                SA19W1_hex = hexDecodedData[2188:2192]
                SA19W1 = reverse_and_concatenate(SA19W1_hex)
        
                SA19W2_hex = hexDecodedData[2192:2196]
                SA19W2 = reverse_and_concatenate(SA19W2_hex)
                
                SA19W3_hex = hexDecodedData[2196:2200]
                SA19W3 = reverse_and_concatenate(SA19W3_hex)
        
                SA19W4_hex = hexDecodedData[2200:2204]
                SA19W4 = reverse_and_concatenate(SA19W4_hex)
                
                SA19W5_hex = hexDecodedData[2204:2208]
                SA19W5 = reverse_and_concatenate(SA19W5_hex)
        
                SA19W6_hex = hexDecodedData[2208:2212]
                SA19W6 = reverse_and_concatenate(SA19W6_hex)
                
                SA19W7_hex = hexDecodedData[2212:2216]
                SA19W7 = reverse_and_concatenate(SA19W7_hex)
                
                SA19W8_hex = hexDecodedData[2216:2220]
                SA19W8 = reverse_and_concatenate(SA19W8_hex)
        
                SA19W9_hex = hexDecodedData[2220:2224]
                SA19W9 = reverse_and_concatenate(SA19W9_hex)
                
                SA19W10_hex = hexDecodedData[2224:2228]
                SA19W10 = reverse_and_concatenate(SA19W10_hex)
        
                SA19W11_hex = hexDecodedData[2228:2232]
                SA19W11 = reverse_and_concatenate(SA19W11_hex)
                
                SA19W12_hex = hexDecodedData[2232:2236]
                SA19W12 = reverse_and_concatenate(SA19W12_hex)
        
                SA19W13_hex = hexDecodedData[2236:2240]
                SA19W13 = reverse_and_concatenate(SA19W13_hex)
                
                SA19W14_hex = hexDecodedData[2240:2244]
                SA19W14 = reverse_and_concatenate(SA19W14_hex)
                
                SA19W15_hex = hexDecodedData[2244:2248]
                SA19W15 = reverse_and_concatenate(SA19W15_hex)
        
                SA19W16_hex = hexDecodedData[2248:2252]
                SA19W16 = reverse_and_concatenate(SA19W16_hex)
                
                SA19W17_hex = hexDecodedData[2252:2256]
                SA19W17 = reverse_and_concatenate(SA19W17_hex)
                
                SA19W18_hex = hexDecodedData[2256:2260]
                SA19W18 = reverse_and_concatenate(SA19W18_hex)
                
                SA19W19_hex = hexDecodedData[2260:2264]
                SA19W19 = reverse_and_concatenate(SA19W19_hex)
                
                SA19W20_hex = hexDecodedData[2264:2268]
                SA19W20 = reverse_and_concatenate(SA19W20_hex)
        
                SA19W21_hex = hexDecodedData[2268:2272]
                SA19W21 = reverse_and_concatenate(SA19W21_hex)
                
                SA19W22_hex = hexDecodedData[2272:2276]
                SA19W22 = reverse_and_concatenate(SA19W22_hex)
        
                SA19W23_hex = hexDecodedData[2276:2280]
                SA19W23 = reverse_and_concatenate(SA19W23_hex)
                
                SA19W24_hex = hexDecodedData[2280:2284]
                SA19W24 = reverse_and_concatenate(SA19W24_hex)
                
                SA19W25_hex = hexDecodedData[2284:2288]
                SA19W25 = reverse_and_concatenate(SA19W25_hex)
        
                SA19W26_hex = hexDecodedData[2288:2292]
                SA19W26 = reverse_and_concatenate(SA19W26_hex)
                
                SA19W27_hex = hexDecodedData[2292:2296]
                SA19W27 = reverse_and_concatenate(SA19W27_hex)
                
                SA19W28_hex = hexDecodedData[2296:2300]
                SA19W28 = reverse_and_concatenate(SA19W28_hex)
                
                SA19W29_hex = hexDecodedData[2300:2304]
                SA19W29 = reverse_and_concatenate(SA19W29_hex)
                
                SA19W30_hex = hexDecodedData[2304:2308]
                SA19W30 = reverse_and_concatenate(SA19W30_hex)
        
                SA19W31_hex = hexDecodedData[2308:2312]
                SA19W31 = reverse_and_concatenate(SA19W31_hex)
                
                SA19W32_hex = hexDecodedData[2312:2316]
                SA19W32 = reverse_and_concatenate(SA19W32_hex)
                
                #===============SA20 ============================#
                SA20W1_hex = hexDecodedData[2316:2320]
                SA20W1 = reverse_and_concatenate(SA20W1_hex)
        
                SA20W2_hex = hexDecodedData[2320:2324]
                SA20W2 = reverse_and_concatenate(SA20W2_hex)
                
                SA20W3_hex = hexDecodedData[2324:2328]
                SA20W3 = reverse_and_concatenate(SA20W3_hex)
        
                SA20W4_hex = hexDecodedData[2328:2332]
                SA20W4 = reverse_and_concatenate(SA20W4_hex)
                
                SA20W5_hex = hexDecodedData[2332:2336]
                SA20W5 = reverse_and_concatenate(SA20W5_hex)
        
                SA20W6_hex = hexDecodedData[2336:2340]
                SA20W6 = reverse_and_concatenate(SA20W6_hex)
                
                SA20W7_hex = hexDecodedData[2340:2344]
                SA20W7 = reverse_and_concatenate(SA20W7_hex)
                
                SA20W8_hex = hexDecodedData[2344:2348]
                SA20W8 = reverse_and_concatenate(SA20W8_hex)
        
                SA20W9_hex = hexDecodedData[2348:2352]
                SA20W9 = reverse_and_concatenate(SA20W9_hex)
                
                SA20W10_hex = hexDecodedData[2352:2356]
                SA20W10 = reverse_and_concatenate(SA20W10_hex)
        
                SA20W11_hex = hexDecodedData[2356:2360]
                SA20W11 = reverse_and_concatenate(SA20W11_hex)
                
                SA20W12_hex = hexDecodedData[2360:2364]
                SA20W12 = reverse_and_concatenate(SA20W12_hex)
        
                SA20W13_hex = hexDecodedData[2364:2368]
                SA20W13 = reverse_and_concatenate(SA20W13_hex)
                
                SA20W14_hex = hexDecodedData[2368:2372]
                SA20W14 = reverse_and_concatenate(SA20W14_hex)
                
                SA20W15_hex = hexDecodedData[2372:2376]
                SA20W15 = reverse_and_concatenate(SA20W15_hex)
        
                SA20W16_hex = hexDecodedData[2376:2380]
                SA20W16 = reverse_and_concatenate(SA20W16_hex)
                
                SA20W17_hex = hexDecodedData[2380:2384]
                SA20W17 = reverse_and_concatenate(SA20W17_hex)
                
                SA20W18_hex = hexDecodedData[2384:2388]
                SA20W18 = reverse_and_concatenate(SA20W18_hex)
                
                SA20W19_hex = hexDecodedData[2388:2392]
                SA20W19 = reverse_and_concatenate(SA20W19_hex)
                
                SA20W20_hex = hexDecodedData[2392:2396]
                SA20W20 = reverse_and_concatenate(SA20W20_hex)
        
                SA20W21_hex = hexDecodedData[2396:2400]
                SA20W21 = reverse_and_concatenate(SA20W21_hex)
                
                SA20W22_hex = hexDecodedData[2400:2404]
                SA20W22 = reverse_and_concatenate(SA20W22_hex)
        
                SA20W23_hex = hexDecodedData[2404:2408]
                SA20W23 = reverse_and_concatenate(SA20W23_hex)
                
                SA20W24_hex = hexDecodedData[2408:2412]
                SA20W24 = reverse_and_concatenate(SA20W24_hex)
                
                SA20W25_hex = hexDecodedData[2412:2416]
                SA20W25 = reverse_and_concatenate(SA20W25_hex)
        
                SA20W26_hex = hexDecodedData[2416:2420]
                SA20W26 = reverse_and_concatenate(SA20W26_hex)
                
                SA20W27_hex = hexDecodedData[2420:2424]
                SA20W27 = reverse_and_concatenate(SA20W27_hex)
                
                SA20W28_hex = hexDecodedData[2424:2428]
                SA20W28 = reverse_and_concatenate(SA20W28_hex)
                
                SA20W29_hex = hexDecodedData[2428:2432]
                SA20W29 = reverse_and_concatenate(SA20W29_hex)
                
                SA20W30_hex = hexDecodedData[2432:2436]
                SA20W30 = reverse_and_concatenate(SA20W30_hex)
        
                SA20W31_hex = hexDecodedData[2436:2440]
                SA20W31 = reverse_and_concatenate(SA20W31_hex)
                
                SA20W32_hex = hexDecodedData[2440:2444]
                SA20W32 = reverse_and_concatenate(SA20W32_hex)
                
                 #===============SA21 ============================#
                SA21W1_hex = hexDecodedData[2444:2448]
                SA21W1 = reverse_and_concatenate(SA21W1_hex)
        
                SA21W2_hex = hexDecodedData[2448:2452]
                SA21W2 = reverse_and_concatenate(SA21W2_hex)
                
                SA21W3_hex = hexDecodedData[2452:2456]
                SA21W3 = reverse_and_concatenate(SA21W3_hex)
        
                SA21W4_hex = hexDecodedData[2456:2460]
                SA21W4 = reverse_and_concatenate(SA21W4_hex)
                
                SA21W5_hex = hexDecodedData[2460:2464]
                SA21W5 = reverse_and_concatenate(SA21W5_hex)
        
                SA21W6_hex = hexDecodedData[2464:2468]
                SA21W6 = reverse_and_concatenate(SA21W6_hex)
                
                SA21W7_hex = hexDecodedData[2468:2472]
                SA21W7 = reverse_and_concatenate(SA21W7_hex)
                
                SA21W8_hex = hexDecodedData[2472:2476]
                SA21W8 = reverse_and_concatenate(SA21W8_hex)
        
                SA21W9_hex = hexDecodedData[2476:2480]
                SA21W9 = reverse_and_concatenate(SA21W9_hex)
                
                SA21W10_hex = hexDecodedData[2480:2484]
                SA21W10 = reverse_and_concatenate(SA21W10_hex)
        
                SA21W11_hex = hexDecodedData[2484:2488]
                SA21W11 = reverse_and_concatenate(SA21W11_hex)
                
                SA21W12_hex = hexDecodedData[2488:2492]
                SA21W12 = reverse_and_concatenate(SA21W12_hex)
        
                SA21W13_hex = hexDecodedData[2492:2496]
                SA21W13 = reverse_and_concatenate(SA21W13_hex)
                
                SA21W14_hex = hexDecodedData[2496:2500]
                SA21W14 = reverse_and_concatenate(SA21W14_hex)
                
                SA21W15_hex = hexDecodedData[2500:2504]
                SA21W15 = reverse_and_concatenate(SA21W15_hex)
        
                SA21W16_hex = hexDecodedData[2504:2508]
                SA21W16 = reverse_and_concatenate(SA21W16_hex)
                
                SA21W17_hex = hexDecodedData[2508:2512]
                SA21W17 = reverse_and_concatenate(SA21W17_hex)
                
                SA21W18_hex = hexDecodedData[2512:2516]
                SA21W18 = reverse_and_concatenate(SA21W18_hex)
                
                SA21W19_hex = hexDecodedData[2516:2520]
                SA21W19 = reverse_and_concatenate(SA21W19_hex)
                
                SA21W20_hex = hexDecodedData[2520:2524]
                SA21W20 = reverse_and_concatenate(SA21W20_hex)
        
                SA21W21_hex = hexDecodedData[2524:2528]
                SA21W21 = reverse_and_concatenate(SA21W21_hex)
                
                SA21W22_hex = hexDecodedData[2528:2532]
                SA21W22 = reverse_and_concatenate(SA21W22_hex)
        
                SA21W23_hex = hexDecodedData[2532:2536]
                SA21W23 = reverse_and_concatenate(SA21W23_hex)
                
                SA21W24_hex = hexDecodedData[2536:2540]
                SA21W24 = reverse_and_concatenate(SA21W24_hex)
                
                SA21W25_hex = hexDecodedData[2540:2544]
                SA21W25 = reverse_and_concatenate(SA21W25_hex)
        
                SA21W26_hex = hexDecodedData[2544:2548]
                SA21W26 = reverse_and_concatenate(SA21W26_hex)
                
                SA21W27_hex = hexDecodedData[2548:2552]
                SA21W27 = reverse_and_concatenate(SA21W27_hex)
                
                SA21W28_hex = hexDecodedData[2552:2556]
                SA21W28 = reverse_and_concatenate(SA21W28_hex)
                
                SA21W29_hex = hexDecodedData[2556:2560]
                SA21W29 = reverse_and_concatenate(SA21W29_hex)
                
                SA21W30_hex = hexDecodedData[2560:2564]
                SA21W30 = reverse_and_concatenate(SA21W30_hex)
        
                SA21W31_hex = hexDecodedData[2564:2568]
                SA21W31 = reverse_and_concatenate(SA21W31_hex)
                
                SA21W32_hex = hexDecodedData[2568:2572]
                SA21W32 = reverse_and_concatenate(SA21W32_hex)
                
                #===============SA22 ============================#
                SA22W1_hex = hexDecodedData[2572:2576]
                SA22W1 = reverse_and_concatenate(SA22W1_hex)
        
                SA22W2_hex = hexDecodedData[2576:2580]
                SA22W2 = reverse_and_concatenate(SA22W2_hex)
                
                SA22W3_hex = hexDecodedData[2580:2584]
                SA22W3 = reverse_and_concatenate(SA22W3_hex)
        
                SA22W4_hex = hexDecodedData[2584:2588]
                SA22W4 = reverse_and_concatenate(SA22W4_hex)
                
                SA22W5_hex = hexDecodedData[2588:2592]
                SA22W5 = reverse_and_concatenate(SA22W5_hex)
        
                SA22W6_hex = hexDecodedData[2592:2596]
                SA22W6 = reverse_and_concatenate(SA22W6_hex)
                
                SA22W7_hex = hexDecodedData[2596:2600]
                SA22W7 = reverse_and_concatenate(SA22W7_hex)
                
                SA22W8_hex = hexDecodedData[2600:2604]
                SA22W8 = reverse_and_concatenate(SA22W8_hex)
        
                SA22W9_hex = hexDecodedData[2604:2608]
                SA22W9 = reverse_and_concatenate(SA22W9_hex)
                
                SA22W10_hex = hexDecodedData[2608:2612]
                SA22W10 = reverse_and_concatenate(SA22W10_hex)
        
                SA22W11_hex = hexDecodedData[2612:2616]
                SA22W11 = reverse_and_concatenate(SA22W11_hex)
                
                SA22W12_hex = hexDecodedData[2616:2620]
                SA22W12 = reverse_and_concatenate(SA22W12_hex)
        
                SA22W13_hex = hexDecodedData[2620:2624]
                SA22W13 = reverse_and_concatenate(SA22W13_hex)
                
                SA22W14_hex = hexDecodedData[2624:2628]
                SA22W14 = reverse_and_concatenate(SA22W14_hex)
                
                SA22W15_hex = hexDecodedData[2628:2632]
                SA22W15 = reverse_and_concatenate(SA22W15_hex)
        
                SA22W16_hex = hexDecodedData[2632:2636]
                SA22W16 = reverse_and_concatenate(SA22W16_hex)
                
                SA22W17_hex = hexDecodedData[2636:2640]
                SA22W17 = reverse_and_concatenate(SA22W17_hex)
                
                SA22W18_hex = hexDecodedData[2640:2644]
                SA22W18 = reverse_and_concatenate(SA22W18_hex)
                
                SA22W19_hex = hexDecodedData[2644:2648]
                SA22W19 = reverse_and_concatenate(SA22W19_hex)
                
                SA22W20_hex = hexDecodedData[2648:2652]
                SA22W20 = reverse_and_concatenate(SA22W20_hex)
        
                SA22W21_hex = hexDecodedData[2652:2656]
                SA22W21 = reverse_and_concatenate(SA22W21_hex)
                
                SA22W22_hex = hexDecodedData[2656:2660]
                SA22W22 = reverse_and_concatenate(SA22W22_hex)
        
                SA22W23_hex = hexDecodedData[2660:2664]
                SA22W23 = reverse_and_concatenate(SA22W23_hex)
                
                SA22W24_hex = hexDecodedData[2664:2668]
                SA22W24 = reverse_and_concatenate(SA22W24_hex)
                
                SA22W25_hex = hexDecodedData[2668:2672]
                SA22W25 = reverse_and_concatenate(SA22W25_hex)
        
                SA22W26_hex = hexDecodedData[2672:2676]
                SA22W26 = reverse_and_concatenate(SA22W26_hex)
                
                SA22W27_hex = hexDecodedData[2676:2680]
                SA22W27 = reverse_and_concatenate(SA22W27_hex)
                
                SA22W28_hex = hexDecodedData[2680:2684]
                SA22W28 = reverse_and_concatenate(SA22W28_hex)
                
                SA22W29_hex = hexDecodedData[2684:2688]
                SA22W29 = reverse_and_concatenate(SA22W29_hex)
                
                SA22W30_hex = hexDecodedData[2688:2692]
                SA22W30 = reverse_and_concatenate(SA22W30_hex)
        
                SA22W31_hex = hexDecodedData[2692:2696]
                SA22W31 = reverse_and_concatenate(SA22W31_hex)
                
                SA22W32_hex = hexDecodedData[2696:2700]
                SA22W32 = reverse_and_concatenate(SA22W32_hex)
                
                #===============SA23 ============================#
                SA23W1_hex = hexDecodedData[2700:2704]
                SA23W1 = reverse_and_concatenate(SA23W1_hex)
        
                SA23W2_hex = hexDecodedData[2704:2708]
                SA23W2 = reverse_and_concatenate(SA23W2_hex)
                
                SA23W3_hex = hexDecodedData[2708:2712]
                SA23W3 = reverse_and_concatenate(SA23W3_hex)
        
                SA23W4_hex = hexDecodedData[2712:2716]
                SA23W4 = reverse_and_concatenate(SA23W4_hex)
                
                SA23W5_hex = hexDecodedData[2716:2720]
                SA23W5 = reverse_and_concatenate(SA23W5_hex)
        
                SA23W6_hex = hexDecodedData[2720:2724]
                SA23W6 = reverse_and_concatenate(SA23W6_hex)
                
                SA23W7_hex = hexDecodedData[2724:2728]
                SA23W7 = reverse_and_concatenate(SA23W7_hex)
                
                SA23W8_hex = hexDecodedData[2728:2732]
                SA23W8 = reverse_and_concatenate(SA23W8_hex)
        
                SA23W9_hex = hexDecodedData[2732:2736]
                SA23W9 = reverse_and_concatenate(SA23W9_hex)
                
                SA23W10_hex = hexDecodedData[2736:2740]
                SA23W10 = reverse_and_concatenate(SA23W10_hex)
        
                SA23W11_hex = hexDecodedData[2740:2744]
                SA23W11 = reverse_and_concatenate(SA23W11_hex)
                
                SA23W12_hex = hexDecodedData[2744:2748]
                SA23W12 = reverse_and_concatenate(SA23W12_hex)
        
                SA23W13_hex = hexDecodedData[2748:2752]
                SA23W13 = reverse_and_concatenate(SA23W13_hex)
                
                SA23W14_hex = hexDecodedData[2752:2756]
                SA23W14 = reverse_and_concatenate(SA23W14_hex)
                
                SA23W15_hex = hexDecodedData[2756:2760]
                SA23W15 = reverse_and_concatenate(SA23W15_hex)
        
                SA23W16_hex = hexDecodedData[2760:2764]
                SA23W16 = reverse_and_concatenate(SA23W16_hex)
                
                SA23W17_hex = hexDecodedData[2764:2768]
                SA23W17 = reverse_and_concatenate(SA23W17_hex)
                
                SA23W18_hex = hexDecodedData[2768:2772]
                SA23W18 = reverse_and_concatenate(SA23W18_hex)
                
                SA23W19_hex = hexDecodedData[2772:2776]
                SA23W19 = reverse_and_concatenate(SA23W19_hex)
                
                SA23W20_hex = hexDecodedData[2776:2780]
                SA23W20 = reverse_and_concatenate(SA23W20_hex)
        
                SA23W21_hex = hexDecodedData[2780:2784]
                SA23W21 = reverse_and_concatenate(SA23W21_hex)
                
                SA23W22_hex = hexDecodedData[2784:2788]
                SA23W22 = reverse_and_concatenate(SA23W22_hex)
        
                SA23W23_hex = hexDecodedData[2788:2792]
                SA23W23 = reverse_and_concatenate(SA23W23_hex)
                
                SA23W24_hex = hexDecodedData[2792:2796]
                SA23W24 = reverse_and_concatenate(SA23W24_hex)
                
                SA23W25_hex = hexDecodedData[2796:2800]
                SA23W25 = reverse_and_concatenate(SA23W25_hex)
        
                SA23W26_hex = hexDecodedData[2800:2804]
                SA23W26 = reverse_and_concatenate(SA23W26_hex)
                
                SA23W27_hex = hexDecodedData[2804:2808]
                SA23W27 = reverse_and_concatenate(SA23W27_hex)
                
                SA23W28_hex = hexDecodedData[2808:2812]
                SA23W28 = reverse_and_concatenate(SA23W28_hex)
                
                SA23W29_hex = hexDecodedData[2812:2816]
                SA23W29 = reverse_and_concatenate(SA23W29_hex)
                
                SA23W30_hex = hexDecodedData[2816:2820]
                SA23W30 = reverse_and_concatenate(SA23W30_hex)
        
                SA23W31_hex = hexDecodedData[2820:2824]
                SA23W31 = reverse_and_concatenate(SA23W31_hex)
                
                SA23W32_hex = hexDecodedData[2824:2828]
                SA23W32 = reverse_and_concatenate(SA23W32_hex)
                
                #===============SA24 ============================#
                SA24W1_hex = hexDecodedData[2828:2832]
                SA24W1 = reverse_and_concatenate(SA24W1_hex)
        
                SA24W2_hex = hexDecodedData[2832:2836]
                SA24W2 = reverse_and_concatenate(SA24W2_hex)
                
                SA24W3_hex = hexDecodedData[2836:2840]
                SA24W3 = reverse_and_concatenate(SA24W3_hex)
        
                SA24W4_hex = hexDecodedData[2840:2844]
                SA24W4 = reverse_and_concatenate(SA24W4_hex)
                
                SA24W5_hex = hexDecodedData[2844:2848]
                SA24W5 = reverse_and_concatenate(SA24W5_hex)
        
                SA24W6_hex = hexDecodedData[2848:2852]
                SA24W6 = reverse_and_concatenate(SA24W6_hex)
                
                SA24W7_hex = hexDecodedData[2852:2856]
                SA24W7 = reverse_and_concatenate(SA24W7_hex)
                
                SA24W8_hex = hexDecodedData[2856:2860]
                SA24W8 = reverse_and_concatenate(SA24W8_hex)
        
                SA24W9_hex = hexDecodedData[2860:2864]
                SA24W9 = reverse_and_concatenate(SA24W9_hex)
                
                SA24W10_hex = hexDecodedData[2864:2868]
                SA24W10 = reverse_and_concatenate(SA24W10_hex)
        
                SA24W11_hex = hexDecodedData[2868:2872]
                SA24W11 = reverse_and_concatenate(SA24W11_hex)
                
                SA24W12_hex = hexDecodedData[2872:2876]
                SA24W12 = reverse_and_concatenate(SA24W12_hex)
        
                SA24W13_hex = hexDecodedData[2876:2880]
                SA24W13 = reverse_and_concatenate(SA24W13_hex)
                
                SA24W14_hex = hexDecodedData[2880:2884]
                SA24W14 = reverse_and_concatenate(SA24W14_hex)
                
                SA24W15_hex = hexDecodedData[2884:2888]
                SA24W15 = reverse_and_concatenate(SA24W15_hex)
        
                SA24W16_hex = hexDecodedData[2888:2892]
                SA24W16 = reverse_and_concatenate(SA24W16_hex)
                
                SA24W17_hex = hexDecodedData[2892:2896]
                SA24W17 = reverse_and_concatenate(SA24W17_hex)
                
                SA24W18_hex = hexDecodedData[2896:2900]
                SA24W18 = reverse_and_concatenate(SA24W18_hex)
                
                SA24W19_hex = hexDecodedData[2900:2904]
                SA24W19 = reverse_and_concatenate(SA24W19_hex)
                
                SA24W20_hex = hexDecodedData[2904:2908]
                SA24W20 = reverse_and_concatenate(SA24W20_hex)
        
                SA24W21_hex = hexDecodedData[2908:2912]
                SA24W21 = reverse_and_concatenate(SA24W21_hex)
                
                SA24W22_hex = hexDecodedData[2912:2916]
                SA24W22 = reverse_and_concatenate(SA24W22_hex)
        
                SA24W23_hex = hexDecodedData[2916:2920]
                SA24W23 = reverse_and_concatenate(SA24W23_hex)
                
                SA24W24_hex = hexDecodedData[2920:2924]
                SA24W24 = reverse_and_concatenate(SA24W24_hex)
                
                SA24W25_hex = hexDecodedData[2924:2928]
                SA24W25 = reverse_and_concatenate(SA24W25_hex)
        
                SA24W26_hex = hexDecodedData[2928:2932]
                SA24W26 = reverse_and_concatenate(SA24W26_hex)
                
                SA24W27_hex = hexDecodedData[2932:2936]
                SA24W27 = reverse_and_concatenate(SA24W27_hex)
                
                SA24W28_hex = hexDecodedData[2936:2940]
                SA24W28 = reverse_and_concatenate(SA24W28_hex)
                
                SA24W29_hex = hexDecodedData[2940:2944]
                SA24W29 = reverse_and_concatenate(SA24W29_hex)
                
                SA24W30_hex = hexDecodedData[2944:2948]
                SA24W30 = reverse_and_concatenate(SA24W30_hex)
        
                SA24W31_hex = hexDecodedData[2948:2952]
                SA24W31 = reverse_and_concatenate(SA24W31_hex)
                
                SA24W32_hex = hexDecodedData[2952:2956]
                SA24W32 = reverse_and_concatenate(SA24W32_hex)
                
               #===============SA25 ============================#
                SA25W1_hex = hexDecodedData[2956:2960]
                SA25W1 = reverse_and_concatenate(SA25W1_hex)
        
                SA25W2_hex = hexDecodedData[2960:2964]
                SA25W2 = reverse_and_concatenate(SA25W2_hex)
                
                SA25W3_hex = hexDecodedData[2964:2968]
                SA25W3 = reverse_and_concatenate(SA25W3_hex)
        
                SA25W4_hex = hexDecodedData[2968:2972]
                SA25W4 = reverse_and_concatenate(SA25W4_hex)
                
                SA25W5_hex = hexDecodedData[2972:2976]
                SA25W5 = reverse_and_concatenate(SA25W5_hex)
        
                SA25W6_hex = hexDecodedData[2976:2980]
                SA25W6 = reverse_and_concatenate(SA25W6_hex)
                
                SA25W7_hex = hexDecodedData[2980:2984]
                SA25W7 = reverse_and_concatenate(SA25W7_hex)
                
                SA25W8_hex = hexDecodedData[2984:2988]
                SA25W8 = reverse_and_concatenate(SA25W8_hex)
        
                SA25W9_hex = hexDecodedData[2988:2992]
                SA25W9 = reverse_and_concatenate(SA25W9_hex)
                
                SA25W10_hex = hexDecodedData[2992:2996]
                SA25W10 = reverse_and_concatenate(SA25W10_hex)
        
                SA25W11_hex = hexDecodedData[2996:3000]
                SA25W11 = reverse_and_concatenate(SA25W11_hex)
                
                SA25W12_hex = hexDecodedData[3000:3004]
                SA25W12 = reverse_and_concatenate(SA25W12_hex)
        
                SA25W13_hex = hexDecodedData[3004:3008]
                SA25W13 = reverse_and_concatenate(SA25W13_hex)
                
                SA25W14_hex = hexDecodedData[3008:3012]
                SA25W14 = reverse_and_concatenate(SA25W14_hex)
                
                SA25W15_hex = hexDecodedData[3012:3016]
                SA25W15 = reverse_and_concatenate(SA25W15_hex)
        
                SA25W16_hex = hexDecodedData[3016:3020]
                SA25W16 = reverse_and_concatenate(SA25W16_hex)
                
                SA25W17_hex = hexDecodedData[3020:3024]
                SA25W17 = reverse_and_concatenate(SA25W17_hex)
                
                SA25W18_hex = hexDecodedData[3024:3028]
                SA25W18 = reverse_and_concatenate(SA25W18_hex)
                
                SA25W19_hex = hexDecodedData[3028:3032]
                SA25W19 = reverse_and_concatenate(SA25W19_hex)
                
                SA25W20_hex = hexDecodedData[3032:3036]
                SA25W20 = reverse_and_concatenate(SA25W20_hex)
        
                SA25W21_hex = hexDecodedData[3036:3040]
                SA25W21 = reverse_and_concatenate(SA25W21_hex)
                
                SA25W22_hex = hexDecodedData[3040:3044]
                SA25W22 = reverse_and_concatenate(SA25W22_hex)
        
                SA25W23_hex = hexDecodedData[3044:3048]
                SA25W23 = reverse_and_concatenate(SA25W23_hex)
                
                SA25W24_hex = hexDecodedData[3048:3052]
                SA25W24 = reverse_and_concatenate(SA25W24_hex)
                
                SA25W25_hex = hexDecodedData[3052:3056]
                SA25W25 = reverse_and_concatenate(SA25W25_hex)
        
                SA25W26_hex = hexDecodedData[3056:3060]
                SA25W26 = reverse_and_concatenate(SA25W26_hex)
                
                SA25W27_hex = hexDecodedData[3060:3064]
                SA25W27 = reverse_and_concatenate(SA25W27_hex)
                
                SA25W28_hex = hexDecodedData[3064:3068]
                SA25W28 = reverse_and_concatenate(SA25W28_hex)
                
                SA25W29_hex = hexDecodedData[3068:3072]
                SA25W29 = reverse_and_concatenate(SA25W29_hex)
                
                SA25W30_hex = hexDecodedData[3072:3076]
                SA25W30 = reverse_and_concatenate(SA25W30_hex)
        
                SA25W31_hex = hexDecodedData[3076:3080]
                SA25W31 = reverse_and_concatenate(SA25W31_hex)
                
                SA25W32_hex = hexDecodedData[3080:3084]
                SA25W32 = reverse_and_concatenate(SA25W32_hex)
                
                #===============SA26 ============================#
                SA26W1_hex = hexDecodedData[3084:3088]
                SA26W1 = reverse_and_concatenate(SA26W1_hex)
        
                SA26W2_hex = hexDecodedData[3088:3092]
                SA26W2 = reverse_and_concatenate(SA26W2_hex)
                
                SA26W3_hex = hexDecodedData[3092:3096]
                SA26W3 = reverse_and_concatenate(SA26W3_hex)
        
                SA26W4_hex = hexDecodedData[3096:3100]
                SA26W4 = reverse_and_concatenate(SA26W4_hex)
                
                SA26W5_hex = hexDecodedData[3100:3104]
                SA26W5 = reverse_and_concatenate(SA26W5_hex)
        
                SA26W6_hex = hexDecodedData[3104:3108]
                SA26W6 = reverse_and_concatenate(SA26W6_hex)
                
                SA26W7_hex = hexDecodedData[3108:3112]
                SA26W7 = reverse_and_concatenate(SA26W7_hex)
                
                SA26W8_hex = hexDecodedData[3112:3116]
                SA26W8 = reverse_and_concatenate(SA26W8_hex)
        
                SA26W9_hex = hexDecodedData[3116:3120]
                SA26W9 = reverse_and_concatenate(SA26W9_hex)
                
                SA26W10_hex = hexDecodedData[3120:3124]
                SA26W10 = reverse_and_concatenate(SA26W10_hex)
        
                SA26W11_hex = hexDecodedData[3124:3128]
                SA26W11 = reverse_and_concatenate(SA26W11_hex)
                
                SA26W12_hex = hexDecodedData[3128:3132]
                SA26W12 = reverse_and_concatenate(SA26W12_hex)
        
                SA26W13_hex = hexDecodedData[3132:3136]
                SA26W13 = reverse_and_concatenate(SA26W13_hex)
                
                SA26W14_hex = hexDecodedData[3136:3140]
                SA26W14 = reverse_and_concatenate(SA26W14_hex)
                
                SA26W15_hex = hexDecodedData[3140:3144]
                SA26W15 = reverse_and_concatenate(SA26W15_hex)
        
                SA26W16_hex = hexDecodedData[3144:3148]
                SA26W16 = reverse_and_concatenate(SA26W16_hex)
                
                SA26W17_hex = hexDecodedData[3148:3152]
                SA26W17 = reverse_and_concatenate(SA26W17_hex)
                
                SA26W18_hex = hexDecodedData[3152:3156]
                SA26W18 = reverse_and_concatenate(SA26W18_hex)
                
                SA26W19_hex = hexDecodedData[3156:3160]
                SA26W19 = reverse_and_concatenate(SA26W19_hex)
                
                SA26W20_hex = hexDecodedData[3160:3164]
                SA26W20 = reverse_and_concatenate(SA26W20_hex)
        
                SA26W21_hex = hexDecodedData[3164:3168]
                SA26W21 = reverse_and_concatenate(SA26W21_hex)
                
                SA26W22_hex = hexDecodedData[3168:3172]
                SA26W22 = reverse_and_concatenate(SA26W22_hex)
        
                SA26W23_hex = hexDecodedData[3172:3176]
                SA26W23 = reverse_and_concatenate(SA26W23_hex)
                
                SA26W24_hex = hexDecodedData[3176:3180]
                SA26W24 = reverse_and_concatenate(SA26W24_hex)
                
                SA26W25_hex = hexDecodedData[3180:3184]
                SA26W25 = reverse_and_concatenate(SA26W25_hex)
        
                SA26W26_hex = hexDecodedData[3184:3188]
                SA26W26 = reverse_and_concatenate(SA26W26_hex)
                
                SA26W27_hex = hexDecodedData[3188:3192]
                SA26W27 = reverse_and_concatenate(SA26W27_hex)
                
                SA26W28_hex = hexDecodedData[3192:3196]
                SA26W28 = reverse_and_concatenate(SA26W28_hex)
                
                SA26W29_hex = hexDecodedData[3196:3200]
                SA26W29 = reverse_and_concatenate(SA26W29_hex)
                
                SA26W30_hex = hexDecodedData[3200:3204]
                SA26W30 = reverse_and_concatenate(SA26W30_hex)
        
                SA26W31_hex = hexDecodedData[3204:3208]
                SA26W31 = reverse_and_concatenate(SA26W31_hex)
                
                SA26W32_hex = hexDecodedData[3208:3212]
                SA26W32 = reverse_and_concatenate(SA26W32_hex)
                
               #===============SA27 ============================#
                SA27W1_hex = hexDecodedData[3212:3216]
                SA27W1 = reverse_and_concatenate(SA27W1_hex)
        
                SA27W2_hex = hexDecodedData[3216:3220]
                SA27W2 = reverse_and_concatenate(SA27W2_hex)
                
                SA27W3_hex = hexDecodedData[3220:3224]
                SA27W3 = reverse_and_concatenate(SA27W3_hex)
        
                SA27W4_hex = hexDecodedData[3224:3228]
                SA27W4 = reverse_and_concatenate(SA27W4_hex)
                
                SA27W5_hex = hexDecodedData[3228:3232]
                SA27W5 = reverse_and_concatenate(SA27W5_hex)
        
                SA27W6_hex = hexDecodedData[3232:3236]
                SA27W6 = reverse_and_concatenate(SA27W6_hex)
                
                SA27W7_hex = hexDecodedData[3236:3240]
                SA27W7 = reverse_and_concatenate(SA27W7_hex)
                
                SA27W8_hex = hexDecodedData[3240:3244]
                SA27W8 = reverse_and_concatenate(SA27W8_hex)
        
                SA27W9_hex = hexDecodedData[3244:3248]
                SA27W9 = reverse_and_concatenate(SA27W9_hex)
                
                SA27W10_hex = hexDecodedData[3248:3252]
                SA27W10 = reverse_and_concatenate(SA27W10_hex)
        
                SA27W11_hex = hexDecodedData[3252:3256]
                SA27W11 = reverse_and_concatenate(SA27W11_hex)
                
                SA27W12_hex = hexDecodedData[3256:3260]
                SA27W12 = reverse_and_concatenate(SA27W12_hex)
        
                SA27W13_hex = hexDecodedData[3260:3264]
                SA27W13 = reverse_and_concatenate(SA27W13_hex)
                
                SA27W14_hex = hexDecodedData[3264:3268]
                SA27W14 = reverse_and_concatenate(SA27W14_hex)
                
                SA27W15_hex = hexDecodedData[3268:3272]
                SA27W15 = reverse_and_concatenate(SA27W15_hex)
        
                SA27W16_hex = hexDecodedData[3272:3276]
                SA27W16 = reverse_and_concatenate(SA27W16_hex)
                
                SA27W17_hex = hexDecodedData[3276:3280]
                SA27W17 = reverse_and_concatenate(SA27W17_hex)
                
                SA27W18_hex = hexDecodedData[3280:3284]
                SA27W18 = reverse_and_concatenate(SA27W18_hex)
                
                SA27W19_hex = hexDecodedData[3284:3288]
                SA27W19 = reverse_and_concatenate(SA27W19_hex)
                
                SA27W20_hex = hexDecodedData[3288:3292]
                SA27W20 = reverse_and_concatenate(SA27W20_hex)
        
                SA27W21_hex = hexDecodedData[3292:3296]
                SA27W21 = reverse_and_concatenate(SA27W21_hex)
                
                SA27W22_hex = hexDecodedData[3296:3300]
                SA27W22 = reverse_and_concatenate(SA27W22_hex)
        
                SA27W23_hex = hexDecodedData[3300:3304]
                SA27W23 = reverse_and_concatenate(SA27W23_hex)
                
                SA27W24_hex = hexDecodedData[3304:3308]
                SA27W24 = reverse_and_concatenate(SA27W24_hex)
                
                SA27W25_hex = hexDecodedData[3308:3312]
                SA27W25 = reverse_and_concatenate(SA27W25_hex)
        
                SA27W26_hex = hexDecodedData[3312:3316]
                SA27W26 = reverse_and_concatenate(SA27W26_hex)
                
                SA27W27_hex = hexDecodedData[3316:3320]
                SA27W27 = reverse_and_concatenate(SA27W27_hex)
                
                SA27W28_hex = hexDecodedData[3320:3324]
                SA27W28 = reverse_and_concatenate(SA27W28_hex)
                
                SA27W29_hex = hexDecodedData[3324:3328]
                SA27W29 = reverse_and_concatenate(SA27W29_hex)
                
                SA27W30_hex = hexDecodedData[3328:3332]
                SA27W30 = reverse_and_concatenate(SA27W30_hex)
        
                SA27W31_hex = hexDecodedData[3332:3336]
                SA27W31 = reverse_and_concatenate(SA27W31_hex)
                
                SA27W32_hex = hexDecodedData[3336:3340]
                SA27W32 = reverse_and_concatenate(SA27W32_hex)
                #=============================================
                est_rec_clk_hex = hexDecodedData[956:960]
       
                #===========
                est_rec_clk_hex = hexDecodedData[956:960]
                est_rec_clk = reverse_and_concatenate(est_rec_clk_hex)
                
                est_rec_clk_bias_hex = hexDecodedData[1068:1076]
                Est_rec_clk_bias = reverse_and_concatenate(est_rec_clk_bias_hex,is_signed=True)/100.0
                
                
                LCOR_hex = hexDecodedData[1076:1084]
                LCOR =reverse_and_concatenate (LCOR_hex)
                
                Str_crr_clk_hex = hexDecodedData[1084:1092]
                Str_crr_clk = reverse_and_concatenate(Str_crr_clk_hex)

                ephem_constel_word = hexDecodedData[440:444]  # Word#12
                ephem_constel_hex = reverse_and_concatenate(ephem_constel_word)

                # Constellation flag (B0 to B7) → for channels 1 to 8
                constel_flag = [(ephem_constel_hex >> i) & 1 for i in range(8)]  # B0 to B7
                # Ephemeris flag (B8 to B15) → for channels 1 to 8
                ephem_flag   = [(ephem_constel_hex >> i) & 1 for i in range(8, 16)]  # B8 to B15

                # P (Constellation): 0 = Used → Y, 1 = Not used → N
                constel_flag_display = ['Y' if flag == 1 else 'N' for flag in constel_flag]

                # E (Ephemeris): 0 = Available → Y, 1 = Not available → N
                ephem_flag_display = ['Y' if flag == 1 else 'N' for flag in ephem_flag]


                E_T_P_D9_10 = hexDecodedData[692:696]
                E_T_P_D9_10_hex = reverse_and_concatenate(E_T_P_D9_10)

                # Extract each field using bitwise ops
                eph_10_bits = (E_T_P_D9_10_hex >> 13) & 0x1
                #print(f"E10:{eph_10_bits}")
                eph_9_bits  = (E_T_P_D9_10_hex >> 12) & 0x1
                #print(f"E9:{eph_9_bits}")
                status_10_bits = (E_T_P_D9_10_hex >>10) & 0x3
                status_9_bits  = (E_T_P_D9_10_hex >> 8) & 0x3

                constel_10 = (E_T_P_D9_10_hex >> 7) & 0x1
                constel_9  = (E_T_P_D9_10_hex >> 6) & 0x1

                dr_10 = (E_T_P_D9_10_hex >> 5) & 0x1
                dr_9  = (E_T_P_D9_10_hex >> 4) & 0x1

                # TOA-aLM: lower 4 bits from this word (b3–b0)
                #toa_alm_ls_4 = E_T_P_D9_10_hex & 0xF

                # You can combine this with MS 4 bits from next word to form full TOA if needed

                # Format displays


                if eph_9_bits == 0b00:
                    e9_flag = 'N'
                elif eph_9_bits == 0b01:
                    e9_flag = 'Y'
                else:
                    e9_flag ="UN"

                if eph_10_bits == 0b00:
                    e10_flag = 'N'
                elif eph_10_bits == 0b01:
                    e10_flag = 'Y'
                else:
                    eph_10_bits ="UN"







                t_map = {0b00: 'I', 0b01: 'A', 0b10: 'T', 0b11: 'N'}

                t9_flag = t_map.get(status_9_bits, 'N')
                t10_flag = t_map.get(status_10_bits, 'N')

                p9_flag  = 'Y' if constel_9 == 1 else 'N'
                p10_flag  = 'Y' if constel_10 == 1 else 'N'

                d9_flag  = 'Y' if dr_9 == 1 else 'N'
                d10_flag  = 'Y' if dr_10 == 1 else 'N'

                E_T_P_D11_12 = hexDecodedData[752:756]
                E_T_P_D11_12_hex = reverse_and_concatenate(E_T_P_D11_12)

                # Extract bit fields
                eph_12_bits = (E_T_P_D11_12_hex >> 13) & 0x1
                #print(f"E12:{eph_12_bits}")
                eph_11_bits = (E_T_P_D11_12_hex >> 12) & 0x1
                #print(f"E11:{eph_11_bits}")

                status_12_bits = (E_T_P_D11_12_hex >> 10) & 0X3
                status_11_bits = (E_T_P_D11_12_hex >> 8) & 0X3

                constel_12 = (E_T_P_D11_12_hex >> 7) & 0x1
                constel_11 = (E_T_P_D11_12_hex >> 6) & 0x1

                dr_12 = (E_T_P_D11_12_hex >> 5) & 0x1
                dr_11 = (E_T_P_D11_12_hex >> 4) & 0x1

                # Format the display outputs
                e11_flag  = 'Y' if eph_11_bits == 1 else 'N'
                e12_flag  = 'Y' if eph_12_bits == 1 else 'N'

                t_map = {0b00: 'I', 0b01: 'A', 0b10: 'T', 0b11: 'N'}
                t11_flag  = t_map.get(status_11_bits, 'N')
                t12_flag  = t_map.get(status_12_bits, 'N')

                p11_flag  = 'Y' if constel_11 == 1 else 'N'
                p12_flag  = 'Y' if constel_12 == 1 else 'N'

                d11_flag  = 'Y' if dr_11 == 1 else 'N'
                d12_flag  = 'Y' if dr_12 == 1 else 'N'

                T = hexDecodedData[444:448]  # Word#13 (2 bytes = 1 word)

                # Convert to integer
                channel_status_word = reverse_and_concatenate(T)

                # Mapping of 2-bit status to display
                status_map = {
                    0b00: 'I',  # IDLE
                    0b01: 'A',  # ACQ
                    0b10: 'T',  # TRK
                    0b11: 'N'   # NA
                }

                # Extract and decode status for channels 1 to 8
                T_flag_display = []
                for i in range(8):
                    status_bits = (channel_status_word >> (i * 2)) & 0b11
                    T_flag_display.append(status_map.get(status_bits, 'N'))  # Default to 'N' if unknown

                D = hexDecodedData[452:456]

                # Convert full word to integer
                word15_int = reverse_and_concatenate(D)

                # Extract LSB (lower 8 bits) for DR flags
                dr_status_lsb = word15_int & 0xFF

                # DR Flag Display (Channel 1–8)
                D_flag_display = []
                for i in range(8):
                    bit = (dr_status_lsb >> i) & 1
                    D_flag_display.append('Y' if bit else 'N')

                Sol_config =  (word15_int >> 15) & 0x1
                if Sol_config == 0b00:
                    Sol = "NA"
                    sol.config(fg="dark red")
                if Sol_config == 0b01:
                    Sol = "A"
                    sol.config(fg="dark green")
                else:
                    Sol = "UN"
                    sol.config(fg="black")


                Pos_E_config = (word15_int >> 14) & 0x1
                if Pos_E_config == 0b00:
                    Pos_E = "NA"
                    pos_e.config(fg="dark red")
                if Pos_E_config == 0b01:
                    Pos_E = "A"
                    pos_e.config(fg="dark green")
                else:
                    Pos_E = "UN"
                    pos_e.config(fg="black")


                alm_config = (word15_int >> 12) & 0x3

                if alm_config == 0b00:
                    ALM = "A"
                    alm.config(fg="dark green")
                elif alm_config == 0b01:
                    ALM = "NA"
                    alm.config(fg="dark red")
                elif alm_config == 0b10:
                    ALM = "No"
                    alm.config(fg="black")
                else:
                    ALM = "Unknown"
                    alm.config(fg="black")

                Time_config = (word15_int >> 11) & 0x1
                if Time_config == 0b00:
                    Time = "NA"
                    time.config(fg="dark red")
                elif Time_config == 0b01:
                    Time = "A"
                    time.config(fg="dark green")
                else:
                    Time = "UN"
                    time.config(fg="black")

                d_2d = (word15_int >> 9) & 0x3
                if d_2d == 0b00:
                    D2_3D_config = "3D"
                    d2_3d.config(fg="dark green")
                elif d_2d == 0b01:
                    D2_3D_config = "2D"
                    d2_3d.config(fg="dark red")
                elif d_2d == 0b10:
                    D2_3D_config = "NA"
                    d2_3d.config(fg="red")
                else:
                    D2_3D_config = "Unknown"
                    d2_3d.config(fg="black")
                '''d_map = {
                    0b00: "3D",
                    0b01: "2D",
                    0b10: "NA"
                }
                D2_3D_config = d_map[d_2d]'''

                pos_config = (word15_int >> 8) & 0x1
                if pos_config == 0b00:
                    Pos = "NA"
                    position.config(fg="dark red")
                elif pos_config == 0b01:
                    Pos = "A"
                    position.config(fg="dark green")
                else:
                    Pos = "UN"
                    position.config(fg="black")



                H = hexDecodedData[500:504]

                # Convert to integer
                word27_int = reverse_and_concatenate(H)

                # Extract bits B0 to B11 → CH1 to CH12 SV Health/URA Status
                H_flag_display = []
                for i in range(12):
                    bit = (word27_int >> i) & 0x1
                    H_flag_display.append('G' if bit == 0 else 'B')
                # Decode Port1 (B13:B12)
                port1_bits = (word27_int >> 12) & 0x3
                port1_map = {
                    0b00: "GPS",
                    0b01: "NAVIC",
                    0b10: "Combined",
                    0b11: "Reserved"
                }
                port1_config = port1_map[port1_bits]

                # Decode Port2 (B15:B14)
                port2_bits = (word27_int >> 14) & 0x3
                port2_map = {
                    0b00: "GPS",
                    0b01: "NAVIC",
                    0b10: "Combined",
                    0b11: "Reserved"
                }
                port2_config = port2_map[port2_bits]


                I = hexDecodedData[508:512]  # Adjust index as per actual layout

               
                word29_int = reverse_and_concatenate(I)

                # Decode B0–B11 → CH1 to CH12
                I_flag_display = []
                for i in range(12):
                    bit = (word29_int >> i) & 0x1
                    I_flag_display.append('A' if bit == 1 else 'N')


                A = hexDecodedData[512:516]  # Adjust index if needed

               
                word30_int = reverse_and_concatenate(A)

                # Decode B0–B11: RF chain per channel
                A_flag_display = []
                for i in range(12):  # Ch1–Ch12
                    bit = (word30_int >> i) & 0x1
                    A_flag_display.append('2' if bit == 1 else '1')  # 0 → RF1, 1 → RF2

                R = hexDecodedData[516:520]  # Adjust index if required

                # Convert to integer
                word31_int = reverse_and_concatenate(R)

                # Decode B0–B11: Health/URA Rejection Flags
                R_flag_display = []
                for i in range(12):
                    bit = (word31_int >> i) & 0x1
                    R_flag_display.append('R' if bit else 'P')  # 0 = Healthy, 1 = Unhealthy

                # Decode Additional Bits
                odp_status = 'Enabled' if ((word31_int >> 12) & 0x1) == 1 else 'Disabled'
                phase_corr = 'Enabled' if ((word31_int >> 13) & 0x1) == 1 else 'Disabled'
                phase_corr_sps = 'Enabled' if ((word31_int >> 14) & 0x1) == 1 else 'Disabled'

                sbas_fast_crr = hexDecodedData[776:780]  # Adjust index if needed

                # Convert to int
                word32_int = reverse_and_concatenate(sbas_fast_crr)
                # Decode Additional Bits
                #elev_flag = 'Disabled' if ((word32_int >> 12) & 0x1) == 0 else 'Enabled'
                ccsds_flag = 'Enabled' if ((word32_int >> 15) & 0x1) == 1 else 'Disabled'
                randomizer_flag = 'on' if ((word32_int >> 14) & 0x1) == 1 else 'off'
                #pr_mode_flag = 'old' if ((word32_int >> 13) & 0x1) == 1 else 'new'

                word31_hex = hexDecodedData [772:776]
                word31 = reverse_and_concatenate(word31_hex)
                decoded_data =  Multiplexing(word31)

                Spacecraft_id_hex = hexDecodedData[764:766]
                Spacecraft_id=reverse_and_concatenate(Spacecraft_id_hex)
                Navic_cmd_hex = hexDecodedData[766:768]
                Navic_cmd = reverse_and_concatenate(Navic_cmd_hex)
                
                
                odp_par_hex = hexDecodedData[1036:1040] #
                odp_par = reverse_and_concatenate(odp_par_hex)

                odp_flags = odp_parameter(odp_par)

                # Example: Update GUI entry widgets
                for label, value in odp_flags.items():
                    entry = odp_entries.get(label)
                    if entry:
                        entry.config(state="normal")
                        entry.delete(0, END)
                        entry.insert(0, value)
                        entry.config(state="readonly")
                        set_status_colored(entry, value)

                #Steering BIAS
                Steering_B_hex = hexDecodedData[1068:1072]
                Steering_B = reverse_and_concatenate(Steering_B_hex)
                value1 = (Steering_B & 0X7FFF)/100.0
                b_flag = (Steering_B >> 15) & 0x1

                if b_flag == 1:
                    Steering_Bias = -value1
                else:
                    Steering_Bias = value1

                #U1 DATA

                U1_hex =  hexDecodedData[1072:1076]
                U1_h = reverse_and_concatenate(U1_hex)
                value2 = (U1_h & 0X7FFF)/100.0
                b_flag = (U1_h >> 15) & 0x1

                if b_flag == 1:
                    U1_data = -value2
                else:
                    U1_data = value2


                #Steering DRIFT
                Steering_Drift_hex = hexDecodedData[1076:1080]
                Steering_D = reverse_and_concatenate(Steering_Drift_hex)
                value3 = (Steering_D & 0X7FFF)/10.0
                b_flag = (Steering_D >> 15) & 0x1

                if b_flag == 1:
                    Steering_Drift = -value3
                else:
                    Steering_Drift = value3


                #U2 DATA
                U2_hex =  hexDecodedData[1080:1084]
                U2_h = reverse_and_concatenate(U2_hex)
                value4 = (U2_h & 0X7FFF)/10.0
                b_flag = (U2_h >> 15) & 0x1

                if b_flag == 1:
                    U2_data = -value4
                else:
                    U2_data = value4

                #Steering CLOCK
                Steering_clock_hex = hexDecodedData[1084:1092]
                Steering_clock = reverse_and_concatenate(Steering_clock_hex,is_signed=True)/1000.0

                '''SA10W20_hex = hexDecodedData[1112:1116]
                SA10W20=reverse_and_concatenate(SA10W20_hex)
                #ill_cnd_val = SA10W20
                #ill_cnd_val = (SA10W20 & 0xFFF8) >> 3
                #pre_cntr = SA10W20 & 0x0007

                SA10W21_hex = hexDecodedData[1116:1120]
                SA10W21=reverse_and_concatenate(SA10W21_hex)
                #ill_cnd_Limit = SA10W21
                #ill_cnd_Limit = (SA10W21 &0xFFC0) >> 6
                #post_cntr = SA10W21 & 0x003F

                SA10W22_hex = hexDecodedData[1120:1124]
                SA10W22=reverse_and_concatenate(SA10W22_hex)
                cond_pre_check = SA10W22 & 0x00FF
                cond_post_check = (SA10W22 >> 8) & 0x00FF

                SA10W23_hex = hexDecodedData[1124:1128]
                SA10W23=reverse_and_concatenate(SA10W23_hex)
                ODP_prop_used = (SA10W23 >> 0) & 1'''


                PPS_3D_hex = hexDecodedData[2444:2448]
                #print(PPS_3D_hex)
                pps_3d=reverse_and_concatenate(PPS_3D_hex)

                if pps_3d == 3:
                    PPS_3D = "2D Fix"
                elif pps_3d == 7:
                    PPS_3D = "3D Fix"
                else :
                    PPS_3D = "No Fix"

                PPS_NanoSec_hex = hexDecodedData[2448:2456]
                #print(PPS_NanoSec_hex)
                PPS_NanoSec=reverse_and_concatenate(PPS_NanoSec_hex)
                PPS_Sec_hex = hexDecodedData[2456:2464]
                PPS_Sec=reverse_and_concatenate(PPS_Sec_hex)
                PPS_Week_hex = hexDecodedData[2464:2468]
                PPS_Week=reverse_and_concatenate(PPS_Week_hex)

                CHECKSUM=reverse_and_concatenate(CHECKSUM_hex)
                chechsum_calulation_covert_decimal(SYN_NanoSecond_hex,SYN_Second_hex,SYN_Weeknumber_hex,CHECKSUM)

                SYS_NanoSecond=reverse_and_concatenate(SYS_NanoSecond_hex)

                SYS_Second=reverse_and_concatenate(SYS_Second_hex)
                
                
                # ✅ Update global sync variable for SA1
                global latest_sys_second, sys_second_lock
                with sys_second_lock:
                    latest_sys_second = SYS_Second
                SYS_Weeknumber=reverse_and_concatenate(SYS_Weeknumber_hex)
                
                INST_x = reverse_and_concatenate(Inst_x_hex , is_signed=True)/100.0
                INST_y = reverse_and_concatenate(Inst_y_hex , is_signed=True)/100.0
                INST_z = reverse_and_concatenate(Inst_z_hex , is_signed=True)/100.0
                INST_vx = reverse_and_concatenate(Inst_vx_hex , is_signed=True)/1000.0
                INST_vy = reverse_and_concatenate(Inst_vy_hex , is_signed=True)/1000.0
                INST_vz = reverse_and_concatenate(Inst_vz_hex , is_signed=True)/1000.0
                
                EST_x = reverse_and_concatenate(Est_x_hex, is_signed=True)/100.0
                EST_y = reverse_and_concatenate(Est_y_hex, is_signed=True)/100.0
                EST_z = reverse_and_concatenate(Est_z_hex, is_signed=True)/100.0
                EST_vx = reverse_and_concatenate(Est_vx_hex, is_signed=True)/1000.0
                EST_vy = reverse_and_concatenate(Est_vy_hex, is_signed=True)/1000.0
                EST_vz = reverse_and_concatenate(Est_vz_hex, is_signed=True)/1000.0
                
                              
                # ============================================================
                # RECEIVER TIME
                # ============================================================
                
                receiver_time = SYS_Second + SYS_NanoSecond / 1e9
                    
                
                
                # ============================================================
                # DEFAULT VALUES
                # ============================================================
                
                current_time_diff = 0.0
                
                current_precise = None
                
                px_p = 0.0
                py_p = 0.0
                pz_p = 0.0
                
                vx_p = 0.0
                vy_p = 0.0
                vz_p = 0.0
                
                
                dx = 0.0
                dy = 0.0
                dz = 0.0
                
                dvx = 0.0
                dvy = 0.0
                dvz = 0.0
                
                odp_dx = 0.0
                odp_dy = 0.0
                odp_dz = 0.0
                
                odp_dvx = 0.0
                odp_dvy = 0.0
                odp_dvz = 0.0
                
              
                
                rss_pos = 0.0
                rss_vel = 0.0
                
                odp_rss_pos = 0.0 
                odp_rss_vel = 0.0
                
                
                # ============================================================
                # FIND CLOSEST PRECISE TOW
                # ============================================================
                
                if precise_loaded and precise_data and precise_times:
                
                
                    pos = bisect.bisect_left(
                
                        precise_times,
                
                        receiver_time
                
                    )
                
                
                    # --------------------------------------------------------
                    # Receiver time before first precise time
                    # --------------------------------------------------------
                
                    if pos == 0:
                
                        current_precise = precise_data[0]
                
                
                    # --------------------------------------------------------
                    # Receiver time after last precise time
                    # --------------------------------------------------------
                
                    elif pos == len(precise_times):
                
                        current_precise = precise_data[-1]
                
                
                    # --------------------------------------------------------
                    # Find nearest precise record
                    # --------------------------------------------------------
                
                    else:
                
                        before = precise_data[pos - 1]
                
                        after = precise_data[pos]
                
                
                        before_diff = abs(
                            receiver_time -
                            before["tow"]
                        )
                
                
                        after_diff = abs(
                            after["tow"] -
                            receiver_time
                        )
                
                
                        if before_diff <= after_diff:
                
                            current_precise = before
                
                        else:
                
                            current_precise = after
                
                
                    # ========================================================
                    # TIME DIFFERENCE
                    # ========================================================
                
                    current_time_diff = (
                
                        receiver_time -
                
                        current_precise["tow"]
                
                    )
                
                
                    # ========================================================
                    # GET PRECISE VALUES
                    # ========================================================
                
                    px = current_precise["px"]
                    py = current_precise["py"]
                    pz = current_precise["pz"]
                
                
                    vx = current_precise["vx"]
                    vy = current_precise["vy"]
                    vz = current_precise["vz"]
                
                
                    ax = current_precise["ax"]
                    ay = current_precise["ay"]
                    az = current_precise["az"]
                
                
                    # ========================================================
                    # PROPAGATE PRECISE POSITION
                    # ========================================================
                
                    t = current_time_diff
                
                # Propagation
                    px_p = px + vx*t + 0.5*ax*t*t
                    py_p = py + vy*t + 0.5*ay*t*t
                    pz_p = pz + vz*t + 0.5*az*t*t
                
                    vx_p = vx + ax*t
                    vy_p = vy + ay*t
                    vz_p = vz + az*t
                
                    # Differences
                    dx = px_p - INST_x
                    dy = py_p - INST_y
                    dz = pz_p - INST_z
                
                    dvx = (vx_p - INST_vx) * 100
                    dvy = (vy_p - INST_vy) * 100
                    dvz = (vz_p - INST_vz) * 100
                    
                    # Differences
                    odp_dx = px_p - EST_x
                    odp_dy = py_p - EST_y
                    odp_dz = pz_p - EST_z
                
                    odp_dvx = (vx_p - EST_vx) * 100
                    odp_dvy = (vy_p - EST_vy) * 100
                    odp_dvz = (vz_p - EST_vz) * 100
                                
                
                      # RSS POS n VEL
                    rss_pos = np.sqrt(dx**2 + dy**2 + dz**2)
                    rss_vel = np.sqrt(dvx**2 + dvy**2 + dvz**2)
                
                        # RSS POS n VEL
                    odp_rss_pos = np.sqrt(odp_dx**2 + odp_dy**2 + odp_dz**2)
                    odp_rss_vel = np.sqrt(odp_dvx**2 + odp_dvy**2 + odp_dvz**2)
                
                

                


                UpdateCounter=reverse_and_concatenate(UpdateCounter_hex)

                

                #validation_flag=reverse_and_concatenate(validation_flag_hex)

                CHECKSUM1=reverse_and_concatenate(CHECKSUM1_hex)
                SA4chechsum_calulation_covert_decimal(SYS_NanoSecond_hex,SYS_Second_hex,SYS_Weeknumber_hex,Inst_x_hex,Inst_y_hex,Inst_z_hex,Inst_vx_hex,Inst_vy_hex,Inst_vz_hex,UpdateCounter_hex,Est_x_hex ,Est_y_hex ,Est_z_hex ,Est_vx_hex ,Est_vy_hex ,Est_vz_hex ,validation_flag_hex,CHECKSUM1)

                CLOCKBIAS = reverse_and_concatenate(CLOCKBIAS_hex,is_signed=True)/100.0
                PDOP = reverse_and_concatenate(PDOP_hex, is_signed=True)/100.0
                INTER_SYSTEM_BIAS= reverse_and_concatenate(INTER_SYSTEM_BIAS_hex,is_signed=True)/1000.0
                SWDT_RST_COUNTER = reverse_and_concatenate(SWDT_RST_COUNTER_hex)
                Last_cmd_excuted_byte4 = reverse_and_concatenate(Last_cmd_excuted_byte4_hex)
                Last_cmd_excuted_byte1_2 = reverse_and_concatenate(Last_cmd_excuted_byte1_2_hex)


                ACQ1_SVID = reverse_and_concatenate(ACQ1_SVID_hex)
                Last_cmd_excuted_byte3 = reverse_and_concatenate(Last_cmd_excuted_byte3_hex)
                MC = reverse_and_concatenate(MC_hex)
                LRT = reverse_and_concatenate(LAST_RESET_TIME_hex)
                ISD = reverse_and_concatenate(INTER_SYSTEM_Drift_hex)

                SVID = reverse_and_concatenate(SVID_hex)
                IODE = reverse_and_concatenate(IODE_hex)
                CRS = reverse_and_concatenate(CRS_hex)



                SPS_CMD_COUNTER = reverse_and_concatenate(TELE_CMD_COUNTER_hex)
                UPSET_COUNTER = reverse_and_concatenate(UPSET_COUNTER_hex)

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
                
                Remote_Read_Write1 = reverse_and_concatenate(Remote_Read_Write1_hex)
                Remote_Read_Write2 = reverse_and_concatenate(Remote_Read_Write2_hex)
                Remote_Read_Write3 = reverse_and_concatenate(Remote_Read_Write3_hex)
                Remote_Read_Write4 = reverse_and_concatenate(Remote_Read_Write4_hex)
                Remote_Read_Write5 = reverse_and_concatenate(Remote_Read_Write5_hex)
                Remote_Read_Write6 = reverse_and_concatenate(Remote_Read_Write6_hex)
                
                
                

                SA29_hex = hexDecodedData[1932:1992]
                if isinstance(SA29_hex,(bytes,bytearray)):
                    SA29_hex = SA29_hex.hex()
                SA29_Raw = " ".join([SA29_hex[i:i+4]for i in range (0,len(SA29_hex),4)])
                # ✅ SAFE GUI UPDATES (Thread-safe wrapper)
                def apply_updates():
                    safe_gui_update(csm, f"{checksum}")
                    safe_gui_update(time_entry1, str(SYS_Second))
                    safe_gui_update(nanotime_entry1, str(SYS_NanoSecond))
                    safe_gui_update(week_entry1, str(SYS_Weeknumber))
                    safe_gui_update(time_entry3, str(PPS_Sec))
                    safe_gui_update(nanotime_entry3, str(PPS_NanoSec))
                    safe_gui_update(week_entry3, str(PPS_Week))
                    safe_gui_update(fix_status, str(PPS_3D))
                    safe_gui_update(position_entry, str(INST_x))
                    safe_gui_update(position_entry1, str(INST_y))
                    safe_gui_update(position_entry2, str(INST_z))
                    safe_gui_update(velocity_entry, str(INST_vx))
                    safe_gui_update(velocity_entry1, str(INST_vy))
                    safe_gui_update(velocity_entry2, str(INST_vz))
                    safe_gui_update(update_entry, f"{UpdateCounter}")
                    safe_gui_update(position_entry3, str(EST_x))
                    safe_gui_update(position_entry4, str(EST_y))
                    safe_gui_update(position_entry5, str(EST_z))
                    safe_gui_update(velocity_entry3, str(EST_vx))
                    safe_gui_update(velocity_entry4, str(EST_vy))
                    safe_gui_update(velocity_entry5, str(EST_vz))
                    safe_gui_update(flag, f"{ODP_FLAG}")
                    safe_gui_update(flag1,f"{odp_run_mode}")
                    safe_gui_update(csm1, f"{checksum1}")
                    safe_gui_update(cb, f"{CLOCKBIAS}")
                    safe_gui_update(pdop, f"{PDOP}")
                    safe_gui_update(icb, f"{INTER_SYSTEM_BIAS}")
                    safe_gui_update(st_bias, f"{Steering_Bias}")
                    safe_gui_update(clk_crr, f"{Steering_clock}")
                    safe_gui_update(st_drift, f"{Steering_Drift}")
                    safe_gui_update(U1, f"{U1_data}")
                    safe_gui_update(U2, f"{U2_data}")
                    safe_gui_update(swdt, f"{SWDT_RST_COUNTER}")
                    safe_gui_update(last_cmd_b1_b2, f"{Last_cmd_excuted_byte1_2}")
                    safe_gui_update(last_cmd_b3, f"{Last_cmd_excuted_byte3}")
                    safe_gui_update(last_cmd_b4, f"{Last_cmd_excuted_byte4}")
                    safe_gui_update(acq1_svid, f"{ACQ1_SVID}")
                    safe_gui_update(mc, f"{MC}")
                    safe_gui_update(lrt, f"{LRT}")
                    safe_gui_update(isd, f"{ISD}")
                    safe_gui_update(drift, f"{DRIFT}")
                    safe_gui_update(SI, f"{SVID}")
                    safe_gui_update(iode, f"{IODE}")
                    safe_gui_update(crs, f"{CRS}")
                    for idx, sv in enumerate([SVID1,SVID2,SVID3,SVID4,SVID5,SVID6,SVID7,SVID8,SVID9,SVID10,SVID11,SVID12], 1):
                        safe_gui_update(eval(f"svid{idx}"), f"{sv}")
                    for idx, cd in enumerate([CNDR1,CNDR2,CNDR3,CNDR4,CNDR5,CNDR6,CNDR7,CNDR8,CNDR9,CNDR10,CNDR11,CNDR12], 1):
                        safe_gui_update(eval(f"cndr{idx}"), f"{cd}")
                    refresh_cndr_plot()
                    for idx, val in enumerate(T_flag_display): safe_gui_update(eval(f"t{idx+1}"), val)
                    for idx, val in enumerate(D_flag_display): safe_gui_update(eval(f"d{idx+1}"), val)
                    for idx, val in enumerate(ephem_flag_display): safe_gui_update(eval(f"e{idx+1}"), val)
                    for idx, val in enumerate(constel_flag_display): safe_gui_update(eval(f"p{idx+1}"), val)
                    for idx, val in enumerate(H_flag_display): safe_gui_update(eval(f"h{idx+1}"), val)
                    for idx, val in enumerate(I_flag_display): safe_gui_update(eval(f"i{idx+1}"), val)
                    for idx, val in enumerate(A_flag_display): safe_gui_update(eval(f"a{idx+1}"), val)
                    for idx, val in enumerate(R_flag_display): safe_gui_update(eval(f"r{idx+1}"), val)
                    safe_gui_update(t9, t9_flag); safe_gui_update(t10, t10_flag)
                    safe_gui_update(t11, t11_flag); safe_gui_update(t12, t12_flag)
                    safe_gui_update(d9, d9_flag); safe_gui_update(d10, d10_flag)
                    safe_gui_update(d11, d11_flag); safe_gui_update(d12, d12_flag)
                    safe_gui_update(e9, e9_flag); safe_gui_update(e10, e10_flag)
                    safe_gui_update(e11, e11_flag); safe_gui_update(e12, e12_flag)
                    safe_gui_update(p9, p9_flag); safe_gui_update(p10, p10_flag)
                    safe_gui_update(p11, p11_flag); safe_gui_update(p12, p12_flag)
                    for idx, val in enumerate([IODE1,IODE2,IODE3,IODE4,IODE5,IODE6,IODE7,IODE8,IODE9,IODE10,IODE11,IODE12], 1):
                        safe_gui_update(eval(f"iode{idx}"), f"{val}")
                    for idx, val in enumerate([PR1,PR2,PR3,PR4,PR5,PR6,PR7,PR8,PR9,PR10,PR11,PR12], 1):
                        safe_gui_update(eval(f"pr{idx}"), f"{val}")
                    for idx, val in enumerate([DR1,DR2,DR3,DR4,DR5,DR6,DR7,DR8,DR9,DR10,DR11,DR12], 1):
                        safe_gui_update(eval(f"dr{idx}"), f"{val}")
                  
                    
                    safe_gui_update(tele_cmd_counter, f"{SPS_CMD_COUNTER}")
                    safe_gui_update(upset_cmd_counter, f"{UPSET_COUNTER}")
                    safe_gui_update(mux_entry, f"{decoded_data}")
                    safe_gui_update(odp, odp_status); set_status_colored(odp, odp_status)
                    safe_gui_update(phase_center, phase_corr)
                    safe_gui_update(phase_center_sps, phase_corr_sps)
                    safe_gui_update(port1, port1_config)
                    safe_gui_update(port2, port2_config)
                    safe_gui_update(sol, Sol)
                    safe_gui_update(pos_e, Pos_E)
                    safe_gui_update(alm, ALM)
                    safe_gui_update(time, Time)
                    safe_gui_update(d2_3d, D2_3D_config)
                    safe_gui_update(position, Pos)
                    safe_gui_update(ccsds, ccsds_flag); set_status_colored(ccsds, ccsds_flag)
                    safe_gui_update(rand, randomizer_flag); set_status_colored(rand, randomizer_flag)
                    safe_gui_update(space_crf_id, Spacecraft_id); set_status_colored(space_crf_id, Spacecraft_id)
                    safe_gui_update(navic_cmd, Navic_cmd)
                    safe_gui_update(tmillcond, ill_cnd_val)
                    safe_gui_update(tmillcondlim, ill_cnd_Limit)
                    safe_gui_update(pre_chk_cntr, pre_cntr)
                    safe_gui_update(post_chk_cntr, post_cntr)
                    safe_gui_update(cond_pre, cond_pre_check)
                    safe_gui_update(cond_post, cond_post_check)
                    safe_gui_update(odp_prop, ODP_prop_used)
                    safe_gui_update(raw_data, SA29_Raw)
                    safe_gui_update(remote1_entry, Remote_Read_Write1)
                    safe_gui_update(remote2_entry, Remote_Read_Write2)
                    safe_gui_update(remote3_entry, Remote_Read_Write3)
                    safe_gui_update(remote4_entry, Remote_Read_Write4)
                    safe_gui_update(remote5_entry, Remote_Read_Write5)
                    safe_gui_update(remote6_entry, Remote_Read_Write6)
                    safe_gui_update(sa8_w3_entry, SA8W3)
                    safe_gui_update(sa8_w4_entry, SA8W4)
                    safe_gui_update(sa8_w5_entry, SA8W5)
                    safe_gui_update(sa8_w6_entry, SA8W6)
                    safe_gui_update(sa8_w7_entry, SA8W7)
                    safe_gui_update(sa8_w8_entry, SA8W8)
                    safe_gui_update(sa8_w9_w10_entry, SA8W9_W10)
                    safe_gui_update(sa8_w11_w12_entry, SA8W11_W12)
                    safe_gui_update(sa8_w13_w14_entry, SA8W13_W14)
                    safe_gui_update(sa8_w15_w16_entry, SA8W15_W16)
                    safe_gui_update(sa8_w17_w18_entry, SA8W17_W18)
                    safe_gui_update(sa8_w19_w20_entry, SA8W19_W20)
                    safe_gui_update(sa8_w21_w22_entry, SA8W21_W22)
                    safe_gui_update(sa8_w23_w24_entry, SA8W23_W24)
                    safe_gui_update(sa8_w25_w26_entry, SA8W25_W26)
                    safe_gui_update(sa8_w27_w28_entry, SA8W27_W28)
                    safe_gui_update(sa8_w29_w30_entry, SA8W29_W30)
                    safe_gui_update(sa8_w31_w32_entry, SA8W31_W32)
                    
                    safe_gui_update(sa9_w1_entry,SA9W1)
                    safe_gui_update(sa9_w2_entry,SA9W2)
                    safe_gui_update(sa9_w3_entry,SA9W3)
                    safe_gui_update(sa9_w4_entry,SA9W4)
                    safe_gui_update(sa9_w5_entry,SA9W5)
                    safe_gui_update(sa9_w6_entry,SA9W6)
                    safe_gui_update(sa9_w7_entry,SA9W7)
                    safe_gui_update(sa9_w8_entry,SA9W8)
                    safe_gui_update(sa9_w9_entry,SA9W9)
                    safe_gui_update(sa9_w10_entry,SA9W10)
                    safe_gui_update(sa9_w11_entry,SA9W11)
                    safe_gui_update(sa9_w12_entry,SA9W12)
                    safe_gui_update(sa9_w13_entry,SA9W13)
                    safe_gui_update(sa9_w14_w15_entry,SA9W14_W15)
                    safe_gui_update(sa9_w16_w17_entry,SA9W16_W17)
                    safe_gui_update(sa9_w18_w19_entry,SA9W18_W19)
                    safe_gui_update(sa9_w20_w21_entry,SA9W20_W21)
                    safe_gui_update(sa9_w22_w23_entry,SA9W22_W23)
                    safe_gui_update(sa9_w24_w25_entry,SA9W24_W25)
                    safe_gui_update(sa9_w26_entry,SA9W26)
                    safe_gui_update(sa9_w27_entry,SA9W27)
                    safe_gui_update(sa9_w28_entry,SA9W28)
                    safe_gui_update(sa9_w29_entry,SA9W29)
                    safe_gui_update(sa9_w30_w31_entry,SA9W30_W31)
                    safe_gui_update(sa9_w32_entry,SA9W32)
                    
                    safe_gui_update(sa10_w1_entry,SA10W1)
                    safe_gui_update(sa10_w2_entry,SA10W2)
                    safe_gui_update(sa10_w3_entry,SA10W3)
                    safe_gui_update(sa10_w4_entry,SA10W4)
                    safe_gui_update(sa10_w5_entry,SA10W5)
                    safe_gui_update(sa10_w6_entry,SA10W6)
                    safe_gui_update(sa10_w7_entry,SA10W7)
                    safe_gui_update(sa10_w8_entry,SA10W8)
                    safe_gui_update(sa10_w9_w10_entry,SA10W9_W10)
                    safe_gui_update(sa10_w11_w12_entry,SA10W11_W12)
                    safe_gui_update(sa10_w13_w14_entry,SA10W13_W14)
                    safe_gui_update(sa10_w15_entry,SA10W15)
                    safe_gui_update(sa10_w16_entry,SA10W16)
                    safe_gui_update(sa10_w17_entry,SA10W17)
                    safe_gui_update(sa10_w18_entry,SA10W18)
                    safe_gui_update(sa10_w19_entry,SA10W19)
                    safe_gui_update(sa10_w20_entry,SA10W20)
                    safe_gui_update(sa10_w21_entry,SA10W21)
                    safe_gui_update(sa10_w22_entry,SA10W22)
                    safe_gui_update(sa10_w23_w24_entry,SA10W23_W24)
                    safe_gui_update(sa10_w25_w26_entry,SA10W25_W26)
                    safe_gui_update(sa10_w27_w28_entry,SA10W27_W28)
                    safe_gui_update(sa10_w29_w30_entry,SA10W29_W30)
                    safe_gui_update(sa10_w31_w32_entry,SA10W31_W32)
                    
                    safe_gui_update(sa11_w1_w2_entry,SA11W1_W2)
                    safe_gui_update(sa11_w3_w4_entry,SA11W3_W4)
                    safe_gui_update(sa11_w5_w6_entry,SA11W5_W6)
                    safe_gui_update(sa11_w7_w8_entry,SA11W7_W8)
                    safe_gui_update(sa11_w9_w10_entry,SA11W9_W10)
                    safe_gui_update(sa11_w11_w12_entry,SA11W11_W12)
                    safe_gui_update(sa11_w13_w14_entry,SA11W13_W14)
                    safe_gui_update(sa11_w15_entry,SA11W15 )
                    safe_gui_update(sa11_w16_entry,SA11W16 )
                    safe_gui_update(sa11_w17_w18_entry,SA11W17_W18 )
                    safe_gui_update(sa11_w19_entry,SA11W19 )
                    safe_gui_update(sa11_w20_entry,SA11W20 )
                    safe_gui_update(sa11_w21_entry,SA11W21 )
                    safe_gui_update(sa11_w22_entry,SA11W22 )
                    safe_gui_update(sa11_w23_entry,SA11W23)
                    safe_gui_update(sa11_w24_entry,SA11W24 )
                    safe_gui_update(sa11_w25_w26_entry,SA11W25_W26)
                    safe_gui_update(sa11_w27_w28_entry,SA11W27_W28)
                    safe_gui_update(sa11_w29_entry,SA11W29 )
                    safe_gui_update(sa11_w30_w31_entry,SA11W30_W31)
                    safe_gui_update(sa11_w32_entry,SA11W32 )
                    
                    safe_gui_update(sa12_w1_entry,SA12W1)
                    safe_gui_update(sa12_w2_entry,SA12W2)
                    safe_gui_update(sa12_w3_entry,SA12W3)
                    safe_gui_update(sa12_w4_entry,SA12W4)
                    safe_gui_update(sa12_w5_entry,SA12W5)
                    safe_gui_update(sa12_w6_entry,SA12W6)
                    safe_gui_update(sa12_w7_entry,SA12W7)
                    safe_gui_update(sa12_w8_entry,SA12W8)
                    safe_gui_update(sa12_w9_entry,SA12W9)
                    safe_gui_update(sa12_w10_entry,SA12W10)
                    safe_gui_update(sa12_w11_entry,SA12W11)
                    safe_gui_update(sa12_w12_entry,SA12W12)
                    safe_gui_update(sa12_w13_entry,SA12W13)
                    safe_gui_update(sa12_w14_entry,SA12W14)
                    safe_gui_update(sa12_w15_entry,SA12W15)
                    safe_gui_update(sa12_w16_entry,SA12W16)
                    safe_gui_update(sa12_w17_entry,SA12W17)
                    safe_gui_update(sa12_w18_entry,SA12W18)
                    safe_gui_update(sa12_w19_w20_entry,SA12W19_W20)
                    safe_gui_update(sa12_w21_w22_entry,SA12W21_W22)
                    safe_gui_update(sa12_w23_w24_entry,SA12W23_W24)
                    safe_gui_update(sa12_w25_w26_entry,SA12W25_W26)
                    safe_gui_update(sa12_w27_w28_entry,SA12W27_W28)
                    safe_gui_update(sa12_w29_w30_entry,SA12W29_W30)
                    safe_gui_update(sa12_w31_entry,SA12W31)
                    safe_gui_update(sa12_w32_entry,SA12W32)
                    
                    safe_gui_update(sa13_w1_entry,SA13W1)
                    safe_gui_update(sa13_w2_entry,SA13W2)
                    safe_gui_update(sa13_w3_entry,SA13W3)
                    safe_gui_update(sa13_w4_entry,SA13W4)
                    safe_gui_update(sa13_w5_entry,SA13W5)
                    safe_gui_update(sa13_w6_entry,SA13W6)
                    safe_gui_update(sa13_w7_entry,SA13W7)
                    safe_gui_update(sa13_w8_entry,SA13W8)
                    safe_gui_update(sa13_w9_entry,SA13W9)
                    safe_gui_update(sa13_w10_entry,SA13W10)
                    safe_gui_update(sa13_w11_entry,SA13W11)
                    safe_gui_update(sa13_w12_entry,SA13W12)
                    safe_gui_update(sa13_w13_entry,SA13W13)
                    safe_gui_update(sa13_w14_entry,SA13W14)
                    safe_gui_update(sa13_w15_entry,SA13W15)
                    safe_gui_update(sa13_w16_entry,SA13W16)
                    safe_gui_update(sa13_w17_entry,SA13W17)
                    safe_gui_update(sa13_w18_entry,SA13W18)
                    safe_gui_update(sa13_w19_entry,SA13W19)
                    safe_gui_update(sa13_w20_entry,SA13W20)
                    safe_gui_update(sa13_w21_entry,SA13W21)
                    safe_gui_update(sa13_w22_entry,SA13W22)
                    safe_gui_update(sa13_w23_entry,SA13W23)
                    safe_gui_update(sa13_w24_entry,SA13W24)
                    safe_gui_update(sa13_w25_entry,SA13W25)
                    safe_gui_update(sa13_w26_entry,SA13W26)
                    safe_gui_update(sa13_w27_entry,SA13W27)
                    safe_gui_update(sa13_w28_entry,SA13W28)
                    safe_gui_update(sa13_w29_entry,SA13W29)
                    safe_gui_update(sa13_w30_entry,SA13W30)
                    safe_gui_update(sa13_w31_entry,SA13W31)
                    safe_gui_update(sa13_w32_entry,SA13W32)
                    
                    safe_gui_update(sa14_w1_entry,SA14W1)
                    safe_gui_update(sa14_w2_entry,SA14W2)
                    safe_gui_update(sa14_w3_entry,SA14W3)
                    safe_gui_update(sa14_w4_entry,SA14W4)
                    safe_gui_update(sa14_w5_entry,SA14W5)
                    safe_gui_update(sa14_w6_entry,SA14W6)
                    safe_gui_update(sa14_w7_entry,SA14W7)
                    safe_gui_update(sa14_w8_entry,SA14W8)
                    safe_gui_update(sa14_w9_entry,SA14W9)
                    safe_gui_update(sa14_w10_entry,SA14W10)
                    safe_gui_update(sa14_w11_entry,SA14W11)
                    safe_gui_update(sa14_w12_entry,SA14W12)
                    safe_gui_update(sa14_w13_entry,SA14W13)
                    safe_gui_update(sa14_w14_entry,SA14W14)
                    safe_gui_update(sa14_w15_entry,SA14W15)
                    safe_gui_update(sa14_w16_entry,SA14W16)
                    safe_gui_update(sa14_w17_entry,SA14W17)
                    safe_gui_update(sa14_w18_entry,SA14W18)
                    safe_gui_update(sa14_w19_entry,SA14W19)
                    safe_gui_update(sa14_w20_entry,SA14W20)
                    safe_gui_update(sa14_w21_entry,SA14W21)
                    safe_gui_update(sa14_w22_entry,SA14W22)
                    safe_gui_update(sa14_w23_entry,SA14W23)
                    safe_gui_update(sa14_w24_entry,SA14W24)
                    safe_gui_update(sa14_w25_entry,SA14W25)
                    safe_gui_update(sa14_w26_entry,SA14W26)
                    safe_gui_update(sa14_w27_entry,SA14W27)
                    safe_gui_update(sa14_w28_entry,SA14W28)
                    safe_gui_update(sa14_w29_entry,SA14W29)
                    safe_gui_update(sa14_w30_entry,SA14W30)
                    safe_gui_update(sa14_w31_entry,SA14W31)
                    safe_gui_update(sa14_w32_entry,SA14W32)
                    
                    safe_gui_update(sa15_w1_entry,SA15W1)
                    safe_gui_update(sa15_w2_entry,SA15W2)
                    safe_gui_update(sa15_w3_w4_entry,SA15W3_W4)
                    safe_gui_update(sa15_w5_w6_entry,SA15W5_W6)
                    safe_gui_update(sa15_w7_w8_entry,SA15W7_W8)
                    safe_gui_update(sa15_w9_w10_entry,SA15W9_W10)
                    safe_gui_update(sa15_w11_w12_entry,SA15W11_W12)
                    safe_gui_update(sa15_w13_w14_entry,SA15W13_W14)
                    safe_gui_update(sa15_w15_w16_entry,SA15W15_W16)
                    safe_gui_update(sa15_w17_w18_entry,SA15W17_W18)
                    safe_gui_update(sa15_w19_w20_entry,SA15W19_W20)
                    safe_gui_update(sa15_w21_w22_entry,SA15W21_W22)
                    safe_gui_update(sa15_w23_w24_entry,SA15W23_W24)
                    safe_gui_update(sa15_w25_w26_entry,SA15W25_W26)
                    safe_gui_update(sa15_w27_w28_entry,SA15W27_W28)
                    safe_gui_update(sa15_w29_w30_entry,SA15W29_W30)
                    safe_gui_update(sa15_w31_entry,SA15W31)
                    safe_gui_update(sa15_w32_entry,SA15W32)
                    
                    
                    safe_gui_update(sa16_w1_entry,SA16W1)
                    safe_gui_update(sa16_w2_entry,SA16W2)
                    safe_gui_update(sa16_w3_w4_entry,SA16W3_W4)
                    safe_gui_update(sa16_w5_entry,SA16W5)
                    safe_gui_update(sa16_w6_entry,SA16W6)
                    safe_gui_update(sa16_w7_entry,SA16W7)
                    safe_gui_update(sa16_w8_w9_entry,SA16W8_W9)
                    safe_gui_update(sa16_w10_w11_entry,SA16W10_W11)
                    safe_gui_update(sa16_w12_w13_entry,SA16W12_W13)
                    safe_gui_update(sa16_w14_w15_entry,SA16W14_W15)
                    safe_gui_update(sa16_w16_w17_entry,SA16W16_W17)
                    safe_gui_update(sa16_w18_w19_entry,SA16W18_W19)
                    safe_gui_update(sa16_w20_w21_entry,SA16W20_W21)
                    safe_gui_update(sa16_w22_w23_entry,SA16W22_W23)
                    safe_gui_update(sa16_w24_w29_entry,SA16W24_W29_hex)
                    safe_gui_update(sa16_w30_w31_entry,SA16W30_W31)
                    safe_gui_update(sa16_w32_entry,SA16W32)
                    
                    safe_gui_update(sa17_w1_entry,SA17W1)
                    safe_gui_update(sa17_w2_entry,SA17W2)
                    safe_gui_update(sa17_w3_entry,SA17W3)
                    safe_gui_update(sa17_w4_entry,SA17W4)
                    safe_gui_update(sa17_w5_entry,SA17W5)
                    safe_gui_update(sa17_w6_entry,SA17W6)
                    safe_gui_update(sa17_w7_entry,SA17W7)
                    safe_gui_update(sa17_w8_entry,SA17W8)
                    safe_gui_update(sa17_w9_entry,SA17W9)
                    safe_gui_update(sa17_w10_entry,SA17W10)
                    safe_gui_update(sa17_w11_entry,SA17W11)
                    safe_gui_update(sa17_w12_entry,SA17W12)
                    safe_gui_update(sa17_w13_entry,SA17W13)
                    safe_gui_update(sa17_w14_entry,SA17W14)
                    safe_gui_update(sa17_w15_entry,SA17W15)
                    safe_gui_update(sa17_w16_entry,SA17W16)
                    safe_gui_update(sa17_w17_entry,SA17W17)
                    safe_gui_update(sa17_w18_entry,SA17W18)
                    safe_gui_update(sa17_w19_entry,SA17W19)
                    safe_gui_update(sa17_w20_entry,SA17W20)
                    safe_gui_update(sa17_w21_entry,SA17W21)
                    safe_gui_update(sa17_w22_entry,SA17W22)
                    safe_gui_update(sa17_w23_entry,SA17W23)
                    safe_gui_update(sa17_w24_entry,SA17W24)
                    safe_gui_update(sa17_w25_entry,SA17W25)
                    safe_gui_update(sa17_w26_w30_entry,SA17W26_w30_hex)
                    safe_gui_update(sa17_w31_entry,SA17W31)
                    safe_gui_update(sa17_w32_entry,SA17W32)
                    
                    safe_gui_update(sa18_w1_entry,SA18W1)
                    safe_gui_update(sa18_w2_entry,SA18W2)
                    safe_gui_update(sa18_w3_entry,SA18W3)
                    safe_gui_update(sa18_w4_entry,SA18W4)
                    safe_gui_update(sa18_w5_entry,SA18W5)
                    safe_gui_update(sa18_w6_entry,SA18W6)
                    safe_gui_update(sa18_w7_entry,SA18W7)
                    safe_gui_update(sa18_w8_entry,SA18W8)
                    safe_gui_update(sa18_w9_entry,SA18W9)
                    safe_gui_update(sa18_w10_entry,SA18W10)
                    safe_gui_update(sa18_w11_entry,SA18W11)
                    safe_gui_update(sa18_w12_entry,SA18W12)
                    safe_gui_update(sa18_w13_entry,SA18W13)
                    safe_gui_update(sa18_w14_entry,SA18W14)
                    safe_gui_update(sa18_w15_entry,SA18W15)
                    safe_gui_update(sa18_w16_entry,SA18W16)
                    safe_gui_update(sa18_w17_entry,SA18W17)
                    safe_gui_update(sa18_w18_entry,SA18W18)
                    safe_gui_update(sa18_w19_entry,SA18W19)
                    safe_gui_update(sa18_w20_entry,SA18W20)
                    safe_gui_update(sa18_w21_entry,SA18W21)
                    safe_gui_update(sa18_w22_entry,SA18W22)
                    safe_gui_update(sa18_w23_entry,SA18W23)
                    safe_gui_update(sa18_w24_entry,SA18W24)
                    safe_gui_update(sa18_w25_entry,SA18W25)
                    safe_gui_update(sa18_w26_w30_entry,SA18W26_w30_hex)
                    safe_gui_update(sa18_w31_entry,SA18W31)
                    safe_gui_update(sa18_w32_entry,SA18W32)
                    
                    safe_gui_update(sa19_w1_entry,SA19W1)
                    safe_gui_update(sa19_w2_entry,SA19W2)
                    safe_gui_update(sa19_w3_entry,SA19W3)
                    safe_gui_update(sa19_w4_entry,SA19W4)
                    safe_gui_update(sa19_w5_entry,SA19W5)
                    safe_gui_update(sa19_w6_entry,SA19W6)
                    safe_gui_update(sa19_w7_entry,SA19W7)
                    safe_gui_update(sa19_w8_entry,SA19W8)
                    safe_gui_update(sa19_w9_entry,SA19W9)
                    safe_gui_update(sa19_w10_entry,SA19W10)
                    safe_gui_update(sa19_w11_entry,SA19W11)
                    safe_gui_update(sa19_w12_entry,SA19W12)
                    safe_gui_update(sa19_w13_entry,SA19W13)
                    safe_gui_update(sa19_w14_entry,SA19W14)
                    safe_gui_update(sa19_w15_entry,SA19W15)
                    safe_gui_update(sa19_w16_entry,SA19W16)
                    safe_gui_update(sa19_w17_entry,SA19W17)
                    safe_gui_update(sa19_w18_entry,SA19W18)
                    safe_gui_update(sa19_w19_entry,SA19W19)
                    safe_gui_update(sa19_w20_entry,SA19W20)
                    safe_gui_update(sa19_w21_entry,SA19W21)
                    safe_gui_update(sa19_w22_entry,SA19W22)
                    safe_gui_update(sa19_w23_entry,SA19W23)
                    safe_gui_update(sa19_w24_entry,SA19W24)
                    safe_gui_update(sa19_w25_entry,SA19W25)
                    safe_gui_update(sa19_w26_entry,SA19W26)
                    safe_gui_update(sa19_w27_entry,SA19W27)
                    safe_gui_update(sa19_w28_entry,SA19W28)
                    safe_gui_update(sa19_w29_entry,SA19W29)
                    safe_gui_update(sa19_w30_entry,SA19W30)
                    safe_gui_update(sa19_w31_entry,SA19W31)
                    safe_gui_update(sa19_w32_entry,SA19W32)
                    
                    safe_gui_update(sa20_w1_entry,SA20W1)
                    safe_gui_update(sa20_w2_entry,SA20W2)
                    safe_gui_update(sa20_w3_entry,SA20W3)
                    safe_gui_update(sa20_w4_entry,SA20W4)
                    safe_gui_update(sa20_w5_entry,SA20W5)
                    safe_gui_update(sa20_w6_entry,SA20W6)
                    safe_gui_update(sa20_w7_entry,SA20W7)
                    safe_gui_update(sa20_w8_entry,SA20W8)
                    safe_gui_update(sa20_w9_entry,SA20W9)
                    safe_gui_update(sa20_w10_entry,SA20W10)
                    safe_gui_update(sa20_w11_entry,SA20W11)
                    safe_gui_update(sa20_w12_entry,SA20W12)
                    safe_gui_update(sa20_w13_entry,SA20W13)
                    safe_gui_update(sa20_w14_entry,SA20W14)
                    safe_gui_update(sa20_w15_entry,SA20W15)
                    safe_gui_update(sa20_w16_entry,SA20W16)
                    safe_gui_update(sa20_w17_entry,SA20W17)
                    safe_gui_update(sa20_w18_entry,SA20W18)
                    safe_gui_update(sa20_w19_entry,SA20W19)
                    safe_gui_update(sa20_w20_entry,SA20W20)
                    safe_gui_update(sa20_w21_entry,SA20W21)
                    safe_gui_update(sa20_w22_entry,SA20W22)
                    safe_gui_update(sa20_w23_entry,SA20W23)
                    safe_gui_update(sa20_w24_entry,SA20W24)
                    safe_gui_update(sa20_w25_entry,SA20W25)
                    safe_gui_update(sa20_w26_entry,SA20W26)
                    safe_gui_update(sa20_w27_entry,SA20W27)
                    safe_gui_update(sa20_w28_entry,SA20W28)
                    safe_gui_update(sa20_w29_entry,SA20W29)
                    safe_gui_update(sa20_w30_entry,SA20W30)
                    safe_gui_update(sa20_w31_entry,SA20W31)
                    safe_gui_update(sa20_w32_entry,SA20W32)
                    
                    safe_gui_update(sa21_w1_entry,SA21W1)
                    safe_gui_update(sa21_w2_entry,SA21W2)
                    safe_gui_update(sa21_w3_entry,SA21W3)
                    safe_gui_update(sa21_w4_entry,SA21W4)
                    safe_gui_update(sa21_w5_entry,SA21W5)
                    safe_gui_update(sa21_w6_entry,SA21W6)
                    safe_gui_update(sa21_w7_entry,SA21W7)
                    safe_gui_update(sa21_w8_entry,SA21W8)
                    safe_gui_update(sa21_w9_entry,SA21W9)
                    safe_gui_update(sa21_w10_entry,SA21W10)
                    safe_gui_update(sa21_w11_entry,SA21W11)
                    safe_gui_update(sa21_w12_entry,SA21W12)
                    safe_gui_update(sa21_w13_entry,SA21W13)
                    safe_gui_update(sa21_w14_entry,SA21W14)
                    safe_gui_update(sa21_w15_entry,SA21W15)
                    safe_gui_update(sa21_w16_entry,SA21W16)
                    safe_gui_update(sa21_w17_entry,SA21W17)
                    safe_gui_update(sa21_w18_entry,SA21W18)
                    safe_gui_update(sa21_w19_entry,SA21W19)
                    safe_gui_update(sa21_w20_entry,SA21W20)
                    safe_gui_update(sa21_w21_entry,SA21W21)
                    safe_gui_update(sa21_w22_entry,SA21W22)
                    safe_gui_update(sa21_w23_entry,SA21W23)
                    safe_gui_update(sa21_w24_entry,SA21W24)
                    safe_gui_update(sa21_w25_entry,SA21W25)
                    safe_gui_update(sa21_w26_entry,SA21W26)
                    safe_gui_update(sa21_w27_entry,SA21W27)
                    safe_gui_update(sa21_w28_entry,SA21W28)
                    safe_gui_update(sa21_w29_entry,SA21W29)
                    safe_gui_update(sa21_w30_entry,SA21W30)
                    safe_gui_update(sa21_w31_entry,SA21W31)
                    safe_gui_update(sa21_w32_entry,SA21W32)
                    
                    safe_gui_update(sa22_w2_entry,SA22W2)
                    safe_gui_update(sa22_w3_entry,SA22W3)
                    safe_gui_update(sa22_w4_entry,SA22W4)
                    safe_gui_update(sa22_w5_entry,SA22W5)
                    safe_gui_update(sa22_w6_entry,SA22W6)
                    safe_gui_update(sa22_w7_entry,SA22W7)
                    safe_gui_update(sa22_w8_entry,SA22W8)
                    safe_gui_update(sa22_w9_entry,SA22W9)
                    safe_gui_update(sa22_w10_entry,SA22W10)
                    safe_gui_update(sa22_w11_entry,SA22W11)
                    safe_gui_update(sa22_w12_entry,SA22W12)
                    safe_gui_update(sa22_w13_entry,SA22W13)
                    safe_gui_update(sa22_w14_entry,SA22W14)
                    safe_gui_update(sa22_w15_entry,SA22W15)
                    safe_gui_update(sa22_w16_entry,SA22W16)
                    safe_gui_update(sa22_w17_entry,SA22W17)
                    safe_gui_update(sa22_w18_entry,SA22W18)
                    safe_gui_update(sa22_w19_entry,SA22W19)
                    safe_gui_update(sa22_w20_entry,SA22W20)
                    safe_gui_update(sa22_w21_entry,SA22W21)
                    safe_gui_update(sa22_w22_entry,SA22W22)
                    safe_gui_update(sa22_w23_entry,SA22W23)
                    safe_gui_update(sa22_w24_entry,SA22W24)
                    safe_gui_update(sa22_w25_entry,SA22W25)
                    safe_gui_update(sa22_w26_entry,SA22W26)
                    safe_gui_update(sa22_w27_entry,SA22W27)
                    safe_gui_update(sa22_w28_entry,SA22W28)
                    safe_gui_update(sa22_w29_entry,SA22W29)
                    safe_gui_update(sa22_w30_entry,SA22W30)
                    safe_gui_update(sa22_w31_entry,SA22W31)
                    safe_gui_update(sa22_w32_entry,SA22W32)
                    
                    safe_gui_update(sa23_w1_entry,SA23W1)
                    safe_gui_update(sa23_w2_entry,SA23W2)
                    safe_gui_update(sa23_w3_entry,SA23W3)
                    safe_gui_update(sa23_w4_entry,SA23W4)
                    safe_gui_update(sa23_w5_entry,SA23W5)
                    safe_gui_update(sa23_w6_entry,SA23W6)
                    safe_gui_update(sa23_w7_entry,SA23W7)
                    safe_gui_update(sa23_w8_entry,SA23W8)
                    safe_gui_update(sa23_w9_entry,SA23W9)
                    safe_gui_update(sa23_w10_entry,SA23W10)
                    safe_gui_update(sa23_w11_entry,SA23W11)
                    safe_gui_update(sa23_w12_entry,SA23W12)
                    safe_gui_update(sa23_w13_entry,SA23W13)
                    safe_gui_update(sa23_w14_entry,SA23W14)
                    safe_gui_update(sa23_w15_entry,SA23W15)
                    safe_gui_update(sa23_w16_entry,SA23W16)
                    safe_gui_update(sa23_w17_entry,SA23W17)
                    safe_gui_update(sa23_w18_entry,SA23W18)
                    safe_gui_update(sa23_w19_entry,SA23W19)
                    safe_gui_update(sa23_w20_entry,SA23W20)
                    safe_gui_update(sa23_w21_entry,SA23W21)
                    safe_gui_update(sa23_w22_entry,SA23W22)
                    safe_gui_update(sa23_w23_entry,SA23W23)
                    safe_gui_update(sa23_w24_entry,SA23W24)
                    safe_gui_update(sa23_w25_entry,SA23W25)
                    safe_gui_update(sa23_w26_entry,SA23W26)
                    safe_gui_update(sa23_w27_entry,SA23W27)
                    safe_gui_update(sa23_w28_entry,SA23W28)
                    safe_gui_update(sa23_w29_entry,SA23W29)
                    safe_gui_update(sa23_w30_entry,SA23W30)
                    safe_gui_update(sa23_w31_entry,SA23W31)
                    safe_gui_update(sa23_w32_entry,SA23W32)
                    
                    safe_gui_update(sa24_w2_entry,SA24W2)
                    safe_gui_update(sa24_w3_entry,SA24W3)
                    safe_gui_update(sa24_w4_entry,SA24W4)
                    safe_gui_update(sa24_w5_entry,SA24W5)
                    safe_gui_update(sa24_w6_entry,SA24W6)
                    safe_gui_update(sa24_w7_entry,SA24W7)
                    safe_gui_update(sa24_w8_entry,SA24W8)
                    safe_gui_update(sa24_w9_entry,SA24W9)
                    safe_gui_update(sa24_w10_entry,SA24W10)
                    safe_gui_update(sa24_w11_entry,SA24W11)
                    safe_gui_update(sa24_w12_entry,SA24W12)
                    safe_gui_update(sa24_w13_entry,SA24W13)
                    safe_gui_update(sa24_w14_entry,SA24W14)
                    safe_gui_update(sa24_w15_entry,SA24W15)
                    safe_gui_update(sa24_w16_entry,SA24W16)
                    safe_gui_update(sa24_w17_entry,SA24W17)
                    safe_gui_update(sa24_w18_entry,SA24W18)
                    safe_gui_update(sa24_w19_entry,SA24W19)
                    safe_gui_update(sa24_w20_entry,SA24W20)
                    safe_gui_update(sa24_w21_entry,SA24W21)
                    safe_gui_update(sa24_w22_entry,SA24W22)
                    safe_gui_update(sa24_w23_entry,SA24W23)
                    safe_gui_update(sa24_w24_entry,SA24W24)
                    safe_gui_update(sa24_w25_entry,SA24W25)
                    safe_gui_update(sa24_w26_entry,SA24W26)
                    safe_gui_update(sa24_w27_entry,SA24W27)
                    safe_gui_update(sa24_w28_entry,SA24W28)
                    safe_gui_update(sa24_w29_entry,SA24W29)
                    safe_gui_update(sa24_w30_entry,SA24W30)
                    safe_gui_update(sa24_w31_entry,SA24W31)
                    safe_gui_update(sa24_w32_entry,SA24W32)
                    
                    safe_gui_update(sa25_w1_entry,SA25W1)
                    safe_gui_update(sa25_w2_entry,SA25W2)
                    safe_gui_update(sa25_w3_entry,SA25W3)
                    safe_gui_update(sa25_w4_entry,SA25W4)
                    safe_gui_update(sa25_w5_entry,SA25W5)
                    safe_gui_update(sa25_w6_entry,SA25W6)
                    safe_gui_update(sa25_w7_entry,SA25W7)
                    safe_gui_update(sa25_w8_entry,SA25W8)
                    safe_gui_update(sa25_w9_entry,SA25W9)
                    safe_gui_update(sa25_w10_entry,SA25W10)
                    safe_gui_update(sa25_w11_entry,SA25W11)
                    safe_gui_update(sa25_w12_entry,SA25W12)
                    safe_gui_update(sa25_w13_entry,SA25W13)
                    safe_gui_update(sa25_w14_entry,SA25W14)
                    safe_gui_update(sa25_w15_entry,SA25W15)
                    safe_gui_update(sa25_w16_entry,SA25W16)
                    safe_gui_update(sa25_w17_entry,SA25W17)
                    safe_gui_update(sa25_w18_entry,SA25W18)
                    safe_gui_update(sa25_w19_entry,SA25W19)
                    safe_gui_update(sa25_w20_entry,SA25W20)
                    safe_gui_update(sa25_w21_entry,SA25W21)
                    safe_gui_update(sa25_w22_entry,SA25W22)
                    safe_gui_update(sa25_w23_entry,SA25W23)
                    safe_gui_update(sa25_w24_entry,SA25W24)
                    safe_gui_update(sa25_w25_entry,SA25W25)
                    safe_gui_update(sa25_w26_entry,SA25W26)
                    safe_gui_update(sa25_w27_entry,SA25W27)
                    safe_gui_update(sa25_w28_entry,SA25W28)
                    safe_gui_update(sa25_w29_entry,SA25W29)
                    safe_gui_update(sa25_w30_entry,SA25W30)
                    safe_gui_update(sa25_w31_entry,SA25W31)
                    safe_gui_update(sa25_w32_entry,SA25W32)
                    
                    safe_gui_update(sa26_w2_entry,SA26W2)
                    safe_gui_update(sa26_w3_entry,SA26W3)
                    safe_gui_update(sa26_w4_entry,SA26W4)
                    safe_gui_update(sa26_w5_entry,SA26W5)
                    safe_gui_update(sa26_w6_entry,SA26W6)
                    safe_gui_update(sa26_w7_entry,SA26W7)
                    safe_gui_update(sa26_w8_entry,SA26W8)
                    safe_gui_update(sa26_w9_entry,SA26W9)
                    safe_gui_update(sa26_w10_entry,SA26W10)
                    safe_gui_update(sa26_w11_entry,SA26W11)
                    safe_gui_update(sa26_w12_entry,SA26W12)
                    safe_gui_update(sa26_w13_entry,SA26W13)
                    safe_gui_update(sa26_w14_entry,SA26W14)
                    safe_gui_update(sa26_w15_entry,SA26W15)
                    safe_gui_update(sa26_w16_entry,SA26W16)
                    safe_gui_update(sa26_w17_entry,SA26W17)
                    safe_gui_update(sa26_w18_entry,SA26W18)
                    safe_gui_update(sa26_w19_entry,SA26W19)
                    safe_gui_update(sa26_w20_entry,SA26W20)
                    safe_gui_update(sa26_w21_entry,SA26W21)
                    safe_gui_update(sa26_w22_entry,SA26W22)
                    safe_gui_update(sa26_w23_entry,SA26W23)
                    safe_gui_update(sa26_w24_entry,SA26W24)
                    safe_gui_update(sa26_w25_entry,SA26W25)
                    safe_gui_update(sa26_w26_entry,SA26W26)
                    safe_gui_update(sa26_w27_entry,SA26W27)
                    safe_gui_update(sa26_w28_entry,SA26W28)
                    safe_gui_update(sa26_w29_entry,SA26W29)
                    safe_gui_update(sa26_w30_entry,SA26W30)
                    safe_gui_update(sa26_w31_entry,SA26W31)
                    safe_gui_update(sa26_w32_entry,SA26W32)
                    
                    safe_gui_update(sa27_w1_entry,SA27W1)
                    safe_gui_update(sa27_w2_entry,SA27W2)
                    safe_gui_update(sa27_w3_entry,SA27W3)
                    safe_gui_update(sa27_w4_entry,SA27W4)
                    safe_gui_update(sa27_w5_entry,SA27W5)
                    safe_gui_update(sa27_w6_entry,SA27W6)
                    safe_gui_update(sa27_w7_entry,SA27W7)
                    safe_gui_update(sa27_w8_entry,SA27W8)
                    safe_gui_update(sa27_w9_entry,SA27W9)
                    safe_gui_update(sa27_w10_entry,SA27W10)
                    safe_gui_update(sa27_w11_entry,SA27W11)
                    safe_gui_update(sa27_w12_entry,SA27W12)
                    safe_gui_update(sa27_w13_entry,SA27W13)
                    safe_gui_update(sa27_w14_entry,SA27W14)
                    safe_gui_update(sa27_w15_entry,SA27W15)
                    safe_gui_update(sa27_w16_entry,SA27W16)
                    safe_gui_update(sa27_w17_entry,SA27W17)
                    safe_gui_update(sa27_w18_entry,SA27W18)
                    safe_gui_update(sa27_w19_entry,SA27W19)
                    safe_gui_update(sa27_w20_entry,SA27W20)
                    safe_gui_update(sa27_w21_entry,SA27W21)
                    safe_gui_update(sa27_w22_entry,SA27W22)
                    safe_gui_update(sa27_w23_entry,SA27W23)
                    safe_gui_update(sa27_w24_entry,SA27W24)
                    safe_gui_update(sa27_w25_entry,SA27W25)
                    safe_gui_update(sa27_w26_entry,SA27W26)
                    safe_gui_update(sa27_w27_entry,SA27W27)
                    safe_gui_update(sa27_w28_entry,SA27W28)
                    safe_gui_update(sa27_w29_entry,SA27W29)
                    safe_gui_update(sa27_w30_entry,SA27W30)
                    safe_gui_update(sa27_w31_entry,SA27W31)
                    safe_gui_update(sa27_w32_entry,SA27W32)
                    

                    
                    safe_gui_update(est_rec_clk_entry, est_rec_clk)
                    safe_gui_update(est_rec_clk_bias_entry,Est_rec_clk_bias)
                    safe_gui_update(LCOR_entry, LCOR)
                    safe_gui_update(str_crr_clk_entry, Str_crr_clk)
                    safe_gui_update(diff_entry,f"{current_time_diff:.3f}")
                    safe_gui_update(time_entry4, f"{rss_pos:.3f}")
                    safe_gui_update(nanotime_entry4, f"{rss_vel:.3f}")
                    safe_gui_update(odp_pos_err_entry, f"{odp_rss_pos:.3f}")
                    safe_gui_update(odp_vel_err_entry, f"{odp_rss_vel:.3f}")

                root.after(0, apply_updates)  # ✅ Thread-safe GUI commit

                current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                base_name = file_entry1.get()

                '''data_row = [current_timestamp,SYN_Second,SYN_NanoSecond,SYN_Weeknumber]
                write_to_SYN(data_row,base_name)'''

                data_row = [Raw_data]
                write_to_raw(data_row,base_name)
                
                
                data_row = [current_timestamp,hexDecodedData]
                write_to_raw_withheader1(data_row,base_name)
                




                data_row = [current_timestamp,SYS_Second,SYS_NanoSecond,SYS_Weeknumber,
                            PPS_Sec,PPS_NanoSec,PPS_Week,PPS_3D,
                            INST_x,INST_y,INST_z,INST_vx,INST_vy,INST_vz,
                            EST_x,EST_y,EST_z,EST_vx,EST_vy,EST_vz,
                            UpdateCounter,MC,SPS_CMD_COUNTER,UPSET_COUNTER,
                            checksum,checksum1,ODP_FLAG,PDOP,
                            CLOCKBIAS,INTER_SYSTEM_BIAS,DRIFT,ISD,Steering_Bias,
                            Steering_Drift,Steering_clock,U1_data,U2_data,
                            Last_cmd_excuted_byte1_2,Last_cmd_excuted_byte3,Last_cmd_excuted_byte4,ACQ1_SVID,SWDT_RST_COUNTER,Remote_Read_Write1,Remote_Read_Write2,Remote_Read_Write3,Remote_Read_Write4,Remote_Read_Write5,Remote_Read_Write6,
                            SA8W3,SA8W4,SA8W5,SA8W6,SA8W7,SA8W8,SA8W9_W10, SA8W11_W12,SA8W13_W14,SA8W15_W16,SA8W17_W18,SA8W19_W20,SA8W21_W22,SA8W23_W24,SA8W25_W26,SA8W27_W28,SA8W29_W30,SA8W31_W32,
                            SA9W1,SA9W2,SA9W3, SA9W4,SA9W5, SA9W6,SA9W7,SA9W8, SA9W9,SA9W10, SA9W11, SA9W12,SA9W13,SA9W14_W15,SA9W16_W17, SA9W18_W19,SA9W20_W21,SA9W22_W23,SA9W24_W25,SA9W26, SA9W27,SA9W28, SA9W29,SA9W30_W31,SA9W32,
                            SA10W1,SA10W2,SA10W3,SA10W4,SA10W5,SA10W6,SA10W7,SA10W8,SA10W9_W10,SA10W11_W12, SA10W13_W14,SA10W15, SA10W16,SA10W17,SA10W18,SA10W19,SA10W20,SA10W21,SA10W22,SA10W23_W24,SA10W25_W26,SA10W27_W28,SA10W29_W30,SA10W31_W32,
                            SA11W1_W2,SA11W3_W4,SA11W5_W6,SA11W7_W8,SA11W9_W10,SA11W11_W12,SA11W13_W14,SA11W15,SA11W16,SA11W17_W18,SA11W19,SA11W20,SA11W21,SA11W22,SA11W23,SA11W24,SA11W25_W26,SA11W27_W28,SA11W29,SA11W30_W31,SA11W32,
                            SA12W1,SA12W2,SA12W3,SA12W4,SA12W5,SA12W6,SA12W7,SA12W8,SA12W9,SA12W10,SA12W11,SA12W12,SA12W13,SA12W14,SA12W15,
                            SA12W16,SA12W17,SA12W18,SA12W19_W20,SA12W21_W22,SA12W23_W24,SA12W25_W26,SA12W27_W28,SA12W29_W30,SA12W31,SA12W32,
                            SA13W1,SA13W2,SA13W3,SA13W4,SA13W5,SA13W6,SA13W7,SA13W8,SA13W9,SA13W10,SA13W11,SA13W12,SA13W13,SA13W14,SA13W15,
                            SA13W16,SA13W17,SA13W18,SA13W19,SA13W20,SA13W21,SA13W22,SA13W23,SA13W24,SA13W25,SA13W26,SA13W27,SA13W28,SA13W29,SA13W30,SA13W31,SA13W32,
                            SA14W1,SA14W2,SA14W3,SA14W4,SA14W5,SA14W6,SA14W7,SA14W8,SA14W9,SA14W10,SA14W11,SA14W12,SA14W13,SA14W14,SA14W15,
                            SA14W16,SA14W17,SA14W18,SA14W19,SA14W20,SA14W21,SA14W22,SA14W23,SA14W24,SA14W25,SA14W26,SA14W27,SA14W28,SA14W29,SA14W30,SA14W31,SA14W32,
                            SA15W1,SA15W2,SA15W3_W4,SA15W5_W6,SA15W7_W8,SA15W9_W10,SA15W11_W12,SA15W13_W14,SA15W15_W16,SA15W17_W18,SA15W19_W20,SA15W21_W22,SA15W23_W24,SA15W25_W26,SA15W27_W28,SA15W29_W30,SA15W31,SA15W32,
                            SA16W1,SA16W2,SA16W3_W4,SA16W5,SA16W6,SA16W7,SA16W8_W9,SA16W10_W11,SA16W12_W13,SA16W14_W15,SA16W16_W17,SA16W18_W19,SA16W20_W21,SA16W22_W23,SA16W24_W29_hex,SA16W30_W31,SA16W32,
                            SA17W1,SA17W2,SA17W3,SA17W4,SA17W5,SA17W6,SA17W7,SA17W8,SA17W9,SA17W10,SA17W11,SA17W12,SA17W13,SA17W14,SA17W15,
                            SA17W16,SA17W17,SA17W18,SA17W19,SA17W20,SA17W21,SA17W22,SA17W23,SA17W24,SA17W25,SA17W26_w30_hex,SA17W31,SA17W32,
                            SA18W1,SA18W2,SA18W3,SA18W4,SA18W5,SA18W6,SA18W7,SA18W8,SA18W9,SA18W10,SA18W11,SA18W12,SA18W13,SA18W14,SA18W15,
                            SA18W16,SA18W17,SA18W18,SA18W19,SA18W20,SA18W21,SA18W22,SA18W23,SA18W24,SA18W25,SA18W26_w30_hex,SA18W31,SA18W32,
                            SA19W1,SA19W2,SA19W3,SA19W4,SA19W5,SA19W6,SA19W7,SA19W8,SA19W9,SA19W10,SA19W11,SA19W12,SA19W13,SA19W14,SA19W15,
                            SA19W16,SA19W17,SA19W18,SA19W19,SA19W20,SA19W21,SA19W22,SA19W23,SA19W24,SA19W25,SA19W26,SA19W27,SA19W28,SA19W29,SA19W30,SA19W31,SA19W32,
                            SA20W1,SA20W2,SA20W3,SA20W4,SA20W5,SA20W6,SA20W7,SA20W8,SA20W9,SA20W10,SA20W11,SA20W12,SA20W13,SA20W14,SA20W15,
                            SA20W16,SA20W17,SA20W18,SA20W19,SA20W20,SA20W21,SA20W22,SA20W23,SA20W24,SA20W25,SA20W26,SA20W27,SA20W28,SA20W29,SA20W30,SA20W31,SA20W32,
                            SA21W1,SA21W2,SA21W3,SA21W4,SA21W5,SA21W6,SA21W7,SA21W8,SA21W9,SA21W10,SA21W11,SA21W12,SA21W13,SA21W14,SA21W15,
                            SA21W16,SA21W17,SA21W18,SA21W19,SA21W20,SA21W21,SA21W22,SA21W23,SA21W24,SA21W25,SA21W26,SA21W27,SA21W28,SA21W29,SA21W30,SA21W31,SA21W32,
                            SA22W1,SA22W2,SA22W3,SA22W4,SA22W5,SA22W6,SA22W7,SA22W8,SA22W9,SA22W10,SA22W11,SA22W12,SA22W13,SA22W14,SA22W15,
                            SA22W16,SA22W17,SA22W18,SA22W19,SA22W20,SA22W21,SA22W22,SA22W23,SA22W24,SA22W25,SA22W26,SA22W27,SA22W28,SA22W29,SA22W30,SA22W31,SA22W32,
                            SA23W1,SA23W2,SA23W3,SA23W4,SA23W5,SA23W6,SA23W7,SA23W8,SA23W9,SA23W10,SA23W11,SA23W12,SA23W13,SA23W14,SA23W15,
                            SA23W16,SA23W17,SA23W18,SA23W19,SA23W20,SA23W21,SA23W22,SA23W23,SA23W24,SA23W25,SA23W26,SA23W27,SA23W28,SA23W29,SA23W30,SA23W31,SA23W32,
                            SA24W1,SA24W2,SA24W3,SA24W4,SA24W5,SA24W6,SA24W7,SA24W8,SA24W9,SA24W10,SA24W11,SA24W12,SA24W13,SA24W14,SA24W15,
                            SA24W16,SA24W17,SA24W18,SA24W19,SA24W20,SA24W21,SA24W22,SA24W23,SA24W24,SA24W25,SA24W26,SA24W27,SA24W28,SA24W29,SA24W30,SA24W31,SA24W32,
                            SA25W1,SA25W2,SA25W3,SA25W4,SA25W5,SA25W6,SA25W7,SA25W8,SA25W9,SA25W10,SA25W11,SA25W12,SA25W13,SA25W14,SA25W15,
                            SA25W16,SA25W17,SA25W18,SA25W19,SA25W20,SA25W21,SA25W22,SA25W23,SA25W24,SA25W25,SA25W26,SA25W27,SA25W28,SA25W29,SA25W30,SA25W31,SA25W32,
                            SA26W1,SA26W2,SA26W3,SA26W4,SA26W5,SA26W6,SA26W7,SA26W8,SA26W9,SA26W10,SA26W11,SA26W12,SA26W13,SA26W14,SA26W15,
                            SA26W16,SA26W17,SA26W18,SA26W19,SA26W20,SA26W21,SA26W22,SA26W23,SA26W24,SA26W25,SA26W26,SA26W27,SA26W28,SA26W29,SA26W30,SA26W31,SA26W32,
                            SA27W1,SA27W2,SA27W3,SA27W4,SA27W5,SA27W6,SA27W7,SA27W8,SA27W9,SA27W10,SA27W11,SA27W12,SA27W13,SA27W14,SA27W15,
                            SA27W16,SA27W17,SA27W18,SA27W19,SA27W20,SA27W21,SA27W22,SA27W23,SA27W24,SA27W25,SA27W26,SA27W27,SA27W28,SA27W29,SA27W30,SA27W31,SA27W32,]


                str_Est = decoded32["Str_Est"]
                str_En = decoded32["Str_En"]
                reset_C = decoded32["Reset_C"]
                init = decoded32["Init"]

                data_row.extend([str_Est, str_En, reset_C,init]),


                hwdt_reset_counter = decoded25["HWDT Reset Counter"]
                swdt_reset_id = decoded25["SWDT Reset ID"]
                #pb_storage_mode = decoded25["PB Storage Mode"]

                data_row.extend([hwdt_reset_counter, swdt_reset_id]),

                interupt_cmd = decoded_cmd["Interupt CMD Counter"]
                no_of_sat = decoded_cmd["No Of Satellite"]

                data_row.extend([interupt_cmd,no_of_sat])

                valid_1553_cmd_counter = decoded_wdt["Valid 1553 CMD CTR"]
                tm_selection = decoded_wdt["TM Selection"]
                sw_line_status=decoded_wdt["SW Line/WDT Status"]
                hw_wdt_status = decoded_wdt["HW WDT Status"]
                mnv_status = decoded_wdt["MNV Status"]
                sps1_sw_wdt_status = decoded_wdt["SPS1 S/W WDT STATUS"]
                sps_sw_status = decoded_wdt["SPS Software Status"]


                data_row.extend([valid_1553_cmd_counter, tm_selection, sw_line_status,hw_wdt_status,mnv_status,sps1_sw_wdt_status,sps_sw_status])


                iono_smoothing = decoded_flags["Iono Smoothing"]
                inono_enable = decoded_flags["INONO Enable"]
                gp2015_lock = decoded_flags["GP2015 Lock"]
                rffc5071_lock = decoded_flags["RFFC5071 Lock"]
                nav_1a = decoded_flags["Nav 1A"]
                velocity_smoothing = decoded_flags["Velocity Smoothing"]
                gps2015_ant2_lock = decoded_flags["GPS2015 Ant2 Lock"]
                raim = decoded_flags["RAIM"]
                carrier_smoothing = decoded_flags["Carrier Smoothing"]
                system_mode = decoded_flags["System Mode"]
                time_aligned_to = decoded_flags["Time Aligned To"]
                data_row.extend([iono_smoothing,inono_enable, gp2015_lock, rffc5071_lock, nav_1a, velocity_smoothing,
                                 gps2015_ant2_lock, raim, carrier_smoothing, system_mode, time_aligned_to])


                data_row.extend([LRT,SVID,IODE,CRS,decoded_data,odp_status,phase_corr,phase_corr_sps,port1_config,port2_config,
                                 Sol,Pos_E,ALM,Time,D2_3D_config,Pos,ccsds_flag,randomizer_flag,Spacecraft_id,Navic_cmd])

                no_of_input_sat=odp_flags["No of I/P sat to odp"]
                no_of_sat_est=odp_flags["No of sat est"]
                filter_init=odp_flags["Filter Init reason"]
                filter_init_flag=odp_flags["Filter Init Flag"]
                kf_est_flag=odp_flags["KF Est Flag"]
                ppp_est_flag=odp_flags["PPP Est Flag Unsing"]
                ph_center_en_flag=odp_flags["Ph_center En Flag"]
                data_row.extend([no_of_input_sat,no_of_sat_est,filter_init,filter_init_flag,kf_est_flag,ppp_est_flag,ph_center_en_flag])
                data_row.extend([ill_cnd_val,ill_cnd_Limit,pre_cntr,post_cntr,ODP_prop_used])
                data_row.append(f"{current_time_diff:.3f}") # add precise diff
                data_row.append(dx),data_row.append(dy),data_row.append(dz)
                data_row.append(dvx),data_row.append(dvy),data_row.append(dvz)
                data_row.append(f"{rss_pos:.3f}")
                data_row.append(f"{rss_vel:.3f}")  
                data_row.append(odp_dx),data_row.append(odp_dy),data_row.append(odp_dz)
                data_row.append(odp_dvx),data_row.append(odp_dvy),data_row.append(odp_dvz)
                data_row.append(f"{odp_rss_pos:.3f}")
                data_row.append(f"{odp_rss_vel:.3f}")  
                
                data_row.extend([
                            1,SVID1,CNDR1,T_flag_display[0],constel_flag_display[0],ephem_flag_display[0],D_flag_display[0],I_flag_display[0],R_flag_display[0],H_flag_display[0],A_flag_display[0],IODE1,PR1,DR1,
                            2,SVID2,CNDR2,T_flag_display[1],constel_flag_display[1],ephem_flag_display[1],D_flag_display[1],I_flag_display[1],R_flag_display[1],H_flag_display[1],A_flag_display[1],IODE2,PR2,DR2,
                            3,SVID3,CNDR3,T_flag_display[2],constel_flag_display[2],ephem_flag_display[2],D_flag_display[2],I_flag_display[2],R_flag_display[2],H_flag_display[2],A_flag_display[2],IODE3,PR3,DR3,
                            4,SVID4,CNDR4,T_flag_display[3],constel_flag_display[3],ephem_flag_display[3],D_flag_display[3],I_flag_display[3],R_flag_display[3],H_flag_display[3],A_flag_display[3],IODE4,PR4,DR4,
                            5,SVID5,CNDR5,T_flag_display[4],constel_flag_display[4],ephem_flag_display[4],D_flag_display[4],I_flag_display[4],R_flag_display[4],H_flag_display[4],A_flag_display[4],IODE5,PR5,DR5,
                            6,SVID6,CNDR6,T_flag_display[5],constel_flag_display[5],ephem_flag_display[5],D_flag_display[5],I_flag_display[5],R_flag_display[5],H_flag_display[5],A_flag_display[5],IODE6,PR6,DR6,
                            7,SVID7,CNDR7,T_flag_display[6],constel_flag_display[6],ephem_flag_display[6],D_flag_display[6],I_flag_display[6],R_flag_display[6],H_flag_display[6],A_flag_display[6],IODE7,PR7,DR7,
                            8,SVID8,CNDR8,T_flag_display[7],constel_flag_display[7],ephem_flag_display[7],D_flag_display[7],I_flag_display[7],R_flag_display[7],H_flag_display[7],A_flag_display[7],IODE8,PR8,DR8,
                            9,SVID9,CNDR9,t9_flag,p9_flag,e9_flag,d9_flag,I_flag_display[8],R_flag_display[8],H_flag_display[8],A_flag_display[8],IODE9,PR9,DR9,
                            10,SVID10,CNDR10,t10_flag,p10_flag,e10_flag,d10_flag,I_flag_display[9],R_flag_display[9],H_flag_display[9],A_flag_display[9],IODE10,PR10,DR10,
                            11,SVID11,CNDR11,t11_flag,p11_flag,e11_flag,d11_flag,I_flag_display[10],R_flag_display[10],H_flag_display[10],A_flag_display[10],IODE11,PR11,DR11,
                            12,SVID12,CNDR12,t12_flag,p12_flag,e12_flag,d12_flag,I_flag_display[11],R_flag_display[11],H_flag_display[11],A_flag_display[11],IODE12,PR12,DR12])

                write_to_csv(data_row,base_name)

               
                
                '''data_row = [current_timestamp,SA1_MIL]
                write_to_SA1_FILE (data_row,base_name)
                
               
                data_row = [current_timestamp,SA3_MIL]
                write_to_SA3_FILE (data_row,base_name)
                
                
               
                
                data_row = [current_timestamp,SA4_MIL]
                write_to_SA4_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA5_MIL]
                write_to_SA5_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA6_MIL]
                write_to_SA6_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA7_MIL]
                write_to_SA7_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA8_MIL]
                write_to_SA8_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA9_MIL]
                write_to_SA9_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA10_MIL]
                write_to_SA10_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA11_MIL]
                write_to_SA11_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA12_MIL]
                write_to_SA12_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA13_MIL]
                write_to_SA13_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA14_MIL]
                write_to_SA14_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA15_MIL]
                write_to_SA15_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA16_MIL]
                write_to_SA16_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA17_MIL]
                write_to_SA17_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA18_MIL]
                write_to_SA18_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA28_MIL]
                write_to_SA28_FILE (data_row,base_name)
                
                data_row = [current_timestamp,SA29_MIL]
                write_to_SA29_FILE (data_row,base_name)'''
                
                
                

                try:
                    rec_time = float(SYS_Second) + float(SYS_NanoSecond) * 1e-9
                    plot_time_full = rec_time / 3600.0
                    snapshot = {}
                    for widget, name in PLOTABLE_ENTRIES:
                        if widget.winfo_exists():
                            val = widget.get()
                            numeric_val = parse_plot_value(val)
                            if numeric_val is not None:
                                snapshot[name] = numeric_val
                    snapshot['__plot_time__'] = plot_time_full
                    GLOBAL_TELEMETRY_LOG.append(snapshot)
                except Exception:
                    pass  # Tolerates missing/zero time during jump transitions
            elif data_type == "header2":

                header_length = 10
                Raw_data2 = ' '.join([hexDecodedData[i:i+2]for i in range(header_length,len(hexDecodedData),2)])

                h2NanoSecond_hex=hexDecodedData[12:20]
                h2Second_hex=hexDecodedData[20:28]
                h2Weeknumber_hex=hexDecodedData[28:32]

                # Convert hex to decimal and scale as needed
                SYN_h2NanoSecond=reverse_and_concatenate(h2NanoSecond_hex)

                SYN_h2Second=reverse_and_concatenate(h2Second_hex)

                SYN_h2WeekNumber=reverse_and_concatenate(h2Weeknumber_hex)

                time_entry.config(state="normal")
                time_entry.delete(0,END)
                time_entry.insert(0, str(SYN_h2Second))
                time_entry.config(state="readonly")

                nanotime_entry.config(state="normal")
                nanotime_entry.delete(0,END)
                nanotime_entry.insert(0, str(SYN_h2NanoSecond))
                nanotime_entry.config(state="readonly")

                week_entry.config(state="normal")
                week_entry.delete(0,END)
                week_entry.insert(0, str(SYN_h2WeekNumber))
                week_entry.config(state="readonly")

                current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                base_name = file_entry1.get()

                data_row = [Raw_data2]
                write_to_rawh2(data_row,base_name)

                data_row = [current_timestamp,hexDecodedData]
                write_to_raw_withheader2(data_row,base_name)

                data_row = [current_timestamp,SYN_h2Second,SYN_h2NanoSecond,SYN_h2WeekNumber]
                write_to_SYNh2(data_row,base_name)
                pass
            elif data_type == "header3":
                header_length = 10
                Raw_data3 = ' '.join([hexDecodedData[i:i+2]for i in range(header_length,len(hexDecodedData),2)])
                base_name = file_entry1.get()

                current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                data_row = [current_timestamp,hexDecodedData]
                write_to_raw_withheader3(data_row,base_name)

                data_row = [Raw_data3]
                write_to_rawh3(data_row,base_name)

                pass
            elif data_type == "header4":
                header_length = 10
                Raw_data4 = ' '.join([hexDecodedData[i:i+2]for i in range(header_length,len(hexDecodedData),2)])
                base_name = file_entry1.get()

                current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                data_row = [current_timestamp,hexDecodedData]
                write_to_raw_withheader4(data_row,base_name)

                data_row = [Raw_data4]
                write_to_rawh4(data_row,base_name)






    except KeyboardInterrupt:
        print("Stopped")


def seek_index(target_sec):
    """Handles 3 Jump Conditions: Forward, Backward, Exact Match"""
    if not replay_data:
        return 0

    times = [t for t, _ in replay_data]
    idx = bisect.bisect_left(times, target_sec)

    # Condition 3: Exact Match
    if idx < len(replay_data) and replay_data[idx][0] == target_sec:
        return idx

    # Condition 1 & 2: Forward vs Backward (choose closer)
    if idx > 0 and idx < len(replay_data):
        fwd_diff = abs(replay_data[idx][0] - target_sec)
        bwd_diff = abs(replay_data[idx-1][0] - target_sec)
        return idx if fwd_diff < bwd_diff else idx - 1
    elif idx >= len(replay_data):
        return len(replay_data) - 1  # Jump to end if target exceeds max
    return max(0, idx)  # Jump to start if target < min

def replay_from_file():
    global replay_running, replay_filepath, replay_thread, process_data_thread, serialData, replay_paused, jump_pending, replay_data, replay_index
    filepath = filedialog.askopenfilename(
        title="Select Raw Data File",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    if not filepath:
        return

    serialData = False
    replay_running = True
    replay_paused = False
    jump_pending = None
    replay_data = []
    replay_index = 0

    if process_data_thread is None or not process_data_thread.is_alive():
        process_data_thread = threading.Thread(target=process_data, daemon=True)
        process_data_thread.start()

    replay_filepath = filepath
    filename = os.path.basename(filepath)
    root.after(0, lambda: btn_replay.config(text=filename, fg="blue"))

    replay_thread = threading.Thread(target=process_replay_file, args=(filepath,), daemon=True)
    replay_thread.start()
    safe_status("▶ Replay started")


def stop_replay():
    global replay_running, replay_thread, replay_data, replay_index
    replay_running = False
    if replay_thread and replay_thread.is_alive():
        replay_thread.join(timeout=1)
    replay_data = []
    replay_index = 0
    safe_status("⏹ Replay stopped")
    root.after(0, lambda: btn_replay.config(text="Replay", fg="purple"))


def toggle_pause_resume():
    global replay_paused
    if replay_paused:
        replay_paused = False
        btn_pause_resume.config(text="Pause ⏸", bg="lightyellow")
        safe_status("▶ Replay resumed")
    else:
        replay_paused = True
        btn_pause_resume.config(text="Resume ▶", bg="lightgreen")
        safe_status("⏸ Replay paused")


def jump_to_sys_sec():
    global jump_pending
    if not replay_filepath:
        safe_status("⚠️ Load a CSV file first using REPLAY button.")
        return
    try:
        target = int(jump_entry.get())
        with jump_lock:
            jump_pending = target
        safe_status(f"🔄 Jump requested to SYS_SEC = {target}")
        # If replay isn't running, trigger it
        if not replay_running:
            replay_from_file()
    except ValueError:
        safe_status("⚠️ Invalid SYS_Second value. Enter integer only.")


def process_replay_file(filepath):
    global replay_running, replay_paused, jump_pending, replay_data, replay_index

    # 📦 Load CSV into memory ONCE (fast seek capability)
    if not replay_data:
        replay_data = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header
                for row in reader:
                    if len(row) < 2: continue
                    hex_data = row[1]
                    if hex_data.lower().startswith("acca1f0a"):
                        try:
                            sys_sec = reverse_and_concatenate(hex_data[148:156])
                            replay_data.append((sys_sec, hex_data))
                        except: continue
        except Exception as e:
            safe_status(f"⚠️ CSV load error: {e}")
            root.after(0, lambda: btn_replay.config(text="Replay", fg="purple"))
            return

    if not replay_data:
        safe_status("⚠️ No valid SA1 packets found in CSV.")
        root.after(0, lambda: btn_replay.config(text="Replay", fg="purple"))
        return

    replay_index = 0

    # 🎯 Handle initial jump if pending
    with jump_lock:
        target = jump_pending
        jump_pending = None
    if target is not None:
        replay_index = seek_index(target)
        safe_status(f"📍 Initial jump to SYS_SEC={replay_data[replay_index][0]}")

    # 🔄 MAIN REPLAY LOOP
    while replay_running and replay_index < len(replay_data):
        sys_sec, hex_data = replay_data[replay_index]
        data_queue.put(("header1", hex_data))

        # ⏸ PAUSE HANDLING
        while replay_paused and replay_running:
            pytime.sleep(0.05)

        # 🎯 DYNAMIC JUMP CHECK (Works while running or paused)
        with jump_lock:
            target = jump_pending
            jump_pending = None

        if target is not None:
            replay_paused = True
            btn_pause_resume.config(text="Resume ▶", bg="lightgreen")
            safe_status(f"⏸ Pausing for jump to SYS_SEC={target}")

            replay_index = seek_index(target)
            safe_status(f"📍 Jumped to SYS_SEC={replay_data[replay_index][0]}")

            replay_paused = False
            btn_pause_resume.config(text="Pause ⏸", bg="lightyellow")
            safe_status("▶ Resumed after jump")
            continue  # Skip time.sleep, process new packet immediately

        replay_index += 1
        pytime.sleep(0.5)  # Simulate real-time (adjust as needed)

    # 🧹 Cleanup
    replay_data = []
    replay_index = 0
    print("✅ Replay finished or stopped.")
    root.after(0, lambda: btn_replay.config(text="Replay", fg="purple"))







def start_thread():
    # Use daemon=True directly in constructor (avoids typo & ensures clean exit)
    t1 = threading.Thread(target=readSerial, daemon=True)
    t1.start()

    t2 = threading.Thread(target=process_data, daemon=True)
    t2.start()


def connexion():
    global ser, serialData, replay_running, replay_paused, replay_thread, process_data_thread, GLOBAL_TELEMETRY_LOG
    if connect_btn["text"] == "Disconnect":
        serialData = False
        replay_running = False
        replay_paused = False
        try: data_queue.queue.clear()
        except: pass
        connect_btn["text"] = "Connect"
        refresh_btn["state"] = "active"
        drop_bd["state"] = "active"
        drop_COM["state"] = "active"
        file_entry1.config(state="normal")
        project_entry.config(state="normal")
        if ser and ser.is_open:
            try: ser.close()
            except: pass
        print("Serial port closed & threads signaled to stop.")
    else:
        clear_telemetry_entries()
        GLOBAL_TELEMETRY_LOG.clear()

        serialData = True
        replay_running = False
        connect_btn["text"] = "Disconnect"
        refresh_btn["state"] = "disabled"
        drop_bd["state"] = "disabled"
        drop_COM["state"] = "disabled"
        file_entry1.config(state="disabled")
        project_entry.config(state="disabled")

        port = clicked_com.get()
        baud = clicked_bd.get()
        try:
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            if port not in available_ports:
                status_var1.set(f"❌ {port} is not available. Please refresh!")
                return
            ser = serial.Serial(port, baud, timeout=1)
            ser.flushInput()
            ser.flushOutput()
            try: data_queue.queue.clear()
            except: pass
            start_thread()
            status_var1.set(f"✅ Connected to {port} at {baud} baud.")
        except serial.SerialException as e:
            status_var1.set(f"❌ Serial error: {e}")
        except OSError as e:
            status_var1.set(f"❌ OS error: {e}")
        except Exception as e:
            status_var1.set(f"❌ Unexpected error: {e}")

def clear_telemetry_entries():
    for name, widget in [('time_entry1', time_entry1), ('nanotime_entry1', nanotime_entry1), ('week_entry1', week_entry1),
                         ('time_entry3', time_entry3), ('nanotime_entry3', nanotime_entry3), ('week_entry3', week_entry3),
                         ('fix_status', fix_status), ('position_entry', position_entry), ('position_entry1', position_entry1),
                         ('position_entry2', position_entry2), ('velocity_entry', velocity_entry), ('velocity_entry1', velocity_entry1),
                         ('velocity_entry2', velocity_entry2), ('update_entry', update_entry), ('position_entry3', position_entry3),
                         ('position_entry4', position_entry4), ('position_entry5', position_entry5), ('velocity_entry3', velocity_entry3),
                         ('velocity_entry4', velocity_entry4), ('velocity_entry5', velocity_entry5), ('flag', flag),('flag1', flag1),
                         ('csm', csm), ('csm1', csm1), ('cb', cb), ('pdop', pdop), ('icb', icb), ('st_bias', st_bias),
                         ('st_drift', st_drift), ('clk_crr', clk_crr), ('U1', U1), ('U2', U2), ('swdt', swdt),
                         ('last_cmd_b1_b2', last_cmd_b1_b2), ('last_cmd_b3', last_cmd_b3), ('last_cmd_b4', last_cmd_b4),
                         ('acq1_svid', acq1_svid), ('mc', mc), ('lrt', lrt), ('isd', isd), ('drift', drift),
                         ('SI', SI), ('iode', iode), ('crs', crs),
                         ('tele_cmd_counter', tele_cmd_counter), ('upset_cmd_counter', upset_cmd_counter),
                         ('mux_entry', mux_entry), ('odp', odp), ('phase_center', phase_center), ('phase_center_sps', phase_center_sps),
                         ('port1', port1), ('port2', port2), ('sol', sol), ('pos_e', pos_e), ('alm', alm), ('time', time),
                         ('d2_3d', d2_3d), ('position', position), ('ccsds', ccsds), ('rand', rand), ('space_crf_id', space_crf_id),
                         ('navic_cmd', navic_cmd), ('tmillcond', tmillcond), ('tmillcondlim', tmillcondlim),
                         ('pre_chk_cntr', pre_chk_cntr), ('post_chk_cntr', post_chk_cntr), ('cond_pre', cond_pre),
                         ('cond_post', cond_post), ('odp_prop', odp_prop), ('raw_data', raw_data),
                         ('remote1_entry',remote1_entry),('remote2_entry',remote2_entry),('remote3_entry',remote3_entry),
                         ('remote4_entry',remote4_entry),('remote5_entry',remote5_entry),('remote6_entry',remote6_entry),
                         ('est_rec_clk_entry',est_rec_clk_entry),('est_rec_clk_bias_entry',est_rec_clk_bias_entry),
                         ('LCOR_entry',LCOR_entry),('str_crr_clk_entry',str_crr_clk_entry)]:
        if widget.winfo_exists():
            widget.config(state="normal")
            widget.delete(0, tk.END)
            widget.insert(0, "--")
            widget.config(state="readonly")
    clear_all_plot_buffers()

def get_display_name(key):
    base = PARAM_NAME_MAP.get(key, key.replace("_", " ").title())
    if key.startswith("svid") or key.startswith("cndr") or key.startswith("iode") or key.startswith("pr") or key.startswith("dr"):
        try:
            num = int("".join(filter(str.isdigit, key)))
            return f"{base[:3]} CH{num}" if base[:3] != key[:3] else f"{base} CH{num}"
        except: pass
    return base

def open_param_plot(param_name, entry_widget):
    if param_name in PLOT_REGISTRY:
        reg = PLOT_REGISTRY[param_name]
        win = reg["window"]
        if win.winfo_exists():
            win.lift()
            win.attributes('-topmost', True)
            root.after(100, lambda: win.attributes('-topmost', False))
        return

    win = tk.Toplevel(root)
    win.title(f"📈 {param_name}")
    win.geometry("820x560")
    win.protocol("WM_DELETE_WINDOW", lambda: cleanup_plot(param_name))

    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Navigation Toolbar: Pan, Box Zoom, Home, Save
    toolbar = NavigationToolbar2Tk(canvas, win)
    toolbar.update()

    ax.set_title(f"Live: {param_name}", fontsize=13, fontweight="bold", color="blue")
    ax.set_xlabel("System Time (Hours)", fontsize=11, fontweight="bold", color="green")
    ax.set_ylabel(f"{param_name}", fontweight="bold", fontsize=11, color="green")
    ax.grid(True, linestyle="--", alpha=0.4)

    # Click-inspect point picker (within 5 pixels)
    line, = ax.plot([], [], "b-", linewidth=2.0, marker="o", markersize=3, picker=5)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Hover/Click point annotation
    annot = ax.annotate(
        "", xy=(0, 0), xytext=(12, 12), textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.5", fc="#FFFFCC", alpha=0.9, edgecolor="black"),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0")
    )
    annot.set_visible(False)

    def on_pick(event):
        if event.artist != line:
            return
        ind = event.ind[0]
        x_val = reg["times"][ind]
        y_val = reg["data"][ind]
        annot.xy = (x_val, y_val)
        annot.set_text(f"Time: {x_val:.4f} h\nVal: {y_val:.4f}")
        annot.set_visible(True)
        canvas.draw_idle()

    canvas.mpl_connect("pick_event", on_pick)

    def on_click(event):
        if event.inaxes == ax and not event.dblclick:
            if annot.get_visible():
                annot.set_visible(False)
                canvas.draw_idle()

    canvas.mpl_connect("button_press_event", on_click)

    initial_data, initial_times = [], []
    for snapshot in GLOBAL_TELEMETRY_LOG:
        val = snapshot.get(param_name)
        t = snapshot.get('__plot_time__')
        if val is not None and t is not None:
            try:
                initial_data.append(float(val))
                initial_times.append(float(t))
            except Exception:
                pass

    PLOT_REGISTRY[param_name] = {
        "window": win, "ax": ax, "canvas": canvas, "entry_ref": entry_widget,
        "line": line, "data": initial_data, "times": initial_times,
        "toolbar": toolbar
    }

    schedule_plot_update(param_name)
    win.focus_set()


def schedule_plot_update(param_name):
    global _PLOT_UPDATE_THREAD
    if _PLOT_UPDATE_THREAD is None or not _PLOT_UPDATE_THREAD.is_alive():
        _PLOT_STOP_EVENT.clear()
        _PLOT_UPDATE_THREAD = threading.Thread(target=_plot_collector, daemon=True)
        _PLOT_UPDATE_THREAD.start()

def _plot_collector():
    while not _PLOT_STOP_EVENT.is_set():
        if not PLOT_REGISTRY:
            _PLOT_STOP_EVENT.wait(0.5)
            continue

        try:
            with sys_second_lock:
                t_sec = float(latest_sys_second)
            current_time = t_sec / 3600.0
        except Exception:
            current_time = 0.0

        for name, reg in list(PLOT_REGISTRY.items()):
            try:
                if not reg["window"].winfo_exists():
                    continue

                val_str = reg["entry_ref"].get().strip()
                val = parse_plot_value(val_str)
                if val is None:
                    continue

                if not reg["times"] or reg["times"][-1] != current_time:
                    reg["times"].append(current_time)
                    reg["data"].append(val)

                    # Bounded array size prevents memory bloating over hours of running
                    if len(reg["times"]) > MAX_PLOT_POINTS:
                        reg["times"] = reg["times"][-MAX_PLOT_POINTS:]
                        reg["data"] = reg["data"][-MAX_PLOT_POINTS:]
            except Exception:
                continue

        try:
            root.after(0, _main_thread_plot_renderer)
        except Exception:
            pass

        _PLOT_STOP_EVENT.wait(0.5)


def _main_thread_plot_renderer():
    for name, reg in list(PLOT_REGISTRY.items()):
        try:
            if not reg["window"].winfo_exists() or not reg["data"]:
                continue

            x_data = reg["times"]
            y_data = reg["data"]
            reg["line"].set_data(x_data, y_data)

            toolbar = reg.get("toolbar")
            # If user has an active Zoom or Pan tool, do not override their view
            is_active_tool = toolbar and toolbar.mode != ""

            if not is_active_tool:
                # Dynamic X autoscale
                x_min, x_max = min(x_data), max(x_data)
                if x_min == x_max:
                    reg["ax"].set_xlim(x_min - 0.01, x_max + 0.01)
                else:
                    x_pad = (x_max - x_min) * 0.05
                    reg["ax"].set_xlim(x_min, x_max + x_pad)

                # Dynamic Y autoscale
                y_min, y_max = min(y_data), max(y_data)
                if y_min == y_max:
                    margin = 1.0 if y_min == 0 else abs(y_min) * 0.1
                    reg["ax"].set_ylim(y_min - margin, y_max + margin)
                else:
                    y_pad = (y_max - y_min) * 0.1
                    reg["ax"].set_ylim(y_min - y_pad, y_max + y_pad)

            reg["canvas"].draw_idle()
        except Exception:
            continue

def cleanup_plot(param_name):
    if param_name in PLOT_REGISTRY:
        reg = PLOT_REGISTRY.pop(param_name)
        if reg["window"].winfo_exists():
            reg["window"].destroy()

def clear_all_plot_buffers():
    global GLOBAL_TELEMETRY_LOG
    GLOBAL_TELEMETRY_LOG.clear()

    for name, reg in list(PLOT_REGISTRY.items()):
        try:
            reg["data"] = []
            reg["times"] = []
            reg["line"].set_data([], [])
            reg["ax"].set_xlim(0, 1)
            reg["ax"].set_ylim(0, 1)
            if reg["window"].winfo_exists():
                reg["canvas"].draw_idle()
        except Exception:
            pass

def bind_right_click_menu(widget, display_name):

    # Never open plots for widgets inside COM MANAGER.
    try:
        parent = widget
        while parent is not None:
        
            if parent == frame1:
                return
            elif parent == frame_bus:
                return
            parent = parent.master
    except Exception:
        pass

    def show_plot(event):
        open_param_plot(display_name, widget)

    widget.config(cursor="hand2")
    widget.bind("<Button-1>", show_plot)
    widget.bind(
        "<Button-3>",
        lambda e: open_param_plot(display_name, widget)
    )

'''def bind_right_click_menu(widget, display_name):
    widget.config(cursor="hand2")
    widget.bind("<Button-1>", lambda e: open_param_plot(display_name, widget))
    widget.bind("<Button-3>", lambda e: open_param_plot(display_name, widget))'''

def bind_all_params_to_plots():
    global root
    for key in list(globals().keys()):
        widget = globals()[key]
        if isinstance(widget, tk.Entry):
            if not any(w is widget for w, _ in PLOTABLE_ENTRIES):
                display_name = get_display_name(key)
                bind_right_click_menu(widget, display_name)
                PLOTABLE_ENTRIES.append((widget, display_name))
            try:
                parent = widget.winfo_parent()
                if parent:
                    for child in parent.winfo_children():
                        if isinstance(child, tk.Label) and child.cget("text").endswith(":"):
                            if child.grid_info().get("row") == widget.grid_info().get("row"):
                                bind_right_click_menu(child, display_name)
            except: pass

    for d_name in ["gui_entry_dict", "wdt_entries", "tele_entries", "word25_entries", "word32_entries", "odp_entries"]:
        if d_name in globals():
            for label, entry in globals()[d_name].items():
                if isinstance(entry, tk.Entry):
                    if not any(w is entry for w, _ in PLOTABLE_ENTRIES):
                        bind_right_click_menu(entry, label)
                        PLOTABLE_ENTRIES.append((entry, label))


def close_window():
    global serialData, replay_running, ser, _PLOT_STOP_EVENT
    serialData = False
    replay_running = False
    _PLOT_STOP_EVENT.set()
    if ser and ser.is_open:
        try: ser.close()
        except: pass
    root.winfo_toplevel().destroy()
    sys.exit(0)

if __name__=="__main__":
    connect_menu_init()