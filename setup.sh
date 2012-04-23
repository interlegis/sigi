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

# Verifica se o easy_install e o pip está instalado
easy_install=`find /usr/bin/ -name easy_install`
pip=`find /usr/bin/ -name pip`
git=`find /usr/bin/ -name git`

if [ ! -f $easy_install ] || [ ! -f $pip ]; then
    echo "O aplicativo pip é obrigatório. Favor instalar para continuar a configuração do SIGI."
    sleep 5
    exit
else
    # Executando o arquivo requirements.txt
    if [ -f $requirements ]; then
        echo
        echo "Instalando os módulos contidos no arquivo $requirements ..."
        echo
        sleep 2
        pip install -r $requirements

        # Verifica se o git está instalado
        if [ ! -f $git]; then
            echo
            echo "O aplicativo git não está instalado. Caso contrário, faça o checkout diretamente."
            sleep 5
            exit
        else
            # Faz o checkout do projeto e instala o módulo
            echo
            echo "Fazendo o checkout do projeto..."
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
            cp -Rvf reporting geraldo /usr/local/lib/python2.7/site-packages
            # if you are using virtualenv 'sigi' use
            # cp -Rvf reporting geraldo $WORKON_HOME/sigi/lib/python2.7/site-packages
        fi
    else
        echo
        echo "O arquivo requirements.txt não existe. Verifique se está na mesma pasta do arquivo de instalação do SIGI."
        sleep 5
        exit
    fi
fi


