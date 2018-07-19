from influxdb import InfluxDBClient
import pandas as pd
import time

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


client = InfluxDBClient(host='localhost', port=8086)
db = 'speed_test'

def reset_database(client):
	client.drop_database(db) #borrar database
	client.create_database(db) #crear database

#generador de "points"
def point_generator(n=10**6):
	for i in range(n):
		yield {
	        "measurement": "brushEvents",
	        "tags": {
	            "user": "Carol"
	        },
	        "time": pd.Timestamp('now').value,
	        "fields": {
	            "duration": 10.0
	        }
	    }

def line_generator(n=10**6):
	for i in range(n):
		yield 'brushEvents,user=Carol duration=10.0 {}'.format(pd.Timestamp('now').value) 

@timeit
def test_influx(batch):
	a = [];
	for i in point_generator():
		a.append(i);
		if len(a) >= batch:
			client.write_points(a, database=db)
			a=[]
	if len(a) >= 0:
		client.write_points(a, database=db)


@timeit
def test_influx_line(batch):
	a = [];
	for i in line_generator():
		a.append(i);
		if len(a) >= batch:
			client.write_points(a, database=db, protocol='line')
			a=[]
	if len(a) >= 0:
		client.write_points(a, database=db, protocol='line')


print('json protocol')
reset_database(client)
test_influx(10**2)
reset_database(client)
test_influx(10**3)
reset_database(client)
test_influx(10**4)

print('line protocol')
reset_database(client)
test_influx_line(10**2)
reset_database(client)
test_influx_line(10**3)
reset_database(client)
test_influx_line(10**4)