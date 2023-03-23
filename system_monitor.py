import asyncio
import csv
import os
import sys
import time

import argparse
import psutil
from x_mock.m_random import m_date

from common import create_csv, create_next_date_csv
from process_monitor import process_monitor_info_record_to_file, get_csv_name


# @author Franciz
# @date 2023/2/27 18:59


class SystemMonitorInfo:
    cpu_rate = None  # cpu利用率百分比/s
    disk_read = None  # 磁盘读取速度/MB
    disk_write = None  # 磁盘写入速度/MB
    net_recv = None  # 磁盘网络接收速度/MB
    net_sent = None  # 磁盘网络发送速度/MB
    memory_used = None  # 已用内存/MB

    def __init__(self, interval_time=2):
        self.interval_time = interval_time

    async def get_system_memory_rate(self):
        """

        :return: PC的已用内存/MB
        """
        data = psutil.virtual_memory()
        memory = round(data.used / 1024 / 1024)
        self.memory_used = memory
        return memory

    async def get_system_cpu_rate(self):
        """

        :return: PC的CPU平均使用百分比
        """
        # await asyncio.sleep(1)
        cpu = psutil.cpu_percent(1)
        if self.interval_time > 1:
            time.sleep(self.interval_time - 1)
        self.cpu_rate = cpu
        return cpu

    async def get_system_disk_io(self):
        """

        :return: 系统磁盘io
        """
        disk_io_counter = psutil.disk_io_counters()
        start_time = time.perf_counter()
        disk_read_bytes = disk_io_counter.read_bytes
        disk_write_bytes = disk_io_counter.write_bytes
        disk_read_time = disk_io_counter.read_time
        disk_write_time = disk_io_counter.write_time
        await asyncio.sleep(1)
        disk_io_counter = psutil.disk_io_counters()
        disk_read_bytes1 = disk_io_counter.read_bytes
        disk_write_bytes1 = disk_io_counter.write_bytes
        end_time = time.perf_counter()
        time_diff = end_time - start_time
        disk_read_time1 = disk_io_counter.read_time
        disk_write_time1 = disk_io_counter.write_time
        total_read_time = disk_read_time1 - disk_read_time
        total_write_time = disk_write_time1 - disk_write_time
        # total_read = (disk_read_bytes1 - disk_read_bytes) / total_read_time
        # total_write = (disk_write_bytes1 - disk_write_bytes) / total_write_time
        total_read = (disk_read_bytes1 - disk_read_bytes) / time_diff
        total_write = (disk_write_bytes1 - disk_write_bytes) / time_diff
        # print("Time_Read : ", total_read_time)
        # print("Time_Write : ", total_write_time)
        # 单位mb
        total_read = round(total_read / 1024 / 1024, 2)
        total_write = round(total_write / 1024 / 1024, 2)
        self.disk_read = 0 if total_read < 0 else total_read
        self.disk_write = 0 if total_write < 0 else total_write
        # 读取,写入 MB/s
        return total_read, total_write

    async def get_system_network_io(self):
        """

        :return: 系统网络io
        """
        net_io_counter = psutil.net_io_counters()
        bytes_recv = net_io_counter.bytes_recv
        bytes_sent = net_io_counter.bytes_sent
        start_time = time.perf_counter()
        await asyncio.sleep(1)
        net_io_counter = psutil.net_io_counters()
        bytes_recv1 = net_io_counter.bytes_recv
        bytes_sent1 = net_io_counter.bytes_sent
        end_time = time.perf_counter()
        time_diff = end_time - start_time
        total_recv = (bytes_recv1 - bytes_recv) / time_diff
        total_sent = (bytes_sent1 - bytes_sent) / time_diff
        total_recv = round(total_recv / 1024 / 1024, 2)
        total_sent = round(total_sent / 1024 / 1024, 2)
        self.net_recv = 0 if total_recv < 0 else total_recv
        self.net_sent = 0 if total_sent < 0 else total_sent
        # 发送/接收 MB/s
        return total_sent, total_recv

    async def main(self):
        await asyncio.gather(self.get_system_cpu_rate(), self.get_system_memory_rate(),
                             self.get_system_disk_io(),
                             self.get_system_network_io())
        return [self.cpu_rate, self.memory_used, self.disk_read, self.disk_write, self.net_sent, self.net_recv]


def monitor_info_record_to_file(file_period=1, wait_time=10):
    raw_file_time = m_date.date()
    print(f'开始系统性能监控,记录文件创建周期:{file_period}天/次,监控记录:{wait_time}秒/次')
    # 准备写文件
    header = ['日期', '时间', 'cpu百分比/s', '已用内存/MB', '磁盘读取MB/s', '磁盘写入MB/s', '网络上传MB/s',
              '网络下载MB/s']
    file_name = get_csv_name(raw_file_time)
    create_csv(header, file_name)
    while True:
        if file_period is not None:
            file_name, raw_file_time = create_next_date_csv(file_name, file_period, header, None, raw_file_time)
        with open(file_name, 'a+', encoding='utf-8', newline='') as file_obj:
            # 1:创建writer对象
            writer = csv.writer(file_obj)
            monitor_info = SystemMonitorInfo(wait_time)
            result = asyncio.run(monitor_info.main())
            line = (m_date.date(), m_date.time(), *result)
            print(*line)
            writer.writerow(line)


def argument_parser():
    parser = argparse.ArgumentParser(description="根据软件名称监控指定软件的进程(含子进程)/记录系统性能信息(默认)")
    # 系统监控
    parser.add_argument('-s', '--system', help='记录系统性能信息,不可与-p同时使用', action='store_true', default=True)
    # 进程相关
    parser.add_argument('-p', '--process', help='软件名称')
    parser.add_argument('-port', help='软件对应的端口号', type=str, default=None)
    parser.add_argument('-it', '--interval_time', help='间隔时间', type=int, default=10)
    parser.add_argument('-fp', '--file_period', help='记录周期', type=int, default=7)
    parser.add_argument('-d', '--detail', help='记录进程列表到csv', action='store_false', default=False)
    return parser.parse_args()


if __name__ == "__main__":
    args = argument_parser()
    # print(args)  # 调试
    # args.process = 'SourceTree.exe'
    # args.interval_time = 2
    # args.port = '8083'
    if args.process:
        process_monitor_info_record_to_file(process_name=args.process, process_port=args.port,
                                            file_period=args.file_period,
                                            wait_time=args.interval_time, detail=args.detail)
    elif args.system:
        monitor_info_record_to_file(args.file_period, args.interval_time)
