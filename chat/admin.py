from django.contrib import admin
from chat.models import Topic, TopicGroup, TopicMembership, TopicLike

# Register your models here.
admin.site.register(Topic)
admin.site.register(TopicGroup)
admin.site.register(TopicMembership)
admin.site.register(TopicLike)
