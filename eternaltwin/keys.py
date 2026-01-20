import abc

import jwt

__all__ = ["HS256Key", "RS256Key", "ES256Key", "PS256Key", "EdDSAKey"]


class KeyABC(abc.ABC):
    """Base class for keys used to sign tokens."""

    @property
    @abc.abstractmethod
    def algorithm(self) -> str:
        """The algorithm used to sign the token."""
        pass

    @abc.abstractmethod
    def encode(self, payload: dict) -> str:
        """Encode a payload into a JWT."""
        pass

    @abc.abstractmethod
    def decode(self, token: str) -> dict:
        """Decode a JWT."""
        pass


class SymmetricKey(KeyABC):
    """Base class for symmetric keys used to sign tokens."""

    def __init__(self, key: str):
        self.key = key

    def encode(self, payload: dict) -> str:
        """Encode a payload into a JWT."""
        return jwt.encode(payload, self.key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        """Decode a JWT."""
        return jwt.decode(token, self.key, algorithms=[self.algorithm], options={"verify_exp": False})


class AsymmetricKey(KeyABC):
    """Base class for asymmetric keys used to sign tokens."""

    def __init__(self, public_key: str, private_key: str):
        self.public_key = public_key
        self.private_key = private_key

    def encode(self, payload: dict) -> str:
        """Encode a payload into a JWT."""
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict:
        """Decode a JWT."""
        return jwt.decode(token, self.public_key, algorithms=[self.algorithm], options={"verify_exp": False})


class HS256Key(SymmetricKey):
    """Symmetric key using HMAC SHA-256."""

    algorithm = "HS256"


class RS256Key(AsymmetricKey):
    """Asymmetric key using RSA SHA-256."""

    algorithm = "RS256"


class ES256Key(AsymmetricKey):
    """Asymmetric key using ECDSA SHA-256."""

    algorithm = "ES256"


class PS256Key(AsymmetricKey):
    """Asymmetric key using RSA SHA-256 with PSS padding."""

    algorithm = "PS256"


class EdDSAKey(AsymmetricKey):
    """Asymmetric key using EdDSA."""

    algorithm = "EdDSA"
