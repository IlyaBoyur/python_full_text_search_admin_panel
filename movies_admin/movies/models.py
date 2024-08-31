import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


from .constants import PersonRoleChoice


class CreatedMixin(models.Model):
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    class Meta:
        abstract = True


class UpdatedMixin(models.Model):
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)

    class Meta:
        abstract = True


class CreatedUpdatedMixin(CreatedMixin, UpdatedMixin):
    ...

    class Meta:
        abstract = True


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(
        verbose_name="UUID", primary_key=True, default=uuid.uuid4, editable=False
    )

    class Meta:
        abstract = True


class Person(CreatedUpdatedMixin, UUIDPrimaryKeyMixin):
    full_name = models.CharField(_("Полное имя"), max_length=255)
    birth_date = models.DateField(_("Дата рождения"), blank=True, null=True)

    class Meta:
        db_table = f'{settings.CONTENT_SCHEMA}"."person'
        verbose_name = _("Персона")
        verbose_name_plural = _("Персоны")

    def __str__(self) -> str:
        return self.full_name


class PersonFimwork(CreatedMixin, UUIDPrimaryKeyMixin):
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
        db_table = f'{settings.CONTENT_SCHEMA}"."person_film_work'
        verbose_name = _("Участник кинопроизведения")
        verbose_name_plural = _("Участники кинопроизведений")
        unique_together = ("film_work", "person", "role")

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"


class GenreFilmwork(CreatedMixin, UUIDPrimaryKeyMixin):
    film_work = models.ForeignKey(
        "Filmwork",
        verbose_name=_("Кинопроизведение"),
        related_name="genre_filmworks",
        on_delete=models.CASCADE,
    )
    genre = models.ForeignKey(
        "Genre",
        verbose_name=_("Жанр кинопроизведения"),
        related_name="genre_filmworks",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = f'{settings.CONTENT_SCHEMA}"."genre_film_work'
        verbose_name = _("Жанр кинопроизведения")
        verbose_name_plural = _("Жанры кинопроизведений")
        unique_together = ("film_work", "genre")

    def __str__(self) -> str:
        return f"{self._meta.verbose_name} #{self.pk}"


class Genre(CreatedUpdatedMixin, UUIDPrimaryKeyMixin):
    name = models.CharField(_("Название"), max_length=255)
    description = models.TextField(_("Описание"), max_length=5000, blank=True)

    class Meta:
        db_table = f'{settings.CONTENT_SCHEMA}"."genre'
        verbose_name = _("Жанр")
        verbose_name_plural = _("Жанры")

    def __str__(self) -> str:
        return self.name


class FilmworkType(CreatedUpdatedMixin):
    slug = models.SlugField(_("Слаг"), max_length=255, primary_key=True)
    name = models.CharField(_("Название"), max_length=255)

    class Meta:
        db_table = f'{settings.CONTENT_SCHEMA}"."film_work_type'
        verbose_name = _("Тип кинопроизведения")
        verbose_name_plural = _("Типы кинопроизведений")

    def __str__(self) -> str:
        return self.name


class Filmwork(CreatedUpdatedMixin, UUIDPrimaryKeyMixin):
    type = models.ForeignKey(
        "FilmworkType",
        verbose_name=_("Тип кинопроизведения"),
        related_name="films",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column="type",
    )
    genres = models.ManyToManyField(
        verbose_name=_("Жанры"),
        to="Genre",
        related_name="filmworks",
        through="GenreFilmWork",
    )
    persons = models.ManyToManyField(
        verbose_name=_("Персоны"),
        to="Person",
        related_name="filmworks",
        through="PersonFimwork",
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
        db_table = f'{settings.CONTENT_SCHEMA}"."film_work'
        verbose_name = _("Кинопроизведение")
        verbose_name_plural = _("Кинопроизведения")

    def __str__(self) -> str:
        return self.title
