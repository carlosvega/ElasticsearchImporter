#!/bin/bash

function check_FTS5 {
	echo "[ - Checking if current sqlite3 installation supports FTS5... ]"
	python check_fts5.py &> /dev/null
	fts5_support=$?
	if [[ "$fts5_support" -gt 0 ]]
	then
		echo "[ - Congratulations, your current sqlite3 installation supports FTS5 ]"
	else
		echo "[ - Your current sqlite3 installation DOES NOT supports FTS5 ]"
	fi
}

function install_sqlite3 {
	echo "[ - Installing sqlite3... ]"
	echo "[ - Default sqlite3 version $(sqlite3 --version 2>&1) and python module $(python -c 'import sqlite3; print(sqlite3.sqlite_version)')]"
	wget "https://www.sqlite.org/src/tarball/sqlite.tar.gz?r=release" -O sqlite.tar.gz &> /dev/null && tar -xzvf sqlite.tar.gz && rm -f sqlite.tar.gz
	cd sqlite
	sudo ./configure --enable-fts5 && sudo make && sudo make install
	sudo echo "/usr/local/lib" > /etc/ld.so.conf.d/sqlite.conf && ldconfig
	cd ..
	echo "[ - Installed sqlite3 version $(sqlite3 --version 2>&1) and python module $(python -c 'import sqlite3; print(sqlite3.sqlite_version)')]"
}

check_FTS5

if command -v apt-get &> /dev/null ; then
    echo "[ - Debian/Ubuntu based system detected ]"
    if [[ "$fts5_support" -eq 0 ]]
    then
	    sudo apt-get update -y
		echo "[ - Removing sqlite3... ]"
		sudo apt-get remove -y sqlite3
		sudo apt-get purge -y sqlite3
		sudo apt-get install -y build-essential bzip2 git libbz2-dev libc6-dev libgdbm-dev libgeos-dev liblz-dev liblzma-dev libncurses5-dev libncursesw5-dev libreadline6 libreadline6-dev libsqlite3-dev libssl-dev lzma-dev python-dev python-pip python-software-properties python-virtualenv software-properties-common sqlite3 tcl tk-dev tk8.5-dev wget
		#install sqlite
		install_sqlite3
		sudo apt-get remove -y python python3 python-dev
		sudo apt-get install -y --reinstall python2.7 python3 python-dev
		sudo apt-get install -y build-essential bzip2 git libbz2-dev libc6-dev libgdbm-dev libgeos-dev liblz-dev liblzma-dev libncurses5-dev libncursesw5-dev libreadline6 libreadline6-dev libsqlite3-dev libssl-dev lzma-dev python-dev python-pip python-software-properties python-virtualenv software-properties-common sqlite3 tcl tk-dev tk8.5-dev wget
	fi
fi