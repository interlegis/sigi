Sistema de Informações Gerenciais
==========================

SIGI é um projeto para um Sistema de Informações Gerenciais do
Interlegis, escrito na linguagem de programação Python com o framework
para desenvolvimento web Django.

Maiores informações em ``docs/visaogeral.txt``.

Installation
---------------
Faça o checkout do projeto
 
        $ git clone https://github.com/BrenoTeixeira/SIGI-1.6.git

Instalando as dependências do arquivo `requirements.txt`

        $ pip install -r requirements.txt

Install django-googlecharts

        $ git clone git clone git://github.com/jacobian/django-googlecharts.git
        $ cd django-googlecharts
        $ python setup.py instal

Install a app de reports generator

        $ git clone https://github.com/marinho/geraldo.git
        $ cd geraldo
        $ python setup.py install
        $ cp -Rvf reporting geraldo /usr/local/lib/python2.7/site-packages

Se você estiver suando virtualenv use

        $ cp -Rvf reporting geraldo $WORKON_HOME/virtualenv_name/lib/python2.7/site-packages



Getting Help
-----------------
Existe uma lista de email ([http://groups.google.com/group/sigi][2]) disponível para discussão geral.

Contributing
-----------------
1. Fork it.
2. Create a branch (`git checkout -b my_sigi`)
3. Commit your changes (`git commit -am "Added new feature"`)
4. Push to the branch (`git push origin my_sigi`)
5. Open a [Pull Request] [1]

[1]:https://github.com/BrenoTeixeira/SIGI-1.6/pulls 
[2]:http://groups.google.com/group/sigi


Copyright (c) 2008 Interlegis
