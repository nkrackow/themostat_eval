#!/usr/bin/python3
# evaluate raw adc samples from text file
import argparse
import numpy as np
import matplotlib.pyplot as plt

NO_SAMPLES = 1_000_000
# first lines is startup prints
STARTUP_LINES = 15
F_S = 503.5


def eval_raw(file, fldata):
    f = open(file, 'r')
    if fldata:
        def convert(i): return float(i)
    else:
        def convert(i): return int(i)
    data = list(map(convert, f.readlines()[
                STARTUP_LINES: NO_SAMPLES + STARTUP_LINES]))
    f.close()
    std_dev = np.std(data)
    _, ax = plt.subplots(2)
    ax[0].plot(data)
    ax[0].grid()
    ax[0].text(0.75, 0.1, f'standard deviation: {std_dev}', transform=ax[0].transAxes,
               verticalalignment='top', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round'))
    ax[0].set_title("Time domain data")
    ax[0].set_xlabel("sample nr.")
    ax[0].set_ylabel("adc code")
    ax[1].psd(data, Fs=F_S, NFFT=NO_SAMPLES)
    ax[1].set_title("data PSD")
    ax[1].set_xscale("log")
    plt.show()
    input()


def main():
    """ Main program entry point. """
    parser = argparse.ArgumentParser(description='record thermostat-eem data')
    parser.add_argument('--mode', '-m', type=str, default='raw',
                        help='evaluation mode, eg. raw for raw adc samples of one ch in txt file')
    parser.add_argument('--file', '-f', type=str, default='temp.txt',
                        help='data file location')

    args = parser.parse_args()

    if args.mode == "raw":
        eval_raw(args.file, False)
    elif args.mode == "float":
        eval_raw(args.file, True)
    else:
        print("undefined eval mode")


if __name__ == '__main__':
    main()
