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

from argparse import ArgumentParser

__author__ = "Luca Giovenzana <luca@giovenzana.org>"
__date__ = "2015-02-28"
__version__ = "0.1dev"


def main():

    parser = ArgumentParser()
    parser.add_argument("-g", "--vg",
                        action='store', dest='VOLUMEGROUP',
                        help="source volume group where the logical volume is "
                              "stored", required=True)
    parser.add_argument("-v", "--lv",
                        action='store', dest='LOGICALVOLUME',
                        help="source logical volume that you want to snapshot "
                             "and backup", required=True)
    parser.add_argument("-q", "--qcow2",
                        action='store', dest='IMAGE',
                        help="destination filename for the backup qcow2 image")

    parser.add_argument("-s", "--snapshot-size",
                        action='store', dest='SIZE', type=int,
                        help="")
    parser.add_argument('--version', action='version',
                        version="%(prog)s {}".format(__version__))

    args = parser.parse_args()

    # Check input
    # Check pending snapshots
    # Check space left in the vg
    # Snapshot lv
    # Check number of backups
    # Do qemu-img copy

    return 0

if __name__ == '__main__':
    main()
