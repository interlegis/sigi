#!/bin/bash

THIS_SHELL=`ps --no-heading -p $$ | awk '{print $4}'`
if [ $THIS_SHELL != 'bash' ] ; then
    echo "Você está executando este script com o interpretador '$THIS_SHELL'"
    echo "mas ele só funciona com o 'bash'."
    echo "Tente executar usando 'bash install.sh'."
    exit 1
fi

echo "Instalando python-pip, python-dev e python-psycopg2..."
sudo apt-get install -y python-pip python-dev python-virtualenv

echo "Criando virtualenv..."
virtualenv ./env/

echo "Instalando pacotes python requeridos pelo SIGI..."
pip install --environment=./env/ -r requirements.txt

echo "Ativando o virtualenv..."
source ./env/bin/activate

echo "Isolando arquivos temporários..."
mkdir tmp

echo "Instalando geraldo reports..."
git clone https://github.com/marinho/geraldo.git
cd geraldo
python setup.py install
cp -Rfv reporting geraldo `python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())"`
cd ..

echo "Excluindo arquivos temporários..."
cd ..
rm -Rf tmp

echo "Criando e populando o banco de dados..."
pwd
python manage.py syncdb
