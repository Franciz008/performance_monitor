# @author Franciz
# @date 2023/3/16
import asyncio
import csv
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import psutil
from dateutil.relativedelta import relativedelta
from x_mock.m_random import m_date

from common import create_csv


class ProcessMonitorInfo:
    cpu_percent = 0  # CPU百分比
    used_memory_percent = 0  # 已用内存百分比/MB
    used_memory = 0  # 已用内存/MB
    status = 0
    process_size = None

    def __init__(self, name, path=None, interval_time=2):
        self.name = name
        self.path = path
        self.interval_time = interval_time
        self.process_list = self.get_pids()

    def get_pids(self):
        """

        :return: 根据程序的名称如:Thunder.exe 返回对应程序活动的进程列表
        """
        name = self.name
        procs = []
        for proc in psutil.process_iter():
            if name in proc.name() and proc.status() == psutil.STATUS_RUNNING:
                # 获取名称对应且是运行中的改程序的所有子进程,若有此程序的进程名不一致的,可能会有偏差
                # pid = proc.pid
                procs.append(proc)
        return procs

    async def get_used_memory(self):
        memory_list = []
        for proc in self.process_list:
            memory = proc.memory_full_info().uss
            memory_list.append(round(memory / 1024 / 1024, 2))
        self.used_memory = sum(memory_list)
        return self.used_memory

    async def get_used_memory_percent(self):
        memory_percent_list = []
        for proc in self.process_list:
            memory_percent = proc.memory_percent()
            memory_percent_list.append(memory_percent)
        self.used_memory_percent = round(sum(memory_percent_list), 2)
        return self.used_memory_percent

    async def get_cpu_percent(self):
        cpu_percent_list = []

        def __cpu_percent(process):
            cpu_percent = process.cpu_percent(1)
            if self.interval_time > 1:
                time.sleep(self.interval_time - 1)
            return cpu_percent

        with ThreadPoolExecutor(max_workers=len(self.process_list)) as pool:
            results = pool.map(__cpu_percent, self.process_list)
            for r in results:
                cpu_percent_list.append(r)
        self.cpu_percent = round(sum(cpu_percent_list), 2)
        return

    async def get_io_counters(self):
        io_counters_list = []
        for proc in self.process_list:
            io_counters = proc.io_counters()
            io_counters_list.append(io_counters)
            # todo

    async def get_monitor_info(self):
        proc_size = len(self.get_pids())
        self.process_size = proc_size
        if proc_size > 0:
            self.status = 1
            pros = self.get_pids()
            await asyncio.gather(self.get_used_memory(), self.get_used_memory_percent(),
                                 self.get_cpu_percent())
            return [self.cpu_percent, self.used_memory, self.used_memory_percent, self.status]
            # print('总内存', self.used_memory)
            # print('总内存占比', self.used_memory_percent)
            # print('总CPU占比', self.cpu_percent)
        else:
            self.status = 0
            return [self.cpu_percent, self.used_memory, self.used_memory_percent, self.status]

    def kill(self):
        pass
        # p.terminate()
        # p.kill()
        # p.parent().kill()

        # print(p.memory_info().rss / 1024 / 1024, 'MB')
        # # memory_full_info()
        # # 此方法返回与memory_info（）相同的信息，同时，在某些平台（Linux，macOS，Windows）上，该方法还提供其他指标（USS，PSS和swap）。
        # # pss： 该进程实际使用物理内存（比例分配共享库占用内存）
        # # uss：进程独立占用的物理内存（不包含共享库占用的内存）
        # print(p.memory_full_info().uss / 1024 / 1024, 'MB')


def get_csv_name(file_time, pr_name):
    file_name = f'{file_time}_{pr_name}{"_ProcessMonitorInfo"}.csv'
    return file_name


def create_next_date_csv(file_name, file_period: int, header, pr_name, raw_file_time):
    """

    :param file_name: 原始文件的名称
    :param file_period: 创建文件的周期/天
    :param header: 创建文件的表头
    :param pr_name: 监控的程序名称
    :param raw_file_time: 原始的文件名称的日期,用于
    :return: 创建新的日期的文件,返回修改后的[新文件名称,新的文件名的日期]
    """
    old_date = datetime.strptime(raw_file_time, '%Y-%m-%d')
    new_date = old_date + relativedelta(days=file_period)
    now_date = datetime.strptime(m_date.date(), '%Y-%m-%d')
    if now_date >= new_date:
        raw_file_time = now_date.strftime('%Y-%m-%d')
        file_name = get_csv_name(raw_file_time, pr_name)
        create_csv(header, file_name)
    return file_name, raw_file_time


def process_monitor_info_record_to_file(prc_name, file_period=1, wait_time=2):
    """

    :param prc_name: 软件名称,示例:java.exe
    :param wait_time: 间隔时间/秒
    :param file_period:  件创建周期/天
    :return:
    """
    raw_file_time = m_date.date()
    pr_name = prc_name
    print(f'监控的软件名称:{pr_name}')
    header = ['时间', 'cpu百分比/s', '已用内存/MB', '已用内存百分比', '状态']
    file_name = get_csv_name(raw_file_time, pr_name)
    create_csv(header, file_name)
    while True:
        if file_period is not None:
            file_name, raw_file_time = create_next_date_csv(file_name, file_period, header, pr_name, raw_file_time)
        with open(file_name, 'a+', encoding='utf-8', newline='') as file_obj:
            # 1:创建writer对象
            writer = csv.writer(file_obj)
            process_monitor_info = ProcessMonitorInfo(pr_name, wait_time)
            try:
                result = asyncio.run(process_monitor_info.get_monitor_info())
            except:
                pass
            finally:
                if process_monitor_info.status == 0:
                    time.sleep(process_monitor_info.interval_time)
            line = (m_date.time(), *result)
            print(*line)
            writer.writerow(line)

# if __name__ == "__main__":
#     process_monitor_info_record_to_file()
