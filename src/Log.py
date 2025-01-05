# Library imports
import os
from os.path import join,exists,abspath,dirname,isdir,basename
import time
from enum import IntEnum

# Local imports
from file_io_util import ask_overwrite
from paths import LOG_DIR


class Logger:
	"""
	
	"""
	def __init__(self,filename,verbose=False,level=0,force_overwrite=False):
		self.filename = filename
		self.level = level
		self.verbose = verbose
		self.open_file = False
		if self.filename is not None and self.filename.lower() != "none":
			if exists(self.filename) and not force_overwrite:
				self.filename = ask_overwrite(self.filename,LOG_DIR)
			self.f = open(self.filename,"w+")
			self.open_file = True

	def re_init(self,filename,verbose=False,level=0,force_overwrite=False):
		if self.open_file:
			self.f.close()
		self.__init__(filename,
									verbose=verbose,
									level=level,
									force_overwrite=force_overwrite
									)

	def log(self,msg,level,also_print=False):
		"""
			Handles logging message to file and/or terminal with time marker
				- If file open, log to file
				- Else log to terminal
				- Also if ${also_print}$, log to terminal
				- Finally if ${verbose}$ and level 0, log to terminal
		"""
		clock = time.strftime("[%H:%M:%S]",time.localtime())
		msg = "{} {}".format(clock,msg)
		if level <= self.level:
			if self.open_file:
				self.f.write("{}\n".format(msg))
			else:
				print(msg)
				return
			if also_print:
				print(msg)
				return
		if self.verbose and level == 0:
			print(msg)
		return
	
	def error(self,msg):
		self.log(msg,0,also_print=True)

	def __del__(self):
		if self.open_file:
			self.f.close()
			self.open_file = False
			self.error("Closed {}".format(self.filename))

################################################################################
LOGGER=Logger(None)

def log(msg,level,also_print=False):
	LOGGER.log(msg,level,also_print=False)

def error(msg):
	LOGGER.error(msg)

################################################################################
if __name__ == "__main__":
	LOGGER.re_init("test.out")
	log("Test text",2)
