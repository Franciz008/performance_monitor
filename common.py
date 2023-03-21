# @author Franciz
# @date 2023/3/16 19:16
import csv
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta
from x_mock.m_random import m_date


def create_csv(header: list, file_name, log_info=None):
    if os.path.exists(file_name) is False:
        # 表头
        print(f'格式说明:{" ".join(header)}')
        with open(file_name, 'w', encoding='utf-8', newline='') as file_obj:
            writer = csv.writer(file_obj)
            if log_info:
                writer.writerow(log_info)
            writer.writerow(header)
        print(f'创建文件:{file_name}')
    else:
        print(f'文件:{file_name}已存在')
    return file_name


def get_csv_name(file_time, pr_name=None):
    pr_name = f'{pr_name}_Process' if pr_name is not None else "System"
    file_name = f'{file_time}_{pr_name}{"MonitorInfo"}.csv'
    return file_name


def create_next_date_csv(file_name, file_period: int, header, pr_name, raw_file_time):
    """

    :param file_name: 原始文件的名称
    :param file_period: 创建文件的周期/天
    :param header: 创建文件的表头
    :param pr_name: 监控的程序名称
    :param raw_file_time: 原始的文件名称的日期,用于比对是否生成新文件
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
