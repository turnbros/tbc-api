import json
import http.client

from util import config
from util.cache import time_cache
from flask import Blueprint, Response, request

static_asset_repo = config.get_string_value("site", "static_asset_repo")
workspace_routes = Blueprint('workspace', __name__, url_prefix='/workspace')

@time_cache(10)
def workspace_manifest():
  conn = http.client.HTTPSConnection(static_asset_repo)
  conn.request("GET", "/workspace-manifest.json")
  response = conn.getresponse()
  if response.status == 200:
    return json.loads(response.read())
  else:
    print(f"Got Status {response.status} with reason {response.reason}")
    return {}

@time_cache(10)
def get_workspace_module(module_name) -> dict:
  return workspace_manifest().get(module_name)

@time_cache(10)
def get_workspace_module_attribute(module_name, attribute_name):
  return get_workspace_module(module_name)[attribute_name]

######################
## Workspace Module ##
######################
@workspace_routes.route('/manifest', methods=['GET'])
def get_workspace_manifest():

  # We'll just get the list of modules now
  module_list = list(workspace_manifest().values())

  response = {}
  selected_attributes = request.args.get("select", None)
  if selected_attributes is None:
    return Response(json.dumps(module_list), content_type='application/json'), 200
  else:
    # The attributes should be passed in as an array -> eg: ?select=icon,name,module
    # We will need to turn that comma delimited string into an array.
    selected_attributes = selected_attributes.split(',')

    # Now we go through each module and selected attribute to compile a new dictionary of filtered values.
    for module in module_list:
      module_name = module["name"]
      response[module_name] = {}
      for attribute in selected_attributes:
        if attribute in module.keys():
          response[module_name][attribute] = module[attribute]
        else:
          response[module_name][attribute] = None
    return Response(json.dumps(response), content_type='application/json'), 200

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
  module_variables = get_workspace_module_attribute(module, "variables")
  return Response(json.dumps(module_variables), content_type='application/json'), 200
