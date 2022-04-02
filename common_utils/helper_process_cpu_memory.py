# 监控代码如下
#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Author: roninsswang
@File:MonitorProcess.py
@Time:2022/4/2 10:32
"""
import psutil
import re
import requests
import time
import json
MONITOR_API_URL = "http://localhost:2058/api/collector/push"
APP_NAME = "Dzookeeper.log.dir=/data/apps/zookeeper-3.5.3-beta_2/bin/"
MONITOR_TAG_NAME = "trip-corp-web"
TIME_INTERVAL = 20
class MonitorProcessInfo(object):
    pid_number = None
    process = None
    @classmethod
    def __init__(cls, process_name):
        """
        Get process ID number according to process name
        :param process_name:
        """
        pids = psutil.process_iter()
        for pid in pids:
            # Find PID by process name
            '''
            str_pid = str(pid)
            f = re.compile(process_name, re.I)
            if f.search(str_pid):
                global pid_number, process
                pid_number = int(str_pid.split('pid=')[1].split(',')[0])
                process = psutil.Process(pid_number)
            '''
            # Find PID based on process name CmdLine
            if process_name in ''.join(pid.cmdline()):
                global pid_number, process
                pid_number = pid.pid
                process = psutil.Process(pid_number)
    @classmethod
    def process_memory(cls):
        """
        Get process memory usage
        :return:
        """
        process_memory_percent = process.memory_percent()
        process_memory_info = process.memory_info()
        return process_memory_percent, process_memory_info.rss
    @classmethod
    def process_cpu(cls):
        """
        Get the CPU usage of the process
        :return:
        """
        process_cpu_percent = process.cpu_percent(interval=1.0)
        return process_cpu_percent
    @classmethod
    def process_io(cls):
        """
        Get process IO status
        :return:
        """
        process_io_count = process.io_counters()
        return process_io_count.read_bytes, process_io_count.write_bytes
    @classmethod
    def process_threads(cls):
        """
        Get Process Threads
        :return:
        """
        process_threads = process.num_threads()
        return process_threads
class PushMonitorProcessInfo(MonitorProcessInfo):
    def __init__(self, process_name, tag_name):
        """Monitoring indicators
            - memory_rss :      Memory size used by process
            - memory_percent:   Percentage of process memory used
            - process_threads:  Number of process threads
            - io_read_bytes:    Process IO read operation
            - io_write_bytes:   Process IO write operation
            - cpu_percent:      Percentage of CPU used by process
        :param process_name:
        :param tag_name:
        """
        # py3 super
        # super().__init__(process_name)
        """When super inherits the parent class in py2, the parent class needs to add the object attribute, 
        MonitorProcessInfo (object), otherwise it will be thrown incorrectly
        TypeError: must be type, not classobj"""
        super(PushMonitorProcessInfo, self).__init__(process_name)
        cpu_percent = PushMonitorProcessInfo.process_cpu()
        memory_percent, memory_rss = PushMonitorProcessInfo.process_memory()
        io_read_bytes, io_write_bytes = PushMonitorProcessInfo.process_io()
        thread_number = PushMonitorProcessInfo.process_threads()
        pro_data = {
            "memory_rss": memory_rss,
            "memory_percent": memory_percent,
            "io_read_bytes": io_read_bytes,
            "io_write_bytes": io_write_bytes,
            "cpu_percent": cpu_percent,
            "threads": thread_number
        }
        payload = []
        t = int(time.time())
        for k, v in pro_data.items():
            metric_data = {
                "metric": "process.%s" % k,
                "endpoint": "10.86.12.13",
                "tags": "tomcat_name=%s" % tag_name,
                "value": int(v),
                "timestamp": t,
                "step": TIME_INTERVAL
            }
            payload.append(metric_data)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                                        (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
            "Content-Type": "application/json"
        }
        rsp = requests.post(url=MONITOR_API_URL, data=json.dumps(payload), headers=headers)
        print(rsp.text)
while True:
    push_data = PushMonitorProcessInfo(APP_NAME, MONITOR_TAG_NAME)
    time.sleep(TIME_INTERVAL)
