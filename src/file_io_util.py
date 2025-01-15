# Library imports
import contextlib
import os
from os.path import exists,join,abspath,dirname,basename,isdir,isfile

# FILE_IO Operations that do not require logging
# Separated to avoid circular import

################################################################################
# CONTEXT MANAGER, for performing required actions at file locations
@contextlib.contextmanager
def quick_cd(path):
	"""
		Save current path, temporarily cd into specified path,
		perform required actions, and cd back to the original path
	"""
	old_dir = os.getcwd()
	try:
		os.chdir(path)
		yield
	except NotADirectoryError:
		raise NotADirectoryError(path)
	finally:
		os.chdir(old_dir)
	return
################################################################################

################################################################################
# CONFIRM BEFORE OVERWRITING FILE
def ask_overwrite(filename,path):
		"""
			Check before overwriting 
		"""
		original = filename
		confirm_overwrite = False
		while confirm_overwrite == False:
			response = input("File: {} already exists. Would you like to overwrite it? (Y/n)".format(filename))
			if not response.lower() in ["","y","ye","yes"]:
				invalid_filename = True
				while invalid_filename:
					new_file = input("Enter alternate filename: ")
					if basename(new_file) == new_file:
						new_file = join(path,new_file)
					if isdir(dirname(new_file)):
						invalid_filename = False
					else:
						print("Path does not exist, try again...")
				filename = new_file
				if not exists(filename):
					confirm_overwrite = True
					print("File changed from {} to {}".format(original,filename))
			else:
				confirm_overwrite = True
				print("Overwrite of {} confirmed".format(filename))
		return filename
################################################################################
