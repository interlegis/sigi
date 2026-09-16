FROM python:3.14-slim-trixie

# Setup env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# App env
ENV INTERLEGIS=/srv/interlegis
ENV HOME=${INTERLEGIS}/sigi
ENV SOCKS=${INTERLEGIS}/socks

# Settings args - must be provided in the build process
ENV DEBUG=False
ENV ADMINS="(('SIGI Administrator', 'sigi@interlegis.leg.br'),)"
ENV EMAIL_PORT=25
ENV EMAIL_HOST=mail.interlegis.leg.br
ENV EMAIL_HOST_USER=''
ENV EMAIL_SUBJECT_PREFIX='[SIGI]'
ENV EMAIL_USE_LOCALTIME=True
ENV EMAIL_USE_TLS=False
ENV EMAIL_USE_SSL=False
ENV EMAIL_TIMEOUT=120
ENV DEFAULT_FROM_EMAIL=sigi@interlegis.leg.br
ENV DATABASE_URL='sqlite:////:memory:'

# Install env
# Install required packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y gcc locales build-essential python3-dev graphviz \
      libgraphviz-dev pkg-config libmagic-dev libpq-dev postgresql-client \
      libsasl2-dev libldap2-dev libssl-dev vim nginx cron git

# Set encode language/charset
ENV DESIRED_LANG=pt_BR.UTF-8
RUN sed -i -e "s/# ${DESIRED_LANG}.*/${DESIRED_LANG} UTF-8/" /etc/locale.gen && \
    locale-gen pt_BR.UTF-8 && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=${DESIRED_LANG}
ENV LANG=${DESIRED_LANG}

# Create work and unix socket dirs
RUN mkdir -p ${HOME} && \
    mkdir ${SOCKS} && \
    mkdir ${HOME}/media && \
    mkdir ${HOME}/static

# Add sigi to container
WORKDIR ${HOME}
ADD . ${HOME}

# Install python packages
RUN pip install -qq --upgrade pip setuptools && \
    pip install -qq -r ${HOME}/requirements/requirements.txt

# Remove .env trash file
RUN rm -f ${HOME}/sigi/.env

# Generate a new secret key
RUN echo $'\n\n'SECRET_KEY=`python manage.py generate_secret_key` >> ${HOME}/sigi/.env

# Prepare run script to start application server
RUN chmod +x ${HOME}/bin/run_sigi
RUN chmod +x ${HOME}/bin/prepare_environment.sh

# Static files
RUN python manage.py collectstatic --noinput --clear

# nginx setup
RUN rm -f /etc/nginx/sites-enabled/*
RUN ln -s ${HOME}/etc/nginx/sites-available/sigi.vhost /etc/nginx/sites-enabled/sigi.vhost
RUN mkdir -p /var/log/sigi

# schedule cron jobs
RUN crontab -l | { cat; echo "* * * * * /usr/local/bin/python ${HOME}/manage.py runjob job_controller >> /var/log/sigi/cron.log 2>&1"; } | crontab -
EXPOSE 80/tcp 443/tcp

ENV DEBIAN_FRONTEND=teletype

VOLUME ["/srv/interlegis/sigi/media"]

# Start web server
CMD service cron start && service nginx start && /srv/interlegis/sigi/bin/run_sigi