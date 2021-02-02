FROM debian:buster as ep-basic
MAINTAINER Master Cerber <cerber@dianet.com.ua>

RUN mkdir -p /usr/ac-back/
WORKDIR /usr/ac-back/

COPY ./dpkg_requirements.txt /usr/ac-back/

RUN apt-get update
RUN apt-get install -yqq $(cat dpkg_requirements.txt)


COPY ./requirements.txt /usr/ac-back/

RUN pip3 install --no-cache-dir -r requirements.txt



EXPOSE 9090

