import http.client
from util import config
from flask import Blueprint, Response

static_asset_repo = config.get_string_value("site", "static_asset_repo")
workspace_routes = Blueprint('workspace', __name__, url_prefix='/workspace')

######################
## Workspace Module ##
######################
@workspace_routes.route('/manifest', methods=['GET'])
def get_workspace_manifest():
  conn = http.client.HTTPSConnection(static_asset_repo)
  conn.request("GET", "/workspace-manifest.json")
  response = conn.getresponse()

  if response.status == 200:
    return Response(response.read(), content_type='application/json'), 200
  return response.reason, response.status
