#!/bin/bash

cat > /etc/apt/apt.conf.d/99stop-update <<- EOM
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::AutocleanInterval "0";
APT::Periodic::Unattended-Upgrade "0";
EOM
