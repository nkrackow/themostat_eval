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


def eval_raw(file, fldata, eval_psd, no_samples, skip, temp_curr):
    f = open(file, 'r')
    if fldata:
        if temp_curr:
            def convert(i): return [float(j) for j in i.split(", ")]
        else:
            def convert(i): return float(i)
    else:
        def convert(i): return int(i)
    data = list(map(convert, f.readlines()[
                STARTUP_LINES + skip: no_samples + STARTUP_LINES + skip]))
    f.close()
    if temp_curr:
        curr = [j for _, j in data]
        data = [i for i, _ in data]
    mean = np.mean(data)
    data = signal.detrend(data)
    curr = signal.detrend(curr)
    std_dev = np.std(data)
    print(f'std deviation: {std_dev}')
    print(f'mean value: {mean}')
    if eval_psd:
        fig, ax = plt.subplots(2)
        # fig.tight_layout()
        # if temp_curr:
        #     ax[0].plot(curr)
        # ax[0].plot(data)
        # ax[0].grid()
        # ax[0].set_xlim(0, no_samples)
        # # ax[0].text(0.75, 0.1, f'standard deviation: {std_dev}', transform=ax[0].transAxes,
        # #            verticalalignment='top', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round'))
        # ax[0].set_title("Time domain data")
        # ax[0].set_xlabel("sample nr.")
        # ax[0].set_ylabel("adc code")
        # if temp_curr:
        #     pxx, freqs = plt.psd(curr, Fs=F_S, NFFT=no_samples)
        pxx, freqs = ax[1].psd(data, Fs=F_S, NFFT=no_samples)
        # ax[1].set_title("data PSD (dB(LSB^2)/Hz)")
        ax[1].set_xscale("log")
        # ax[1].set_xlim(0.0005, freqs[-1])

        sum = 0
        nr_samples = 0
        for f, p in zip(freqs, pxx):
            if 0.01 < f < 1.0:
                sum += p
                nr_samples += 1

        # 0.01 - 1 Hz -> ~1Hz bandwidth
        rms_noise = np.sqrt(sum/nr_samples)

        print(f'RMS noise in 0.01-1 Hz: {rms_noise}')
    # else:
    #     fig, ax = plt.subplots(1)
    #     fig.tight_layout()
    #     ax.plot(data)
    #     ax.grid()
    #     ax.set_xlim(0, no_samples)
    #     # ax.text(0.75, 0.1, f'standard deviation: {std_dev}', transform=ax.transAxes,
    #     #            verticalalignment='top', bbox=dict(facecolor='none', edgecolor='black', boxstyle='round'))
    #     ax.set_title("Time domain data")
    #     ax.set_xlabel("sample nr.")
    #     ax.set_ylabel("adc code")#

    fig, ax = plt.subplots(1)

    pxx[200:] = 0

    # ax.plot(data)
    fft = np.fft.fft(data)
    fft[200:-200] = 0
    fftcut = np.append(fft[:200], fft[-200:])
    data = np.fft.ifft(fft)
    datacut = np.fft.ifft(fftcut) * len(fftcut)/len(fft)

    t = np.linspace(0, 100, len(data))
    ax.plot(t, data*1000)
    # ax.plot(datacut)

    # ax.plot(pxx)

    data = np.fft.ifft(pxx)
    # fig, ax = plt.subplots(1)
    # fig.tight_layout()
    # ax.plot(data)
    ax.set_title("Thermostat-EEM data")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Temperature (mK)")
    # ax.text(0.9, 0.05, "0.01 - 1 Hz RMS noise: {rms_noise} °K")
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax.text(0.02, 0.05, f"0.01 - 1 Hz RMS noise: {rms_noise*1000:.3f} mK", transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
    ax.margins(0, 0.1)
    ax.grid()

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
    parser.add_argument('--skip', '-k', type=int, default=0,
                        help='Number of samples to skip at the beginning of dataset.')

    args = parser.parse_args()

    if args.mode == "raw":
        eval_raw(args.file, False, True, args.no_samples, args.skip, False)
    elif args.mode == "float":
        eval_raw(args.file, True, True, args.no_samples, args.skip, False)
    elif args.mode == "samples":
        eval_raw(args.file, True, False, args.no_samples, args.skip, False)
    elif args.mode == "temp_curr_psd":
        eval_raw(args.file, True, True, args.no_samples, args.skip, True)
    else:
        print("undefined eval mode")


if __name__ == '__main__':
    main()
