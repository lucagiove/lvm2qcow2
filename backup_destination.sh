#!/bin/bash
# Source this file to verify which path between two is 
# available for storing data.

DST_1=/mnt/usb_backup_6tb/snapshots
DST_2=/mnt/usb_backup_6tb_2/snapshots

if [[ -d "$DST_1" ]]; then
	DST_AVAIL=$DST_1
elif [[ -d "$DST_2" ]]; then
	DST_AVAIL=$DST_2
else
	echo "ERROR: Cannot find backup destination"
	exit 1
fi
