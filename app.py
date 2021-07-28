import config_handler
from flask import Flask
from auth_handler import AuthHandler
from tenant_handler import tenant_routes

app = Flask(__name__)
app.register_blueprint(tenant_routes)

if __name__ == "__main__":
  auth = AuthHandler(app)
  config = config_handler.Config()
  app.secret_key = config.get_string_value("site", "secret_key")
  app.config['SESSION_TYPE'] = config.get_string_value("site", "session_type")
  Flask.run(app, host=config.get_string_value("site", "bind_ip"), port=config.get_int_value("site", "bind_port"))
