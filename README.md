# Nwrapy
## Nmap Wrapper written in Python

Nmap wrapper written in Python3. Inspired by [gh0x0st](https://github.com/gh0x0st/pythonizing_nmap)

Aiming to automate most of the Nmap commands used to scan a network. 
Stores it nicely in a db, after which it is written into .csv files for easy reviewing. Also aims to do all of this without making a load of noise on the target network (so not a lot of script execution). If you need evidence of what happened during the scan, all nmap commands that are executed are also stored and all results can be found in the .xml files.

## Install

The installation can best be done as root user, since it will otherwise install it only for the current user. The script needs to be run as root, so it needs to be in the path for the root user.
```
sudo pip install .
```

## Usage
Most of the scans used in Nwrapy require root privileges.

Scan CIDR range:
```
nwrapy scan 192.168.0.0/24 database.db
```

Scan individual target:
```
nwrapy scan 192.168.0.10 database.db
```

Scan specific targets:
```
nwrapy scan "192.168.0.10 192.168.1.100 10.10.0.17" database.db
```

Specify intensity (default is 6, while normal nmap default is 7)
```
nwrapy scan 192.168.0.1 database.db -i 7
```

Perform scan of network (CIDR /24) the current device is connected to and output to specific directory (usefull for automated scheduled testing using cron for example):
```
nwrapy autoscan 24 database.db -o output_dir
```

The same but for CIDR /16:
```
nwrapy autoscan 16 database.db -o output_dir
```

For more info:
```
nwrapy --help
```

Or:
```
nwrapy scan --help
```

## Reports
By default a output directory is made, with subdirectories and the resulting file. The following is an example directory tree:
```
nwrapy_output/
|__csv_files/
   |__summary.csv
   |__report.csv
|__xml_files/
   |__<nmap_output>
   |__<nmap_output>
   |__...
```

## Uninstall
```
sudo pip uninstall nwrapy
```

![GitHub Contributors Image](https://contrib.rocks/image?repo=SneakyBeagle/nwrapy)
