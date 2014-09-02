class { 'nginx': }

nginx::resource::vhost { 'localhost':
  www_root => '/vagrant/www_temp',
}
