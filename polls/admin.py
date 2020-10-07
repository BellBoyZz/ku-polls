"""Admin site for KU-Polls."""

from django.contrib import admin

from .models import Choice, Question

# Register your models here.

class ChoiceInline(admin.TabularInline):
    """Class for in-line choice."""

    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    """Class for admin question."""

    fieldsets = [
        (None, {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date', 'end_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)
