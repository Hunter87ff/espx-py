from __future__ import annotations


class ESPXError(Exception):
    """Base exception for all client-side ESPX errors."""


class ESPXConfigurationError(ESPXError):
    """Raised when the client is misconfigured."""


class ESPXTransportError(ESPXError):
    """Raised when the HTTP request could not be completed."""


class ESPXResponseError(ESPXError):
    """Raised when the server response cannot be interpreted safely."""

    def __init__(self, message: str, *, payload: object | None = None) -> None:
        super().__init__(message)
        self.payload = payload


class ESPXHTTPError(ESPXError):
    """Raised for non-success HTTP responses."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        payload: object | None = None,
    ) -> None:
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.payload = payload


class ESPXAuthenticationError(ESPXHTTPError):
    """Raised when the access token is missing or invalid."""


class ESPXValidationError(ESPXHTTPError):
    """Raised when the request payload is rejected by the server."""


class ESPXTemplateNotFoundError(ESPXHTTPError):
    """Raised when a requested template does not exist."""


class ESPXServerError(ESPXHTTPError):
    """Raised when the server fails while handling the request."""
