:: run pyvoyager image 'vg' in docker container named 'vg'
:: build image first with build.bat
@docker run -it --rm -v "%cd%\data":/usr/src/app/data --name vg vg %*
