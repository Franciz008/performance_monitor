[中文文档](https://github.com/Franciz008/performance_monitor/blob/main/中文ReadMe.md)

# Software Process Monitoring Tool

## Description

This is a command-line tool used to monitor the processes (including subprocesses) of specified software, or to record system performance information. You can choose to monitor the processes of a specific software, or record system performance information, or both.

## Options

- `-s, --system`: The default option, used to record system performance information.
- `-p, --process`: Specifies the name of the software to be monitored.
- `-port`: Specifies the port number of the monitored software.
- `-it, --interval_time`: Specifies the time interval for recording system performance information, default is 10 seconds.
- `-fp, --file_period`: Specifies the data period to be recorded, default is 7 days.
- `-d, --detail`: Specifies whether to record the process list to a CSV file, default is not recorded.

## Usage

### Monitor the process of the software

```bash
python process_monitor.py -p <software_name> -port <port_number>
```

### Record system performance information

```bash
python process_monitor.py -s
```

### Monitor the process of the software and record system performance information at the same time

```bash
python process_monitor.py -p <software_name> -port <port_number> -it <interval_time> -fp <file_period> -d
```