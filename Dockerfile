FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements/dev-requirements.txt /
RUN pip install -r requirements/dev-requirements.txt
CMD python ./manage.py runserver