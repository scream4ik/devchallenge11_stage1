from django.contrib import admin

from .models import Council, Session, Vote, Deputy, Voice
from .utils import recalc_vote_results


@admin.register(Council)
class CouncilAdmin(admin.ModelAdmin):
    pass


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    list_filter = ('date',)
    date_hierarchy = 'date'


class VoiceAdminInline(admin.TabularInline):
    model = Voice
    extra = 0


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'types', 'council', 'session')
    list_filter = ('types', 'council', 'session')
    search_fields = ('title',)
    inlines = (VoiceAdminInline,)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Пересчитываем результаты голосования
        recalc_vote_results(obj)


@admin.register(Deputy)
class DeputyAdmin(admin.ModelAdmin):
    pass


@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    raw_id_fields = ('vote',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Пересчитываем результаты голосования
        recalc_vote_results(obj.vote)
