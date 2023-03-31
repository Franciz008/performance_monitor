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

The options "-s" and "-p" are mutually exclusive and cannot be used simultaneously.

## Windows Usage

### Monitor the process of the software

```bash
monitx.exe -p <software_name> -port <port_number>
```

### Record system performance information

```bash
monitx.exe -s
```

### Monitor the process of the software and record system performance information at the same time

```bash
monitx.exe -p <software_name> -port <port_number> -it <interval_time> -fp <file_period> -d
```

## Linux Usage

### Monitor the process of the software

```bash
monitx -p <software_name> -port <port_number>
```

### Record system performance information

```bash
monitx -s
```

### Monitor the process of the software and record system performance information at the same time

```bash
monitx -p <software_name> -port <port_number> -it <interval_time> -fp <file_period> -d
```

**Monitor the performance information of all processes that contain the process name "frp" every 2 seconds.**

```
monitx -p frp -it 2
```

