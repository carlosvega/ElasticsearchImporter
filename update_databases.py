import urllib3, logging, os
from six import iteritems

def update_tor_databases(path='db'):
	http = urllib3.PoolManager()
	db_urls = {
		'Tor_query_EXPORT.csv': 'http://torstatus.blutmagie.de/query_export.php/Tor_query_EXPORT.csv',
		'Tor_ip_list_ALL.csv' : 'http://torstatus.blutmagie.de/ip_list_all.php/Tor_ip_list_ALL.csv',
		'Tor_ip_list_EXIT.csv': 'http://torstatus.blutmagie.de/ip_list_exit.php/Tor_ip_list_EXIT.csv'}

	thislog = logging.getLogger(__name__)
	logging.basicConfig(format="[ %(asctime)s %(levelname)s %(threadName)s ] " + "%(message)s", level=logging.INFO)
	for filename, url in iteritems(db_urls):
		thislog.info('Updating {} from {}'.format(filename, url))
		r = http.request('GET', url)
		f = open(os.path.join(path, filename), 'wb')
		f.write(r.data)
		f.close()


update_tor_databases()