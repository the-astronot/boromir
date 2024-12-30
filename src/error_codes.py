from enum import IntEnum

################################################################################
## FILE_IO #####################################################################

# Trajectory File Check
class TrajFileReadError(IntEnum):
	SUCCESS=0
	FILENOTFOUND=1
	INCOMPLETEPOSE=2

# Random File Check
class RandFileReadError(IntEnum):
	SUCCESS=0
