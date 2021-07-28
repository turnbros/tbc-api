import json
import auth_handler
from tenant_handler import datastore
from flask import Blueprint, Response
import tenant_handler.state.route_blueprint as state_routes
import tenant_handler.resource.route_blueprint as resource_routes

tenant_routes = Blueprint('tenant', __name__, url_prefix='/tenant')
named_tenant_routes = Blueprint('tenants', __name__, url_prefix='/<tenant_name>')
named_tenant_routes.register_blueprint(state_routes.routes)
named_tenant_routes.register_blueprint(resource_routes.routes)
tenant_routes.register_blueprint(named_tenant_routes)

@tenant_routes.route('', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_list():
  return Response(json.dumps(datastore.get_tenant_store().get_tenant_names()), content_type='application/json'), 200

@named_tenant_routes.route('', methods=['GET'])
@auth_handler.requires_auth
def get_tenant(tenant_name=None):
  return Response(json.dumps(datastore.get_tenant_store().get_tenant(tenant_name).to_json()), content_type='application/json'), 200
