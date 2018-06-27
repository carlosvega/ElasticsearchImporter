# -*- coding: utf-8 -*-

import pytest

from geodb import *
from debug_utils import *

@pytest.mark.skipif(get_available_memory() < 4000, reason='Not enough memory to test. Minimum 4GB to regenerate the databases.')
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
	def test_FTS5_support(self):
		assert ZIPLevel_GeoDB.check_FTS5_support() == True, 'FTS5 extension not available in your sqlite3 installation. py-sqlite3 version: {}. sqlite3 version: {}. Please, recompile or reinstall sqlite3 modules with FTS5 support.'.format(sqlite3.version, sqlite3.sqlite_version)

	@pytest.mark.skipif(ZIPLevel_GeoDB.check_FTS5_support() == False, reason='FTS5 extension not available in your sqlite3 installation. py-sqlite3 version: {}. sqlite3 version: {}. Please, recompile or reinstall sqlite3 modules with FTS5 support.'.format(sqlite3.version, sqlite3.sqlite_version))
	def test_multilevel_db(self, multilevel_db):
		result = multilevel_db.get_geodata(['place_name', 'admin_name1', 'country_code'], ['MADRID', 'MADRID', 'ES'])
		check_val = {'accuracy': 4.0, 'admin_code1': 'MD', 'admin_code2': 'M', 'admin_code3': '28079', 'admin_name1': 'MADRID', 'admin_name2': 'MADRID', 'admin_name3': 'MADRID', 'country_code': 'ES', 'country_name': None, 'location': '40.4165,-3.7026', 'place_name': 'MADRID', 'representative_point': '40.4165,-3.7026', 'zip_code': '28001'}
		assert result == check_val
		result = multilevel_db.get_geodata(['place_name', 'admin_name1', 'country_code'], ['madrid', 'madrid', 'es'])
		check_val = {'accuracy': 4.0, 'admin_code1': 'MD', 'admin_code2': 'M', 'admin_code3': '28079', 'admin_name1': 'MADRID', 'admin_name2': 'MADRID', 'admin_name3': 'MADRID', 'country_code': 'ES', 'country_name': None, 'location': '40.4165,-3.7026', 'place_name': 'MADRID', 'representative_point': '40.4165,-3.7026', 'zip_code': '28001'}
		assert result == check_val
		assert multilevel_db.get_geodata('country_name', 'spain') is None
		result = multilevel_db.get_geodata('country_code', 'FR')
		check_val = {'accuracy': 5.0, 'location': '48.8534,2.3488', 'representative_point': '47.0011,2.7465', 'admin_name1': 'ÎLE-DE-FRANCE', 'admin_name2': 'PARIS', 'admin_name3': 'PARIS', 'admin_code2': '75', 'admin_code3': '751', 'country_code': 'FR', 'admin_code1': '11', 'country_name': None, 'zip_code': '75000', 'place_name': 'PARIS'}
		assert result == check_val
		result = multilevel_db.get_geodata('', 'BILBAO')
		check_val = {'accuracy': 4.0, 'location': '43.2627,-2.9253', 'representative_point': '43.2627,-2.9253', 'admin_name1': 'PAIS VASCO', 'admin_name2': 'VIZCAYA', 'admin_name3': 'BILBAO', 'admin_code2': 'BI', 'admin_code3': '48020', 'country_code': 'ES', 'admin_code1': 'PV', 'country_name': None, 'zip_code': '48001', 'place_name': 'BILBAO'}
		assert result == check_val

	#IP LEVEL
	def test_ip_level_db(self, ip_level_db):
		result = ip_level_db.get_geodata('ip', '8.8.8.8')
		check_val = {'country_code': 'US', 'country_name': 'UNITED STATES', 'location': '37.405992,-122.078515', 'place_name': 'MOUNTAIN VIEW', 'region_name': 'CALIFORNIA', 'representative_point': '37.405992,-122.078515', 'zip_code': '94043'}
		assert result == check_val
		result = ip_level_db.get_geodata('ip', 134744072, str_ip=False)
		check_val = {'country_code': 'US', 'country_name': 'UNITED STATES', 'location': '37.405992,-122.078515', 'place_name': 'MOUNTAIN VIEW', 'region_name': 'CALIFORNIA', 'representative_point': '37.405992,-122.078515', 'zip_code': '94043'}
		assert result == check_val



