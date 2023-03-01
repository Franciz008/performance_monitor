import asyncio
import csv
import os
import sys
import time

import psutil
from x_mock.m_random import m_date

# @author Franciz
# @date 2023/2/27 18:59

# 性能监控的间隔时间
interval_time = int(sys.argv[1]) if len(sys.argv) > 1 else 10
print(f'性能监控记录:{interval_time}秒/次')


class MonitorInfo:
    cpu_rate = None  # cpu利用率百分比
    disk_read = None  # 磁盘读取速度/MB
    disk_write = None  # 磁盘写入速度/MB
    net_recv = None  # 磁盘网络接收速度/MB
    net_sent = None  # 磁盘网络发送速度/MB
    memory_used = None  # 已用内存/MB

    async def get_memory_rate(self):
        """

        :return: PC的已用内存/MB
        """
        data = psutil.virtual_memory()
        memory = round(data.used / 1024 / 1024)
        self.memory_used = memory
        return memory

    async def get_cpu_rate(self):
        """

        :return: PC的CPU平均使用百分比
        """
        # await asyncio.sleep(1)
        cpu = psutil.cpu_percent(interval_time)
        self.cpu_rate = cpu
        return cpu

    async def get_disk_io(self):
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
        self.disk_read = total_read
        self.disk_write = total_write
        # 读取,写入 MB/s
        return total_read, total_write

    async def get_network_io(self):
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
        self.net_recv = total_recv
        self.net_sent = total_sent
        # 发送/接收 MB/s
        return total_sent, total_recv

    async def main(self):
        return await asyncio.gather(self.get_network_io(), self.get_disk_io(), self.get_memory_rate(),
                                    self.get_cpu_rate())


def monitor_info_record_to_file():
    # 表头
    header = ['时间', 'cpu百分比', '已用内存/MB', '磁盘读取MB/s', '磁盘写入MB/s', '网络上传MB/s', '网络下载MB/s']
    print(f'格式说明:{" ".join(header)}')
    file_name = f'{m_date.date() + "MonitorInfo"}.csv'
    if os.path.exists(file_name) is False:
        with open(file_name, 'w', encoding='utf-8', newline='') as file_obj:
            writer = csv.writer(file_obj)
            writer.writerow(header)
    while True:
        with open(file_name, 'a+', encoding='utf-8', newline='') as file_obj:
            # 1:创建writer对象
            writer = csv.writer(file_obj)
            # # 2:写表头
            # writer.writerow(header)
            monitor_info = MonitorInfo()
            # print(monitor_info.interval_time)
            asyncio.run(monitor_info.main())
            line = (m_date.time(), monitor_info.cpu_rate, monitor_info.memory_used, monitor_info.disk_read,
                    monitor_info.disk_write,
                    monitor_info.net_recv, monitor_info.net_sent)
            print(*line)
            writer.writerow(line)


def get_pid(name):
    """

    :param name:
    :return: 根据完整的程序名称获取程序的pid
    """
    pids = psutil.process_iter()
    for pid in pids:
        if pid.name() == name:
            print(f"[{name}]'s pid is:{pid.pid}")
            return pid.pid


if __name__ == "__main__":
    monitor_info_record_to_file()

    # for i in range(20):
    #     print(asyncio.run(MonitorInfo().get_disk_io()))

    # p = psutil.Process(get_pid('pycharm64.exe'))
    # print(p.memory_info().rss / 1024 / 1024, 'MB')
    # # memory_full_info()
    # # 此方法返回与memory_info（）相同的信息，同时，在某些平台（Linux，macOS，Windows）上，该方法还提供其他指标（USS，PSS和swap）。
    # # pss： 该进程实际使用物理内存（比例分配共享库占用内存）
    # # uss：进程独立占用的物理内存（不包含共享库占用的内存）
    # print(p.memory_full_info().uss / 1024 / 1024, 'MB')
