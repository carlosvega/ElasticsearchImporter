#!/bin/bash

if command -v apt-get &> /dev/null ; then
    echo "[ - Debian/Ubuntu based system detected ]"
	sudo apt-get update -y
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
	sudo echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite.conf && ldconfig
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
	echo "[ - Installing repo ]"
	virtualenv .envpypy --python=`which pypy`
	source .envpypy/bin/activate
	pypy -m pip install -r requirements.txt
	py.test
	deactivate
	echo "[ - Remember to enable the virtualenv with 'source .envpypy/bin/activate' ]"
elif yum --version &> /dev/null; then
	echo "[ - RHEL/CentOS based system detected ]"
	yum update -y
	yum groupinstall -y 'Development Tools'
	yum install -y sudo wget which git python-pip python-virtualenv sqlite-devel tcl tcl-devel epel-release
	sudo yum update -y
	echo "[ - Default sqlite3 version $(sqlite3 --version) and python module $(python -c 'import sqlite3; print(sqlite3.sqlite_version)')]"
	wget "https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release" -O sqlite.tar.gz &> /dev/null && tar -xzvf sqlite.tar.gz && rm -f sqlite.tar.gz
	cd sqlite
	sudo ./configure --enable-fts5 && make && make install
	sudo echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite.conf && ldconfig
	echo "[ - Installed sqlite3 version $(sqlite3 --version) and python module $(python -c 'import sqlite3; print(sqlite3.sqlite_version)')]"
	cd -
	echo "installing pypy"
	yum install -y pypy pypy-devel geos-devel
	echo "[ - Repository pypy version $(pypy --version) ]"
	pip install pip --upgrade
	pypy -m ensurepip
	echo "[ - Installing repo ]"
	wget https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-5.10.0-linux_x86_64-portable.tar.bz2 -O pypy.tar.bz2 &> /dev/null
	tar jxf pypy.tar.bz2 && rm -f pypy.tar.bz2
	echo "[ - Downloaded pypy version $(./pypy/bin/pypy --version) ]"
	virtualenv .envpypy --python="$(pwd)/pypy/bin/pypy"
	source .envpypy/bin/activate
	pypy -m ensurepip
	python -m pip install -r requirements.txt
	py.test
	deactivate
	echo "[ - Remember to enable the virtualenv with 'source .envpypy/bin/activate' ]"
else
    echo "[ - Sorry, at the moment, the installation script only supports ubuntu systems, preferably Ubuntu 16.04 ]"
    exit
fi