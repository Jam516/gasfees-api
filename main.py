from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_caching import Cache
from datetime import datetime
import os

from dune_client.types import QueryParameter
from dune_client.client import DuneClient
from dune_client.query import QueryBase

DUNE_API_KEY = os.environ['DUNE_API_KEY']
REDIS_LINK = os.environ['REDIS_URL']

config = {
  "CACHE_TYPE": "redis",
  "CACHE_DEFAULT_TIMEOUT": 600,
  "CACHE_REDIS_URL": REDIS_LINK
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)
CORS(app)


def make_cache_key(*args, **kwargs):
  path = request.path
  args = str(hash(frozenset(request.args.items())))
  return (path + args).encode('utf-8')


@app.route('/actions')
@cache.memoize(make_name=make_cache_key)
def actions():
  query = QueryBase(name="gas", query_id=3448534)
  dune = DuneClient(DUNE_API_KEY)
  results = dune.get_latest_result(query)
  return results.result.rows

@app.route('/chain')
@cache.memoize(make_name=make_cache_key)
def chain():
  chain_name = request.args.get('chain_name', 'optimism')
  
  query = QueryBase(name="gas", query_id=3569863)
  dune = DuneClient(DUNE_API_KEY)
  results = dune.get_latest_result(query)
  filtered_rows = [row for row in results.result.rows if row['chain'] == chain_name]
  return filtered_rows


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=81)
