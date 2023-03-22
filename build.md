windows打包

```bash
pyinstaller -n monitx -F -i "C:\Users\Franciz\Pictures\我的照片\speedometer.ico" .\system_monitor.py -p .\common.py -p .\process_monitor.py --distpath=E:\WORK\测试工具\性能监控工具
```

linux打包

```shell
pyinstaller -n monitx -F system_monitor.py
```
