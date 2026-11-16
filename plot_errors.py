import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import argparse
import re

def setfont(TITLE_SIZE=20, AXES_SIZE=10):
    FONT_PATH="/usr/share/texmf/fonts/opentype/public/lm/lmsans10-regular.otf"
    # Load the font into Matplotlib's font manager
    custom_font_title = fm.FontProperties(fname=FONT_PATH, size=TITLE_SIZE)
    custom_font_axes = fm.FontProperties(fname=FONT_PATH, size=AXES_SIZE)
    
    return custom_font_title, custom_font_axes

SETFONT = True
if SETFONT:
    FONT_TI, FONT_AX = setfont()
else:
    FONT_TI, FONT_AX = None, None

def plot_errors(filename, q, r, motion):
    df = pd.read_csv(filename)
    time = [(val - df["stamp"][0])/ 1e9 for val in df["stamp"]]
    
    est_x = df["kf_x"]
    est_y = df["kf_y"]

    est_ax = df["kf_ax"]
    measured_ax = df["imu_ax"]

    est_ay = df["kf_ay"]
    measured_ay = df["imu_ay"]

    fig, axes = plt.subplots(3,1, figsize=(14,10))

    # first plot is estimated x vs y
    axes[0].plot(est_x, est_y, label="estimated trajectory (kf_x, kf_y)")
    axes[0].set_title(f"Estimated x position [m] vs y position [m]: {motion} (Q = {q}, R = {r})", fontproperties=FONT_TI)
    axes[0].set_xlabel("x [m]")
    axes[0].set_ylabel("y [m]")
    axes[0].legend(prop=FONT_AX)
    axes[0].grid()

    axes[1].plot(time, est_ax, label="estimated acceleration (kf_ax)")
    axes[1].plot(time, measured_ax, label="measured acceleration (imu_ax)")
    axes[1].set_title(f"Estimated and Measured Acceleration (x): {motion} (Q = {q}, R = {r})", fontproperties=FONT_TI)
    axes[1].set_xlabel("Time [s]")
    axes[1].set_xlim([min(time), max(time)])
    axes[1].set_ylabel("Acceleration (x) [m/s^2]")
    axes[1].legend(prop=FONT_AX)
    axes[1].grid()
    
    axes[2].plot(time, est_ay, label="estimated acceleration (kf_ay)")
    axes[2].plot(time, measured_ay, label="measured acceleration (imu_ay)")
    axes[2].set_title(f"Estimated and Measured Acceleration (y): {motion} (Q = {q}, R = {r})", fontproperties=FONT_TI)
    axes[2].set_xlabel("Time [s]")
    axes[2].set_xlim([min(time), max(time)])
    axes[2].set_ylabel("Acceleration (y) [m/s^2]")
    axes[2].legend(prop=FONT_AX)
    axes[2].grid()

    plt.tight_layout()
    fig.savefig(f"figures/{motion}_q_{q}_r_{r}.png")
    plt.show()

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--file', required=True, help='The file to process')
    args = parser.parse_args()
    
    print("plotting the files", args.file)
    print(args.file)
    match = re.search(r"in_lab_data_(\w+)/q_([\d.]+)_r_([\d.]+)", args.file)
    if match:
        motion = match.group(1)
        q = float(match.group(2))
        r = float(match.group(3))

    plot_errors(args.file, q, r, motion)
