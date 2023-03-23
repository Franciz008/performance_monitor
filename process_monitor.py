# @author Franciz
# @date 2023/3/16
import asyncio
import csv
import time
from concurrent.futures import ThreadPoolExecutor

import psutil
from x_mock.m_random import m_date

from common import create_csv, create_next_date_csv, get_csv_name


class ProcessMonitorInfo:
    cpu_percent = 0  # CPU百分比
    used_memory_percent = 0  # 已用内存百分比/MB
    used_memory = 0  # 已用内存/MB
    status = 0
    process_size = 0
    proc_names = []  # 进程名称的列表

    def __init__(self, name, port=None, interval_time=5):
        self.name = name
        self.port = port
        self.interval_time = interval_time
        self.process_list = self.get_pids()

    def get_all_info(self):
        return [self.cpu_percent, self.used_memory, self.used_memory_percent, self.process_size, self.status]

    def get_pids(self):
        """

        :return: 根据程序的名称如:Thunder.exe 返回对应程序活动的进程列表
        """

        def add():
            procs.append(proc)
            children_pids = proc.children()
            if len(children_pids) > 0:
                for i in proc.children():
                    procs.append(i)

        name = self.name
        procs = []
        for proc in psutil.process_iter():
            if name in proc.name() and proc.status() in (psutil.STATUS_RUNNING, psutil.STATUS_SLEEPING):
                # 获取名称对应且是运行中的改程序的所有进程(含子进程)
                # pid = proc.pid
                # cmdline = proc.as_dict().get('cmdline')
                # print(json.dumps(proc.as_dict(), indent=2))
                proc_environ = proc.as_dict().get('environ')
                proc_port = None if proc_environ is None else proc_environ.get('PORT')
                if self.port is not None and proc_port and self.port == proc_port:
                    # 根据名称和端口号确定监控的进程
                    add()
                elif self.port is None:
                    # 根据名称确定监控的进程
                    add()
        self.proc_names = [i.name() for i in procs]
        return procs

    async def get_used_memory(self):
        """

        :return: 已用内存
        """
        memory_list = []
        for proc in self.process_list:
            memory = proc.memory_full_info().uss
            memory_list.append(round(memory / 1024 / 1024, 2))
        self.used_memory = float('%.2f' % sum(memory_list))
        return self.used_memory

    async def get_used_memory_percent(self):
        """

        :return: 已用内存百分比
        """
        memory_percent_list = []
        for proc in self.process_list:
            memory_percent = proc.memory_percent()
            memory_percent_list.append(memory_percent)
        self.used_memory_percent = float('%.2f' % sum(memory_percent_list))
        return self.used_memory_percent

    def cpu_wait(self):
        if self.interval_time > 1.5:
            time.sleep(self.interval_time - 1.5)

    cpu_percent_list = []

    async def get_cpu_percent(self):
        """

        :return: cpu的使用频率
        """

        def __cpu_percent(process):
            cpu_percent = process.cpu_percent(1)
            self.cpu_wait()
            return cpu_percent

        with ThreadPoolExecutor(max_workers=len(self.process_list)) as pool:
            results = pool.map(__cpu_percent, self.process_list)
            for r in results:
                self.cpu_percent_list.append(r)
        # with multiprocessing.Pool() as pool:
        #     results = pool.map(__cpu_percent, self.process_list)
        #     for r in results:
        #         self.cpu_percent_list.append(r)
        self.cpu_percent = float('%.2f' % sum(self.cpu_percent_list))
        return self.cpu_percent

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
            # pros = self.get_pids()
            await asyncio.gather(self.get_used_memory(), self.get_used_memory_percent(),
                                 self.get_cpu_percent())
        else:
            self.status = 0
        return self.get_all_info()

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


def process_monitor_info_record_to_file(process_name, process_port=None, file_period=1, wait_time=5, detail=False):
    """

    :param process_port: 进程的端口
    :param detail: 详细信息
    :param process_name: 软件名称,示例:java.exe
    :param wait_time: 间隔时间/秒
    :param file_period:  记录文件创建周期/天
    :return:
    """
    raw_file_time = m_date.date()
    pr_name = process_name
    start_info = f'--监控的软件名称:{pr_name},端口:{process_port},记录文件创建周期:{file_period}天/次,间隔时间:{wait_time}秒/次'
    print(start_info)
    header = ['日期', '时间', 'cpu百分比/s', '已用内存/MB', '已用内存百分比', '进程数/个', '状态(1存活/0死亡)',
              '进程列表']
    header = handle_detail(detail, header)
    file_name = get_csv_name(raw_file_time, pr_name)
    create_csv(header, file_name, [start_info])
    while True:
        # start_time = time.perf_counter()
        if file_period is not None:
            file_name, raw_file_time = create_next_date_csv(file_name, file_period, header, pr_name, raw_file_time)
        with open(file_name, 'a+', encoding='utf-8', newline='') as file_obj:
            # 1:创建writer对象
            writer = csv.writer(file_obj)
            process_monitor_info = ProcessMonitorInfo(name=pr_name, port=process_port, interval_time=wait_time)
            try:
                result = asyncio.run(process_monitor_info.get_monitor_info())
            except:
                result = process_monitor_info.get_all_info()
            finally:
                if process_monitor_info.status == 0:
                    process_monitor_info.cpu_wait()
            line = (m_date.date(), m_date.time(), *result, process_monitor_info.proc_names)
            print(*line[:-1])
            line = handle_detail(detail, line)
            writer.writerow(line)
        # end_time = time.perf_counter()
        # time_diff = end_time - start_time
        # print(f'耗时:{time_diff}')


def handle_detail(detail, line):
    if detail is False:
        # 不展示细节则删除进程列表
        line = line[:-1]
    return line
