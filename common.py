# @author Franciz
# @date 2023/3/16 19:16
import csv
import os


def create_csv(header: list, file_name):
    if os.path.exists(file_name) is False:
        # 表头
        print(f'格式说明:{" ".join(header)}')
        with open(file_name, 'w', encoding='utf-8', newline='') as file_obj:
            writer = csv.writer(file_obj)
            writer.writerow(header)
        print(f'创建文件:{file_name}')
    else:
        print(f'文件:{file_name}已存在')
    return file_name
