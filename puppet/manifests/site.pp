group { 'sigi':
  ensure => 'present',
}

user { 'sigi':
  ensure  => 'present',
  system  => true,
  gid     => 'sigi',
  require => Group['sigi']
}

package { [ 'git', 'tree', 'python-psycopg2', 'supervisor', 'memcached', ]: }

$sigi_dir = '/srv/sigi'

vcsrepo { $sigi_dir:
  ensure   => latest,
  provider => git,
  source   => 'https://github.com/interlegis/sigi.git',
  revision => 'producao',
  require  => Package['git'],
}

file { [
  '/var/log/sigi',
  '/var/run/sigi',
  "${sigi_dir}/media",
  "${sigi_dir}/media/apps",
  "${sigi_dir}/media/apps/metas",
  ]:
  ensure  => 'directory',
  owner   => 'sigi',
  group   => 'sigi',
  require => Vcsrepo[$sigi_dir],
}

# TODO A pasta "${sigi_dir}/media" deve ser compartilhada entre instancias de cluster

file { '/var/log/sigi/sigi-supervisor.log':
  ensure => file,
}

###########################################################################
# PYTHON

if !defined(Class['python']) {
  class { 'python':
    version    => 'system',
    dev        => true,
    virtualenv => true,
    pip        => true,
  }
}

$python_ldap_deps = ['libldap2-dev', 'libsasl2-dev', 'libssl-dev']

package { $python_ldap_deps: }

$sigi_venv_dir = '/srv/.virtualenvs/sigi'

file { ['/srv/.virtualenvs',]:
  ensure => 'directory',
}

python::virtualenv { $sigi_venv_dir :
  requirements => "${sigi_dir}/requirements/producao.txt",
  require      => [ File['/srv/.virtualenvs'],
                    Vcsrepo[$sigi_dir],
                    Package[$python_ldap_deps] ]
}

###########################################################################
# NGINX

class { 'nginx': }

nginx::resource::vhost { 'localhost':
  www_root => '/vagrant/www_temp',
}

