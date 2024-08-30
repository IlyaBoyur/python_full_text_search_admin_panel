from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class PersonRoleChoice(TextChoices):
    ACTOR = "actor", _("Актер")
    DIRECTOR = "director", _("Режиссер")
    WRITER = "writer", _("Сценарист")
