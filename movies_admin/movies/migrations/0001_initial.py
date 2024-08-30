# Generated by Django 5.1 on 2024-08-30 04:04

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FilmworkType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создано"),
                ),
                (
                    "modified",
                    models.DateTimeField(auto_now=True, verbose_name="Обновлено"),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
            ],
            options={
                "verbose_name": "Тип кинопроизведения",
                "verbose_name_plural": "Типы кинопроизведений",
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создано"),
                ),
                (
                    "modified",
                    models.DateTimeField(auto_now=True, verbose_name="Обновлено"),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                (
                    "description",
                    models.TextField(
                        blank=True, max_length=5000, verbose_name="Описание"
                    ),
                ),
            ],
            options={
                "verbose_name": "Жанр",
                "verbose_name_plural": "Жанры",
            },
        ),
        migrations.CreateModel(
            name="Filmwork",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создано"),
                ),
                (
                    "modified",
                    models.DateTimeField(auto_now=True, verbose_name="Обновлено"),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                (
                    "description",
                    models.TextField(
                        blank=True, max_length=5000, verbose_name="Описание"
                    ),
                ),
                (
                    "creation_date",
                    models.DateField(blank=True, verbose_name="Дата создания фильма"),
                ),
                (
                    "certificate",
                    models.TextField(blank=True, verbose_name="Сертификат"),
                ),
                (
                    "file_path",
                    models.FileField(
                        blank=True, upload_to="film_works/", verbose_name="Файл"
                    ),
                ),
                (
                    "rating",
                    models.FloatField(
                        blank=True,
                        validators=[django.core.validators.MinValueValidator(0)],
                        verbose_name="Рейтинг",
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="films",
                        to="movies.filmworktype",
                        verbose_name="Тип кинопроизведения",
                    ),
                ),
                (
                    "genres",
                    models.ManyToManyField(
                        related_name="filmworks",
                        to="movies.genre",
                        verbose_name="Жанры",
                    ),
                ),
            ],
            options={
                "verbose_name": "Кинопроизведение",
                "verbose_name_plural": "Кинопроизведения",
            },
        ),
    ]
