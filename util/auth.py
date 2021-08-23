from util import config
from functools import wraps
from authlib.integrations.flask_client import OAuth


def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    #if 'profile' not in session:
    #  return "No.", 403
    return f(*args, **kwargs)
  return decorated

class AuthHandler(object):
    def __init__(self, flask_app):
        self._oauth = OAuth(flask_app)
        self._auth0 = self._oauth.register(
            'auth0',
            client_id=config.get_string_value("auth", "client_id"),
            client_secret=config.get_string_value("auth", "client_secret"),
            api_base_url=config.get_string_value("auth", "api_base_url"),
            access_token_url=config.get_string_value("auth", "access_token_url"),
            authorize_url=config.get_string_value("auth", "authorize_url"),
            client_kwargs={
                'scope': 'openid profile email',
            },
        )

    @property
    def auth0(self):
        return self._auth0
