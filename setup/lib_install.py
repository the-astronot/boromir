import os
from os.path import dirname,abspath,join
req_file = join(dirname(dirname(__file__)),"requirements.txt")
os.system("pip3 install -r {}".format(req_file))
