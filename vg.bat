
:: launch vg.py command handler

:: note: %~dp0 gives you the drive and path of the current batch file,
:: so you can refer to other files in this same folder.
:: -tt throws an error if it finds tabs mixed with spaces
@python -tt %~dp0\src\vg.py %*

