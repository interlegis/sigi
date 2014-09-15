#!/bin/bash

puppet_install () {
    puppet module list | grep $1 || puppet module install $1
}

puppet_install puppetlabs-vcsrepo
puppet_install stankevich-python

# XXX Usando provisoriamente o modulo oficial ate que sincronizemos nosso repo
# XXX retirar esta linha entao
puppet_install jfryman-nginx

