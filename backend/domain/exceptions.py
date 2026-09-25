class DomainError(Exception):
    """Базовая ошибка домена."""


class InvalidTicketTransitionError(DomainError):
    def __init__(self, message: str = "Недопустимый переход статуса заявки"):
        super().__init__(message)


class OrganizationMismatchError(DomainError):
    def __init__(self, message: str = "Специалист принадлежит другой организации"):
        super().__init__(message)


class TicketNotFoundError(DomainError):
    def __init__(self, message: str = "Заявка не найдена"):
        super().__init__(message)


class BuildingNotFoundError(DomainError):
    def __init__(self, message: str = "Дом не найден"):
        super().__init__(message)


class CategoryNotFoundError(DomainError):
    def __init__(self, message: str = "Категория не найдена"):
        super().__init__(message)


class SpecialistNotFoundError(DomainError):
    def __init__(self, message: str = "Специалист не найден"):
        super().__init__(message)


class AuthenticationError(DomainError):
    def __init__(self, message: str = "Неверный логин или пароль"):
        super().__init__(message)


class ValidationError(DomainError):
    def __init__(self, message: str = "Ошибка валидации"):
        super().__init__(message)
