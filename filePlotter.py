import matplotlib.font_manager as fm
from utilities import FileReader
import matplotlib.pyplot as plt
from itertools import islice
import numpy as np
import argparse
import csv
import ast

SENSOR_CSVS = {
    "imu" : "imu_content_{shape}_corrected.csv",
    "odom" : "odom_content_{shape}_corrected.csv",
    "laser" : "laser_content_{shape}_corrected.csv"
}

def setfont(TITLE_SIZE=20, AXES_SIZE=10):
    FONT_PATH="/usr/share/texmf/fonts/opentype/public/lm/lmsans10-regular.otf"
    # Load the font into Matplotlib's font manager
    custom_font_title = fm.FontProperties(fname=FONT_PATH, size=TITLE_SIZE)
    custom_font_axes = fm.FontProperties(fname=FONT_PATH, size=AXES_SIZE)
    
    return custom_font_title, custom_font_axes

FONT_TI, FONT_AX = setfont()

def plot_imu(ax, sensor_csvs, shape):
    """
    Plot all the linear and angular accelerations against time (for IMU data)
    """
    file = sensor_csvs["imu"]
    headers, values=FileReader(file).read_file() 
    time_list=[]
    first_stamp=values[0][-1]
    
    for val in values:
        time_list.append((val[-1] - first_stamp)/1e9)

    acc_x = [lin[0] for lin in values]
    acc_y = [lin[1] for lin in values]
    ang_z = [lin[2] for lin in values]

    ax.plot(time_list, acc_x, label="linear acceleration (x)")
    ax.plot(time_list, acc_y, label="linear acceleration (y)")
    ax.plot(time_list, ang_z, label="angular velocity (z)")
    
    ax.set_title(f"IMU Measured Robot Linear Acceleration and Angular Velocity (motion: {shape})", fontproperties=FONT_TI)
    ax.set_xlabel("Time [s]", fontproperties=FONT_AX)
    ax.set_ylabel("Linear Acceleration [m/s$^2$] and Angular Velocity [rad/s])", fontproperties=FONT_AX)
    ax.set_xlim([min(time_list), max(time_list)])
    ax.legend(prop = FONT_AX)
    ax.grid()
    
def plot_odom_xy(ax, sensor_csvs, shape):
    """
    Plot the robot's position top view (for Odom data)
    """
    file = sensor_csvs["odom"]
    _, values=FileReader(file).read_file()
    x_vals = [lin[0] for lin in values]
    y_vals  = [lin[1] for lin in values]
    ax.plot(x_vals, y_vals, label="robot position")
    ax.scatter(x_vals[0], y_vals[0], label="start")
    ax.scatter(x_vals[-1], y_vals[-1], marker="*", color="red", label="end")
    ax.set_title(f"Odometry Measured Robot Position Top View (motion: {shape})", fontproperties=FONT_TI)
    ax.set_xlabel("Robot x position [m]", fontproperties=FONT_AX)
    ax.set_ylabel("Robot y position [m]", fontproperties=FONT_AX)
    ax.set_aspect('equal', adjustable='box')
    ax.legend(prop = FONT_AX, loc = "center left", bbox_to_anchor=(1, 0.5))
    ax.grid()

def plot_imu_odom_data(sensor_csvs, shape):
    fig, ax = plt.subplots(2, 1, figsize=(14, 10))

    plot_odom_xy(ax[0], sensor_csvs, shape)
    plot_imu(ax[1], sensor_csvs, shape)

    plt.tight_layout()
    plt.show()
    return fig

def plot_laser_data(sensor_csvs, shape):
    file = sensor_csvs["laser"]
    ROW = 30
    THETA_MIN = -np.pi
    with open(file, 'r') as f:
        csv_reader = csv.DictReader(f)
        csv_row = next(islice(csv_reader, ROW, ROW + 1), None)

        timestamp_s = float(csv_row["stamp"]) / 1e9
        ranges = csv_row["ranges"]
        increment = float(csv_row["angle_increment"])

    ranges = np.fromstring(csv_row["ranges"].strip("[]"), sep=",")
    x_list = []
    y_list = []
    for i in range (0, len(ranges)):
        theta_i = THETA_MIN + (i * increment)
        if np.isfinite(ranges[i]):
            x = ranges[i] * np.cos(theta_i)
            y = ranges[i] * np.sin(theta_i)
            x_list.append(x)
            y_list.append(y)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.scatter(x_list, y_list, linewidth=1.0, alpha=0.4, color="0.2", label="laser ranges")
    ax.scatter(0.0, 0.0, label="robot location", color="red")
    ax.set_title(f"Laser Scan Ranges and Robot Location Top View at Time {timestamp_s} sec \n (motion: {shape})", fontproperties=FONT_TI)
    ax.set_xlabel("x [m]", fontproperties=FONT_AX)
    ax.set_ylabel("y [m]", fontproperties=FONT_AX)
    ax.legend()
    ax.grid()

    plt.show()
    return fig
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument("--shape", type=str, required=True, help="the motion shape to plot")
    parser.add_argument("--laser", action="store_true", help="to plot the laser scan messages")
    
    args = parser.parse_args()
    sensor_csvs = {
        key: filename.format(shape=args.shape)
        for key, filename in SENSOR_CSVS.items()
    }

    if args.laser:
        figure = plot_laser_data(sensor_csvs, args.shape)
        figure.savefig(f"figures/fig_laser_{args.shape}.png")
    else:
        figure = plot_imu_odom_data(sensor_csvs, args.shape)
        figure.savefig(f"figures/fig_imu_odom_{args.shape}.png")