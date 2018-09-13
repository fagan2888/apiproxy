import eventlet
import json
websocket = eventlet.import_patched('websocket')
import websocket
from cooltools import *


def smoked_rpc_func(url,method,request_api=None):
    class rpc_func:
       def __call__(self,*params):
           ws = websocket.WebSocket()
           ws.connect(url)
           if request_api == None:
              req = json.dumps({'id':1,'method':method,'params':params,'jsonrpc':'2.0'})
              ws.send(req)
              resp = ws.recv()
              retval = json.loads(resp)['result']
           else:
              ws.send(json.dumps({"id":1,"method":"call","params":[1,"login",["",""]]}))
              ws.recv()
              ws.send(json.dumps({"id":2,"method":"call","params":[1,"get_api_by_name",[request_api]]}))
              retval = json.loads(ws.recv())
              req = json.dumps({"id":3,"method":"call","params":[retval['result'],"broadcast_transaction",params]})
              ws.send(req)
              resp = ws.recv()
              retval = json.loads(resp)['result']
           ws.shutdown()
           return retval
    return rpc_func()

smoked_rpc_url   = 'ws://127.0.0.1:8090'
get_smoke_categories                = smoked_rpc_func(smoked_rpc_url,'get_trending_categories')
get_trending_tags                   = single_field(with_args(get_smoke_categories,[None,10]),"name")
get_smoke_config                    = memcached(smoked_rpc_func(smoked_rpc_url,'get_config'))
get_smoke_dynamic_global_properties = smoked_rpc_func(smoked_rpc_url,'get_dynamic_global_properties')
get_user_data                       = listify(smoked_rpc_func(smoked_rpc_url,'lookup_account_names'))
get_user_post                       = memcached(smoked_rpc_func(smoked_rpc_url,'get_content'))
get_witness_data                    = with_args(smoked_rpc_func(smoked_rpc_url,'get_witness_by_account'),['charlieshrem'])
get_discussions_before_date         = smoked_rpc_func(smoked_rpc_url,'get_discussions_by_author_before_date')
get_network_data                    = joined(get_smoke_config,get_smoke_dynamic_global_properties)
get_smoke_data                      = multifunc(witness=get_witness_data,network=get_network_data)
get_smoke_block                     = memcached(smoked_rpc_func(smoked_rpc_url,'get_block'))
get_account_history                 = smoked_rpc_func(smoked_rpc_url,"get_account_history")
broadcast_tx                        = smoked_rpc_func(smoked_rpc_url,"broadcast_transaction",request_api="network_broadcast_api")

def _get_tag_posts(tag):
    return smoked_rpc_func(smoked_rpc_url,"get_discussions_by_created")({'tag':tag,'limit':10})

get_tag_posts     = memcached(_get_tag_posts)

get_post_comments = memcached(smoked_rpc_func(smoked_rpc_url,"get_content_replies"))

