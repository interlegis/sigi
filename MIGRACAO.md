NOTAS PARA MIGRAÇÃO PARA DJANGO 4.0
===================================

Para montar o ambiente
----------------------

* Em uma máquina que nunca rodou SIGI, deve-se instalar alguns pacotes (Testado em Ubuntu 20.04), que são:
```
sudo apt install build-essential python3-dev graphviz libgraphviz-dev pkg-config libpq-dev
```

* Clonar o sigi em sua máquina:
  ```
  git clone git@github.com:interlegis/sigi.git
  ```
* Entrar no diretório e mudar para o branch master:
  ```
  cd sigi
  git checkout --track origin/master
  ```
* Criar o ambiente virtual:
  ```
  mkdir env
  virtualenv -p python3 env/sigi
  ```
* Instalar os requirements:
  ```
  source env/sigi/bin/activate
  pip install --upgrade pip
  pip install -r requirements/dev-requirements.txt
  ```

Pronto! Tá instalado!

Para executar o SIGI:
---------------------
```
cd sigi
source env/sigi/bin/activate
./manage.py runserver
```
**No browser use o endereço 127.0.0.1:8000/admin**

