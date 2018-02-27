# -*- coding: utf-8 -*-
# encoding=utf8
import sys
if sys.version_info < (3,0,0):
	reload(sys)
	sys.setdefaultencoding('utf8')
import elasticsearch_dsl
es_dsl_version = elasticsearch_dsl.__version__
from six import iteritems
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import *
from elasticsearch_dsl.connections import connections
import fileinput, logging, argparse, gc, codecs, json, math, hashlib, signal, os, traceback
from argparse import RawTextHelpFormatter
from datetime import datetime
from geodb import *

log = logging.getLogger(__name__)
logging.basicConfig(format="[ %(asctime)s %(levelname)s %(threadName)s ] " + "%(message)s", level=logging.INFO)
args = None
translate_cfg_property = None
es_version = None

if es_dsl_version >= (6, 0, 0):
	#no string object
	#http://elasticsearch-dsl.readthedocs.io/en/latest/Changelog.html?highlight=String#id2
	log.error('Please, use the versions provided in requirements.txt. Version >=6.0.0 of elasticsearch-dsl modules break backward compatibility.')
	sys.exit()

def parse_args():
	parser = argparse.ArgumentParser(description='This program indexes files to elasticsearch.\n', formatter_class=RawTextHelpFormatter)
	parser.add_argument('-i', '--input', dest='input', required=False, default='-', help='Input file. Default: stdin.')
	parser.add_argument('-c', '--cfg', dest='cfg', required=True, help='Configuration file.')
	parser.add_argument('-s', '--separator', dest='separator', required=False, default=';', help='File Separator. Default: ;')
	#override configuration stuff
	parser.add_argument('-x', '--index', dest='index', required=False, default=None, help='Elasticsearch index. It overrides the cfg JSON file values. Default: the index specified in the JSON file.')
	parser.add_argument('-t', '--type', dest='type', required=False, default=None, help='Elasticsearch document type. It overrides the cfg JSON file values. Default: the type specified in the JSON file.')
	#elastic connection stuff
	parser.add_argument('-n', '--node', dest='node', required=False, default='localhost', help='Elasticsearch node. Default: localhost')
	parser.add_argument('-p', '--port', dest='port', required=False, default=9200, help='Elasticsearch port. Default: 9200')
	parser.add_argument('-u', '--user', dest='user', required=False, default=None, help='Elasticsearch user if needed.')
	parser.add_argument('-P', '--password', dest='password', required=False, default='', help='Elasticsearch password if needed.')
	#extra stuff to consider when indexing
	parser.add_argument('--skip_first_line', dest='skip_first_line', default=False, action='store_true', help='Skips first line.')
	parser.add_argument('--dates_in_seconds', dest='dates_in_seconds', default=False, action='store_true', help='If true, assume dates are provided in seconds.')
	parser.add_argument('--refresh', dest='refresh', default=False, action='store_true', help='Refresh the index when finished.')
	parser.add_argument('--delete', dest='delete', default=False, action='store_true', help='Delete the index before process.')
	#meta stuff to consider when creating indices
	parser.add_argument('--replicas', dest='replicas', default=0, help='Number of replicas for the index if it does not exist. Default: 0')
	parser.add_argument('--shards', dest='shards', default=2, help='Number of shards for the index if it does not exist. Default: 2')
	parser.add_argument('--refresh_interval', dest='refresh_interval', default='60s', help='Refresh interval for the index if it does not exist. Default: 60s')
	#index sutff for elastic
	parser.add_argument('--bulk', dest='bulk', required=False, default=2000, help='Elasticsearch bulk size parameter. Default: 2000')
	parser.add_argument('--threads', dest='threads', required=False, default=5, help='Number of threads for the parallel bulk. Default: 5')
	parser.add_argument('--queue', dest='queue', required=False, default=5, help='Size of queue for the parallel bulk. Default: 6')
	parser.add_argument('--timeout', dest='timeout', required=False, default=600, help='Connection timeout in seconds. Default: 600')
	#internal stuff for the elastic API
	parser.add_argument('--debug', dest='debug', default=False, action='store_true', help='If true log level is set to DEBUG.')
	parser.add_argument('--no_progress', dest='noprogress', default=False, action='store_true', help='If true do not show progress.')
	parser.add_argument('--show_elastic_logger', dest='show_elastic_logger', default=False, action='store_true', help='If true show elastic logger at the same loglevel as the importer.')
	parser.add_argument('--raise_on_error', dest='raise_on_error', default=False, action='store_true', help='Raise BulkIndexError containing errors (as .errors) from the execution of the last chunk when some occur. By default we DO NOT raise.')
	parser.add_argument('--raise_on_exception', dest='raise_on_exception', default=False, action='store_true', help='By default we DO NOT propagate exceptions from call to bulk and just report the items that failed as failed. Use this option to propagate exceptions.')
	#stuff to avoid duplicates
	parser.add_argument('--md5_id', dest='md5_id', default=False, action='store_true', help='Uses the MD5 hash of the line as ID.')
	parser.add_argument('--md5_exclude', dest='md5_exclude', nargs = '*', required=False, default=[], help='List of column names to be excluded from the hash.')

	#stuff to add geographical information from data fields
	parser.add_argument('--geo_precission', dest='geo_precission', default=None, help='If set, geographical information will be added to the indexed documents. Possible values: country_level, multilevel, IP. If country_level is used in the geo_precission parameter, a column must be provided with either the country_code with 2 letters (ISO 3166-1 alpha-2) or the country_name in the format of the countries.csv file of the repository, for better results use country_code. If multilevel is set in the geo_precission option, then, a column or list of columns must be provided with either the country_code, region_name, city_name, or zip_code. If IP is set in the geo_precission option, then a column name containing IP addresses must be provided.')

	parser.add_argument('--geo_column_country_code', dest='geo_column_country_code', default=None, help='Column name containing country codes with 2 letters (ISO 3166-1 alpha-2). Used if geo_precission is set to either country_level or multilevel.')
	parser.add_argument('--geo_column_country_name', dest='geo_column_country_name', default=None, help='Column name containing country names. Used if geo_precission is set to either country_level.')
	parser.add_argument('--geo_column_region_name', dest='geo_column_region_name', default=None, help='Column name containing region names. Used if geo_precission is set to multilevel.')
	parser.add_argument('--geo_column_place_name', dest='geo_column_place_name', default=None, help='Column name containing place names. Used if geo_precission is set to multilevel.')
	parser.add_argument('--geo_column_zip_code', dest='geo_column_zip_code', default=None, help='Column name containing zip codes. Used if geo_precission is set to multilevel.')
	parser.add_argument('--geo_column_ip', dest='geo_column_ip', default=None, help='Column name containing IP addresses. Used if geo_precission is set to IP.')
	parser.add_argument('--geo_int_ip', dest='geo_int_ip', default=False, help='Set if the provided IP addresses are integer numbers.')

	args = parser.parse_args()

	args.geo_precission = args.geo_precission.lower() if args.geo_precission is not None else args.geo_precission
	if args.geo_precission not in ['ip', 'multilevel', 'country_level', None]:
		log.error("Please, provide a valid --geo_precission option {'ip', 'multilevel', 'country_level'}.")
		sys.exit(-1)

	args.geo_fields = {}
	if args.geo_precission == 'ip':
		if args.geo_column_ip is not None:
			args.geo_fields['ip'] = args.geo_column_ip
	elif args.geo_precission == 'multilevel':
		if args.geo_column_country_code is not None:
			args.geo_fields['country_code'] = args.geo_column_country_code
		if args.geo_column_country_name is not None:
			args.geo_fields['country_name'] = args.geo_column_country_name
		if args.geo_column_region_name is not None:
			args.geo_fields['region_name'] = args.geo_column_region_name
		if args.geo_column_place_name is not None:
			args.geo_fields['place_name'] = args.geo_column_place_name
		if args.geo_column_zip_code is not None:
			args.geo_fields['zip_code'] = args.geo_column_zip_code
	elif args.geo_precission == 'country_level':
		if args.geo_column_country_code is not None:
			args.geo_fields['country_code'] = args.geo_column_country_code
		if args.geo_column_country_name is not None:
			args.geo_fields['country_name'] = args.geo_column_country_name
	if args.geo_precission is not None and len(args.geo_fields) == 0:
		log.error('Please provide the --geo_column options')
		sys.exit(-1)

	args.geodb = load_geo_database(args.geo_precission)

	return args

