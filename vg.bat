:: build pyvoyager image named 'vg' - see Dockerfile
docker build -t vg .

:: run pyvoyager image 'vg' in docker container named 'vg' also
docker run -it --rm --name vg vg %*
