# -*- coding: utf-8 -*-
"""
Created on Wed Apr 8 09:22:46 2026

@author: Adminservice
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
import matplotlib.ticker as ticker
import re

title = "G1 QM 'TharmalCycling' Analysis" # OR {G1 Debbost Run @ RND Lab} "SPS QM 'Humidity Chamber' Analysis"


def process_files_full(receiver_file, precise_file, output_file):
    # =========================================================
    # 1. CREATE OUTPUT FOLDER
    # =========================================================
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"Results_IONO_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    print("📁 Output folder:", output_dir)

    # =========================================================
    # 2. LOAD RECEIVER (RAW)
    # =========================================================
    print("nStep 1: Loading receiver...")

    receiver_full = pd.read_csv(receiver_file, low_memory=False, encoding='latin1')
    receiver_full.columns = receiver_full.columns.str.strip()

    receiver_full['time_av_f'] = np.where(
        receiver_full['TIME AV'].astype(str).str.strip() == 'TIME AV', 1, 0
    )

    receiver_full['pos_mode_f'] = np.where(
        receiver_full['POS MODE'].astype(str).str.strip() == '3D', 0, 1
    )

    receiver_full['pos_av_f'] = np.where(
        receiver_full['POS AV'].astype(str).str.strip() == 'POS AV', 1, 0
    )

    # Convert numeric columns safely
    for col in receiver_full.columns:
        try:
            receiver_full[col] = pd.to_numeric(receiver_full[col])
        except (ValueError, TypeError):
            pass

    # Create time axis
    receiver_full['rec_time'] = receiver_full['Sys_Second'] + receiver_full['Sys_NanoSecond'] * 1e-9
    plot_time_full = receiver_full['rec_time'] / 3600

    receiver_full['sec_diff'] = receiver_full['Update Counter'].diff()

    # ==========================================================#
    # SPS QM 'Humidity Chamber' Analysis : Succ Diff of SYS_SEC #
    # ==========================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))
    plt.plot(plot_time_full, receiver_full['sec_diff'], label='Succ_Diff', color="blue")
    plt.title(f"{title} : Successive_Diff")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("Succ Diff")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "Succ Diff.png"), dpi=300)
    plt.show()
    plt.close()

    # =====================================================#
    # SPS QM 'Humidity Chamber' Analysis :Succ Diff vs SA3 COUNTER #
    # =====================================================#
    plt.ion()
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(plot_time_full, receiver_full['Update Counter'], label='SA3 Update Counter', color="blue")
    ax1.set_xlabel("GPS time(hrs)")
    ax1.set_ylabel("SA3 Update Counter", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.grid(True)
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(nbins=11))

    ax2 = ax1.twinx()
    ax2.plot(plot_time_full, receiver_full['sec_diff'], label='Succ_Diff', color="green")
    ax2.set_ylabel("Succ_Diff", color="green")
    ax2.tick_params(axis="y", labelcolor="green")
    plt.title(f"{title} : : Update Counter Vs Succ_Diff")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "Succ Diff vs Update_Ctr.png"), dpi=300)
    plt.tight_layout()
    plt.show()
    plt.close()

   
    # =========================================================
    # 3. RAW PLOTS
    # =========================================================
    print("Step 2: Saving plots...")

    # Clock Bias & Drift
    if 'Clock bais' in receiver_full.columns and 'Drift' in receiver_full.columns:
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(plot_time_full, receiver_full['Clock bais'], label='Clock Bias', color="blue")
        ax1.set_ylabel("Clock Bias", color="blue")
        ax1.set_xlabel("GPS time(hrs)")
        ax1.tick_params(axis="y", color="blue")
        ax1.grid(True)
        ax1.legend()
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
        ax2 = ax1.twinx()

        ax2.plot(plot_time_full, receiver_full['Drift'], label='Drift', color="red")
        ax2.set_ylabel("Clock Drift", color="red")
        ax2.tick_params(axis="y", labelcolor="red")
        plt.title(f"{title}:Clock bias vs Drift ")
        plt.savefig(os.path.join(output_dir, "Clock Bias vs Drift.png"), dpi=300)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        plt.close()

    # PDOP vs Satellites
    if 'PDOP' in receiver_full.columns and 'NO OF SAT TRACKED' in receiver_full.columns:
        plt.ion()
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(plot_time_full, receiver_full['NO OF SAT TRACKED'], label='No Of Sat Tracked', color="blue")
        ax1.set_xlabel("GPS time(hrs)")
        ax1.set_ylabel("NO Of Tracked Sat", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")
        ax1.grid(True)
        ax1.legend()
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
        ax2 = ax1.twinx()
        ax2.plot(plot_time_full, receiver_full['PDOP'], label='PDOP', color="green")
        ax2.set_ylabel("PDOP", color="green")
        ax2.tick_params(axis="y", labelcolor="green")
        plt.title(f"{title}:PDOP vs No of sat Tracked")
        plt.savefig(os.path.join(output_dir, "PDOP vs NO of Sat Tracked.png"), dpi=300)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        plt.close()

    # ==============================================================================#
    # SPS QM 'Humidity Chamber' Analysis :REC Time Vs TIME_AV,POS_MODE,POS_AV FLAGS #
    # ==============================================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))

    plt.plot(plot_time_full, receiver_full['time_av_f'], label='POS_MODE')
    plt.plot(plot_time_full, receiver_full['pos_mode_f'], label='TIME_AV')
    plt.plot(plot_time_full, receiver_full['pos_av_f'], label='POS_AV')

    plt.title(f"{title} : REC Time Vs TIME_AV,POS_MODE,POS_AV FLAGS")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("FLAGS")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "Health Flags.png"), dpi=300)
    plt.show()
    plt.close()

    # =====================================================#
    # SPS QM 'Humidity Chamber' Analysis : SA3 COUNTER #
    # =====================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))

    plt.plot(plot_time_full, receiver_full['Update Counter'], label='SA3 UPDATE_C', color="blue")

    plt.title(f"{title} : SA3 COUNTER")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("UPDATE_C")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "SA3 Update_Conter.png"), dpi=300)
    plt.show()
    plt.close()


    # =========================================================
    # 4. CNDR GROUPING FIX
    # =========================================================
    print("Step 4: CNDR Grouping...")

    cndr_cols = [col for col in receiver_full.columns if col.startswith('CNDR')]

    def get_number(col):
        return int(re.search(r'\d+', col).group())

    cndr_cols = sorted(cndr_cols, key=get_number)

    group_size = 6
    cndr_groups = [cndr_cols[i:i + group_size] for i in range(0, len(cndr_cols), group_size)]

    for i, grp in enumerate(cndr_groups, 1):
        if grp:
            plt.ion()
            plt.figure(figsize=(12, 6))
            for col in grp:
                plt.plot(plot_time_full, receiver_full[col], label=col)

            plt.legend(fontsize=6)
            ax = plt.gca()
            ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
            plt.ylim(10, 60)
            plt.grid()
            plt.title(f"{title} :REC Time Vs CNDR Group {i}")
            plt.savefig(os.path.join(output_dir, f"cndr_group_{i}.png"), dpi=300)
            plt.show()
            plt.close()

    # =========================================================
    # 5. LOAD PRECISE (MILLISECOND -> SECONDS)
    # =========================================================
    print("\nStep 4: Loading precise...")

    precise = pd.read_csv(
        precise_file,
        header=1, # second line is header
        low_memory=False,
        encoding='latin1'
    )

    precise.columns = precise.columns.str.strip().str.replace('²', '2')

    required_cols = [
        'TOW_ms',
        'Pos_X','Pos_Y','Pos_Z',
        'Vel_X','Vel_Y','Vel_Z',
        'Acc_X','Acc_Y','Acc_Z',
    ]#'v1_veh_z_acc(m/s2)'

    precise = precise[required_cols].apply(pd.to_numeric, errors='coerce').dropna()

    # Non-zero filter (pos + vel)
    precise = precise[(precise.iloc[:, 1:7] != 0).all(axis=1)].copy()

    # Scale millisecond TOW to seconds
    precise['TOW_ms'] = precise['TOW_ms'] / 1000.0

    # Sort by exact timestamp for nearest-millisecond matching
    precise = precise.sort_values('TOW_ms').reset_index(drop=True)

    print("Precise rows after filter:", len(precise))

    # =========================================================
    # 6. FILTER RECEIVER
    # =========================================================
    print("\nStep 5: Filtering receiver...")

    receiver = receiver_full[
        (receiver_full['TIME AV'] == 'TIME AV') &
        (receiver_full['POS MODE'] == '3D') &
        (receiver_full['POS AV'] == 'POS AV')
    ].copy()

    receiver = receiver[
        (receiver[['POS_X', 'POS_Y', 'POS_Z', 'POS_VX', 'POS_VY', 'POS_VZ']] != 0).all(axis=1)
    ].dropna(subset=['rec_time'])

    # Sort by exact timestamp for nearest-millisecond matching
    receiver = receiver.sort_values('rec_time').reset_index(drop=True)

    print("Filtered receiver rows:", len(receiver))

    # =========================================================
    # 7. MERGE (NEAREST MILLISECOND)
    # =========================================================
    print("\nStep 6: Merging...")

    df = pd.merge_asof(
        receiver,
        precise,
        left_on='rec_time',
        right_on='TOW_ms',
        direction='nearest',
        tolerance=0.5
    ).dropna(subset=['TOW_ms']).reset_index(drop=True)

    print("Merged rows:", len(df))

    if df.empty:
        print("❌ No matching data after merge")
        return

    # =========================================================
    # 8. COMPUTATION
    # =========================================================
    print("\nStep 7: Computing errors...")

    df['time_diff'] = df['rec_time'] - df['TOW_ms']
    t = df['time_diff'].values

    px = df['Pos_X']
    py = df['Pos_Y']
    pz = df['Pos_Z']

    vx = df['Vel_X']
    vy = df['Vel_Y']
    vz = df['Vel_Z']

    ax = df['Acc_X']
    ay = df['Acc_Y']
    az = df['Acc_Z']

    rx = df['POS_X']
    ry = df['POS_Y']
    rz = df['POS_Z']

    rvx = df['POS_VX']
    rvy = df['POS_VY']
    rvz = df['POS_VZ']
    
    odp_x = df['EST_X']
    odp_y = df['EST_Y']
    odp_z = df['EST_Z']
    
    odp_vx = df['EST_VX']
    odp_vy = df['EST_VY']
    odp_vz = df['EST_VZ']

    # Propagation
    px_p = px + vx * t + 0.5 * ax * t * t
    py_p = py + vy * t + 0.5 * ay * t * t
    pz_p = pz + vz * t + 0.5 * az * t * t

    vx_p = vx + ax * t
    vy_p = vy + ay * t
    vz_p = vz + az * t

    # Differences
    dx = px_p - rx
    dy = py_p - ry
    dz = pz_p - rz

    dvx = (vx_p - rvx) * 100
    dvy = (vy_p - rvy) * 100
    dvz = (vz_p - rvz) * 100

    # ODP Differences
    od_x = px_p - odp_x
    od_y = py_p - odp_y
    od_z = pz_p - odp_z

    odp_dvx = (vx_p - odp_vx) * 100
    odp_dvy = (vy_p - odp_vy) * 100
    odp_dvz = (vz_p - odp_vz) * 100

    # RSS POS n VEL
    rss_pos = np.sqrt(dx**2 + dy**2 + dz**2)
    rss_vel = np.sqrt(dvx**2 + dvy**2 + dvz**2)

    std_rss_pos = np.std(rss_pos)
    three_sigma_pos = 3 * std_rss_pos

    std_rss_vel = np.std(rss_vel)
    three_sigma_vel = 3 * std_rss_vel

    # ODP RSS POS n VEL
    odp_rss_pos = np.sqrt(od_x**2 + od_y**2 + od_z**2)
    odp_rss_vel = np.sqrt(odp_dvx**2 + odp_dvy**2 + odp_dvz**2)

    std_odp_rss_pos = np.std(odp_rss_pos)
    three_sigma_odp_pos = 3 * std_odp_rss_pos

    std_odp_rss_vel = np.std(odp_rss_vel)
    three_sigma_odp_vel = 3 * std_odp_rss_vel

    Altitude = np.sqrt(px**2 + py**2 + pz**2) - 6378136.00
    Alt_KM = Altitude / 1000

    Abs_Acc = np.sqrt(ax**2 + ay**2 + az**2)
    Acc_g = Abs_Acc / 9.81

    Abs_vel = np.sqrt(vx**2 + vy**2 + vz**2)
    Abs_Vel_km = Abs_vel / 1000

    df['PRECISE_SV_PROP_0'] = px_p
    df['PRECISE_SV_PROP_1'] = py_p
    df['PRECISE_SV_PROP_2'] = pz_p
    df['PRECISE_SV_PROP_3'] = vx_p
    df['PRECISE_SV_PROP_4'] = vy_p
    df['PRECISE_SV_PROP_5'] = vz_p

    df['SV_Diff_0'] = dx
    df['SV_Diff_1'] = dy
    df['SV_Diff_2'] = dz
    df['SV_Diff_3'] = dvx
    df['SV_Diff_4'] = dvy
    df['SV_Diff_5'] = dvz

    df['ODP_SV_Diff_0'] = od_x
    df['ODP_SV_Diff_1'] = od_y
    df['ODP_SV_Diff_2'] = od_z
    df['ODP_SV_Diff_3'] = odp_dvx
    df['ODP_SV_Diff_4'] = odp_dvy
    df['ODP_SV_Diff_5'] = odp_dvz

    df['Altitude'] = Alt_KM
    df['ACC_G'] = Acc_g
    df['ABS_Vel'] = Abs_Vel_km

    df['RSS_POS'] = rss_pos
    df['RSS_VEL'] = rss_vel

    df['Odp_RSS_POS'] = odp_rss_pos
    df['Odp_RSS_VEL'] = odp_rss_vel

    # =========================================================
    # 9. SAVE OUTPUT CSV
    # =========================================================
    output_path = os.path.join(output_dir, output_file)
    df.to_csv(output_path, index=False)

    print("CSV saved at:", output_path)

    # =========================================================
    # 10. FILTERED PLOTS (ORIGINAL PLOT LIMITS PRESERVED)
    # =========================================================
    print("Step 8: Saving filtered plots...")

    plot_time = df['rec_time'] / 3600

    # SPS QM 'Humidity Chamber' Analysis : SPS Pos Error #
    # ==================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))

    plt.plot(plot_time, dx, label='Pos_Error_X')
    plt.plot(plot_time, dy, label='Pos_Error_Y')
    plt.plot(plot_time, dz, label='Pos_Error_Z')
    plt.plot(plot_time, rss_pos, label='RSS Pos Error')

    stats_text = (f"Mean Pos:{rss_pos.mean():.3f}m\n"
                  f"STD Pos:{three_sigma_pos:.2f}m\n")
    plt.text(0.02, 0.92,
             stats_text, transform=plt.gca().transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor="white", alpha=0.8))

    plt.title(f"{title} : SPS Pos Error")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("SPS Pos Error(m)")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "RSS POSITION ERROR.png"), dpi=300)
    plt.show()
    plt.close()

    # ==================================================#
    # SPS QM 'Humidity Chamber' Analysis : SPS Vel Error #
    # ==================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))

    plt.plot(plot_time, dvx, label='Vel_Error_X')
    plt.plot(plot_time, dvy, label='Vel_Error_Y')
    plt.plot(plot_time, dvz, label='Vel_Error_Z')
    plt.plot(plot_time, rss_vel, label='RSS VEL Error')
    stats_text = (f"Mean Vel:{rss_vel.mean():.3f}cm/s\n"
                  f"STD Vel:{three_sigma_vel:.2f}cm/s\n")
    plt.text(0.02, 0.92,
             stats_text, transform=plt.gca().transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor="white", alpha=0.8))

    plt.title(f"{title} : SPS Vel Error")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("SPS Vel Error(cm/s)")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "RSS VELOCITY ERROR.png"), dpi=300)
    plt.show()
    plt.close()

    # ========================================================#
    # SPS QM 'Humidity Chamber' Analysis : SPS ODP Pos Error #
    # ========================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))

    plt.plot(plot_time, od_x, label='ODP_Pos_Error_X')
    plt.plot(plot_time, od_y, label='ODP_Pos_Error_Y')
    plt.plot(plot_time, od_z, label='ODP_Pos_Error_Z')
    plt.plot(plot_time, odp_rss_pos, label='ODP RSS Pos Error')

    stats_text = (f"ODP Mean Pos:{odp_rss_pos.mean():.3f}m\n"
                  f"ODP STD Pos:{three_sigma_odp_pos:.2f}m\n")
    plt.text(0.02, 0.92,
             stats_text, transform=plt.gca().transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor="white", alpha=0.8))

    plt.title(f"{title}:ODP SPS Pos Error")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("SPS ODP Pos Error(m)")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "ODP POSITION Error.png"), dpi=300)
    plt.show()
    plt.close()

    # =======================================================#
    # SPS QM 'Humidity Chamber' Analysis : SPS ODP Vel Error #
    # =======================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))

    plt.plot(plot_time, odp_dvx, label='ODP Vel_Error_X')
    plt.plot(plot_time, odp_dvy, label='ODP Vel_Error_Y')
    plt.plot(plot_time, odp_dvz, label='ODP Vel_Error_Z')
    plt.plot(plot_time, odp_rss_vel, label='ODP RSS VEL Error')

    stats_text = (f"ODP Mean Vel:{odp_rss_vel.mean():.3f}cm/s\n"
                  f"ODP STD Vel:{three_sigma_odp_vel:.2f}cm/s\n")
    plt.text(0.02, 0.92,
             stats_text, transform=plt.gca().transAxes,
             fontsize=11, verticalalignment='top', bbox=dict(boxstyle='round', facecolor="white", alpha=0.8))

    plt.title(f"{title}: SPS ODP Vel Error")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("SPS ODP Vel Error(cm/s)")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "ODP Velocity Error.png"), dpi=300)
    plt.show()
    plt.close()

    # =====================================================================#
    # SPS QM 'Humidity Chamber' Analysis :REC Time Vs RSS Pos and Altitude #
    # =====================================================================#
    plt.ion()
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(plot_time, rss_pos, label='RSS POS', color="blue")
    ax1.set_xlabel("GPS time(hrs)")
    ax1.set_ylabel("RSS POS(m)", color="blue")
    ax1.tick_params(axis="y", color="blue")
    ax1.grid(True)
    ax1.legend()
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
    ax2 = ax1.twinx()
    ax2.plot(plot_time, Alt_KM, label='Altitude', color="green")
    ax2.set_ylabel("Altitude(km)", color="green")
    ax2.tick_params(axis="y", color="green")
    plt.title(f"{title} : REC Time Vs RSS POS and Altitude")
    ax2.legend()
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(nbins=25))
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "RSS POS vs ALTITUDE.png"), dpi=300)
    plt.show()
    plt.close()

    # =====================================================================#
    # SPS QM 'Humidity Chamber' Analysis :REC Time Vs Altitude, ABS VEL #
    # =====================================================================#
    plt.ion()
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(plot_time, Alt_KM, color="blue", label='Altitude')
    ax1.set_xlabel("GPS time(hrs)")
    ax1.set_ylabel("Altitude(km)", color="blue")
    ax1.tick_params(axis="y", color="blue")
    ax1.grid(True)
    ax1.legend()
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(nbins=25))
    ax2 = ax1.twinx()
    ax2.plot(plot_time, Acc_g, label='ACC G', color="green")
    ax2.plot(plot_time, Abs_Vel_km, label='RSS VEL', color="orange")
    ax2.set_ylabel("ACC G and Abs VEL", color="green")
    ax2.tick_params(axis="y", color="green")
    plt.title(f"{title} : REC Time Vs Altitude,ABS VEL,ACC G")
    ax2.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "ALTITUDE Vs ACC_G.png"), dpi=300)
    plt.show()
    plt.close()

    # ==============================================================================#
    # SPS QM 'Humidity Chamber' Analysis :REC Time Vs RSS vel and Altitude #
    # ==============================================================================#
    plt.ion()
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.plot(plot_time, rss_vel, label='RSS VEL', color="blue")
    ax1.set_xlabel("GPS time(hrs)")
    ax1.set_ylabel("RSS VEL(cm/s)", color="blue")
    ax1.tick_params(axis="y")
    ax1.grid(True)
    ax1.legend()
    ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    ax2 = ax1.twinx()
    ax2.plot(plot_time, Alt_KM, label='Altitude', color="green")
    ax2.set_ylabel("Altitude(km)", color="green")
    ax2.tick_params(axis="y", color="green")
    plt.title(f"{title} : REC Time Vs RSS Vel and Altitude")
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(nbins=25))
    ax2.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "RSS VEL VS ALT.png"), dpi=300)
    plt.show()
    plt.close()

    # SPS QM 'Humidity Chamber' Analysis : SPS Pos Error and oDP POS ERROR #
    # =====================================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))

    plt.plot(plot_time, rss_pos, label='RSS Pos Error')
    plt.plot(plot_time, odp_rss_pos, label='ODP Pos Error')

    plt.title(f"{title} : SPS Pos Error and ODP Pos Error")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("SPS Pos Error(m),ODP Pos Error(m)", color="blue")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "RSS POSITION ERROR and ODP POSITION ERROR.png"), dpi=300)
    plt.show()
    plt.close()

    # SPS QM 'Humidity Chamber' Analysis : SPS Vel Error and oDP Vel ERROR #
    # =====================================================================#
    plt.ion()
    plt.figure(figsize=(12, 6))

    plt.plot(plot_time, rss_vel, label='RSS VEL Error')
    plt.plot(plot_time, odp_rss_vel, label='ODP VEL Error')

    plt.title(f"{title} : SPS Vel Error and ODP Vel Error")
    plt.xlabel("GPS time(hrs)")
    plt.ylabel("SPS Vel Error(cm/s),ODP Vel Error(cm/s)")

    ax = plt.gca()
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=10))

    plt.xticks(rotation=45)
    plt.legend(loc='upper right')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "RSS VELOCITY ERROR and ODP VEL Error.png"), dpi=300)
    plt.show()
    plt.close()

    print("\n✅ ALL DONE — Everything saved in:", output_dir)


if __name__=="__main__":
    process_files_full("D:/TEJASWINI APPRENTICE/G1-POS-VEL ANALYSIS/QM_thermalcycling/GAGANYAAN_RT1_2026-11-15_07-25-55__PVT.csv","D:/TEJASWINI APPRENTICE/G1-POS-VEL ANALYSIS/motion_V1_openloop_singleAnt.csv","output_file.csv")