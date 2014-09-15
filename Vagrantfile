# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.network :forwarded_port, guest: 80, host: 8080

  config.vm.provision :shell, :path => "puppet/bootstrap.sh"

  # XXX Usando provisoriamente o modulo oficial ate que sincronizemos nosso repo
  # XXX descomentar este trecho entao

  # config.vm.provision :shell,
  #   :path => "puppet/puppet_module_install_from_github.sh",
  #   :args => "jfryman-nginx interlegis/puppet-nginx"

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "puppet/manifests"
    puppet.manifest_file  = "site.pp"
  end

end
