"""Domain errors, mapped to HTTP responses in one place (see app.main).

Services raise these instead of HTTPException so business logic stays
independent of the web framework and is easy to unit test.
"""


class DomainError(Exception):
    status_code = 400
    code = "bad_request"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = 404
    code = "not_found"


class PermissionDeniedError(DomainError):
    status_code = 403
    code = "forbidden"


class ValidationFailedError(DomainError):
    status_code = 422
    code = "validation_failed"


class ConflictError(DomainError):
    status_code = 409
    code = "conflict"


class UnsupportedFileError(DomainError):
    status_code = 415
    code = "unsupported_file"


class PayloadTooLargeError(DomainError):
    status_code = 413
    code = "payload_too_large"
