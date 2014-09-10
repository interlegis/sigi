group { 'sigi':
  ensure => 'present',
}

user { 'sigi':
  ensure  => 'present',
  system  => true,
  gid     => 'sigi',
  require => Group['sigi']
}

package { [ 'git', 'python-psycopg2', 'supervisor', 'memcached',
            ]: }

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
  require => File['/srv/.virtualenvs'],
}

python::requirements { "${sigi_dir}/requirements/producao.txt":
  virtualenv  => $sigi_venv_dir,
  forceupdate => true,
  require     => [
    Python::Virtualenv[$sigi_venv_dir],
    Vcsrepo[$sigi_dir],
    Package[$python_ldap_deps] ]
}

###########################################################################
# GERALDO (reporting)
file { "${sigi_venv_dir}/lib/python2.7/site-packages/reporting":
  ensure => link,
  target => "${sigi_venv_dir}/src/geraldo/reporting",
}

###########################################################################
# DJANGO

exec { 'collectstatic':
  command => "${sigi_venv_dir}/bin/python manage.py collectstatic --noinput",
  cwd     => $sigi_dir,
}

# TODO local_settings.py ...



###########################################################################
# NGINX

class { 'nginx': }

nginx::resource::vhost { 'localhost':
  www_root => '/vagrant/www_temp',
}

