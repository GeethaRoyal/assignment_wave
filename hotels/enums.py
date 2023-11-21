from enum import Enum


class PaymentStatus(Enum):
    PAID = 'PAID'
    UNPAID = 'UNPAID'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class TableStatus(Enum):
    VACANT = "VACANT"
    OCCUPIED = "OCCUPIED"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class BillingStatus(Enum):
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class DJRequestStatus(Enum):
    PENDING = "PENDING"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    AWAITING_CONFIRMATION = 'AWAITING_CONFIRMATION'
    SCHEDULED = 'SCHEDULED'
    IN_PROGRESS = 'IN_PROGRESS'
    DELAYED = 'DELAYED'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class UserRoles(Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    CUSTOMER = "CUSTOMER"
    WAITER = "WAITER"

class OrderStatus(Enum):
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    PENDING = "PENDING"