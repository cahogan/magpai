from django.contrib import admin
from core.models import Game, Question, Judge, QuestionResponse


admin.site.register(Game)
admin.site.register(Question)
admin.site.register(Judge)
admin.site.register(QuestionResponse)
