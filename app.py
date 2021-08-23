from util import config
from flask import Flask
import workspace
from tenant_handler import tenant_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(tenant_routes)
app.register_blueprint(workspace.workspace_routes)

if __name__ == "__main__":
  app.secret_key = config.get_string_value("site", "secret_key")
  app.config['SESSION_TYPE'] = config.get_string_value("site", "session_type")
  Flask.run(app, host=config.get_string_value("site", "bind_ip"), port=config.get_int_value("site", "bind_port"))
