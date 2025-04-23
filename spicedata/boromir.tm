This is the kernel used in calculating the Sun LoS on the Moon given a UTC time and date.

Filename                             Contents
------------------------------------ --------------------------
naif0012.tls                         Generic LSK File
de440.bsp                            Solar System Ephemeris
moon_pa_de440_200625.bpc             Moon Ephemeris Data
moon_de440_250416.tf                 Data for IAU_MOON Ref Frame
earth_1962_240827_2124_combined.bpc  Data for ITRF93 Ref Frame

\begindata
KERNELS_TO_LOAD = ( 'naif0012.tls',
										'de440.bsp',
										'moon_pa_de440_200625.bpc',
										'moon_de440_250416.tf',
										'earth_1962_240827_2124_combined.bpc')
\begintext
