#!/bin/bash

puppet_nginx_instalado=$( puppet module list | grep -ic nginx )

if [ $puppet_nginx_instalado -eq 0 ]
then
  TAR_FILE=/tmp/puppet-nginx.tar.gz

  wget https://github.com/interlegis/puppet-nginx/archive/master.tar.gz -O $TAR_FILE
  rm -fr /tmp/puppet-nginx-master
  tar -C /tmp -xf $TAR_FILE

  echo 'Building module puppet-nginx...'
  TAR_MODULE=$(puppet module build /tmp/puppet-nginx-master | grep 'Module built' | cut -d\  -f 3)
  echo 'Installing module puppet-nginx from ' $TAR_MODULE ' ...'
  puppet module install $TAR_MODULE
fi
