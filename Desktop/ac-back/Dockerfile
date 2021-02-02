FROM git.disoft.us:5050/nastya/ac-back:basic
MAINTAINER Master Cerber <cerber@dianet.com.ua>


#COPY requirements.txt /usr/ac-back/
COPY . /usr/ac-back/
RUN pip3 install --no-cache-dir -r requirements.txt

ADD https://github.com/ufoscout/docker-compose-wait.git /sbin/wait
RUN chmod +x /sbin/wait

#CMD  [ "python3 manage.py  runserver 0.0.0.0:9090"  ]
EXPOSE 9090
