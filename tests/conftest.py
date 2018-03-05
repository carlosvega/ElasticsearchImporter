# -*- coding: utf-8 -*-

import sys, os, py, pytest
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

if sys.version_info < (3,0,0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	long = int

from geodb import *



#SYS STUFF
@pytest.fixture(scope = 'session')
def script_path():
	return os.path.dirname(os.path.abspath(__file__)) + '/../'

@pytest.fixture(scope = 'session')
def sample_ips():
	ips  = ['192.168.2.1', '83.112.12.2', '172.14.12.12', '65.43.115.255']
	ints = [3232236033, 1399852034, 2886601740, 1093366783]
	masks= ['192.168.2.0/24', '83.112.12.0/24', '172.14.12.0/24', '65.43.115.0/24']
	return zip(ips,ints,masks)

@pytest.fixture(scope = 'session')
def bad_sample_ips():
	ips  = ['192.168.2.1', '83.112.12.2', '172.14.12.12', '65.43.115.255']
	ints = [3232236033, 1399852034, 2886601740, 1093366783]
	masks= ['192.168.2.0/24', '83.112.12.0/24', '172.14.12.0/24', '65.43.115.0/24']
	return zip(ips,ints,masks[::-1])

# GEO DB

@pytest.fixture(scope='session')
def sessiondir(request):
		"""Temporal session directory"""
		d = py.path.local.mkdtemp()
		request.addfinalizer(lambda: d.remove(rec=1)) #execute after finishing tests

		return d

@pytest.fixture(scope='session')
def country_level_db(sessiondir, script_path):
	db = sessiondir.join('db')
	if not db.exists():
		db.mkdir() 
	path = str(sessiondir)
	return CountryLevel_GeoDB('db0', '{}/db/countries.csv'.format(script_path), '{}/db/geodb0.db'.format(path), update=False)

@pytest.fixture(scope='session')
def ip_level_db(sessiondir, script_path):
	db = sessiondir.join('db')
	if not db.exists():
		db.mkdir()
	path = str(sessiondir)
	return ZIP_GeoIPDB('db9', '{}/db/IP2LOCATION-LITE-DB9.CSV.gz'.format(script_path), '{}/db/geodb9.db'.format(path), update=False)