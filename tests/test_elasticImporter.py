# -*- coding: utf-8 -*-

import pytest, sys

from elasticImporter import *

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

		
