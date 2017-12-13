from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import *
from elasticsearch_dsl.connections import connections
import fileinput, sys, logging, argparse, gc, codecs, json
from argparse import RawTextHelpFormatter
from datetime import datetime

def parse_args():
	parser = argparse.ArgumentParser(description='This program indexes file with certificate details to an elasticsearch cluster.\n', formatter_class=RawTextHelpFormatter)
	parser.add_argument('-i', '--input', dest='input', required=False, default='-', help='Input file. Default: stdin.')
	parser.add_argument('-c', '--cfg', dest='cfg', required=True, help='Configuration file.')
	parser.add_argument('-s', '--separator', dest='separator', required=False, default=';', help='File Separator. Default: ;')
	parser.add_argument('-n', '--node', dest='node', required=False, default='localhost', help='Elasticsearch node. Default: localhost')
	parser.add_argument('--bulk', dest='bulk', required=False, default=2000, help='Elasticsearch bulk size parameter. Default: 2000')
	parser.add_argument('--threads', dest='threads', required=False, default=5, help='Number of threads for the parallel bulk. Default: 5')
	parser.add_argument('--queue', dest='queue', required=False, default=5, help='Size of queue for the parallel bulk. Default: 6')
	parser.add_argument('--timeout', dest='timeout', required=False, default=600, help='Connection timeout. Default: 600')
	parser.add_argument('--skip_first_line', dest='skip_first_line', default=False, action='store_true', help='Skips first line.')
	parser.add_argument('--refresh', dest='refresh', default=False, action='store_true', help='Refresh the index when finished.')
	args = parser.parse_args()
	return args

def translate_cfg_property(v):
	if v == 'date':
		return Date()
	elif v == 'text':
		return Text()
	elif v == 'keyword':
		return Keyword()
	elif v == 'integer':
		return Integer()
	elif v == 'float':
		return Float()
	elif v == 'geopoint':
		return GeoPoint()
	elif v == 'ip':
		return Ip()

def create_doc_class(cfg, doc_type):
	#create class
	print cfg['properties'].items()
	dicc = {}
	for k, v in cfg['properties'].items():
		dicc[k] = translate_cfg_property(v)
	DocClass = type(doc_type, (DocType,), dicc)
	return DocClass

def parse_property(value, t):
	if t == 'date' or t == 'integer':
		return int(value)
	elif t == 'float':
		return float(value)
	else: # t == 'text' or t == 'keyword' or t == 'ip' or t == 'geopoint':
		return value

def input_generator(cfg, index, doc_type, args):
	properties = cfg['properties']
	fields = cfg['order_in_file']
	n_fields = len(cfg['order_in_file'])
	if args.input != '-':
		f = codecs.open(args.input, buffering=1, encoding='latin-1')
	else:
		f = sys.stdin

	ctr = 0
	for line in f:
		try:
			if ctr == 0 and args.skip_first_line:
				continue
			ctr+=1
			sline = line.rstrip().split(args.separator)
			dicc = {fields[i]: parse_property(value, properties[fields[i]]) for i, value in enumerate(sline)}
			a = {
				'_source' : dicc,
				'_index'  : index,
				'_type'   : doc_type
			}
			yield a
		except Exception as e:
			logging.warn('Error processing line |{}| ({}). Ignoring line. Details {}'.format(line, ctr, sys.exc_info()[0]))
			continue

if __name__ == '__main__':
	for _ in ("elasticsearch", "urllib3"):
		logging.getLogger(_).setLevel(logging.CRITICAL)

	logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
	#load parameters
	args = parse_args()
	#load cfg file
	cfg = json.load(open(args.cfg))
	index = cfg['meta']['index']
	doc_type = str(cfg['meta']['type'])
	#create class from the cfg
	#this class is used to initialize the mapping
	DocClass = create_doc_class(cfg, doc_type)
	#connection to elasticsearch
	es = Elasticsearch(args.node, timeout=args.timeout)
	connections.create_connection(hosts=[args.node], timeout=args.timeout) #connection for api
	#initialize mapping
	DocClass.init(index=index, using=es)
	#create the file iterator
	documents = input_generator(cfg, index, doc_type, args)
	ret = helpers.parallel_bulk(es, documents, raise_on_exception=False, thread_count=args.threads, queue_size=args.queue, chunk_size=args.bulk)

	failed = 0; success = 0;
	for ok, item in ret:
		#STATS
		if ok:
			success+=1	
		else:
			failed+=1
		#PROGRESS
		if (success+failed)%100000 == 0:
			logging.info('Success: {0}, Failed: {1}'.format(success, failed))

	logging.info('Success: {0}, Failed: {1}'.format(success, failed))

	if failed > 0:
		logging.error('There were some errors during the process: Success: {0}, Failed: {1}'.format(success, failed))

	if args.refresh:
		es.indices.refresh(index=index)