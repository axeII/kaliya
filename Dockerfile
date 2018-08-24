FROM ubuntu:16.04
# Install Python.

RUN apt-get update
RUN apt-get install -y git wget curl
RUN apt-get install -y software-properties-common vim
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update

RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip 
RUN pip install --upgrade pip

ADD requirements.txt /
ADD Makefile /
ADD kaliya.py /

RUN pip3 install --upgrade -r requirements.txt

RUN make install

CMD [ "python3.6", "kaliya.py"]
