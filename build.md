windows打包

```bash
pyinstaller -n system_monitor -F -i "C:\Users\Franciz\Pictures\我的照片\performance_monitor.ico" .\system_monitor.py -p .\common.py -p .\process_monitor.py --distpath=E:\WORK\测试工具\性能监控工具
```

linux打包

```shell
pyinstaller -n linux_system_monitor -F system_monitor.py
```
