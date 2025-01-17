# Library imports
import os
from os.path import join,exists,abspath,dirname,isdir,basename
import time
from enum import IntEnum

# Local imports
from file_io_util import ask_overwrite
from paths import LOG_DIR


class Log_Levels():
	CRITICAL = 0
	WARNING = 1
	INFORMATION = 2
	DEBUG = 3


class Logger:
	"""
		Handles all of the logging for the program
	"""
	def __init__(self,filename,verbose=False,level=0,force_overwrite=False):
		self.filename = filename
		self.level = level
		self.verbose = verbose
		self.open_file = False
		if self.filename is not None and self.filename.lower() != "none":
			if exists(self.filename) and not force_overwrite:
				self.filename = ask_overwrite(self.filename,LOG_DIR)
			self.f = open(self.filename,"w+",buffering=1) # Buffer by line
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
		levels = ["ERROR: ","WARNING: ","INFO: ","DEBUG: "]
		msg = "{} {}{}".format(clock,levels[level],msg)
		if level <= self.level:
			if self.open_file:
				self.f.write("{}\n".format(msg))
			elif self.verbose:
				print(msg)
				return
			if also_print:
				print(msg)
				return
		return
	
	def error(self,msg):
		self.log(msg,0,also_print=True)

	def __del__(self):
		if self.open_file:
			self.f.close()
			self.open_file = False
			clock = time.strftime("[%H:%M:%S]",time.localtime())
			print("{} Closed {}".format(clock,self.filename))

################################################################################
LOGGER=Logger(None)
LOG_LEVEL=Log_Levels()

# Versatile Logging functions
def log(msg,level,also_print=False):
	LOGGER.log(msg,level,also_print=also_print)

def error(msg):
	LOGGER.error(msg)

# By log level, easier to reference
def critical(msg):
	LOGGER.log(msg,level=LOG_LEVEL.CRITICAL,also_print=True)

def warning(msg):
	LOGGER.log(msg,level=LOG_LEVEL.WARNING,also_print=True)

def info(msg):
	LOGGER.log(msg,level=LOG_LEVEL.INFORMATION,also_print=False)

def debug(msg):
	LOGGER.log(msg,level=LOG_LEVEL.DEBUG,also_print=False)

################################################################################
if __name__ == "__main__":
	LOGGER.re_init("test.out")
	log("Test text",2)
