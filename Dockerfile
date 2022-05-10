# PyVoyager Docker image build instructions
#
# To build and run,
#   docker build -t vg .
#   docker run -it --rm --name vg vg

# see https://hub.docker.com/_/python
FROM python:2

WORKDIR /usr/src/app

# install requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src src

# RUN python src/vg.py download 5101

# this is python 2
# ENTRYPOINT [ "python", "src/vg.py" ]
# can override this with docker run
CMD [ "python", "src/vg.py" ]
