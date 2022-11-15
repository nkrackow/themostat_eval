#!/usr/bin/python3
# Try influxDB
import argparse
import influxdb
import matplotlib.pyplot as plt
from scipy import signal
import numpy as np


def main():
    """Main program entry point."""

    idb = influxdb.InfluxDBClient(host="murray.ber.quartiq.de", database="telegraf")
    data = idb.query(
        """SELECT mean(/statistics_._mean/) FROM "ai_artiq" WHERE ("topic" =~ /^dt\/sinara\/thermostat-eem\/80-1f-12-63-84-1b\/telemetry$/) AND time >= 1668432639407ms and time <= 1668433239407ms GROUP BY time(1000ms)""",
        epoch="ms",
    )
    temp = []
    no_samples = 0
    for point in list(data.get_points()):
        # print(point.get("time"))
        if point.get("mean_statistics_0_mean") != None:
            temp.append(point.get("mean_statistics_0_mean"))
            no_samples += 1

    mean = np.mean(temp)
    data = signal.detrend(temp)
    std_dev = np.std(data)
    print(f"std deviation / RMS: {std_dev}")
    print(f"mean value: {mean}")
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
    pxx, freqs = ax[1].psd(data, Fs=1, NFFT=no_samples)
    ax[1].set_title("data PSD (dB(K^2)/Hz)")
    ax[1].set_xscale("log")
    ax[1].set_xlim(0.001, freqs[-1])

    plt.show()
    input()


if __name__ == "__main__":
    main()
