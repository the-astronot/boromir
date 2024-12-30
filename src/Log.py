# Library imports
import os
from os.path import join,exists,isfile,dirname,isdir
import time
from enum import IntEnum

# Local imports



class Logger:
	"""
	
	"""
	def __init__(self,filename,verbose=False,level=0,force_overwrite=False):
		self.filename = filename
		self.level = level
		self.verbose = verbose
		self.open_file = False
		if self.filename is not None:
			if exists(self.filename) and not force_overwrite:
				self.ask_overwrite()
			self.f = open(self.filename,"w+")
			self.open_file = True

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
		
	def ask_overwrite(self):
		"""
			Check before overwriting 
		"""
		confirm_overwrite = False
		while confirm_overwrite == False:
			response = input("File: {} already exists. Would you like to overwrite it? (Y/n)".format(self.filename))
			if not response.lower() in ["","y","ye","yes"]:
				invalid_filename = True
				while invalid_filename:
					new_file = input("Enter alternate filename: ")
					if isdir(dirname(new_file)):
						invalid_filename = False
					else:
						print("Path does not exist, try again...")
				self.filename = new_file
				if not exists(self.filename):
					confirm_overwrite = True
			else:
				confirm_overwrite = True

	def __del__(self):
		if self.open_file:
			self.f.close()
			self.open_file = False
			self.error("Closed {}".format(self.filename))

			


if __name__ == "__main__":
	Logger("test.out")
	Logger.log("Test text",2)
