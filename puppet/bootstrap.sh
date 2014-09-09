#!/bin/bash

puppet module list | grep puppetlabs-vcsrepo || puppet module install puppetlabs/vcsrepo
