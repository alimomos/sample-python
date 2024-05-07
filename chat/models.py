from django.db import models
from twilio.rest import Client
from django.db.models.signals import post_save
from django.dispatch import receiver
import twilio.rest
from twilio.jwt.access_token import AccessToken
import os
from account.models import User

# Create your models here.

class Common(models.Model):  # COMM0N
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Topic(Common):
    name = models.CharField(max_length=200, unique=True)
    moderate = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.name


class TopicGroup(Common):
    group_name = models.CharField(max_length=200)
    group_sid = models.CharField(max_length=225, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)



@receiver(post_save, sender=TopicGroup)
def create_group_name(sender, instance, **kwargs):
    try:
        TWILIO_ACCOUNT_SID=os.environ.get('tWILIO_aCCOUNT_sID')
        TWILIO_API_KEY=os.environ.get('tWILIO_aPI_kEY')
        TWILIO_API_SECRET=os.environ.get('tWILIO_aPI_sECRET')

        twilio_client = twilio.rest.Client(TWILIO_API_KEY, TWILIO_API_SECRET, TWILIO_ACCOUNT_SID)

        room_name = f"{instance.topic.name}_{instance.group_name}"
        try:
            twilio_client.video.rooms(room_name).fetch()
        except twilio.base.exceptions.TwilioRestException as e:
            if e.status == 404:
                create_room = twilio_client.video.rooms.create(unique_name=room_name, type="group")
                instance.group_sid = create_room.sid
                print("Created Room", create_room)
                if create_room:
                    instance.is_public = True
                instance.save()
            else:
                print("Error", e)
    except Exception as e:
        print("Error define ", e)


class TopicMembership(Common):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="members")
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} has joined {self.topic.name}"
    class Meta:
        unique_together = ('user', 'topic')


class TopicLike(Common):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="liked_by")
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user.get_full_name()} likes {self.topic.name}"
    class Meta:
        unique_together = ('user', 'topic')

