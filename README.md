#lvm2qcow2

Script that create a live copy of a logical volume and convert it in qcow2 format

##Suggested installation
That's just an example by the way the paths and filenames should be kept for 
Has been tested on ubuntu 12.04 and 14.04

Install git and requirements

    apt-get install git python

Download the latest version of lvm2qcow2

    cd /usr/local/lib/
    sudo git clone https://github.com/lucagiove/lvm2qcow2

Create a link to the binary in order to run it easily

    sudo ln -s /usr/local/lib/lvm2qcow2/lvm2qcow2.py /usr/local/bin/

Create a script for a daily basis backup

    touch /etc/cron.daily/snapshot-backup
    chmod a+x /etc/cron.daily/snapshot-backup
    vim /etc/cron.daily/snapshot-backup

Example of script
```
#!/bin/bash
# lvm2qcow2.py -s path-to-logical-volume -d path-to-folder -n number-of-copies-to-keep >> /var/log/snapshot-backup.log
lvm2qcow2.py -s /dev/raid/mail-root -d /mnt/hd-2TB/snapshots -n 5 >> /var/log/snapshot-backup.log
lvm2qcow2.py -s /dev/raid/mail-var -d /mnt/hd-2TB/snapshots -n 5 >> /var/log/snapshot-backup.log
lvm2qcow2.py -s /dev/raid/pdc-system -d /mnt/hd-2TB/snapshots -n 5 >> /var/log/snapshot-backup.log
lvm2qcow2.py -s /dev/raid/pdc-shares -d /mnt/hd-2TB/snapshots -n 5 >> /var/log/snapshot-backup.log
```

##Usage and options

```
usage: lvm2qcow2.py [-h] -s SOURCE -d DESTINATION [-i IMAGE_PREFIX]
                    [-n COPIES] [-S SIZE] [--version]

optional arguments:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        source logical volume device that you want to snapshot
                        and backup
  -d DESTINATION, --destination DESTINATION
                        destination path where the script saves the qcow2
  -i IMAGE_PREFIX, --image-prefix IMAGE_PREFIX
                        destination prefix for the backup qcow2 image name
  -n COPIES, --number-of-copies COPIES
                        0 means infinite, 1 keeps only the current image
                        otherwise keeps the number of specified copies
  -S SIZE, --snapshot-size SIZE
  --version             show program's version number and exit
```



