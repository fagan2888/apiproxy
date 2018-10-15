""" PyYAML has some annoying bugs that were causing me to waste a load of time.
    It's faster (since it uses the C binding for libyaml), but since we generate the API spec at startup and then serve it as static data, who cares?
    This isn't a generic YAML library either, it's heavily targeted specifically at this one project, because i'm naughty like that.
    This is a quick hack, not a stable library intended for longterm use.
"""

import sexpdata
import config
from utils import *

def openapi_header():
    """Generates the header for the OpenAPI file
    """
    return """
swagger: "2.0"

info:
  version: %s
  title: smoke.io API
  description: API for interacting with the smoke.io blockchain

schemes:
  - https
"""[1:] % config.api_version

def openapi_paths(data_model):
    return """
paths:
%s
""" % '\n'.join(map(lambda e: """
  /%s:
    get:
      summary: %s
      description: %s 
""" %  (car(e).value(),dictalise(e)['summary'],dictalise(e)['description']),  data_model))
