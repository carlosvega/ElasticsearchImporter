# -*- coding: utf-8 -*-

import pytest
from net_utils import *
from torinfo import *

class Test_torinfo(object):
	def test_none(self, torinfo_db):
		assert torinfo_db.getTorInfo('', int_ip=True) == 'Invalid IP'
		assert torinfo_db.getTorInfo('', int_ip=False) == 'Invalid IP'

	def test_exit_node_list(self, tor_exit_nodes, torinfo_db):
		exit_node_ip = tor_exit_nodes[0]
		print(exit_node_ip)
		assert torinfo_db.getTorInfo(exit_node_ip, int_ip=False) == 'TOR Exit Node'
		assert torinfo_db.getTorInfo(ip2int(exit_node_ip), int_ip=True) == 'TOR Exit Node'
		assert torinfo_db.getTorInfo(exit_node_ip, int_ip=True) == 'None'
		with pytest.raises(Exception) as e_info:
			torinfo_db.getTorInfo(ip2int(exit_node_ip), int_ip=False) == 'Node'

	def test_tor_node_list(self, tor_non_exit_nodes, torinfo_db):
		tor_node_ip = tor_non_exit_nodes[0]
		print(tor_node_ip)
		assert torinfo_db.getTorInfo(tor_node_ip, int_ip=False) == 'TOR Server'
		assert torinfo_db.getTorInfo(ip2int(tor_node_ip), int_ip=True) == 'TOR Server'
		assert torinfo_db.getTorInfo(tor_node_ip, int_ip=True) == 'None'
		with pytest.raises(Exception) as e_info:
			assert torinfo_db.getTorInfo(ip2int(tor_node_ip), int_ip=False) == 'None'
