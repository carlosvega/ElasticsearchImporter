#!/bin/bash

if command -v apt-get &> /dev/null ; then
    echo "[ - Debian/Ubuntu based system detected ]"
	sudo apt-get update -y
	#only docker stuff
	#sudo DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true apt-get install -y apt-utils tzdata
	#sudo DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true dpkg-reconfigure tzdata
	#sudo echo "Europe/Madrid" > /etc/timezone
	#sudo dpkg-reconfigure -f noninteractive tzdata
	#sudo apt-get update -y
	echo "[ - Removing sqlite3... ]"
	sudo apt-get remove -y sqlite3
	sudo apt-get purge -y sqlite3
	sudo apt-get install -y build-essential bzip2 git libbz2-dev libc6-dev libgdbm-dev libgeos-dev liblz-dev liblzma-dev libncurses5-dev libncursesw5-dev libreadline6 libreadline6-dev libsqlite3-dev libssl-dev lzma-dev python-dev python-pip python-software-properties python-virtualenv software-properties-common sqlite3 tcl tk-dev tk8.5-dev wget
	#install sqlite
	echo "[ - Installing sqlite3... ]"
	sudo wget "https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release" -O sqlite.tar.gz &> /dev/null
	sudo tar -xzvf sqlite.tar.gz
	cd sqlite
	sudo ./configure --enable-fts5
	sudo make
	sudo make install
	cd ..
	sudo apt-get remove -y python python3 python-dev
	sudo apt-get install -y --reinstall python2.7 python3 python-dev
	sudo apt-get install -y build-essential bzip2 git libbz2-dev libc6-dev libgdbm-dev libgeos-dev liblz-dev liblzma-dev libncurses5-dev libncursesw5-dev libreadline6 libreadline6-dev libsqlite3-dev libssl-dev lzma-dev python-dev python-pip python-software-properties python-virtualenv software-properties-common sqlite3 tcl tk-dev tk8.5-dev wget
	#install pypy
	echo "[ - Installing pypy... ]"
	sudo add-apt-repository -y ppa:pypy/ppa
	sudo apt-get update -y
	sudo apt-get install -y pypy pypy-dev
	sudo apt-get install -y --only-upgrade pypy 
	sudo pip install pip --upgrade
	#install repo
	#echo "[ - Installing ElasticsearchImporter repository... ]"
	#sudo git clone https://github.com/carlosvega/ElasticsearchImporter.git ElasticsearchImporter
	#cd ElasticsearchImporter
	virtualenv .envpypy --python=`which pypy`
	source .envpypy/bin/activate
	pypy -m pip install -r requirements.txt
	py.test
	deactivate
	echo "[ - Remember to enable the virtualenv with 'source .envpypy/bin/activate' ]"
else
    echo "[ - Sorry, at the moment, the installation script only supports ubuntu systems, preferably Ubuntu 16.04 ]"
    exit
fi