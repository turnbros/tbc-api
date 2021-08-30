import json
import http.client
from functools import lru_cache

from util import config
from flask import Blueprint, Response

static_asset_repo = config.get_string_value("site", "static_asset_repo")
workspace_routes = Blueprint('workspace', __name__, url_prefix='/workspace')

def workspace_manifest():
  conn = http.client.HTTPSConnection(static_asset_repo)
  conn.request("GET", "/workspace-manifest.json")
  response = conn.getresponse()
  if response.status == 200:
    return json.loads(response.read())
  else:
    print(f"Got Status {response.status} with reason {response.reason}")
    return {}

@lru_cache(369)
def get_workspace_module(module_name) -> dict:
  return workspace_manifest().get(module_name)

@lru_cache(369)
def get_workspace_module_attribute(module_name, attribute_name):
  return get_workspace_module(module_name)[attribute_name]

######################
## Workspace Module ##
######################
@workspace_routes.route('/manifest', methods=['GET'])
def get_workspace_manifest():
  workspace_manifest_values = list(workspace_manifest().values())
  return Response(json.dumps(workspace_manifest_values), content_type='application/json'), 200

@workspace_routes.route('/manifest/<module>', methods=['GET'])
def get_workspace_manifest_module(module):
  workspace_manifest_module = workspace_manifest().get(module)
  return Response(json.dumps(workspace_manifest_module), content_type='application/json'), 200

@workspace_routes.route('/manifest/<module>/icon', methods=['GET'])
def get_workspace_manifest_module_icon(module):
  return Response(get_workspace_module_attribute(module, "icon"), content_type='application/json'), 200

@workspace_routes.route('/manifest/<module>/title', methods=['GET'])
def get_workspace_manifest_module_title(module):
  return Response(get_workspace_module_attribute(module, "title"), content_type='application/json'), 200

@workspace_routes.route('/manifest/<module>/description', methods=['GET'])
def get_workspace_manifest_module_description(module):
  return Response(get_workspace_module_attribute(module, "description"), content_type='application/json'), 200

@workspace_routes.route('/manifest/<module>/outputs', methods=['GET'])
def get_workspace_manifest_module_outputs(module):
  module_outputs = get_workspace_module_attribute(module, "outputs")
  return Response(json.dumps(module_outputs), content_type='application/json'), 200

@workspace_routes.route('/manifest/<module>/variables', methods=['GET'])
def get_workspace_manifest_module_variables(module):
  module_variables = get_workspace_module_attribute(module, "outputs")
  return Response(json.dumps(module_variables), content_type='application/json'), 200
