#!/usr/bin/env python

import sys
import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', required=True)
parser.add_argument('-p', '--prefix', default='%')

namespace = parser.parse_args(sys.argv[1:])

first_line = False
with open(namespace.file) as fh:
    for line in fh:
        if line.startswith(namespace.prefix):
            command = line[2:].strip()
            print 'NEW ({0:>s})'.format(command)
            subprocess.call(command.split())
            first_line = True
        elif first_line:
            print 'OLD ({0:>s})'.format(command)
            print line
            first_line = False
        else:
            print line

