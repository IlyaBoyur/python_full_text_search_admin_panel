from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    created = models.DateTimeField(_("Создано"), auto_now_add=True)
    modified = models.DateTimeField(_("Обновлено"), auto_now=True)

    class Meta:
        abstract = True


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
        FilmworkType,
        verbose_name=_("Тип кинопроизведения"),
        related_name="films",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    genres = models.ManyToManyField(
        verbose_name=_("Жанры"), to=Genre, related_name="filmworks"
    )
    title = models.CharField(_("Название"), max_length=255)
    description = models.TextField(_("Описание"), max_length=5000, blank=True)
    creation_date = models.DateField(_("Дата создания фильма"), blank=True)
    certificate = models.TextField(_("Сертификат"), blank=True)
    file_path = models.FileField(_("Файл"), upload_to="film_works/", blank=True)
    rating = models.FloatField(
        _("Рейтинг"), validators=[MinValueValidator(0)], blank=True
    )

    class Meta:
        verbose_name = _("Кинопроизведение")
        verbose_name_plural = _("Кинопроизведения")

    def __str__(self) -> str:
        return self.title
