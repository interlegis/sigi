FROM python:3.8-slim-buster

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
ENV EMAIL_HOST_PASSWORD=''
ENV EMAIL_SUBJECT_PREFIX='[SIGI]'
ENV EMAIL_USE_LOCALTIME=True
ENV EMAIL_USE_TLS=False
ENV EMAIL_USE_SSL=False
ENV EMAIL_TIMEOUT=120
ENV DEFAULT_FROM_EMAIL=sigi@interlegis.leg.br
ENV DATABASE_URL='sqlite:////:memory:'
ENV AUTH_LDAP_SERVER_URI=''
ENV AUTH_LDAP_BIND_DN=''
ENV AUTH_LDAP_BIND_PASSWORD=''
ENV AUTH_LDAP_USER=''
ENV AUTH_LDAP_USER_SEARCH_STRING=''
ENV AUTH_LDAP_GROUP=''
ENV AUTH_LDAP_GROUP_SEARCH_STRING=''
ENV AUTH_LDAP_GROUP_TYPE_STRING=''
ENV AUTH_LDAP_USER_ATTR_MAP=''
ENV AUTH_LDAP_PROFILE_ATTR_MAP=''
ENV AUTH_LDAP_FIND_GROUP_PERMS=''
ENV AUTH_LDAP_MIRROR_GROUPS=''
ENV AUTH_LDAP_CACHE_GROUPS=''
ENV AUTH_LDAP_GROUP_CACHE_TIMEOUT=''
ENV AUTH_PROFILE_MODULE=''

# Install env
ENV RUN_PACKAGES gcc locales build-essential python3-dev graphviz \
    libgraphviz-dev pkg-config libpq-dev postgresql-client \
    libsasl2-dev libldap2-dev libssl-dev vim nginx cron

# Install required packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y ${RUN_PACKAGES}

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
    if [ $DEBUG = False ]; then \
    pip install -qq -r ${HOME}/requirements/requirements.txt; \
    else \
    pip install -qq -r ${HOME}/requirements/dev-requirements.txt; \
    fi

# Generate a new secret key
RUN echo $'\n\n'SECRET_KEY=`python manage.py generate_secret_key` >> ${HOME}/sigi/.env

# Prepare run script to start application server
RUN chmod +x ${HOME}/bin/run_sigi

# Static files
RUN python manage.py collectstatic --noinput --clear

# nginx setup
RUN rm -f /etc/nginx/sites-enabled/*
RUN ln -s ${HOME}/etc/nginx/sites-available/sigi.vhost /etc/nginx/sites-enabled/sigi.vhost
RUN mkdir -p /var/log/sigi

# schedule cron jobs
RUN crontab -l | { cat; echo "* * * * * ${HOME}/manage.py runjobs minutely >> /var/log/sigi/minutely.log"; } | crontab -
RUN crontab -l | { cat; echo "0 * * * * ${HOME}/manage.py runjobs hourly >> /var/log/sigi/hourly.log"; } | crontab -
RUN crontab -l | { cat; echo "0 0 * * * ${HOME}/manage.py runjobs daily >> /var/log/sigi/daily.log"; } | crontab -

EXPOSE 80/tcp 443/tcp

ENV DEBIAN_FRONTEND=teletype

VOLUME ["/srv/interlegis/sigi/media"]

# Start web server
CMD service nginx start && /srv/interlegis/sigi/bin/run_sigi