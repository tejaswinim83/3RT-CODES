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
    
    # Bit flags
    bit_names = ["A", "T", "D", "E", "P", "H", "R", "P1", "I", "S", "SR", "E1"]
    
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
    








def process_rt_data(hexDecodedData, rt_name):
    """Process data for a specific RT and update its widgets"""
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
    else:
        return
    
    try:
        # =============== EXTRACT HEX VALUES FROM DATA ===============
        
        # Extract hex values from the data string
        SYN_NanoSecond_hex = hexDecodedData[12:20]
        SYN_Second_hex = hexDecodedData[20:28]
        SYN_Weeknumber_hex = hexDecodedData[28:32]
        Tsm_UpdateCounter_hex = hexDecodedData[32:36]
        csm1_hex = hexDecodedData[36:40]
        
        SYS_NanoSecond_hex = hexDecodedData[40:48]
        SYS_Second_hex = hexDecodedData[48:56]
        SYS_Weeknumber_hex = hexDecodedData[56:60]
        POS_X_hex = hexDecodedData[60:68]
        POS_Y_hex = hexDecodedData[68:76]
        POS_Z_hex = hexDecodedData[76:84]
        POS_Vx_hex = hexDecodedData[84:92]
        POS_Vy_hex = hexDecodedData[92:100]
        POS_Vz_hex = hexDecodedData[100:108]
        UpdateCounter_hex = hexDecodedData[108:112]
        PDOP_hex = hexDecodedData[112:116]
        word20_hex = hexDecodedData[116:120]
        Bais_hex = hexDecodedData[120:128]
        ISB_hex = hexDecodedData[128:132]
        DRIFT_hex = hexDecodedData[132:140]
        ISD_hex = hexDecodedData[140:144]
        SW_reset_counter_hex = hexDecodedData[144:148]
        HW_reset_counter_hex = hexDecodedData[148:152]
        sw_rst_id_hex = hexDecodedData[152:156]
        Navic_msg_22_counter_hex = hexDecodedData[156:160]
        Navic_msg_counter_hex = hexDecodedData[160:164]
        Leo_sat_id_mil_hex = hexDecodedData[164:168]
        No_of_Sat_hex = hexDecodedData[168:172]
        Navic_cmd_var_hex = hexDecodedData[172:176]
        word28_sw_rst_id_hex = hexDecodedData[176:180]
        word29_hex = hexDecodedData[180:184]
        word30_hex = hexDecodedData[184:188]
        word31_hex = hexDecodedData[188:192]
        
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
        
        # Other values
        Last_cmd_ex_hex = hexDecodedData[364:372]
        Last_reset_time_hex = hexDecodedData[372:376]
        Total_cmd_counter_hex = hexDecodedData[376:378]
        Cmd_counter_based_rt_hex = hexDecodedData[378:380]
        
        ACQ1_hex = hexDecodedData[382:384]
        ACQ2_hex = hexDecodedData[380:382]
        ACQ3_hex = hexDecodedData[386:388]
        ACQ4_hex = hexDecodedData[384:386]
        
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
        
        # Other counters
        Dual_exe_cmd_c_hex = hexDecodedData[1186:1188]
        Spu_cmd_c_hex = hexDecodedData[1184:1186]
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
        
        # INS values
        INS_x_hex = hexDecodedData[1292:1300]
        INS_y_hex = hexDecodedData[1300:1308]
        INS_z_hex = hexDecodedData[1308:1316]
        INS_vx_hex = hexDecodedData[1316:1324]
        INS_vy_hex = hexDecodedData[1324:1332]
        INS_vz_hex = hexDecodedData[1332:1340]
        
        # PPS values
        fix_3D_hex = hexDecodedData[1676:1680]
        PPS_Nanosec_hex = hexDecodedData[1680:1688]
        PPS_Sec_hex = hexDecodedData[1688:1696]
        PPS_Week_hex = hexDecodedData[1696:1700]
        Leap_hex = hexDecodedData[1700:1704]
        
        # =============== CONVERT HEX TO DECIMAL VALUES ===============
        
        # Convert all values
        SYN_NanoSecond = reverse_and_concatenate(SYN_NanoSecond_hex)
        SYN_Second = reverse_and_concatenate(SYN_Second_hex)
        SYN_WeekNumber = reverse_and_concatenate(SYN_Weeknumber_hex)
        TSM_update_counter = reverse_and_concatenate(Tsm_UpdateCounter_hex)
        Checksum1 = reverse_and_concatenate(csm1_hex)
        
        SYS_Second = reverse_and_concatenate(SYS_Second_hex)
        SYS_NanoSecond = reverse_and_concatenate(SYS_NanoSecond_hex)
        SYS_WeekNumber = reverse_and_concatenate(SYS_Weeknumber_hex)
        
        POS_x = reverse_and_concatenate(POS_X_hex, is_signed=True)/100.0
        POS_y = reverse_and_concatenate(POS_Y_hex, is_signed=True)/100.0
        POS_z = reverse_and_concatenate(POS_Z_hex, is_signed=True)/100.0
        POS_vx = reverse_and_concatenate(POS_Vx_hex, is_signed=True)/1000.0
        POS_vy = reverse_and_concatenate(POS_Vy_hex, is_signed=True)/1000.0
        POS_vz = reverse_and_concatenate(POS_Vz_hex, is_signed=True)/1000.0
        
        UpdateCounter = reverse_and_concatenate(UpdateCounter_hex)
        PDOP = reverse_and_concatenate(PDOP_hex, is_signed=True)/100.0
        word20 = reverse_and_concatenate(word20_hex)
        Bais = reverse_and_concatenate(Bais_hex)
        ISB = reverse_and_concatenate(ISB_hex)
        DRIFT = reverse_and_concatenate(DRIFT_hex, is_signed=True)/100.0
        ISD = reverse_and_concatenate(ISD_hex)
        
        SW_reset_counter = reverse_and_concatenate(SW_reset_counter_hex)
        HW_reset_counter = reverse_and_concatenate(HW_reset_counter_hex)
        SW_RST_ID = reverse_and_concatenate(sw_rst_id_hex)
        Navic_msg_22_counter = reverse_and_concatenate(Navic_msg_22_counter_hex)
        Navic_msg_counter = reverse_and_concatenate(Navic_msg_counter_hex)
        Leo_sat_id_mil = reverse_and_concatenate(Leo_sat_id_mil_hex)
        No_of_Sat = reverse_and_concatenate(No_of_Sat_hex)
        Navic_cmd_var = reverse_and_concatenate(Navic_cmd_var_hex)
        
        # Convert tracking values
        SVID_values = [reverse_and_concatenate(h) for h in SVID_hex]
        IODE_values = [reverse_and_concatenate(h) for h in IODE_hex]
        CNDR_values = [reverse_and_concatenate(h) for h in CNDR_hex]
        CHANNEL_STATUS = [reverse_and_concatenate(h) for h in CHANNEL_STATUS_hex]
        PR_values = [reverse_and_concatenate(h) for h in PR_hex]
        DR_values = [reverse_and_concatenate(h, is_signed=True)/1000.0 for h in DR_hex]
        Elev_values = [reverse_and_concatenate(h) for h in Elev_hex]
        
        # Convert other values
        Last_cmd_ex = reverse_and_concatenate(Last_cmd_ex_hex)
        Last_reset_time = reverse_and_concatenate(Last_reset_time_hex)
        Total_cmd_counter = reverse_and_concatenate(Total_cmd_counter_hex)
        Cmd_counter_based_rt = reverse_and_concatenate(Cmd_counter_based_rt_hex)
        
        ACQ1 = reverse_and_concatenate(ACQ1_hex)
        ACQ2 = reverse_and_concatenate(ACQ2_hex)
        ACQ3 = reverse_and_concatenate(ACQ3_hex)
        ACQ4 = reverse_and_concatenate(ACQ4_hex)
        
        word31 = reverse_and_concatenate(word31_hex)
        word32 = reverse_and_concatenate(word32_hex)
        flags = extract_word31_flags(word31)
        flag2 = extract_sa4w32_flags(word32)
        
        Dual_exe_cmd_c = reverse_and_concatenate(Dual_exe_cmd_c_hex)
        Spu_cmd_c = reverse_and_concatenate(Spu_cmd_c_hex)
        Nrffc_counter1 = reverse_and_concatenate(Nrffc_counter1_hex)
        Nrffc_counter2 = reverse_and_concatenate(Nrffc_counter2_hex)
        Grffc_counter1 = reverse_and_concatenate(Grffc_counter1_hex)
        Grffc_counter2 = reverse_and_concatenate(Grffc_counter2_hex)
        Grffc_counter3 = reverse_and_concatenate(Grffc_counter3_hex)
        Grffc_counter4 = reverse_and_concatenate(Grffc_counter4_hex)
        
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
        
        # Calculate checksum
        checksum_result = chechsum_calulation_covert_decimal(
            SYN_NanoSecond_hex, SYN_Second_hex, SYN_Weeknumber_hex, 
            Tsm_UpdateCounter_hex, Checksum1
        )
        
        # =============== UPDATE WIDGETS ===============
        
        # Update counter
        if widgets.get('counter_entry'):
            widgets['counter_entry'].config(state="normal")
            widgets['counter_entry'].delete(0, END)
            widgets['counter_entry'].insert(0, str(counter_var))
            widgets['counter_entry'].config(state="readonly")
        
        # Update time entries
        if widgets.get('time_entry1'):
            widgets['time_entry1'].config(state="normal")
            widgets['time_entry1'].delete(0, END)
            widgets['time_entry1'].insert(0, str(SYN_Second))
            widgets['time_entry1'].config(state="readonly")
        
        if widgets.get('nanotime_entry1'):
            widgets['nanotime_entry1'].config(state="normal")
            widgets['nanotime_entry1'].delete(0, END)
            widgets['nanotime_entry1'].insert(0, str(SYN_NanoSecond))
            widgets['nanotime_entry1'].config(state="readonly")
        
        if widgets.get('week_entry1'):
            widgets['week_entry1'].config(state="normal")
            widgets['week_entry1'].delete(0, END)
            widgets['week_entry1'].insert(0, str(SYN_WeekNumber))
            widgets['week_entry1'].config(state="readonly")
        
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
            bit_names = ["A", "T", "D", "E", "P", "H", "R", "P1", "I", "S", "SR", "E1"]
            
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
        
        # Update other widgets
        if widgets.get('update_entry'):
            widgets['update_entry'].config(state="normal")
            widgets['update_entry'].delete(0, END)
            widgets['update_entry'].insert(0, str(UpdateCounter))
            widgets['update_entry'].config(state="readonly")
        
        if widgets.get('tsm_counter_entry'):
            widgets['tsm_counter_entry'].config(state="normal")
            widgets['tsm_counter_entry'].delete(0, END)
            widgets['tsm_counter_entry'].insert(0, str(TSM_update_counter))
            widgets['tsm_counter_entry'].config(state="readonly")
        
        # Update fix_3d and leap if they exist
        if widgets.get('fix_3d'):
            widgets['fix_3d'].config(state="normal")
            widgets['fix_3d'].delete(0, END)
            widgets['fix_3d'].insert(0, str(fix_3D))
            widgets['fix_3d'].config(state="readonly")
        
        if widgets.get('leap'):
            widgets['leap'].config(state="normal")
            widgets['leap'].delete(0, END)
            widgets['leap'].insert(0, str(Leap))
            widgets['leap'].config(state="readonly")
        
        # =============== SAVE TO FILE ===============
        
        # Save data to CSV file
        try:
            # Prepare data for CSV
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Create row data
            row_data = [
                timestamp,                      # TimeStamp
                str(counter_var),               # Counter
                str(SYS_Second),                # Sys_Second
                str(SYS_NanoSecond),            # Sys_NanoSecond
                str(SYS_WeekNumber),            # Sys_WeekNumber
                str(PPS_Sec),                   # PPS_Second
                str(PPS_Nanosec),               # PPS_NanoSecond
                str(PPS_Week),                  # PPS_WeekNo
                str(fix_3D),                    # PPS_3D FIX
                str(Leap),                      # PPS_LEAP SEC
                str(TSM_update_counter),        # TSM_Counter
                str(UpdateCounter),             # Update Counter
                str(checksum_result),           # Checksum
                "N/A",                          # Checksum 2 (placeholder)
                f"{PDOP:.2f}",                  # PDOP
                str(Bais),                      # Clock bais
                str(ISB),                       # InterSystem bais
                f"{DRIFT:.2f}",                 # Drift
                str(ISD),                       # Inter System Drift
                f"{POS_x:.2f}",                 # POS_X
                f"{POS_y:.2f}",                 # POS_Y
                f"{POS_z:.2f}",                 # POS_Z
                f"{POS_vx:.3f}",                # POS_VX
                f"{POS_vy:.3f}",                # POS_VY
                f"{POS_vz:.3f}",                # POS_VZ
                f"{INS_x:.2f}",                 # ESt_X
                f"{INS_y:.2f}",                 # EST_Y
                f"{INS_z:.2f}",                 # EST_Z
                f"{INS_vx:.3f}",                # EST_VX
                f"{INS_vy:.3f}",                # EST_VY
                f"{INS_vz:.3f}",                # EST_VZ
                str(ACQ1),                      # ACQ1
                str(ACQ2),                      # ACQ2
                str(ACQ3),                      # ACQ3
                str(ACQ4),                      # ACQ4
                # Add more fields as needed...
            ]
            
            # Add tracking info for all 18 channels
            for ch in range(18):
                row_data.append(str(ch+1))  # Channel number
                row_data.append(str(SVID_values[ch]))  # SVID
                row_data.append(str(CNDR_values[ch]))  # CNDR
                
                # Add bit flags
                bit_names = ["A", "T", "D", "E", "P", "H", "R", "P1", "I", "S", "SR", "E1"]
                for bit in bit_names:
                    if ch < len(CHANNEL_STATUS):
                        status_meaning = decode_channel_status_meaning(CHANNEL_STATUS[ch])
                        row_data.append(status_meaning.get(bit, ""))
                    else:
                        row_data.append("")
                
                row_data.append(str(IODE_values[ch]))  # IODE
                row_data.append(str(PR_values[ch]))    # PR
                row_data.append(f"{DR_values[ch]:.3f}")  # DR
                row_data.append(str(Elev_values[ch]))  # ELEV
            
            # Generate filename with RT name
            file_name = get_timestamped_filename(f"GAGANYAAN_{rt_name}", "PVT")
            
            # Write to file
            with open(file_name, mode='a', newline='') as file:
                writer = csv.writer(file)
                
                # Write header if file is empty (you need to create this header function)
                if file.tell() == 0:
                    header = create_pvt_header()
                    writer.writerow(header)
                
                writer.writerow(row_data)
            
            print(f"✅ Saved {rt_name} data to {file_name}")
            
        except Exception as save_error:
            print(f"⚠️ Failed to save {rt_name} data to file: {save_error}")
        
        print(f"✅ Successfully processed {rt_name} data")
        
    except Exception as e:
        print(f"❌ Error processing {rt_name} data: {e}")
        import traceback
        traceback.print_exc()
