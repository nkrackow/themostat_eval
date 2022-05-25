#!/usr/bin/python3
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def main():
    f = open('differential_-50mV_offset_10mV_amplitude_long_60dB.csv', 'r')
    def convert(i): return float(i)
    data1 = list(map(convert, f.readlines()))
    f.close()
    f = open('common_mode_2V_offset_1V_amplitude_long.csv', 'r')
    data2 = list(map(convert, f.readlines()))
    f.close()
    f = open('subtracted.csv', 'w')
    f.writelines(str([d2-d1 for d1, d2 in zip(data1, data2)]))
    data3 = [d1-d2-60 for d1, d2 in zip(data1, data2)]
    fig, ax = plt.subplots(1)
    x = np.logspace(0.01, 5, len(data1))
    # x = np.linspace(1, 100_000, len(data1))
    ax.plot(x, data2, label='Common Mode')
    ax.plot(x, data1, label='Differential (60 dB gain)')
    ax.plot(x, data3, label='Difference (CMRR)')
    ax.grid('minor')
    ax.set_title("Thermostat CMRR")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(1, 100_000)
    ax.set_xscale('log')
    ax.legend(loc='center left')
    plt.show()

    f.close()


if __name__ == '__main__':
    main()
