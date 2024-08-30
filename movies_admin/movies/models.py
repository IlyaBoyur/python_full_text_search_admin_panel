from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


from .constants import PersonRoleChoice


class TimeStampedModel(models.Model):
    created = models.DateTimeField(_("Создано"), auto_now_add=True)
    modified = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        abstract = True


class Person(TimeStampedModel):
    full_name = models.CharField(_("Полное имя"), max_length=255)

    class Meta:
        verbose_name = _("Персона")
        verbose_name_plural = _("Персоны")

    def __str__(self) -> str:
        return self.full_name


class PersonRole(TimeStampedModel):
    film_work = models.ForeignKey(
        "Filmwork",
        verbose_name=_("Кинопроизведение"),
        related_name="person_roles",
        on_delete=models.CASCADE,
    )
    person = models.ForeignKey(
        "Person",
        verbose_name=_("Тип кинопроизведения"),
        related_name="person_roles",
        on_delete=models.CASCADE,
    )
    role = models.CharField(_("Роль"), max_length=255, choices=PersonRoleChoice.choices)

    class Meta:
        verbose_name = _("Роль персоны")
        verbose_name_plural = _("Роли персон")
        unique_together = ("film_work_id", "person_id")

    def __str__(self) -> str:
        return self.full_name


class Genre(TimeStampedModel):
    name = models.CharField(_("Название"), max_length=255)
    description = models.TextField(_("Описание"), max_length=5000, blank=True)

    class Meta:
        verbose_name = _("Жанр")
        verbose_name_plural = _("Жанры")

    def __str__(self) -> str:
        return self.name


class FilmworkType(TimeStampedModel):
    name = models.CharField(_("Название"), max_length=255)

    class Meta:
        verbose_name = _("Тип кинопроизведения")
        verbose_name_plural = _("Типы кинопроизведений")

    def __str__(self):
        return self.name


class Filmwork(TimeStampedModel):
    type = models.ForeignKey(
        "FilmworkType",
        verbose_name=_("Тип кинопроизведения"),
        related_name="films",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    genres = models.ManyToManyField(
        verbose_name=_("Жанры"), to="Genre", related_name="filmworks"
    )
    persons = models.ManyToManyField(
        verbose_name=_("Персоны"),
        to="Person",
        related_name="filmworks",
        through="PersonRole",
    )
    title = models.CharField(_("Название"), max_length=255)
    description = models.TextField(_("Описание"), max_length=5000, blank=True)
    creation_date = models.DateField(_("Дата создания фильма"), blank=True, null=True)
    certificate = models.TextField(_("Сертификат"), blank=True)
    file_path = models.FileField(_("Файл"), upload_to="film_works/", blank=True)
    rating = models.FloatField(
        _("Рейтинг"), validators=[MinValueValidator(0)], blank=True, null=True
    )

    class Meta:
        verbose_name = _("Кинопроизведение")
        verbose_name_plural = _("Кинопроизведения")

    def __str__(self) -> str:
        return self.title
