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
import glob
import subprocess
import logging
from argparse import ArgumentParser

__author__ = "Luca Giovenzana <luca@giovenzana.org>"
__date__ = "2017-04-07"
__version__ = "0.2.1"


# TODO add parameter defaults and help
# TODO read a configuration file
# TODO Check space left in the vg (done by lvcreate itself)
# TODO Check number of backups (delete early/after?)
# TODO md5sum file
# TODO write a run function to include subprocess code
# TODO check image file already exists
# TODO if exception occurs snapshot should be removed
# TODO print data transferred and the time required


class LogFilterLessThan(logging.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LogFilterLessThan, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        return True if record.levelno < self.max_level else False


# FIXME change logging level for production
# create logger
logger = logging.getLogger('lvm2qcow2')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - '
                              '%(levelname)s - %(message)s')
# Handler for levels that go to standard output
handler_stdout = logging.StreamHandler(sys.stdout)
handler_stdout.setLevel(logging.DEBUG)
handler_stdout.addFilter(LogFilterLessThan(logging.WARNING))
handler_stdout.setFormatter(formatter)
logger.addHandler(handler_stdout)
# Handler for the remaining levels that go to standard error
handler_stderr = logging.StreamHandler(sys.stderr)
handler_stderr.setFormatter(formatter)
handler_stderr.setLevel(logging.WARNING)
logger.addHandler(handler_stderr)


class Device:

    def __init__(self, path):
        # get path, vg, lv and size from lvdisplay
        try:
            out = subprocess.check_output(['lvdisplay', path],
                                          stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.error(e.output)
            sys.exit(1)
        except OSError as e:
            logger.error("OSError: {}".format(e))
            sys.exit(1)
        else:
            lv_path = re.findall('LV Path\s+(.+)', out)
            lv_name = re.findall('LV Name\s+(.+)', out)
            vg_name = re.findall('VG Name\s+(.+)', out)
            lv_size = re.findall('LV Size\s+(.+)', out)
            # on lvm 2.02.66 LV Name is LV Path which does not exists
            if lv_path:
                self.path = lv_path[0]
                self.lv = lv_name[0]
            else:
                self.path = lv_name[0]
                self.lv = os.path.basename(lv_name[0])
            self.vg = vg_name[0]
            self.size = lv_size[0]

    def __str__(self):
        return ("LV Path: {}\n"
                "LV Name: {}\n"
                "VG Name: {}\n"
                "LV Size: {}".format(self.path, self.lv, self.vg, self.size))

    def create_snapshot(self, name=None, snapshot_size='5g'):
        if name is None:
            name = '{}-lvm2qcow2-snapshot'.format(self.lv)
        try:
            logger.debug("snapshot size: {}".format(snapshot_size))
            subprocess.check_output(['lvcreate', '-s', self.path,
                                     '-n', name,
                                     '-L', snapshot_size],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            if "already exists" in e.output:
                logger.warning("snapshot {} "
                               "already exists deleting it".format(name))
                # delete the pending snapshot
                self.delete_snapshot(name)
                # recursively create the snapshot
                self.create_snapshot(name, snapshot_size)
            else:
                logger.error(e.output)
                sys.exit(1)
        except OSError as e:
            logger.error("OSError: {}".format(e))
            sys.exit(1)
        # adding the full path
        snapshot_name = os.path.join(os.path.dirname(self.path), name)
        return snapshot_name

    def delete_snapshot(self, name=None):
        # check if not used
        if name is None:
            name = '{}-lvm2qcow2-snapshot'.format(self.lv)
        # adding the full path
        snapshot_name = os.path.join(os.path.dirname(self.path), name)
        try:
            subprocess.check_output(['lvremove', '-f', snapshot_name],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            logger.error(e.output)
            sys.exit(1)
        except OSError as e:
            logger.error("OSError: {}".format(e))
            sys.exit(1)

        return snapshot_name


class Images:
    def __init__(self, path, prefix, suffix='.qcow2'):
        self.files = [os.path.abspath(i) for i in glob.glob(os.path.join(path,
                      '{}*{}'.format(prefix, suffix)))]
        self.files = sorted(self.files, reverse=True)

    def keep_only(self, copies):
        # TODO delete also md5sum file
        # 0 means infinite so the loop should not be executed
        logger.debug("images: %s", self.files)
        logger.debug("number of copies to keep: %s", copies)
        while (len(self.files) > copies) and (copies != 0):
            image_to_remove = self.files.pop()
            logger.info("removing image: {}".format(image_to_remove))
            try:
                # added full path to avoid aliases that works with -i
                subprocess.check_output(['/bin/rm', image_to_remove],
                                        stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                logger.error(e.output)
                sys.exit(1)

    def __iter__(self):
        return self.files.__iter__()


def _qemu_img_cmd(source, destination, image):
    """ Run qemu-img command to convert lv to qcow2:
    qemu-img convert -c -O qcow2 SOURCE DESTINATION/IMAGE"""
    destination = os.path.join(destination, image)
    try:
        subprocess.check_output(['qemu-img', 'convert', '-cO', 'qcow2',
                                 source, destination],
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error(e.output)
        sys.exit(1)
    except OSError as e:
        logger.error("OSError: {}".format(e))
        sys.exit(1)
    else:
        return destination


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

    parser.add_argument("-i", "--image-prefix",
                        action='store', dest='IMAGE_PREFIX',
                        help="destination prefix for the backup qcow2 image "
                             "name")

    parser.add_argument("-n", "--number-of-copies",
                        action='store', dest='COPIES', type=int, default=0,
                        help="0 means infinite, 1 keeps only the current image"
                             " otherwise keeps the number of specified copies")

    parser.add_argument("-S", "--snapshot-size",
                        action='store', dest='SNAPSHOT_SIZE', type=str, default="5g",
                        help="size of the temporary logical volume snapshot,"
                             " this is the maximum size of the change accepted"
                             " while doing the backup."
                             " WARNING if the 100 usage of the lv snapshot"
                             " is reached the backup will be corrupted.")

    parser.add_argument('--version', action='version',
                        version="%(prog)s {}".format(__version__))

    # Validate and manipulate arguments input
    args = parser.parse_args()

    logger.info("lvm2qcow2 started")

    # Create the source device object getting data with lvdisplay
    src_device = Device(args.SOURCE)
    logger.info("source: {}".format(src_device.path))

    # Check destination folder exists and is a directory
    if os.path.isdir(args.DESTINATION):
        dst_dir = args.DESTINATION
    else:
        logger.error("OSError: '%s' invalid destination",
                     args.DESTINATION)
        sys.exit(1)
    logger.info("destination: {}".format(dst_dir))

    # If prefix is not provided lv name will be used as default prefix
    if args.IMAGE_PREFIX:
        image_prefix = args.IMAGE_PREFIX
    else:
        image_prefix = src_device.lv
    timestamp = time.strftime('%Y-%m-%d')
    image = '{}-{}.qcow2'.format(image_prefix, timestamp)
    logger.debug("image: {}".format(image))

    # Create the lv snapshot
    snapshot = src_device.create_snapshot(snapshot_size=args.SNAPSHOT_SIZE)
    logger.debug("created snapshot: {}".format(snapshot))
    qcow2_file = _qemu_img_cmd(snapshot, dst_dir, image)
    logger.info("created image: {}".format(qcow2_file))
    snapshot = src_device.delete_snapshot()
    logger.debug("deleted snapshot: {}".format(snapshot))

    # Delete old copies
    images = Images(dst_dir, image_prefix)
    images.keep_only(args.COPIES)

    return 0


if __name__ == '__main__':
    main()
