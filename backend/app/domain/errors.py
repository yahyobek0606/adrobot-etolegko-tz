class DomainError(Exception):
    code = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    code = "not_found"


class InvalidOperationError(DomainError):
    code = "invalid_operation"


class ConflictError(DomainError):
    code = "conflict"


class ProviderError(DomainError):
    code = "provider_error"
