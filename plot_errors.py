import matplotlib.pyplot as plt
import numpy as np
from utilities import FileReader


def plot_errors(filename):

    headers, values = FileReader(filename).read_file()

    time_list = []
    first_stamp = values[0][-1]

    for val in values:
        time_list.append(val[-1] - first_stamp)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # First plot: state trajectory, parabola, and sigmoid
    x_values = [lin[0] for lin in values]
    y_values = [lin[1] for lin in values]

    axes[0].plot(x_values, y_values, label="State trajectory")

    # Plot parabola: y = x^2
    x_curve = np.linspace(min(x_values), max(x_values), 500)

    # axes[0].plot(
    #     x_curve,
    #     x_curve**2,
    #     label=r"$y=x^2$",
    #     linestyle="--"
    # )

    # Plot sigmoid, matching trajectory_planner():
    # y = 2 / (1 + exp(-2*x)) - 1
    sigmoid_y = 2 / (1 + np.exp(-2 * x_curve)) - 1

    axes[0].plot(
        x_curve,
        sigmoid_y,
        label=r"$y=\frac{2}{1+e^{-2x}}-1$",
        linestyle=":"
    )

    axes[0].set_title("State space")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    axes[0].set_aspect("equal", adjustable="box")
    axes[0].grid()
    axes[0].legend()

    # Second plot: each individual state
    axes[1].set_title("Each individual state")

    for i in range(len(headers) - 1):
        axes[1].plot(
            time_list,
            [lin[i] for lin in values],
            label=headers[i] + " linear"
        )

    axes[1].legend()
    axes[1].grid()

    plt.tight_layout()
    plt.show()


import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Process some files."
    )

    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="List of files to process"
    )

    args = parser.parse_args()

    print("Plotting the files", args.files)

    for filename in args.files:
        plot_errors(filename)