#SYS STUFF
def get_script_path():
	return os.path.dirname(os.path.realpath(sys.argv[0]))

#GEO LOCATION STUFF
def get_geodata_field(level):
	"""Creates a geodata field for the DocType considering the following format.

	Format for Country Level geolocalization:

	 {'country_code': 'US',
	  'country_name': 'UNITED STATES',
 	  'location': '37.09024,-95.712891',
 	  'representative_point': '37.09024,-95.712891'}

	Format for Multilevel geolocalization:

	{'accuracy': 4.0,
	 'admin_code1': 'DC',
	 'admin_code2': '001',
	 'admin_code3': '',
	 'admin_name1': 'DISTRICT OF COLUMBIA',
	 'admin_name2': 'DISTRICT OF COLUMBIA',
	 'admin_name3': '',
	 'country_code': 'US',
	 'country_name': None, // always None in Multilevel geolocalization
	 'location': '38.9122,-77.0177',
	 'place_name': 'WASHINGTON',
	 'representative_point': '38.8959,-77.0211',
	 'zip_code': '20001'}

	Format for IP Level geolocalization:

	{'country_code': 'US',
	 'country_name': 'UNITED STATES',
	 'location': '37.44188,-122.14302',
	 'place_name': 'PALO ALTO',
	 'region_name': 'CALIFORNIA',
	 'representative_point': '37.57259,-92.932405',
	 'zip_code': '94301'}

	The three formats match in location, representative_point, country_code

	:return: A geodata field.
	"""
	#
	extra_geo_fields = {}

	if level == 'country_level':
		pass
	if level == 'multilevel':
		extra_geo_fields['geo_accuracy'] = translate_cfg_property('float')
		extra_geo_fields['geo_admin_code2'] = translate_cfg_property('keyword')
		extra_geo_fields['geo_admin_code3'] = translate_cfg_property('keyword')
		extra_geo_fields['geo_admin_name1'] = translate_cfg_property('keyword')
		extra_geo_fields['geo_admin_name2'] = translate_cfg_property('keyword')
		extra_geo_fields['geo_admin_name3'] = translate_cfg_property('keyword')
		extra_geo_fields['geo_place_name'] = translate_cfg_property('keyword')
		extra_geo_fields['geo_zip_code'] = translate_cfg_property('keyword')
	if level == 'ip':
		extra_geo_fields['geo_place_name'] = translate_cfg_property('keyword')
		extra_geo_fields['geo_region_name'] = translate_cfg_property('keyword')
		extra_geo_fields['geo_zip_code'] = translate_cfg_property('keyword')

	extra_geo_fields['geo_country_code'] = translate_cfg_property('keyword')
	extra_geo_fields['geo_country_name'] = translate_cfg_property('keyword')
	extra_geo_fields['geo_location'] = translate_cfg_property('geopoint')
	extra_geo_fields['geo_representative_point'] = translate_cfg_property('geopoint')

	return extra_geo_fields

