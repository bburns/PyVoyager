:: run pyvoyager image 'vg' in docker container named 'vg'
@docker run -it --rm -v "/${PWD}/data":/usr/src/app/data --name vg vg %*

