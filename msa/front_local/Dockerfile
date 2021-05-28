FROM python:3.7.9-stretch

RUN apt-get update
RUN pip install flask
RUN pip install flask-restful
RUN pip install pymysql
RUN pip install python-consul
RUN pip install python-dotenv
RUN pip install authlib

RUN apt-get install -y vim

WORKDIR /front_local
COPY /front_local /front_local

EXPOSE 3000

CMD ["python", "app.py"]
