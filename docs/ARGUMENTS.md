# ARGUMENTS

Laying out the assorted arguments. Boromir has 2 sets of arguments:

1. General Arguments, which are shared between the separate run types
2. Specific Arguments, which are specific to the run specified (trajecory or random)

## GENERAL ARGUMENTS

| Name | Invocation | Default | Description |
| ---- | ---------- | ------- | ----------- |
| help | -h,--help  |  N/A    | Show the help message and exit |
| version | --version | N/A   | Shows the version number and exits |
| verbose | -v,--verbose | False | Toggles output to the terminal |
| logging | --logging | None | Output logging file |
| blender | --blender | blender.json | Which Blender config file to use |
| camera  | --camera  | testcam.json | Which camera config file to use |
| log level | --log_level | 2 | Level of logging from {0..3}->{Critical,Warning,Info,Debug} |
| overwrite | --fo,--forceoverwrite | False | Overwrite old files without asking |

## SPECIFIC ARGUMENTS

### TRAJECTORY ARGS

After completing the General arguments and specifying "trajectory" as the run type, the following arguments are available:

| Name | Invocation | Default | Description |
| ---- | ---------- | ------- | ----------- |
| Filename | (Positional) | (Required) | The filename in configs/trajectories to run |
| job | --job | Filename w/o extension | The name to give the run's output directory |
| outdir | --outdir | outimages/ | The directory to put to put the output in |
| gkm | --disablegkm | False | Whether to disable sharing meshes (can increase run-time and artifacts) |

### RANDOM ARGS

W.I.P.
