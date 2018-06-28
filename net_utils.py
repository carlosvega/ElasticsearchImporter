import socket, struct

def in_net(ipint, net):
	#ipaddr = socket.inet_aton(ip)
	netaddr, netmask = net.split('/')
	netaddr = socket.inet_aton(netaddr)

	#ipint = struct.unpack("!I", ipaddr)[0]
	netint = struct.unpack("!I", netaddr)[0]
	maskint = (0xFFFFFFFF << (32 - int(netmask))) & 0xFFFFFFFF

	return ipint & maskint == netint

# http://stackoverflow.com/a/9591005
def ip2int(ip):
	"""Convert an IP in dot-decimal notation to int.
	:param ip: string.
	"""
	if not isinstance(ip, str) and not isinstance(ip, unicode):
		raise ValueError("ip must be str and is {0} instead".format(type(ip)))
	if isinstance(ip, unicode):
		ip = str(ip)
	packedIP = socket.inet_aton(ip)
	return struct.unpack("!I", packedIP)[0]

def int2ip(ip):
	"""Convert an IP in an 32bit int to a string in dot-decimal notation.
	:param ip: int
	"""
	if not isinstance(ip, int):
			raise ValueError("ip must be int and is {0} instead".format(type(ip)))
	return socket.inet_ntoa(struct.pack('!I', ip))

