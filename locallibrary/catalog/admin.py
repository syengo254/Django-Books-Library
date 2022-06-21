from django.contrib import admin

# Register your models here.

from .models import Author, Genre, Book, BookInstance, Language


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'due_back', 'status', 'borrower')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book','imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back','borrower')
        }),
    )

admin.site.register(Author, AuthorAdmin)
admin.site.register(Genre)
admin.site.register(Book)
# admin.site.register(BookInstance)
admin.site.register(Language)
