from django.contrib import admin

from tours import models


@admin.register(models.Tour)
class TourAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Guide)
class GuideAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    pass
