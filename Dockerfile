FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt update 
RUN apt upgrade -y 
RUN apt install build-essential python3-dev graphviz libgraphviz-dev pkg-config libpq-dev -y
RUN pip install --upgrade pip
WORKDIR /code
COPY . /code/
#RUN pg_ctl -D /var/lib/postgresql/data -l logfile start
# RUN --mount=type=cache,target=/root/.cache/pip pip install -r /code/requirements/dev-requirements.txt
RUN pip install -r /code/requirements/dev-requirements.txt
RUN python manage.py migrate