Exec {
  path => '/usr/bin:/usr/sbin:/bin:/usr/local/bin',
}

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
  require => [
    Python::Virtualenv[$sigi_venv_dir],
    Vcsrepo[$sigi_dir], ]
}

# TODO local_settings.py ...


###########################################################################
# SUPERVISOR

# XXX trocar isso por algum plugin do puppet?

$supervisor_conf = '/etc/supervisor/conf.d/sigi.conf'

file { $supervisor_conf:
  ensure  => link,
  target  => "${sigi_dir}/etc/supervisor/conf.d/sigi.conf",
  require => [
    Vcsrepo[$sigi_dir],
    Package['supervisor'] ]
}

exec { 'supervisor_update':
  command     => 'supervisorctl reread && supervisorctl update',
  refreshonly => true,
  subscribe   => [ File[$supervisor_conf], Vcsrepo[$sigi_dir]],
}

###########################################################################
# NGINX

package { 'nginx': }

file { '/etc/nginx/sites-available/sigi.vhost':
  ensure  => link,
  target  => "${sigi_dir}/etc/nginx/sites-available/sigi.vhost",
  require => [
    Vcsrepo[$sigi_dir],
    Package['nginx'] ]
}

file { '/etc/nginx/sites-enabled/sigi.vhost':
  ensure  => link,
  target  => '/etc/nginx/sites-available/sigi.vhost',
  require => Package['nginx'],
}

exec { 'nginx_restart':
  command     => 'service nginx restart',
  refreshonly => true,
  subscribe   => [
    File['/etc/nginx/sites-enabled/sigi.vhost'],
    Vcsrepo[$sigi_dir]],
}

file { '/etc/nginx/sites-enabled/default':
  ensure => absent,
}

