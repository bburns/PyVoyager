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

#. download img2png, unzip to vendor folder
# see http://bjj.mmedia.is/utils/img2png/
#. uhoh it's a windows program - what do?
# i guess i'll have to bake the pngs into the image, skip steps 1 and 2
# 0.5gb per volume -> 40gb, plus they'll compress well
# http://bjj.mmedia.is/utils/img2png/img2png.zip

COPY src src

#. need a wildcard download, vg download *, or vg download all
RUN python src/vg.py download 5101

# this is python 2
# ENTRYPOINT [ "python", "src/vg.py" ]
# can override this with docker run
CMD [ "python", "src/vg.py" ]
