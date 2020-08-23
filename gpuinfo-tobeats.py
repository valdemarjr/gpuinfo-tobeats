#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import atexit
import json
import pytz
import argparse
from lib.pylogbeat import PyLogBeatClient
from datetime import datetime
from collections import OrderedDict
from py3nvml import py3nvml as nv

class GPUCollector(object):
    def __init__(self):
        self.labels = ['gpu', 'name', 'driver']
        self.driver = nv.nvmlSystemGetDriverVersion()

        self.n_gpu = nv.nvmlDeviceGetCount()
        self.hnds = [nv.nvmlDeviceGetHandleByIndex(i) for i in
                     range(self.n_gpu)]
        self.args = []
        for i, hnd in enumerate(self.hnds):
            args = OrderedDict()
            args['gpu'] = 'gpu%d' % i
            args['name'] = nv.nvmlDeviceGetName(hnd)
            args['driver'] = self.driver
            self.args.append(args)

    def temperature(self, hnd):
        try:
            return nv.nvmlDeviceGetTemperature(hnd, nv.NVML_TEMPERATURE_GPU)
        except nv.NVMLError_NotSupported:
            return -1

    def usage_ratio(self, hnd):
        return nv.nvmlDeviceGetUtilizationRates(hnd).gpu

    def mem_info(self, hnd):
        return nv.nvmlDeviceGetMemoryInfo(hnd)

    def power_usage(self, hnd):
        return nv.nvmlDeviceGetPowerUsage(hnd) / 1000

    def update(self):
        for hnd, args in zip(self.hnds, self.args):
            mem = self.mem_info(hnd)
            log({
                "node_gpu_memory_bytes_used": mem.used,
                "node_gpu_memory_bytes_total": mem.total,
                "node_gpu_power_watts": self.power_usage(hnd),
                "node_gpu_usage_ratio": self.usage_ratio(hnd),
                "node_gpu_temp_celsius": self.temperature(hnd)
                })

def log(message):
    time_fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
    message_snd = {
        "@timestamp": datetime.now(pytz.timezone('UTC')).strftime(time_fmt),
        "host": "SRVCONTAINER-LNX-01",
        "level": "INFO",
        "application":"gpuinfo",
        "logsource": "SRVCONTAINER-LNX-01",
        "source": "SRVCONTAINER-LNX-01",
        "message": json.dumps(message),
        "agent_type": "python-filebeat"
    }
    message_snd.update(message)
    client = PyLogBeatClient(args.server, args.port, ssl_enable=False)
    try:
        client.connect()
        print('Send data trought beats:'+json.dumps(message_snd))
        client.send([message_snd])
        client.close()
    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", help="Server with Beats enable", required=True)
    parser.add_argument("-p", "--port", help="Port of Beats", required=True)
    args = parser.parse_args()
    nv.nvmlInit()
    atexit.register(nv.nvmlShutdown)
    gc = GPUCollector()

    while True:
        gc.update()
        time.sleep(5)