group { 'sigi':
  ensure => 'present',
}

user { 'sigi':
  ensure => 'present',
  system => 'true',
  gid    => 'sigi',
  require => Group['sigi']
}

package { [ 'git', 'tree', 'python-pip', 'python-dev', 'python-psycopg2',
  'supervisor', 'memcached', ]: }

$sigi_dir = '/srv/sigi'

file { [
  '/var/log/sigi',
  '/var/run/sigi',
  "${sigi_dir}/media",
  "${sigi_dir}/media/apps",
  "${sigi_dir}/media/apps/metas",
  ]:
  ensure => 'directory',
  owner  => 'sigi',
  group  => 'sigi',
}

# TODO A pasta "${sigi_dir}/media" deve ser compartilhada entre instancias de cluster

file { '/var/log/sigi/sigi-supervisor.log':
  ensure => file,
}

vcsrepo { $sigi_dir:
  ensure   => latest,
  provider => git,
  source   => 'https://github.com/interlegis/sigi.git',
  revision => 'producao',
  require  => Package['git'],
}

###########################################################################
# NGINX

class { 'nginx': }

nginx::resource::vhost { 'localhost':
  www_root => '/vagrant/www_temp',
}

