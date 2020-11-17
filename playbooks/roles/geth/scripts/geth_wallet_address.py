#!/bin/python

#
# Prints the Ethereum address at the end of a geth keystore filename.
#

from os import listdir
from os.path import expanduser, join
import re
import sys

keys_dir = sys.argv[1]

key = listdir(keys_dir)[0]
regex = "UTC--.*--([0-9a-fA-F].*)"

sys.stdout.write(re.search(regex, key).group(1))
sys.stdout.flush()
