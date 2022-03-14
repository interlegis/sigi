#FROM ubuntu
#FROM python:3
#ENV PYTHONDONTWRITEBYTECODE=1
#ENV PYTHONUNBUFFERED=1
#CMD apt install update
#CMD apt install upgrade -y
#CMD apt install build-essential python3-dev graphviz libgraphviz-dev pkg-config libpq-dev -y
#RUN pip install --upgrade pip
#COPY . /dck/
#RUN pip install -r dck/requirements/dev-requirements.txt
#CMD python ./manage.py runserver

FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt update 
RUN apt upgrade -y 
RUN apt install build-essential python3-dev graphviz libgraphviz-dev pkg-config libpq-dev -y
RUN pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start
RUN pip install --upgrade pip
WORKDIR /code
COPY . /code/
RUN pip install -r /code/requirements/dev-requirements.txt
RUN service pstgresql start