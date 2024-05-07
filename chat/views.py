from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from chat.models import Topic, TopicGroup, TopicMembership, TopicLike
from chat.serializers import TopicSerializer, TopicGroupSerializer
from django.conf import settings
from twilio.jwt.access_token import AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from twilio.jwt.access_token.grants import VideoGrant
import os
from django.shortcuts import get_object_or_404


class CreateTopicView(APIView):

    def check_topic_exists(self, topic_name):
        try:
            Topic.objects.get(name=topic_name)
            return False
        except Topic.DoesNotExist:
            return True

    def get(self, request, format=None):
        topics = Topic.objects.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        if self.check_topic_exists(request.data['name']):
            serializer = TopicSerializer(data=request.data, context={"user": request.user})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Sorry, that name already exists. Create a topic with a different name"}, status=status.HTTP_400_BAD_REQUEST)

class GetByIdTopic(APIView):

    def get(self, request, id):
        try:
            get_by_id_topic = Topic.objects.get(id=id)
        except Topic.DoesNotExist:
            return Response({'result':'error', 'message':'invalid id'})
        serializer = TopicSerializer(get_by_id_topic)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id):
        try:
            instance = Topic.objects.get(id=id)
        except Topic.DoesNotExist:
            return Response({'result':'error', 'message':'invalid id'})
        serializer = TopicSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {'result':'success', 'message':'Topic updated successfully'}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {'result': 'error', 'message':serializer.errors}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, id):
        try:
            instance = Topic.objects.get(id=id)
        except Topic.DoesNotExist:
            return Response({'result':'error', 'message':'invalid id'})
        instance.delete()
        data = {'result':'success', 'message':'Topic deleted successfully'}
        return Response(data=data, status=status.HTTP_200_OK)
    

class CreateTopicGroupView(APIView):

    def check_user_is_moderate(self, topic_name):
        try:
            moderate = Topic.objects.get(name=topic_name).moderate
            return moderate == self.request.user
        except Topic.DoesNotExist:
            return False
        
    def check_topic_joined(self, topic_name):
        try:
            joined = TopicMembership.objects.get(user_id=self.request.user.id, topic__name=topic_name)
            return True
        except Exception as e:
            return False

    def check_topic_liked(self, topic_name):
        try:
            liked = TopicLike.objects.get(user_id=self.request.user.id, topic__name=topic_name)
            return True
        except Exception as e:
            return False


    def get(self, request, format=None):
        try:
            get_name = request.GET['name']
        except:
            return Response({'error':'Topic name is required'})
        instance = TopicGroup.objects.filter(topic__name=get_name, is_public=True)
        serializer = TopicGroupSerializer(instance, many=True)
        topic = Topic.objects.filter(name=get_name).first()
        random_topic = Topic.objects.exclude(id=topic.id).order_by('?')[:6]
        return Response({
            "topic": serializer.data,
            "id": topic.id,
            "randome_topic": TopicSerializer(random_topic, many=True).data,
            "moderate": self.check_user_is_moderate(get_name),
            "is_liked": self.check_topic_liked(get_name),
            "is_joined": self.check_topic_joined(get_name),
        })
    
    def check_topic(self, topic_name):
        try:
            return Topic.objects.get(name=topic_name)
        except Topic.DoesNotExist:
            return None

    def post(self, request, format=None):
        try:
            get_name = request.GET['name']
        except:
            return Response({'error':'Topic name is required'})
        if self.check_topic(get_name):
            serializer = TopicGroupSerializer(data=request.data, context={"topic_name": get_name})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'msg': 'Invalid Topic name'})
    


class GetByIdTopicGroup(APIView):

    def get(self, request, id):
        try:
            instance = TopicGroup.objects.get(id=id)
        except TopicGroup.DoesNotExist:
            return Response({'result':'error', 'message':'invalid id'})
        serializer = TopicGroupSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id):
        try:
            instance = TopicGroup.objects.get(id=id)
        except TopicGroup.DoesNotExist:
            return Response({'result':'error', 'message':'invalid id'})
        serializer = TopicGroupSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = {'result':'success', 'message':'Topic Group updated successfully'}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            data = {'result': 'error', 'message':serializer.errors}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, id):
        try:
            instance = TopicGroup.objects.get(id=id)
        except TopicGroup.DoesNotExist:
            return Response({'result':'error', 'message':'invalid id'})
        instance.delete()
        data = {'result':'success', 'message':'Topic Group deleted successfully'}
        return Response(data=data, status=status.HTTP_200_OK)
        
class Generatetoken(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_access_token(self, room_name, identity):
        TWILIO_ACCOUNT_SID=os.environ.get('tWILIO_aCCOUNT_sID')
        TWILIO_API_KEY=os.environ.get('tWILIO_aPI_kEY')
        TWILIO_API_SECRET=os.environ.get('tWILIO_aPI_sECRET')

        # create the access token
        access_token = AccessToken(
            TWILIO_ACCOUNT_SID, TWILIO_API_KEY, TWILIO_API_SECRET, identity=identity
        )
        # create the video grant
        video_grant = VideoGrant(room=room_name)
        # Add the video grant to the access token
        access_token.add_grant(video_grant)
        return access_token

    def get(self, request):
        room_sid = request.GET.get('room_sid')
        identity = request.GET.get('identity')
        room = TopicGroup.objects.filter(group_sid=room_sid).first()
        token = self.get_access_token(f"{room.topic.name}_{room.group_name}", identity=identity)
        if token:
            return Response({'token': token.to_jwt()})
        else:
            return Response({'error':'Something get wrong'})


class LikeTopicAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        like, created = TopicLike.objects.get_or_create(user=request.user, topic=topic)

        if created:
            # If the like is new, it is set to active by default (see model)
            return Response({'message': 'liked'}, status=status.HTTP_201_CREATED)
        else:
            like.delete()
            return Response({'message': 'like status changed'}, status=status.HTTP_200_OK)


class JoinTopicAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, topic_id):
        topic = get_object_or_404(Topic, id=topic_id)
        membership, created = TopicMembership.objects.get_or_create(user=request.user, topic=topic)

        if created:
            return Response({'message': 'topic joined'}, status=status.HTTP_201_CREATED)
        else:
            membership.delete()
            return Response({'message': 'topic leaved'}, status=status.HTTP_200_OK)