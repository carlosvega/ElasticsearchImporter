# Elasticsearch Importer
Generic Elasticsearch Importer

## Options

| Option | Long option        | Description                                            | Default Value |
|--------|--------------------|--------------------------------------------------------|---------------|
| -h     | --help             | Show this help message and exit.                       |               |
| -i     | --input            | Input file.                                            | stdin         |
| -c     | --cfg              | Configuration file.                                    |               |
| -s     | --separator        | File Separator.                                        | semicolon     |
| -n     | --node             | Elasticsearch node.                                    | localhost     |
| -n     | --node             | Elasticsearch node.                                    | localhost     |
| -x     | --index            | Elasticsearch index.                                   | Value from the JSON cfg file |
| -t     | --type             | Elasticsearch document type.                           | Value from the JSON cfg file |
|        | --bulk             | Elasticsearch bulk size parameter.                     | 2000          |
|        | --threads          | Elasticsearch bulk size parameter.                     | 5             |
|        | --queue            | Size of queue for the parallel bulk.                   | 6             |
|        | --timeout          | Connection timeout in seconds.                         | 600           |
|        | --skip_first_line  | Skips first line.                                      |               |
|        | --refresh          | Refresh the index when finished.                       |               |
|        | --replicas         | Number of replicas for the index if it does not exist. | 0             |
|        | --shards           | Number of shards for the index if it does not exist.   | 2             |
|        | --refresh_interval | Refresh interval for the index if it does not exist.   | 60s           |
|        | --dates_in_seconds | If true, assume dates are provided in seconds.         |               |
|        | --md5_id           | Uses the MD5 hash of the line as ID.                   |               |
|        | --md5_exclude      | List of column names to be excluded from the hash.     |               |

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
#replace pypy with python if you don't want to use pypy.
git clone git@github.com:carlosvega/ElasticsearchImporter.git ElasticsearchImporter
cd ElasticsearchImporter
pip install virtualenv
virtualenv myenv -p `which pypy`
source env/bin/activate 
pip install -r requirements.txt
#index your first 100K lines
time yes '1509750000000;52.5720661, 52.5720661;192.168.1.1;PotatoFriend;This is a potato and it is your friend;20;201.1' | head -100000 | pv -l | pypy elasticImporter.py -c example.cfg
```

## Performance

On a Intel(R) Core(TM) i7-7700 CPU @ 3.60GHz with 32GB of RAM using Elasticsearch 6.0.1  with a 4GB Heap.
Executing a 10 Million lines test:

```Bash
yes '1509750000000;52.5720661, 52.5720661;192.168.1.1;PotatoFriend;This is a potato and it is your friend;20;201.1' | head --10000000 | pv -l | time python elasticImporter.py -c example.cfg                                                             
```

Python: 37871.615 lines/s
