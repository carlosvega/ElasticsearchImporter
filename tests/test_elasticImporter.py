# -*- coding: utf-8 -*-

import pytest, sys

from elasticImporter import *
from argparse import Namespace

class objectview(object):
    def __init__(self, d):
        self.__dict__ = d

class Test_elasticImporter(object):
	def test_nan_or_inf(self):
		values  = ['+inf', '-inf', 'inf', 0, 0.2, 2e2, 5**2, 'nan', 'NaN', float("inf")-float("inf")]
		results = [True, True, True, False, False, False, False, True, True, True]
		ops = zip(values, results)
		for value, result in ops:
			assert is_nan_or_inf(float(value)) == result
	
	def test_parse_property(self):
		args = {}
		args['dates_in_seconds'] = True
		args = objectview(args)
		values = [('', 'float', None),
		('+inf', 'float', None),
		('inf', 'integer', None),
		('1.1', 'float', 1.1),
		('1', "long", long(1)),
		('1', 'integer', int(1)),
		('1', 'string', '1'),
		('1519995883.3099031', 'date', 1519995883309)]
		for v, t, r in values:
			assert parse_property(v, t, args) == r

	def test_no_all_no_source_args(self):
		cfg = {u'order_in_file': [u'person', u'size', u'city'], u'meta': {u'index': u'example', u'type': u'my_doc'}, u'properties': {u'person': u'keyword', u'city': u'keyword', u'size': u'float'}}
		doc = 'my_doc'
		args = Namespace(bulk=2000, cfg='example.cfg', date_fields=[], dates_in_seconds=False, debug=False, deflate_compression=False, delete=True, extra_data=None, geo_column_country_code=None, geo_column_country_name=None, geo_column_ip=None, geo_column_place_name=None, geo_column_region_name=None, geo_column_zip_code=None, geo_fields={}, geo_int_ip=False, geo_precission=None, geodb=None, index=None, input='example.csv', md5_exclude=[], md5_id=False, no_all=True, no_source=True, node='localhost', noprogress=False, password='', port=9200, queue=6, raise_on_error=False, raise_on_exception=False, refresh=True, refresh_interval='60s', regenerate_databases=[], replicas=0, separator=',', shards=2, show_elastic_logger=False, skip_first_line=False, test_processing_speed=False, threads=5, timeout=600, tor_info=None, tor_info_from=False, tor_int_ip=False, type=None, typed_iterator=False, user=None, utf8=False)
		doc_class = create_doc_class(cfg, doc, args)
		assert doc_class.__dict__[doc] == {'_all': {'enabled': False}, '_source': {'enabled': False}}