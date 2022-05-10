# PyVoyager Docker image build instructions
#
# To build and run,
#   docker build -t vg .
#   docker run -it --rm --name vg vg

FROM python:2

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src .
COPY vg .

RUN chmod +x vg

CMD [ "./vg" ]
