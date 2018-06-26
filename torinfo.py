# -*- coding: utf-8 -*-
from net_utils import *
import logging, sys

class TORinfo(object):
	"""A class to get information from an IP
		server from the ToR network
	"""

	def __init__(self, tor_exit_nodes_file_path, tor_server_list_file_path):
		"""Creates a TORinfo object

		:param str tor_exit_nodes_file_path: Name of the table in the database.
		:param str tor_server_list_file_path: Path of the csv file with the data to populate the database.

		:return: A TORinfo object.
		"""
		self.tor_exit_nodes_file_path  = tor_exit_nodes_file_path
		self.tor_server_list_file_path = tor_server_list_file_path
		self.tor_exit_nodes  = self._load_ip_set(tor_exit_nodes_file_path)
		self.tor_servers	 = self._load_ip_set(tor_server_list_file_path)
		self.should_be_empty = self.tor_exit_nodes - self.tor_servers
		if len(self.should_be_empty) > 0:
			logging.info('Some exit nodes are not in the tor server list.')

	def _load_ip_set(self, path):
		logging.info('Creating set from file: {}.'.format(path))
		s = set()
		ctr = 0
		with open(path) as f:
			for line in f:
				ctr+=1
				try:
					ip = ip2int(line.rstrip())
					s.add(ip)
				except Exception as e:
					logging.warning('Error processing line |{}| ({}). Ignoring line. Details {}'.format(line, ctr, sys.exc_info()[0]))
					traceback.print_exc(file=sys.stderr)
					continue
		return s

	def isTorServer(self, ip, int_ip=True):
		if ip is None:
			return False
		if not int_ip:
			ip = ip2int(ip)
		return ip in self.tor_servers

	def isExitNode(self, ip, int_ip=True):
		if ip is None:
			return False
		if not int_ip:
			ip = ip2int(ip)
		return ip in self.tor_exit_nodes

	def getTorInfo(self, ip, int_ip=True):
		if ip is None:
			return 'Invalid IP'
		if not int_ip:
			ip = ip2int(ip)
		if self.isExitNode(ip):
			return 'TOR Exit Node'
		elif self.isTorServer(ip):
			return 'TOR Server'
		else:
			return 'None'
