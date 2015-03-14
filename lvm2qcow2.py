#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) 2014 Luca Giovenzana <luca@giovenzana.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import sys
import time
import subprocess
from argparse import ArgumentParser

__author__ = "Luca Giovenzana <luca@giovenzana.org>"
__date__ = "2015-02-28"
__version__ = "0.1dev"


class Device():

    def __init__(self, path):
        # get path, vg, lv and size from lvdisplay
        try:
            out = subprocess.check_output(['lvdisplay', path])
        except subprocess.CalledProcessError as e:
            print e.cmd
            print e.output
            sys.exit(1)
        except OSError as e:
            print "OSError: lvdisplay command not found"
            sys.exit(1)
        else:
            lv_display = re.findall('LV Path\s+(.+)\s+'
                                    'LV Name\s+(.+)\s+'
                                    'VG Name\s+(.+)', out)
            lv_size = re.findall('LV Size\s+(.+)', out)
            self.path = lv_display[0][0]
            self.lv = lv_display[0][1]
            self.vg = lv_display[0][2]
            self.size = lv_size[0]

    def __str__(self):
        return ("LV Path: {}\n"
                "LV Name: {}\n"
                "VG Name: {}\n"
                "LV Size: {}".format(self.path, self.lv, self.vg, self.size))

    def create_snapshot(self, name=None, snapshot_size='5g'):
        if name is None:
            snapshot_name = '{}-lvm2qcow2-snapshot'.format(self.lv)
        cmd_args = '-s {} -n {} -L {}'.format(self.path, snapshot_name,
                                              snapshot_size)
        try:
            subprocess.check_output(['lvcreate'] + cmd_args.split())
        except subprocess.CalledProcessError as e:
            print e.cmd
            print e.output
            sys.exit(1)
        except OSError as e:
            print "OSError: lvcreate command not found"
            sys.exit(1)
        else:
            snapshot_name = os.path.join(os.path.dirname(self.path),
                                         snapshot_name)
            return snapshot_name

    def delete_snapshot(self, name=None):
        # check if not used
        if name is None:
            name = '{}-lvm2qcow2-snapshot'.format(self.lv)
        # adding the full path
        snapshot_name = os.path.join(os.path.dirname(self.path), name)
        try:
            subprocess.check_output(['lvremove', '-f'] + snapshot_name.split())
        except subprocess.CalledProcessError as e:
            print e.cmd
            print e.output
            sys.exit(1)
        except OSError as e:
            print "OSError: lvremove command not found"
            sys.exit(1)
        else:
            return snapshot_name


def _qemu_img_cmd(source, destination, image=None):
    """ Run qemu-img command to convert lv to qcow2:
    qemu-img convert -c -O qcow2 SOURCE DESTINATION/IMAGE"""
    if image is None:
        image = os.path.basename(source).strip()
        image += '-{}.qcow2'.format(time.strftime('%Y%m%d'))

    cmd_args = '-c -O qcow2 {} {}/{}'.format(source, destination, image)
    print cmd_args


def _md5sum_cmd(filename):
    pass


def _clean_images(image_prefix):
    pass


def main():

    parser = ArgumentParser()
    parser.add_argument("-s", "--source",
                        action='store', dest='SOURCE',
                        help="source logical volume device that you want to "
                             "snapshot and backup", required=True)

    parser.add_argument("-d", "--destination",
                        action='store', dest='DESTINATION',
                        help="destination path where the script saves "
                             "the qcow2", required=True)

    parser.add_argument("-q", "--qcow2",
                        action='store', dest='IMAGE',
                        help="destination filename for the backup qcow2 image")

    parser.add_argument("-S", "--snapshot-size",
                        action='store', dest='SIZE', type=int,
                        help="")

    parser.add_argument('--version', action='version',
                        version="%(prog)s {}".format(__version__))

    args = parser.parse_args()

    src_device = Device(args.SOURCE)
    print src_device
    if os.path.isdir(args.DESTINATION):
        dst_dir = args.DESTINATION
    else:
        print "OSError: '{}' invalid destination".format(args.DESTINATION)
        sys.exit(1)

    print src_device.create_snapshot()
    print src_device.delete_snapshot()

    # TODO read a configuration file
    # TODO check pending snapshots
    # Check space left in the vg (done by lvcreate itself)
    # TODO Check number of backups (delete early/after?)
    # TODO qemu convert image
    # TODO md5sum file
    # FIXME add/validate '{}' in subprocess

    return 0

if __name__ == '__main__':
    main()
