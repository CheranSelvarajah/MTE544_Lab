import matplotlib.pyplot as plt
from utilities import FileReader




def plot_errors(filename):
    
    headers, values=FileReader(filename).read_file()
    
    time_list=[]
    
    first_stamp=values[0][-1]
    
    for val in values:
        time_list.append(val[-1] - first_stamp)

    
    
    fig, axes = plt.subplots(3,1, figsize=(14,6))


    axes[0].plot([lin[len(headers) - 3] for lin in values], [lin[len(headers) - 2] for lin in values])
    axes[0].set_title("state space")
    axes[0].grid()

    
    axes[1].set_title("ax state")
    axes[1].plot(time_list, [lin[0] for lin in values], label= headers[0])
    axes[1].plot(time_list, [lin[2] for lin in values], label= headers[2])

    axes[2].set_title("ay state")
    axes[2].plot(time_list, [lin[1] for lin in values], label= headers[1])
    axes[2].plot(time_list, [lin[3] for lin in values], label= headers[3])

    axes[1].legend()
    axes[1].grid()

    axes[2].legend()
    axes[2].grid()

    plt.show()
    
    





import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')
    
    args = parser.parse_args()
    
    print("plotting the files", args.files)

    filenames=args.files
    for filename in filenames:
        plot_errors(filename)


