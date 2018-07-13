# -*- coding: utf-8 -*-

import sys, os, py, pytest
import pandas as pd
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

if sys.version_info < (3,0,0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	long = int

from geodb import *
from torinfo import *

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

@pytest.fixture(scope='session')
def sessiondir(request):
	"""Temporal session directory"""
	d = py.path.local.mkdtemp()
	request.addfinalizer(lambda: d.remove(rec=1)) #execute after finishing tests

	return d


#TOR

@pytest.fixture(scope='session')
def torinfo_db(sessiondir, script_path):
	db = sessiondir.join('db')
	if not db.exists():
		db.mkdir()
	path = str(sessiondir)
	return TORinfo('{}/db/Tor_ip_list_EXIT.csv'.format(script_path), '{}/db/Tor_ip_list_ALL.csv'.format(script_path))

@pytest.fixture(scope='session')
def tor_exit_nodes(sessiondir, script_path):
	df = pd.read_csv('{}/db/Tor_query_EXPORT.csv'.format(script_path))
	exit_nodes = df['Flag - Exit'] == 1
	return df[exit_nodes][u'IP Address'].tolist()

@pytest.fixture(scope='session')
def tor_non_exit_nodes(sessiondir, script_path):
	df = pd.read_csv('{}/db/Tor_query_EXPORT.csv'.format(script_path))
	non_exit_nodes = df['Flag - Exit'] == 0
	return df[non_exit_nodes][u'IP Address'].tolist()


# GEO DB


@pytest.fixture(scope='session')
def country_level_db(sessiondir, script_path):
	db = sessiondir.join('db')
	if not db.exists():
		db.mkdir()
	path = str(sessiondir)
	return CountryLevel_GeoDB('db0', '{}/db/countries.csv'.format(script_path), '{}/db/geodb0.db'.format(path), update=False)

@pytest.fixture(scope='session')
def multilevel_db(sessiondir, script_path):
	db = sessiondir.join('db')
	if not db.exists():
		db.mkdir()
	path = str(sessiondir)
	return ZIPLevel_GeoDB('geoinfo', '{}/db/create_zip_db.sql.gz'.format(script_path), '{}/db/multilevel.db'.format(path), update=False)

@pytest.fixture(scope='session')
def ip_level_db(sessiondir, script_path):
	db = sessiondir.join('db')
	if not db.exists():
		db.mkdir()
	path = str(sessiondir)
	return ZIP_GeoIPDB('db9', '{}/db/IP2LOCATION-LITE-DB9.CSV.gz'.format(script_path), '{}/db/geodb9.db'.format(path), update=False, db_folder=path)