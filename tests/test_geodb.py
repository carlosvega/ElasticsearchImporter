# -*- coding: utf-8 -*-

import pytest

from geodb import *

class Test_geodb(object):
	def test_country_level_db(self, country_level_db):
		result    = country_level_db.get_geodata('country_code', 'ES')
		check_val = {'country_code': 'ES', 'country_name': 'SPAIN',  'location': '40.463667,-3.74922', 'representative_point': '40.463667,-3.74922'}
		assert result == check_val
		result = country_level_db.get_geodata('country_name', 'SPAIN')
		check_val = {'country_code': 'ES', 'country_name': 'SPAIN',  'location': '40.463667,-3.74922', 'representative_point': '40.463667,-3.74922'}
		assert result == check_val
		assert country_level_db.get_geodata('country_name', 'POTATO') is None


	#MULTI LEVEL
	@pytest.mark.skipif(ZIPLevel_GeoDB.check_FTS5_support() == False, reason='FTS5 extension not available in your sqlite3 installation. py-sqlite3 version: {}. sqlite3 version: {}. Please, recompile or reinstall sqlite3 modules with FTS5 support.'.format(sqlite3.version, sqlite3.sqlite_version))
	def test_multilevel_db(self, sessiondir, script_path):
		db = sessiondir.join('db')
		if not db.exists():
			db.mkdir()
		path = str(sessiondir)
		multilevel_db = ZIPLevel_GeoDB('{}/db/multilevel.db'.format(path), '{}/db/create_zip_db.sql.gz'.format(script_path), update=False)
		#TO DO
		pass

	@pytest.mark.skip(reason='Disabled when testing the tests. LOL.')
	def test_FTS5_support(self):
		assert ZIPLevel_GeoDB.check_FTS5_support() == True, 'FTS5 extension not available in your sqlite3 installation. py-sqlite3 version: {}. sqlite3 version: {}. Please, recompile or reinstall sqlite3 modules with FTS5 support.'.format(sqlite3.version, sqlite3.sqlite_version)


	#IP LEVEL
	def test_ip_level_db(self, ip_level_db):
		result = ip_level_db.get_geodata('ip', '8.8.8.8')
		check_val = {'country_code': 'US', 'country_name': 'UNITED STATES', 'location': '37.405992,-122.078515', 'place_name': 'MOUNTAIN VIEW', 'region_name': 'CALIFORNIA', 'representative_point': '37.405992,-122.078515', 'zip_code': '94043'}
		assert result == check_val
		result = ip_level_db.get_geodata('ip', 134744072, str_ip=False)
		check_val = {'country_code': 'US', 'country_name': 'UNITED STATES', 'location': '37.405992,-122.078515', 'place_name': 'MOUNTAIN VIEW', 'region_name': 'CALIFORNIA', 'representative_point': '37.405992,-122.078515', 'zip_code': '94043'}
		assert result == check_val