def load_geo_database(level):
	path = get_script_path()
	if level == 'country_level':
		return CountryLevel_GeoDB('db0', '{}/db/countries.csv'.format(path), '{}/db/geodb0.db'.format(path), update=False)
	if level == 'multilevel':
		return ZIPLevel_GeoDB('{}/db/multilevel.db'.format(path), '{}/db/create_zip_db.sql.gz'.format(path), update=False)
	if level == 'ip':
		return ZIP_GeoIPDB('db9', '{}/db/IP2LOCATION-LITE-DB9.CSV.gz'.format(path), '{}/db/geodb9.db'.format(path), update=False)
	return None

#END OF GEO LOCATION STUFF

def translate_cfg_property_2x(v):
	if v == 'date':
		return Date()
	elif v == 'text':
		return String()
	elif v == 'keyword':
		return String(index="not_analyzed")
	elif v == 'integer':
		return Integer()
	elif v == 'long':
		return Long()
	elif v == 'float':
		return Float()
	elif v == 'geopoint':
		return GeoPoint()
	elif v == 'ip':
		return Ip()

def translate_cfg_property_std(v):
	if v == 'date':
		return Date()
	elif v == 'text':
		return Text()
	elif v == 'keyword':
		return Keyword()
	elif v == 'integer':
		return Integer()
	elif v == 'long':
		return Long()
	elif v == 'float':
		return Float()
	elif v == 'geopoint':
		return GeoPoint()
	elif v == 'ip':
		return Ip()

