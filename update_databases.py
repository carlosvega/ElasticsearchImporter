import urllib3, logging, os, zipfile, io, gzip
from six import iteritems
from debug_utils import log_rss_memory_usage

def update_tor_databases(path='db'):
	db_urls = {
		'Tor_query_EXPORT.csv': 'http://torstatus.blutmagie.de/query_export.php/Tor_query_EXPORT.csv',
		'Tor_ip_list_ALL.csv' : 'http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv',
		'Tor_ip_list_EXIT.csv': 'http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv'}

	http = urllib3.PoolManager()
	for filename, url in iteritems(db_urls):
		thislog.info('Updating {} from {}'.format(filename, url))
		r = http.request('GET', url)
		with open(os.path.join(path, filename), 'wb') as f:
			f.write(r.data)

def update_db9_database(path='db', filename='IP2LOCATION-LITE-DB9.CSV'):
	ip2location_token = 'dK4xUAjLVqSnFBLxGJdm1auTye5BwQYJB2gvDAhz0aWGMIdsrrPsBjm9xsL3iJMU'
	url = 'http://www.ip2location.com/download/?token={token}&file={db_code}'.format(token=ip2location_token, db_code='DB9LITE')
	http = urllib3.PoolManager()
	r = http.request('GET', url)
	z = zipfile.ZipFile(io.BytesIO(r.data))
	thislog.info('Updating {} from {}'.format(filename, url))
	with z.open(filename, 'r') as f:
		with gzip.open(os.path.join(path, '{}.gz'.format(filename)), 'w', compresslevel=9) as db9:
			for line in f:
				db9.write(line.upper())

thislog = logging.getLogger(__name__)
logging.basicConfig(format="[ %(asctime)s %(levelname)s %(threadName)s ] " + "%(message)s", level=logging.INFO)
update_tor_databases()
update_db9_database()
log_rss_memory_usage('Databases updated.')