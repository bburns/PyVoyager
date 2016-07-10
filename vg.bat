
:: launch vg.py command handler

:: note: %~dp0 gives you the drive and path of the current batch file,
:: so you can refer to other files in this same folder.

@python %~dp0\src\vg.py %*

