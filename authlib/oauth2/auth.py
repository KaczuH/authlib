import base64
from authlib.common.urls import add_params_to_qs
from authlib.common.encoding import to_bytes, to_native
from .rfc6749 import OAuth2Token
from .rfc6750 import add_bearer_token


def encode_client_secret_basic(client, method, uri, headers, body):
    text = '{}:{}'.format(client.client_id, client.client_secret)
    auth = to_native(base64.urlsafe_b64encode(to_bytes(text, 'latin1')))
    headers['Authorization'] = 'Basic {}'.format(auth)
    return uri, headers, body


def encode_client_secret_post(client, method, uri, headers, body):
    body = add_params_to_qs(body or '', [
        ('client_id', client.client_id),
        ('client_secret', client.client_secret or '')
    ])
    return uri, headers, body


def encode_none(client, method, uri, headers, body):
    if method == 'GET':
        uri = add_params_to_qs(uri, [('client_id', client.client_id)])
        return uri, headers, body
    body = add_params_to_qs(body, [('client_id', client.client_id)])
    return uri, headers, body


class ClientAuth(object):
    """Attaches OAuth Client Information to HTTP requests.

    :param client_id: Client ID, which you get from client registration.
    :param client_secret: Client Secret, which you get from registration.
    :param auth_method: Client auth method for token endpoint. The supported
        methods for now:

        * client_secret_basic (default)
        * client_secret_post
        * none
    """
    AUTH_METHODS = {
        'client_secret_basic': encode_client_secret_basic,
        'client_secret_post': encode_client_secret_post,
        'none': encode_none,
    }

    @classmethod
    def register_auth_method(cls, method, func):
        assert method not in cls.AUTH_METHODS
        cls.AUTH_METHODS[method] = func

    def __init__(self, client_id, client_secret, auth_method=None):
        if auth_method is None:
            auth_method = 'client_secret_basic'

        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_method = auth_method

    def prepare(self, method, uri, headers, body):
        func = self.AUTH_METHODS.get(self.auth_method)
        return func(self, method, uri, headers, body)


class TokenAuth(object):
    """Attach token information to HTTP requests.

    :param token: A dict or OAuth2Token instance of an OAuth 2.0 token
    :param token_placement: The placement of the token, default is ``header``,
        available choices:

        * header (default)
        * body
        * uri
    """
    SIGN_METHODS = {
        'bearer': add_bearer_token
    }

    @classmethod
    def register_sign_method(cls, sign_type, func):
        cls.SIGN_METHODS[sign_type] = func

    def __init__(self, token, token_placement='header', client=None):
        self.token = OAuth2Token.from_dict(token)
        self.token_placement = token_placement
        self.client = client
        self.hooks = set()

    def set_token(self, token):
        self.token = OAuth2Token.from_dict(token)

    def prepare(self, uri, headers, body):
        token_type = self.token['token_type']
        sign = self.SIGN_METHODS[token_type.lower()]
        uri, headers, body = sign(
            self.token['access_token'],
            uri, headers, body,
            self.token_placement)

        for hook in self.hooks:
            uri, headers, body = hook(uri, headers, body)

        return uri, headers, body
