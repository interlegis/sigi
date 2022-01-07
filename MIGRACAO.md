NOTAS PARA MIGRAÇÃO PARA DJANGO 4.0
===================================

Para montar o ambiente
----------------------

* Clonar o sigi em sua máquina:
  ```$ git clone git@github.com:interlegis/sigi.git
  ```
* Entrar no diretório e mudar para o branch master:
  ```$ cd sigi
  $ git checkout --track origin/master
  ```
* Criar o ambiente virtual:
  ```$ mkdir env
  $ virtualenv -p python3 env/sigi
  ```
* Instalar os requirements:
  ```$ source env/sigi/bin/activate
  $ pip install --upgrade pip
  $ pip install -r requirements/dev-reuirements.txt
  ```

Pronto! Tá instalado!

Para executar o SIGI:
---------------------
```
$ cd sigi
$ source env/sigi/bin/activate
$ ./manage.py runserver
```
**No browser use o endereço 127.0.0.1:8000/admin**

Macro-tarefas:
--------------

* [x] Definir ambiente python 3 e django 4.0
* [ ] Migração dos APPS, nesta sequência:
  * [x] servidores
  * [x] contatos
  * [ ] casas
  * [ ] convenios
  * [ ] parlamentares
  * [ ] eventos
  * [ ] servicos
  * [ ] ocorrencias
  * [ ] whois
  * [ ] financeiro
  * [ ] inventario
  * [ ] metas
* [ ] Definição de um novo tema *bootstrapado* para o admin
