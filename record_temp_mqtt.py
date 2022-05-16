#!/usr/bin/python3
# Small script that ready mqtt data from thermostat-eem and records one
# channel temperature and one channel current.
import argparse
import asyncio
import json
import sys
import csv
import matplotlib.pyplot as plt
from gmqtt import Client as MqttClient

MAXLEN = 1000000
TEMP_CH = 7
CURR_CH = 3


class TelemetryReader:
    """ Helper utility to read telemetry. """

    @classmethod
    async def create(cls, prefix, broker, queue):
        """Create a connection to the broker and an MQTT device using it."""
        client = MqttClient(client_id='')
        await client.connect(broker)
        return cls(client, prefix, queue)

    def __init__(self, client, prefix, queue):
        """ Constructor. """
        self.client = client
        self._telemetry = []
        self.client.on_message = self.handle_telemetry
        self._telemetry_topic = f'{prefix}/telemetry'
        self.client.subscribe(self._telemetry_topic)
        self.queue = queue

    def handle_telemetry(self, _client, topic, payload, _qos, _properties):
        """ Handle incoming telemetry messages over MQTT. """
        assert topic == self._telemetry_topic
        self.queue.put_nowait(json.loads(payload))


async def get_tele(telemetry_queue):
    latest_values = await telemetry_queue.get()
    return [latest_values['channel_temperatures'][TEMP_CH], latest_values['iir_output'][CURR_CH]]


def main():
    """ Main program entry point. """
    parser = argparse.ArgumentParser(description='record thermostat-eem data')
    parser.add_argument('--broker', '-b', type=str, default='10.42.0.1',
                        help='The MQTT broker to use to communicate with the device.')
    parser.add_argument('--prefix', '-p', type=str, default='dt/sinara/thermostat-eem/80-1f-12-63-84-1b',
                        help='The device prefix to use for communication. E.g. '
                        'dt/sinara/thermostat-eem/80-1f-12-63-84-1b')

    args = parser.parse_args()

    print(args.prefix)

    telemetry_queue = asyncio.LifoQueue()

    async def telemetry():
        await TelemetryReader.create(args.prefix, args.broker, telemetry_queue)
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    telemetry_task = asyncio.Task(telemetry())

    async def record():
        fig = plt.figure()
        plt.title("Thermostat CH1 temperature")
        ax = fig.add_subplot(1, 1, 1)
        plt.ion()

        f = open('temp.csv', 'w')
        writer = csv.writer(f)
        data = []
        temp = []
        for i in range(MAXLEN):
            data.append(await get_tele(telemetry_queue))
            writer.writerow([data[i][0], data[i][1]])
            temp.append(data[i][0])
            print(f'temp: {data[i][0]}, current: {data[i][1]}')
            ax.clear()
            ax.plot(temp)
            plt.grid(True)
            fig.canvas.draw()
            plt.pause(0.0001)
            fig.canvas.flush_events()

        f.close()
        telemetry_task.cancel()

    loop = asyncio.get_event_loop()
    sys.exit(loop.run_until_complete(record()))


if __name__ == '__main__':
    main()
