# lvm2qcow2

Script that create a live copy of a logical volume and convert it in qcow2 format

## Suggested installation
That's just an example by the way the paths and filenames should be kept for
reference.  
Has been tested on ubuntu 12.04, 14.04 and CentOS 6.x

*Note: Require python >= 2.7*

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
# lvm2qcow2.py -s path-to-logical-volume -d path-to-folder -n number-of-copies-to-keep -S 5g| tee -a /var/log/snapshot-backup.log > /dev/null
lvm2qcow2.py -s /dev/raid/mail-root -d /mnt/hd-2TB/snapshots -n 5 | tee -a /var/log/snapshot-backup.log > /dev/null
lvm2qcow2.py -s /dev/raid/mail-var -d /mnt/hd-2TB/snapshots -n 5 | tee -a /var/log/snapshot-backup.log > /dev/null
lvm2qcow2.py -s /dev/raid/pdc-system -d /mnt/hd-2TB/snapshots -n 5 | tee -a /var/log/snapshot-backup.log > /dev/null
lvm2qcow2.py -s /dev/raid/pdc-shares -d /mnt/hd-2TB/snapshots -n 5 | tee -a /var/log/snapshot-backup.log > /dev/null
```

**Note:** if you have configured an alias to administrator mail for
_root@localhost_ you'll be notified only for errors.  
If you want to be always notified just remove redirection to `> /dev/null`

Verify in /etc/crontab when daily jobs are executed to make sure that there is
enough time during the night to complete the jobs, normally is a good choice to
change from 6 to 1 in the night the line:

    25 1    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )

Example of a modified /etc/crontab
```
# /etc/crontab: system-wide crontab

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user  command
17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 1    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 3    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 5    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
#

```

## Usage and options

```
  usage: lvm2qcow2.py [-h] -s SOURCE -d DESTINATION [-i IMAGE_PREFIX]
                    [-n COPIES] [-S SNAPSHOT_SIZE] [--version]

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
  -S SNAPSHOT_SIZE, --snapshot-size SNAPSHOT_SIZE
                        size of the temporary logical volume snapshot, this is
                        the maximum size of the change accepted while doing
                        the backup. WARNING if the 100 usage of the lv
                        snapshot is reached the backup will be corrupted.
  --version             show program's version number and exit
```

### Note for CentOS 6.X
On CentOS 6.X there is only python 2.6 so it's necessary to compile python2.7
or major

In order to compile Python you must first install the development tools:
```
yum groupinstall "Development tools" -y
```
You also need a few extra libs installed before compiling Python or else you
will run into problems later when trying to install various packages:
```
yum install zlib-devel -y
yum install bzip2-devel -y
yum install openssl-devel -y
yum install ncurses-devel -y
yum install sqlite-devel -y
```

Now let's start to compile and install python 2.7
```
cd /opt
wget --no-check-certificate https://www.python.org/ftp/python/2.7.6/Python-2.7.6.tar.xz
tar xf Python-2.7.6.tar.xz
cd Python-2.7.6
./configure --prefix=/usr/local
make && make altinstall
```

Now you can use the script with the new python version, note that also python
2.6 it's still present so you need to specify the full path of the new python
in order to run the script
```
/usr/local/bin/python2.7 lvm2qcow2.py
```
