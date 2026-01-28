class AppError(Exception):
    pass


class ValidationError(AppError):
    pass


class AuthenticationError(AppError):
    pass


class AuthorizationError(AppError):
    pass