def create_doc_class(cfg, doc_type, geo):
	#create class
	dicc = {}
	for k, v in cfg['properties'].items():
		dicc[k] = translate_cfg_property(v)

	if geo is not None:
		extra_geo_fields = get_geodata_field(geo)
		for key, value in iteritems(extra_geo_fields):
			dicc[key] = value

	DocClass = type(doc_type, (DocType,), dicc)
	return DocClass

def is_nan_or_inf(value):
	if math.isinf(value) or math.isnan(value):
		log.debug('Nan or inf encountered in value: |{}|.'.format(value))
		return True
	else:
		return False

numeric_properties = set(('integer', 'long', 'date', 'float'))
def parse_property(str_value, t, args):
	try:
		if t in numeric_properties:
			if str_value == '':
				return None
			float_value = float(str_value)
			if is_nan_or_inf(float_value):
				return None
		if t == 'integer':
			return int(float_value)
		if t == 'long':
			return long(float_value)
		elif t == 'date':
			return int(float_value*1000) if args.dates_in_seconds else int(float_value)
		elif t == 'float':
			return float_value
		else: # t == 'text' or t == 'keyword' or t == 'ip' or t == 'geopoint':
			return str_value
	except ValueError:
		log.warning('ValueError processing value |{}| of type |{}| ignoring this field.'.format(str_value, t))
		return None
	except TypeError:
		log.warning('TypeError processing value |{}| of type |{}| ignoring this field.'.format(str_value, t))
		return None

def input_generator(cfg, index, doc_type, args):
	properties = cfg['properties']
	fields = cfg['order_in_file']
	n_fields = len(cfg['order_in_file'])
	try:
		if args.input != '-':
			f = codecs.open(args.input, buffering=1, encoding='utf-8', errors='ignore')
		else:
			f = sys.stdin
	except IOError as e:
		log.error('Error with the input file |{}|, Details: {}.'.format(args.input, sys.exc_info()[0]))
		return

	ctr = 0

	try:

		for line in f:
			try:
				if ctr == 0 and args.skip_first_line:
					continue
				ctr+=1
				sline = line.rstrip().split(args.separator)
				dicc = {fields[i]: parse_property(value, properties[fields[i]], args) for i, value in enumerate(sline)}

				if args.geo_precission is not None:
					if args.geo_precission == 'ip':
						geo_value = dicc.get(args.geo_column_ip, None)
						geo_data = args.geodb.get_geodata('ip', geo_value, str_ip=(not args.geo_int_ip))
					else:
						geo_columns = []
						geo_values = []
						for db_column, text_column in iteritems(args.geo_fields):
							geo_value = dicc.get(text_column, None)
							if geo_value is not None:
								geo_columns.append(db_column)
								geo_values.append(geo_value.upper())
						geo_data = args.geodb.get_geodata(geo_columns, geo_values)
					if geo_data is not None:
						for gkey, gvalue in iteritems(geo_data):
							dicc['geo_'+gkey] = gvalue

				#dicc = {k : dicc[k] for k in dicc if dicc[k] is not None} #remove nones
				a = {
					'_source' : dicc,
					'_index'  : index,
					'_type'   : doc_type
				}

				if args.md5_id:
					md5_dicc = {}
					for idx, field in enumerate(fields):
						if field not in args.md5_exclude:
							md5_dicc[field] = dicc[field]
					a['_id'] = hashlib.md5(json.dumps(md5_dicc)).hexdigest()
				yield a

			except ValueError as e:
				log.warning('Error processing line |{}| ({}). Ignoring line.'.format(line, ctr))
				continue
			except Exception as e:
				log.warning('Error processing line |{}| ({}). Ignoring line. Details {}'.format(line, ctr, sys.exc_info()[0]))
				traceback.print_exc(file=sys.stderr)
				continue
	except UnicodeDecodeError as e:
		log.warning('UnicodeDecodeError processing the line after |{}| ({})'.format(line, ctr, sys.exc_info()[0]))
		traceback.print_exc(file=sys.stderr)
		return

