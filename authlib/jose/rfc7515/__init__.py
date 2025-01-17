"""
    authlib.jose.rfc7515
    ~~~~~~~~~~~~~~~~~~~~~

    This module represents a direct implementation of
    JSON Web Signature (JWS).

    https://tools.ietf.org/html/rfc7515
"""

from .jws import JsonWebSignature
from .models import JWSAlgorithm, JWSHeader, JWSObject

JWS = JsonWebSignature

__all__ = [
    'JWS', 'JsonWebSignature',
    'JWSAlgorithm', 'JWSHeader', 'JWSObject'
]
