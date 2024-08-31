from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Filmwork, FilmworkType, Genre, GenreFilmwork, Person, PersonFimwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "created_at", "updated_at")


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    extra = 0


class PersonFimworkInline(admin.TabularInline):
    model = PersonFimwork
    extra = 0


@admin.register(FilmworkType)
class FilmworkTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "rating",
        "type",
        "creation_date",
        "get_genres",
        "created_at",
        "updated_at",
    )
    list_filter = ("type", "creation_date")
    search_fields = ("title", "description", "id")

    inlines = [GenreFilmworkInline, PersonFimworkInline]

    @admin.action(description=_("Жанры"))
    def get_genres(self, obj: Filmwork) -> str:
        return ", ".join(genre.name for genre in obj.genres.all())[:50]
