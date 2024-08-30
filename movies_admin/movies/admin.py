from django.contrib import admin

from .models import Filmwork, FilmworkType, Genre, Person, PersonRole


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "created", "modified")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "created", "modified")


class PersonRoleInline(admin.TabularInline):
    model = PersonRole
    extra = 0


@admin.register(FilmworkType)
class FilmworkTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    list_display = ("title", "rating", "type", "creation_date", "get_genres")
    inlines = [PersonRoleInline]

    def get_genres(self, obj: Filmwork) -> str:
        return ", ".join(genre.name for genre in obj.genres.all())
