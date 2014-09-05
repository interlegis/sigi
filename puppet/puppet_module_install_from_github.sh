#!/bin/bash
# argumentos: <nome do modulo> <github_user/nome_repo>

nome_modulo=$1
github_path=$2
nome_repo=$(echo $github_path | cut -d / -f 2)

modulo_instalado=$( puppet module list | grep -ic $nome_modulo )

if [ $modulo_instalado -eq 0 ]
then
  TAR_FILE="/tmp/$nome_modulo.tar.gz"

  wget "https://github.com/$github_path/archive/master.tar.gz" -O $TAR_FILE
  rm -fr "/tmp/$nome_repo-master"
  tar -C /tmp -xf $TAR_FILE

  echo "Building module $nome_modulo..."
  TAR_MODULE=$(puppet module build "/tmp/$nome_repo-master" | grep 'Module built' | cut -d\  -f 3)
  echo "Installing module $nome_modulo from " $TAR_MODULE ' ...'
  puppet module install $TAR_MODULE
fi

