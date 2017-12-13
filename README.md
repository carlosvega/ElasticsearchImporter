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

## Installation

```
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
