#!/usr/bin/python3
# evaluate raw adc samples from text file
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# first lines is startup prints
STARTUP_LINES = 15
F_S = 503.5

# degree celsius/kelvin per adc LSB around 25°C/half scale
D_PER_LSB = 5.314404177170218e-06


def eval_raw(file, fldata, eval_psd, no_samples):
    f = open(file, 'r')
    if fldata:
        def convert(i): return float(i)
    else:
        def convert(i): return int(i)
    data = list(map(convert, f.readlines()[
                STARTUP_LINES: no_samples + STARTUP_LINES]))
    f.close()
    data = signal.detrend(data)
    std_dev = np.std(data)
    mean = np.mean(data)
    print(f'std deviation: {std_dev}')
    print(f'mean value: {mean}')
    if eval_psd:
        fig, ax = plt.subplots(2)
        fig.tight_layout()
        ax[0].plot(data)
        ax[0].grid()
        ax[0].set_xlim(0, no_samples)
        # ax[0].text(0.75, 0.1, f'standard deviation: {std_dev}', transform=ax[0].transAxes,
        #            verticalalignment='top', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round'))
        ax[0].set_title("Time domain data")
        ax[0].set_xlabel("sample nr.")
        ax[0].set_ylabel("adc code")
        pxx, freqs = ax[1].psd(data, Fs=F_S, NFFT=no_samples)
        ax[1].set_title("data PSD (dB(LSB^2)/Hz)")
        ax[1].set_xscale("log")
        ax[1].set_xlim(0.0005, freqs[-1])

        sum = 0
        nr_samples = 0
        for f, p in zip(freqs, pxx):
            if 0.01 < f < 1.0:
                sum += p
                nr_samples += 1

        # 0.01 - 1 Hz -> ~1Hz bandwidth
        rms_noise = np.sqrt(sum/nr_samples)

        print(f'RMS noise in 0.01-1 Hz in LSB: {rms_noise}')
        print(f'in °K: {rms_noise * D_PER_LSB}')
    else:
        fig, ax = plt.subplots(1)
        fig.tight_layout()
        ax.plot(data)
        ax.grid()
        ax.set_xlim(0, no_samples)
        # ax.text(0.75, 0.1, f'standard deviation: {std_dev}', transform=ax.transAxes,
        #            verticalalignment='top', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round'))
        ax.set_title("Time domain data")
        ax.set_xlabel("sample nr.")
        ax.set_ylabel("adc code")

    plt.show()
    input()


def main():
    """ Main program entry point. """
    parser = argparse.ArgumentParser(description='record thermostat-eem data')
    parser.add_argument('--mode', '-m', type=str, default='raw',
                        help='evaluation mode, eg. raw for raw adc samples of one ch in txt file')
    parser.add_argument('--file', '-f', type=str, default='temp.txt',
                        help='data file location')
    parser.add_argument('--no_samples', '-s', type=int, default=1_000_000,
                        help='Number Samples to process')

    args = parser.parse_args()

    if args.mode == "raw":
        eval_raw(args.file, False, True, args.no_samples)
    elif args.mode == "float":
        eval_raw(args.file, True, True, args.no_samples)
    elif args.mode == "samples":
        eval_raw(args.file, True, False, args.no_samples)
    else:
        print("undefined eval mode")


if __name__ == '__main__':
    main()
