FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3-pip
RUN apt-get autoremove -y
RUN apt-get clean

ENV LC_ALL C.UTF-8

RUN pip3 --no-cache-dir install --upgrade setuptools pip

COPY . /etainter/

WORKDIR /etainter

RUN pip3 install -r requirements.txt

ENV PYTHONPATH /etainter

ENTRYPOINT ["python3", "bin/analyzer.py"]
