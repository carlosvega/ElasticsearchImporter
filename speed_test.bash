#!/bin/bash

function generate_lines {

yes | head -n $1 | mawk '


    function dec2ip(dec)
    {
        ip=""; delim="";
        for (e = 3; e >= 0; e--) {
               octet = int(dec / (256 ^ e))
           dec -= octet * 256 ^ e
           ip = ip delim octet
           delim = "."
        }
        return ip;
    }
    function randint(n)

    {
        return int(n * rand());
    }

BEGIN{
    OFS=";";
    srand(1);
    t=int(systime()*1000);
}

{
    int_ip = randint((2^32)-1);
    printf("%.0f;%s, %s;%s;%s;%s;%s;%.4f\n", t, "52.5720661", "52.5720661", dec2ip(int_ip), "ExampleString", "This is a random string and it is your friend", randint(10000), randint(10000)*1.41421356237);
    t=t+1000;
}

'

}

echo "elasticsearch version $(curl -s 'localhost:9200?filter_path=version.number')"

create_mapping=$(mktemp)
cat > $create_mapping <<- EOM
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import *
from elasticsearch_dsl.connections import connections

client = Elasticsearch()
db = 'speed_test'

def reset_index(es):
    settings = {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 0
        },
        "mappings": {
            "my_data": {
                '_source' : {'enabled' : False},
                '_all' : {'enabled' : False},
                "properties": {
                    "timestamp": {
                        "type": "date"
                    },
                    "geo": {
                        "type": "geo_point"
                    },
                    "ip": {
                        "type": "ip"
                    },
                    "name": {
                        "type": "keyword"
                    },
                    "description": {
                        "type": "text"
                    },
                    "age": {
                        "type": "integer"
                    },
                    "size": {
                        "type": "float"
                    }
                }
            }
         }
    }
    es.indices.delete(index=db, ignore=[400, 404])
    es.indices.create(index=db, ignore=400, body=settings)

reset_index(client)
EOM

python $create_mapping &> /dev/null

lines_file=$(mktemp)
test_base=$(mktemp)
test_py2=$(mktemp)
test_py3=$(mktemp)
test_pypy=$(mktemp)
lines=1000000
#Base
generate_lines $lines > $lines_file
#Python 2
echo ""
curl -XDELETE localhost:9200/speed_test &> /dev/null
python $create_mapping &> /dev/null
echo "Test Python2 $(python2 --version) $test_py2"
cat $lines_file | python2 elasticImporter.py -c example.cfg --no_source --threads 2 --no_all --index speed_test --bulk 5000 2> $test_py2
speed_py2=$(tail -1 $test_py2 | awk '{print $(NF-1)}')
echo "Python2: $speed_py2"
#Python 3
echo ""
curl -XDELETE localhost:9200/speed_test &> /dev/null
python $create_mapping &> /dev/null
echo "Test Python3 $(python3 --version) $test_py3"
cat $lines_file | python3 elasticImporter.py -c example.cfg --no_source --threads 2 --no_all --index speed_test --bulk 5000 2> $test_py3
speed_py3=$(tail -1 $test_py3 | awk '{print $(NF-1)}')
echo "Python3: $speed_py3"

#PyPy
echo ""
curl -XDELETE localhost:9200/speed_test &> /dev/null
python $create_mapping &> /dev/null
echo "Test PyPy $(pypy --version) $test_pypy"
cat $lines_file | pypy elasticImporter.py -c example.cfg --no_source  --threads 2 --no_all --index speed_test --bulk 5000 2> $test_pypy
speed_pypy=$(tail -1 $test_pypy | awk '{print $(NF-1)}')
echo "PyPy: $speed_pypy"
