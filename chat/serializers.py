from chat.models import Topic, TopicGroup, TopicMembership, TopicLike
from rest_framework import serializers
from rest_framework.response import Response



class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = ['name', 'created_at', 'updated_at', "id", "moderate"]
    
    def create(self, validated_data):
        user = self.context['user']
        topic, created = Topic.objects.get_or_create(moderate=user, **validated_data)
        return topic



class TopicGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = TopicGroup
        fields = ['group_name', 'topic', "created_at", "updated_at", "id", "group_sid"]
        extra_kwargs = {"topic": {"read_only": True}}

    def create(self, validated_data):
        topic_name = self.context['topic_name']
        topic = Topic.objects.filter(name=topic_name).first()
        topic_group = TopicGroup.objects.create(group_name=validated_data['group_name'], topic=topic)
        return topic_group


class TopicMembershipSerializer(serializers.ModelSerializer):
    topic = serializers.SerializerMethodField()
    class Meta:
        model = TopicMembership
        fields = "__all__"

    def get_topic(self, obj):
        return TopicSerializer(obj.topic).data

class TopicLikeSerializer(serializers.ModelSerializer):
    topic = serializers.SerializerMethodField()
    class Meta:
        model = TopicLike
        fields = "__all__"

    def get_topic(self, obj):
        return TopicSerializer(obj.topic).data
