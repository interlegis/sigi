FROM ubuntu:15.04

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN mkdir /sigi

RUN	apt-get update && \
	apt-get install -y -f \
	build-essential \
	curl \
	git \
	graphviz-dev \
	graphviz \
	libz-dev \
	libffi-dev \
	libfreetype6-dev \
	libjpeg62 \
	libjpeg-dev \
	libldap2-dev \
	libpq-dev \
	libsasl2-dev \
	libssl-dev \
	libxft-dev \
	libxml2-dev \
	libxslt1-dev \
	nginx \
	pkg-config \
	python-dev \
	python-setuptools \
	software-properties-common \
	npm \
	nodejs

# install nodejs
RUN DEBIAN_FRONTEND=noninteractive curl -sL https://deb.nodesource.com/setup_5.x | bash -
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs

# install bower
RUN npm install -g bower

# Bower aceitar root
RUN touch /root/.bowerrc
RUN chmod 751 /root/.bowerrc
RUN echo "{ \"allow_root\": true }" >> /root/.bowerrc

ADD . /sigi

WORKDIR /sigi

RUN easy_install pip
RUN pip2 install -r requirements/dev-requirements.txt
RUN pip2 install --upgrade setuptools

