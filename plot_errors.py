import matplotlib.font_manager as fm
from utilities import FileReader
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

def setfont(SUPTITLE_SIZE = 26, TITLE_SIZE=20, AXES_SIZE=10):
    FONT_PATH="/usr/share/texmf/fonts/opentype/public/lm/lmsans10-regular.otf"
    # Load the font into Matplotlib's font manager
    custom_font_title = fm.FontProperties(fname=FONT_PATH, size=TITLE_SIZE)
    custom_font_axes = fm.FontProperties(fname=FONT_PATH, size=AXES_SIZE)
    
    return custom_font_title, custom_font_axes

FONT_TI, FONT_AX = setfont()

def plot_e_vs_edot(values_linear, values_angular, ax):
    """
    Plots:
        (e vs edot) for bot linear and angular
    """
    e_lin = [val[0] for val in values_linear]
    e_ang = [val[0] for val in values_angular]

    edot_lin = [val[1] for val in values_linear]
    edot_ang = [val[1] for val in values_angular]

    ax.plot(e_lin, edot_lin, label="linear error vs linear error dot")
    ax.plot(e_ang, edot_ang, label="angular error vs angular error dot")

    ax.set_title("Error vs Error Dot (linear and angular)", fontproperties=FONT_TI)
    ax.set_xlabel("Error Linear [m] and Angular [rad]", fontproperties=FONT_AX)
    ax.set_ylabel("Error Dot Linear [m/s] and Angular [rad/s]", fontproperties=FONT_AX)
    ax.grid()
    ax.legend(prop = FONT_AX)

def plot_e_edot_vs_time(values_linear, values_angular, ax):
    """
    Plots
        (e vs t), (edot vs t) for both linear and angular
    """
    e_lin = [val[0] for val in values_linear]
    e_ang = [val[0] for val in values_angular]

    edot_lin = [val[1] for val in values_linear]
    edot_ang = [val[1] for val in values_angular]

    time_robot = [(val[3] - values_linear[0][3])/1e9 for val in values_linear]

    ax.plot(time_robot, e_lin, label="linear error vs t")
    ax.plot(time_robot, e_ang, label="angular error vs t")
    ax.plot(time_robot, edot_lin, label="linear error dot vs t")
    ax.plot(time_robot, edot_ang, label="angular error dot vs t")

    ax.set_xlim(left = 0)
    ax.set_title("Errors (linear and angular) vs Time", fontproperties=FONT_TI)
    ax.set_xlabel("Time [s]", fontproperties=FONT_AX)
    ax.set_ylabel("Error Linear [m] and Angular [rad] Error Dot Linear [m/s] and Angular [rad/s]", fontproperties=FONT_AX)
    ax.grid()
    ax.legend(prop = FONT_AX)

def plot_x_y_theta_vs_t(values, ax):
    """
    Plots:
        (x vs t), (y vs t), (theta vs t)
    """
    x_robot = [val[0] for val in values]
    y_robot = [val[1] for val in values]
    theta_robot = [val[2] for val in values]
    # from the first timestamp converted to seconds
    time_robot = [(val[3] - values[0][3])/1e9 for val in values]

    ax.plot(time_robot, x_robot, label="x vs t")
    ax.plot(time_robot, y_robot, label="y vs t")
    ax.plot(time_robot, theta_robot, label=r"$\theta$ vs t")

    ax.set_xlim(left = 0)
    ax.set_title("Robot State vs Time ([x, y, theta] vs time)", fontproperties=FONT_TI)
    ax.set_xlabel("Time [s]", fontproperties=FONT_AX)
    ax.set_ylabel("Robot Position (x, y) [m] and Angle (theta) [rad]", fontproperties=FONT_AX)
    ax.grid()
    ax.legend(prop = FONT_AX)

