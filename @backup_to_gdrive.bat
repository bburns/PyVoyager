
:: backup all files excluding the data directory to dropbox
:: also exclude the SPICE .bsp files, which are huge
:: robocopy . c:\projects\voyager\backup /mir /xd data /xf *.bsp
robocopy . c:\users\bburns\gdrive\projects\voyager\backup /mir /xd data /xf *.bsp