if __name__ == '__main__':
	#load parameters
	args = parse_args()

	pid = os.getpid()
	def signal_handler(signal, frame):
			log.error('You pressed Ctrl+C! Aborting execution.')
			os.kill(pid, 9)

	signal.signal(signal.SIGINT, signal_handler)

	#set up loggers
	if not args.show_elastic_logger:
		for _ in ("elasticsearch", "urllib3"):
			logging.getLogger(_).setLevel(logging.CRITICAL)

	loggers = [log, logging.getLogger('geodb')]
	loglevel = logging.DEBUG if args.debug else logging.INFO
	logging.basicConfig(format="[ %(asctime)s %(levelname)s %(threadName)s ] " + "%(message)s", level=loglevel)
	#logging.basicConfig(format='%(asctime)s %(message)s', level=loglevel)

	for logger in loggers:
		logger.setLevel(loglevel)

	if args.user is None:
		es = Elasticsearch(args.node, timeout=args.timeout, port=args.port)
	else:
		es = Elasticsearch(args.node, timeout=args.timeout, port=args.port, http_auth=(args.user, args.password))
	full_version = es.info()['version']['number']
	es_version = int(full_version.split('.')[0])

	if es_version == 1:
		log.error('Elasticsearch version 1.x is not supported.')

	log.info('Using elasticsearch version {}'.format(full_version))

	translate_cfg_property = translate_cfg_property_2x if es_version == 2 else translate_cfg_property_std

	#load cfg file
	cfg = json.load(open(args.cfg))
	index = cfg['meta']['index'] if args.index is None else args.index
	doc_type = str(cfg['meta']['type']) if args.type is None else args.type
	#create class from the cfg
	#this class is used to initialize the mapping
	DocClass = create_doc_class(cfg, doc_type, args.geo_precission)
	#connection to elasticsearch
	if args.user is None:
		connections.create_connection(hosts=[args.node], timeout=args.timeout, port=args.port) #connection for api
	else:
		connections.create_connection(hosts=[args.node], timeout=args.timeout, port=args.port, http_auth=(args.user, args.password)) #connection for api

	#delete before doing anything else
	if args.delete:
		log.warning('Deleting index {} whether it exists or not...'.format(index))
		es.indices.delete(index=index, ignore=[400, 404])

	#initialize mapping
	index_obj = Index(index, using=es)
	if not index_obj.exists():
		index_obj.settings(
			number_of_replicas=args.replicas,
			number_of_shards=args.shards,
			refresh_interval=args.refresh_interval
		)
		index_obj.save()
	DocClass.init(index=index, using=es)
	#create the file iterator
	documents = input_generator(cfg, index, doc_type, args)
	ret = helpers.parallel_bulk(es, documents, raise_on_exception=args.raise_on_exception, thread_count=args.threads, queue_size=args.queue, chunk_size=args.bulk, raise_on_error=args.raise_on_error)
	failed_items = []
	failed = 0; success = 0; abs_ctr=0
	for ok, item in ret:
		abs_ctr+=1
		#STATS
		if ok:
			success+=1
		else:
			failed+=1
			failed_items.append(abs_ctr)
		#PROGRESS
		if (success+failed)%10000 == 0 and not args.noprogress:
			log.info('Success: {0}, Failed: {1}'.format(success, failed))

	log.info('Success: {0}, Failed: {1}'.format(success, failed))

	if failed > 0:
		log.error('There were some errors during the process: Success: {0}, Failed: {1}'.format(success, failed))
		log.error('These were the errors in lines: {}'.format(failed_items))

	if args.refresh:
		es.indices.refresh(index=index)