def plot_x_vs_y(values, ax):
    """
    Plots:
        (x vs y)
    """
    x_robot = [val[0] for val in values]
    y_robot = [val[1] for val in values]
    start_point = [x_robot[0], y_robot[0]]
    goal_point = [x_robot[-1], y_robot[-1]]
    ax.plot(x_robot, y_robot, label="robot positions")
    ax.scatter(start_point[0], start_point[1], label="starting location")
    ax.scatter(goal_point[0], goal_point[1], marker = "*", label="goal location")

    ax.set_title("Robot Positions (x vs y)", fontproperties=FONT_TI)
    ax.set_xlabel("Robot Position (x) [m]", fontproperties=FONT_AX)
    ax.set_ylabel("Robot Position (y) [m]", fontproperties=FONT_AX)
    ax.grid()
    ax.legend(prop = FONT_AX)


def plot_point_data(dir: str):
    """
    Plot the four things for the report 
    """
    FILES = {
        "LINEAR" : os.path.join(dir, "linear.csv"),
        "ANGULAR" : os.path.join(dir, "angular.csv"),
        "ROBOT_POSE" : os.path.join(dir, "robot_pose.csv")
    }
    VALUES = {}
    for key, value in FILES.items():
        _, values = FileReader(value).read_file()
        VALUES[key] = values

    fig, ax = plt.subplots(2, 2, figsize=(14, 10))

    # Plot the x vs y
    plot_x_vs_y(VALUES["ROBOT_POSE"], ax[0, 0])

    # Plot
    plot_x_y_theta_vs_t(VALUES["ROBOT_POSE"], ax[0, 1])

    # Plot the error and error dot vs time
    plot_e_edot_vs_time(VALUES["LINEAR"], VALUES["ANGULAR"], ax[1, 0])

    plot_e_vs_edot(VALUES["LINEAR"], VALUES["ANGULAR"], ax[1, 1])

    plt.tight_layout()
    plt.show()

    return fig

def plot_trajectory_data(trajectory, dir):
    """
    Plot the trajectory x vs y
    """
    robot_pose_file = os.path.join(dir, "robot_pose.csv")
    _, values = FileReader(robot_pose_file).read_file()

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    x_robot = [val[0] for val in values]
    y_robot = [val[1] for val in values]
    start_point = [x_robot[0], y_robot[0]]
    goal_point = [x_robot[-1], y_robot[-1]]
    ax.plot(x_robot, y_robot, label="robot positions")
    ax.scatter(start_point[0], start_point[1], label="starting location")
    ax.scatter(goal_point[0], goal_point[1], marker = "*", label="goal location")


    x_curve = np.linspace(min(x_robot), max(x_robot), 500)
    if trajectory == "sigmoid":
        y_traj = 2 / (1 + np.exp(-2 * x_curve)) - 1
        eqn = r"$y=\frac{2}{1+e^{-2x}}-1$"
    elif trajectory == "parabola":
        y_traj = x_curve**2
        eqn = r"$y=x^2$"
    
    ax.plot(x_curve, y_traj, label=eqn, linestyle=":")
    ax.set_title(f"Robot Positions (x vs y): Trajectory Tracking ({trajectory})", fontproperties=FONT_TI)
    ax.set_xlabel("Robot Position (x) [m]", fontproperties=FONT_AX)
    ax.set_ylabel("Robot Position (y) [m]", fontproperties=FONT_AX)
    ax.grid()
    ax.legend(prop = FONT_AX)
    plt.show()

    return fig
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process some files."
    )
    parser.add_argument(
        "--files-dir",
        required=True,
        dest="files_dir",
        help="Directory with the three files (angular.csv, robot_pose.csv, linear.csv)"
    )
    parser.add_argument(
        "--trajectory",
        dest="trajectory"
    )
    parser.add_argument(
        "--name",
        required=True,
        dest="name"
    )
    args = parser.parse_args()
    
    if args.trajectory:
        fig = plot_trajectory_data(args.trajectory, args.files_dir)
        fig.savefig(f"figures/{args.name}.png")
    else:
        fig = plot_point_data(args.files_dir)
        fig.savefig(f"figures/{args.name}.png")