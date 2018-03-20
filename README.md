# Elasticsearch Importer
Generic Elasticsearch Importer

## Options

| Option and Long option        | Description                                           |
|-------------------------------|-------------------------------------------------------|
|  -h, --help           | show this help message and exit|
|  -i INPUT, --input INPUT | Input file. Default: stdin.|
|  -c CFG, --cfg CFG |     Configuration file.|
|  -s SEPARATOR, --separator SEPARATOR |File Separator. Default: ;|
|  -x INDEX, --index INDEX | Elasticsearch index. It overrides the cfg JSON file values. Default: the index specified in the JSON file.|
|  -t TYPE, --type TYPE |  Elasticsearch document type. It overrides the cfg JSON file values. Default: the type specified in the JSON file.|
|  -n NODE, --node NODE |  Elasticsearch node. Default: localhost|
|  -p PORT, --port PORT |  Elasticsearch port. Default: 9200|
|  -u USER, --user USER |  Elasticsearch user if needed.|
|  -P PASSWORD, --password PASSWORD | Elasticsearch password if needed.|
|  --skip_first_line     | Skips first line.|
|  --dates_in_seconds    | If true, assume dates are provided in seconds.|
|  --refresh             | Refresh the index when finished.|
|  --delete              | Delete the index before process.|
|  --replicas REPLICAS |   Number of replicas for the index if it does not exist. Default: 0|
|  --shards SHARDS |       Number of shards for the index if it does not exist. Default: 2|
|  --refresh_interval REFRESH_INTERVAL | Refresh interval for the index if it does not exist. Default: 60s|
|  --bulk BULK |           Elasticsearch bulk size parameter. Default: 2000|
|  --threads THREADS |     Number of threads for the parallel bulk. Default: 5|
|  --queue QUEUE |         Size of queue for the parallel bulk. Default: 6|
|  --timeout TIMEOUT |     Connection timeout in seconds. Default: 600|
|  --debug               | If true log level is set to DEBUG.|
|  --no_progress         | If true do not show progress.|
|  --show_elastic_logger| If true show elastic logger at the same loglevel as the importer.|
|  --raise_on_error      | Raise BulkIndexError containing errors (as .errors) from the execution of the last chunk when some occur. By default we DO NOT raise.|
|  --raise_on_exception  | By default we DO NOT propagate exceptions from call to bulk and just report the items that failed as failed. Use this option to propagate exceptions.|
|  --md5_id              | Uses the MD5 hash of the line as ID.|
|  --md5_exclude [MD5_EXCLUDE [MD5_EXCLUDE ...]] | List of column names to be excluded from the hash.|
|  --geo_precission GEO_PRECISSION | If set, geographical information will be added to the indexed documents. Possible values: country_level, multilevel, IP. If country_level is used in the geo_precission parameter, a column must be provided with either the country_code with 2 letters (ISO 3166-1 alpha-2) or the country_name in the format of the countries.csv file of the repository, for better results use country_code. If multilevel is set in the geo_precission option, then, a column or list of columns must be provided with either the country_code, region_name, city_name, or zip_code. If IP is set in the geo_precission option, then a column name containing IP addresses must be provided.|
|  --geo_column_country_code GEO_COLUMN_COUNTRY_CODE | Column name containing country codes with 2 letters (ISO 3166-1 alpha-2). Used if geo_precission is set to either country_level or multilevel.|
|  --geo_column_country_name GEO_COLUMN_COUNTRY_NAME | Column name containing country names. Used if geo_precission is set to either country_level.|
|  --geo_column_region_name GEO_COLUMN_REGION_NAME | Column name containing region names. Used if geo_precission is set to multilevel.|
|  --geo_column_place_name GEO_COLUMN_PLACE_NAME | Column name containing place names. Used if geo_precission is set to multilevel.|
|  --geo_column_zip_code GEO_COLUMN_ZIP_CODE | Column name containing zip codes. Used if geo_precission is set to multilevel.|
|  --geo_column_ip GEO_COLUMN_IP | Column name containing IP addresses. Used if geo_precission is set to IP.|
|  --geo_int_ip GEO_INT_IP | Set if the provided IP addresses are integer numbers.|

## Configuration file format

In the [example.cfg](https://github.com/carlosvega/ElasticsearchImporter/blob/master/example.cfg) file all possible formats supported by the importer have been used. Nested fields are not supported yet because this tool is intended for formats readable line by line, but could be supported in the future based on syntax.

```JavaScript
{
	"meta" : {
		"index" : "patata",
		"type"  : "my_potato"
	},
	"properties" : {
		"timestamp" : "date",
		"geo" : "geopoint",
		"ip"  : "ip",
		"name" : "keyword",
		"description" : "text",
		"age" : "integer",
		"size" : "float"
	},
	"order_in_file" : ["timestamp", "geo", "ip", "name", "description", "age", "size"]

}
```

## Installation

```Bash
git clone git@github.com:carlosvega/ElasticsearchImporter.git ElasticsearchImporter
cd ElasticsearchImporter
bash install.bash
```

### Ubuntu Docker

```Bash
git clone git@github.com:carlosvega/ElasticsearchImporter.git ElasticsearchImporter
cd ElasticsearchImporter
docker build -f Dockerfile.ubuntu -t ubuntu_esimporter .
```

### CentOS Docker

```Bash
git clone git@github.com:carlosvega/ElasticsearchImporter.git ElasticsearchImporter
cd ElasticsearchImporter
docker build -f Dockerfile.centos -t centos_esimporter .
```

## Considerations

The tool works with elasticsearch 6.2.2 but uses elasticsearch-dsl module version >=5.0.0,<6.0.0 because version 6.x of this module breaks backwards compatibility.
The tool might not work with higher versions of elasticsearch than 6.2.2.

Python 2 does not handle very well the Ctrl+C interruption. Do Ctrl+Z, then jobs, and kill %1 (if the only job is the tool) to kill it.
PyPy sometimes handles it and sometimes not, but Python 3 seems to work without any issue.

## Performance

On a Intel(R) Core(TM) i7-7700 CPU @ 3.60GHz with 32GB of RAM using Elasticsearch 6.2.2  with a 4GB Heap.
Executing a 10 Million lines test:

![Performance Comparison of the tool](https://github.com/carlosvega/ElasticsearchImporter/raw/master/es_importer_bench.png)

### Python 3.5.2

```Bash
yes '1509750000000;52.5720661, 52.5720661;192.168.1.1;PotatoFriend;This is a potato and it is your friend;20;201.1' | head -10000000 | pv -l | time python3 elasticImporter.py -c example.cfg
```

pv command reports: 37.4 K lines/s
tool speed reports: 37.7 K lines/s

### Python 2.7.12

```Bash
yes '1509750000000;52.5720661, 52.5720661;192.168.1.1;PotatoFriend;This is a potato and it is your friend;20;201.1' | head -10000000 | pv -l | time python3 elasticImporter.py -c example.cfg
```

pv command reports: 25.4 K lines/s
tool speed reports: 25.3 K lines/s

### PyPy 5.10

```Bash
yes '1509750000000;52.5720661, 52.5720661;192.168.1.1;PotatoFriend;This is a potato and it is your friend;20;201.1' | head -10000000 | pv -l | time pypy elasticImporter.py -c example.cfg
```

pv command reports: 42.2 K lines/s
tool speed reports: 42.7 K lines/s

