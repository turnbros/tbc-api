import json
import auth_handler
from tenant_handler import datastore
from flask import Blueprint, request, Response

routes = Blueprint('tenant_resources', __name__, url_prefix='/resource')

@routes.route('', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_resources(tenant_name=None):
    return  Response(datastore.get_tenant_store().get_tenant_resources(tenant_name)[0], content_type='application/json'), 200
