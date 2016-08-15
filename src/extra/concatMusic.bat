
:: Concatenate audio files together
:: See http://stackoverflow.com/questions/23188742/working-with-filter-complex-in-ffmpeg-with-a-batch-concat-array

@echo off

set a=
set var=
set array=
set numfiles=

for %%a in ("music\*.*") do call set var=%%var%% -i "%%a"
:: echo %var%

:: Give you the number of files
:: for /f %%a in ('dir "music\*.*" /b /a-d ^|find /c /v "" ') do set "numfiles=%%a"
for /f %%a in ('dir "music\*.*" /b /a-d ^|c:\windows\system32\find.exe /c /v "" ') do set "numfiles=%%a"
echo There are "%numfiles%" files
echo.

set /a "nmax=numfiles-1"
:: echo %numfiles%
for /L %%b in (0,1,%nmax%) do call set array=%%array%% [%%b:0]
set array=%array:~1%
echo "%array%"
echo.

:: echo ffmpeg %var% -filter_complex "%array% concat=n=%numfiles%:v=0:a=1 "[a]"" -map "[a]" -acodec libmp3lame -ab 320k "output.mp3"
ffmpeg %var% -filter_complex "%array% concat=n=%numfiles%:v=0:a=1 "[a]"" -map "[a]" "music.mp3"

:: pause

