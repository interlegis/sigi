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

class { 'nginx': }

nginx::resource::upstream { 'sigi_app_server':
  members               => [ 'unix:/var/run/sigi/sigi.sock' ],
  upstream_fail_timeout => 0
}

# XXX trocar nome para server_name, p.ex. sigi01h.interlegis.leg.br
$sigi_vhost = 'localhost'

nginx::resource::vhost { $sigi_vhost:
  client_max_body_size => '4G',
  access_log           => '/var/log/sigi/sigi-access.log',
  error_log            => '/var/log/sigi/sigi-error.log',
  use_default_location => false,
  require              => Vcsrepo[$sigi_dir],

  # TODO tentar usar try_files ao inves desse "if"
  #      vide http://stackoverflow.com/questions/19845566/in-nginxs-configuration-could-if-f-request-filename-cause-a-performan
  # XXX este raw_append foi uma apelacao devido a limitacoes do modulo nginx
  raw_append           => '
  location / {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_redirect off;
      if (!-f $request_filename) {
          proxy_pass http://sigi_app_server;
          break;
      }
  }
'
}

nginx::resource::location { '/static/':
  vhost          => $sigi_vhost,
  location_alias => '/srv/sigi/static/',
}

nginx::resource::location { '/media/':
  vhost          => $sigi_vhost,
  location_alias => '/srv/sigi/media/',
}
