from sanic import Sanic
from sanic import response

import sexpdata
from sexpdata import car,cdr,Symbol
from utils import *
import openapi_yaml

from cooltools import memcached
from cooltools import with_multi_args

from time import strftime, gmtime


import smoked_rpc

proxy_app = Sanic()

import config


# lisp magic
# literally - all software is magic, because it causes change in reality in accordance with will
data_file = open('data.lisp')
data_model = sexpdata.load(data_file)
data_file.close()


# TODO - switch from rpc method to some more generic method for data source

def gen_entity_multi_handler(entity_dict):
    defargs = []
    has_count = False
    rpc_method_name = car(entity_dict['rpc_method']).value()
    for arg in car(cdr(entity_dict['rpc_method'])):
        if type(arg) is sexpdata.Symbol:
           if arg.value() == '!count':
              has_count = True
           else:
              defargs.append(arg.value())
        else:
          defargs.append(arg)
    rpc_method = with_multi_args(getattr(smoked_rpc,rpc_method_name),defargs)
    max_count  = entity_dict['max_datums']
    def handler_with_count(request):
        if 'count' in request.raw_args.keys():
           count = int(request.raw_args['count'])
           if count > max_count: count=max_count
        else:
           count = max_count
        resp = rpc_method(count)
        return response.json(resp)
    def handler_without_count(request):
        resp = rpc_method()
        return response.json(resp)
    if has_count:
       return handler_with_count
    else:
       return handler_without_count

def gen_entity_single_handler(entity_dict):
    defargs = []
    has_id = False
    rpc_method_name = car(entity_dict['rpc_method']).value()
    for arg in car(cdr(entity_dict['rpc_method'])):
        if type(arg) is sexpdata.Symbol:
           if arg.value() == '!id':
              has_id = True
           else:
              defargs.append(arg.value())
        else:
           defargs.append(arg)
    rpc_method = with_multi_args(getattr(smoked_rpc,rpc_method_name),defargs)
    def handler_with_id(request,name):
        resp = rpc_method(name)
        return response.json(resp)
    def handler_without_id(request):
        resp = rpc_method()
        return response.json(resp)
    if has_id: return handler_with_id
    return handler_without_id

def gen_entity_single_handler_multi_ids(entity_dict):
    defargs = []
    rpc_method_name = car(entity_dict['rpc_method']).value()


custom_handlers = {}

def _get_blog_posts_cached(username,count):
    if count>10: count=10
    retval = []
    for p in smoked_rpc.get_discussions_before_date(username,"",strftime('%Y-%m-%dT%H:%M:%S',gmtime()),str(count)):
        retval.append({'permlink':p['permlink'],'id':p['id']})
    return retval

get_blog_posts_cached = memcached(_get_blog_posts_cached)

def get_blog_posts(request,name):

    count = 10
    if 'count' in request.raw_args.keys():
       count = int(request.raw_args['count'])
    username = name
    return response.json(get_blog_posts_cached(username,count))

def get_head_block_num():
    network_data = smoked_rpc.get_smoke_dynamic_global_properties()
    return network_data['head_block_number']

def _get_recent_blocks_cached(count):
    if count>10: count=10
    headblock = get_head_block_num()
    retval = []
    for block_num in range(headblock-count,headblock):
        block_data = smoked_rpc.get_smoke_block(block_num)
        retval.append(block_data)
    return retval

get_recent_blocks_cached = memcached(_get_recent_blocks_cached,timeout=2)

def get_recent_blocks(request):
    count = 10
    if 'count' in request.raw_args.keys():
       count = int(request.raw_args['count'])
    return response.json(get_recent_blocks_cached(count))

custom_handlers['get_blog_posts']    = get_blog_posts
custom_handlers['get_recent_blocks'] = get_recent_blocks


def add_entity(sanic_app,entity_name,entity_dict):
    if 'custom_handler' in entity_dict.keys():
       if 'unique_id' in entity_dict.keys():
          sanic_app.add_route(custom_handlers[entity_dict['custom_handler'].value()],''.join(('/',entity_name,'/','<name>' )))
       else:
          sanic_app.add_route(custom_handlers[entity_dict['custom_handler'].value()],''.join(('/',entity_name)))
       return
    if 'unique_ids' in entity_dict.keys():
       sanic_app.add_route(gen_entity_single_handler_multi_ids(entity_dict), ''.join('/',entity_name, '/'.join(map(lambda x: '<%s>' % x.value(), entity_dict['unique_ids']))))
       return
    if 'max_datums' in entity_dict.keys():
       sanic_app.add_route(gen_entity_multi_handler(entity_dict),''.join(('/',entity_name)))
    else:
       sanic_app.add_route(gen_entity_single_handler(entity_dict),''.join(('/',entity_name, '/<name>')))


#@proxy_app.route('/post/<author>/<post>')
#async def get_post(request,author,post):
#      pass

from decimal import *
getcontext().prec = 10
@proxy_app.route('/misc/chain_info')
async def chain_info(request):
      dgp = smoked_rpc.get_smoke_dynamic_global_properties()
      total_supply = Decimal(dgp['current_supply'].split(' ')[0])
      smoke_data   = smoked_rpc.get_user_data('smoke')
      reserve_data = smoked_rpc.get_user_data('reserve')

      smoke_balance   = Decimal(smoke_data['balance'].split(' ')[0])
      reserve_balance = Decimal(reserve_data['balance'].split(' ')[0])

      circulating_supply = total_supply - smoke_balance - reserve_balance

      return response.json({"total_supply":total_supply,"circulating_supply":circulating_supply,"smoke_balance":smoke_balance,"reserve_balance":reserve_balance})

@proxy_app.route('/openapi.yaml')
async def openapi_spec(request):
      return response.text(openapi_yaml.openapi_header() + openapi_yaml.openapi_paths(data_model),content_type='text/yaml')

@proxy_app.route('/')
async def smoked(request):
      # TODO - replace this with a nifty autogenerated documentation + API explorer thing
      return response.text('This is an API server, read the documentation to use it')

if __name__ == "__main__":
   for entity in data_model:
       add_entity(proxy_app,car(entity).value(),dictalise(entity))

   proxy_app.run(host="0.0.0.0", port=8000)
