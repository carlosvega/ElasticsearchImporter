# Elasticsearch Importer
Generic Elasticsearch Importer

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
