from tortoise.models import Model
from tortoise import fields
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash


class Problems(Model):
    class PriorityEnum(str, Enum):
        INFO = "INFO"
        CRIT = "CRIT"
        WARN = "WARN"

    class StatusEnum(str, Enum):
        START = "START"
        IN_PROGRESS = "IN_PROGRESS"
        END = "END"

    id = fields.IntField(null=False, pk=True, unique=True)
    priority = fields.CharEnumField(enum_type=PriorityEnum, null=False)
    description = fields.CharField(max_length=2000, null=True)
    message = fields.CharField(max_length=2000, null=True)
    status = fields.CharEnumField(enum_type=StatusEnum, null=True)
    type = fields.ForeignKeyField(
        'models_type.Type',
        related_name='problems',
        on_delete=fields.SET_NULL,
        null=True
    )
    time = fields.DatetimeField(auto_now_add=True)
    change_time = fields.DatetimeField(auto_now=True)
    responsible = fields.ForeignKeyField(
        'models_person.Person',
        related_name='problems',
        on_delete=fields.SET_NULL,
        null=True
    )

    class Meta:
        table = "problems"
        app = "models_problems"


class Person(Model):
    class ChannelEnum(str, Enum):
        TG = "TG"
        MAIL = "MAIL"

    id = fields.IntField(null=False, pk=True, unique=True)
    description = fields.CharField(max_length=2000, null=True)
    role = fields.CharField(max_length=2000, null=True)
    full_name = fields.CharField(max_length=2000, null=True)
    login = fields.CharField(max_length=2000, null=True)
    password = fields.CharField(max_length=2000, null=True)
    channel = fields.CharEnumField(enum_type=ChannelEnum, null=True)
    type = fields.ForeignKeyField(
        'models_type.Type',
        related_name='person',
        on_delete=fields.SET_NULL,
        null=True
    )
    tg_id = fields.CharField(max_length=2000, null=True)
    email = fields.CharField(max_length=2000, null=True)

    password_hash = fields.CharField(max_length=2000, null=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    class Meta:
        table = "person"
        app = "models_person"


class Type(Model):
    id = fields.IntField(null=False, pk=True, unique=True)
    full_name = fields.CharField(null=False, max_length=255)

    class Meta:
        table = "type"
        app = "models_type"
