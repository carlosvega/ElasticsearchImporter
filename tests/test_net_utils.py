# -*- coding: utf-8 -*-

import pytest


from net_utils import *

class Test_netutils(object):
	def test_int2ip(self, sample_ips):
		for ip, int_ip, mask in sample_ips:
			assert int2ip(int_ip) == ip 

	def test_ip2int(self, sample_ips):
		for ip, int_ip, mask in sample_ips:
			assert ip2int(ip) == int_ip

	def test_in_net(self, sample_ips, bad_sample_ips):
		for ip, int_ip, mask in sample_ips:
			assert in_net(int_ip, mask) == True

		for ip, int_ip, mask in bad_sample_ips:
			assert in_net(int_ip, mask) == False
