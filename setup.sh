#!/bin/bash

#############################################################
## Arquivo: setup.sh                                       ##
##                                                         ##
## Esse arquivo foi criado para automatizar a instalação   ##
## do projeto SIGI.                                        ##
##                                                         ##
## Autor: Gilson Filho <contato@gilsondev.com>             ##
## Data: 23 de Novembro de 2011                            ##
## Versão: 1.0                                             ##
##                                                         ##
#############################################################

# Definindo o nome do arquivo que contem as informações das dependências
requirements="requirements.txt"

# Executando o arquivo requirements.txt
if [ -f $requirements ]; then
        echo
        echo "Instalando os módulos contidos no arquivo $requirements ..."
        echo
        sleep 2
        pip install -r $requirements

        # Faz o checkout do projeto e instala o módulo
        echo
        echo "Fazendo o checkout do projeto googlecharts"
        echo
        sleep 2
        git clone git://github.com/jacobian/django-googlecharts.git

        echo
        echo "Iniciando a instalacao..."
        echo
        sleep 2
        cd django-googlecharts
        python setup.py install

        # Instalando o django-geraldo
        echo
        echo "Fazendo o checkout do projeto django-geraldo..."
        echo
        sleep 2
        git clone https://github.com/marinho/geraldo.git

        echo
        echo "Instalando o django-geraldo..."
        echo
        cd geraldo
        python setup.py install
        # cp -Rvf reporting geraldo /usr/local/lib/python2.7/site-packages
        # if you are using virtualenv 'sigi' use
        cp -Rvf reporting geraldo $WORKON_HOME/sigi/lib/python2.7/site-packages
else
    echo
    echo "O arquivo requirements.txt não existe. Verifique se está na mesma pasta do arquivo de instalação do SIGI."
    sleep 5
    exit
fi
