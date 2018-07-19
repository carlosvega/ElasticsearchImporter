from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import *
from elasticsearch_dsl.connections import connections
import pandas as pd
import time, json

#decorador para medir la duracion de la funcion
def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
        return result
    return timed

client = Elasticsearch()
db = 'speed_test'

def reset_index(es):
	settings = {
	    "settings": {
	        "number_of_shards": 3,
	        "number_of_replicas": 0
	    },
	    "mappings": {
	        "point": {
	        	'_source' : {'enabled' : False},
	        	'_all' : {'enabled' : False},
	            "properties": {
	                "time": {
	                    "type": "date"
	                },
	                "duration": {
	                	"type": "float"
	                }
	                ,
	                "user": {
	                	"type": "keyword"
	                }
	            }
	        }
	     }
	}
	es.indices.delete(index=db, ignore=[400, 404])
	es.indices.create(index=db, ignore=400, body=settings)

#generador de "points"
def point_generator(n=10**6):
	for i in range(n):
		yield {
			'_source': json.dumps({
				u'time': str(int(pd.Timestamp('now').value/1e6)),
				u'user': 'Carol',
				u'duration': "10.0"
			}),
			'_index': db,
			'_type' : 'point'
	    }

@timeit
def test_es(batch, p=False):
	if p:
		ret = helpers.parallel_bulk(client, point_generator(), chunk_size=batch, queue_size=6, thread_count=5)
	else:
		ret = helpers.streaming_bulk(client, point_generator(), chunk_size=batch)
	return sum([int(ok) for ok, _ in ret])

print('streaming_bulk')
reset_index(client)
test_es(10**2)
reset_index(client)
test_es(10**3)
reset_index(client)
test_es(10**4)

print('parallel_bulk')
reset_index(client)
test_es(10**2, p=True)
reset_index(client)
test_es(10**3, p=True)
reset_index(client)
test_es(10**4, p=True)