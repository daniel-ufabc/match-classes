FROM debian:stable-20200803-slim

RUN apt update && apt install -y build-essential python3-dev python3-pip zip
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir /app
RUN mkdir /data
WORKDIR /app

COPY ./aux/src/sort_students.c .
RUN mkdir -p /app/driver/bin
RUN gcc sort_students.c -O2 -o ./driver/bin/sort_students

COPY ./requirements.txt ./requirements.txt
RUN pip3 install -U pip setuptools
RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "--preload", "-b", "0.0.0.0:8000", "iturmas.index:app"]

