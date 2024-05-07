from django.urls import path
from chat.views import (
    CreateTopicView, 
    GetByIdTopic, 
    CreateTopicGroupView, 
    GetByIdTopicGroup,
    Generatetoken,
    LikeTopicAPIView,
    JoinTopicAPIView
)

urlpatterns = [
    
    path('topic/', CreateTopicView.as_view(), name="create_topic"),  
    path('get-by-id-topic/<int:id>/', GetByIdTopic.as_view(), name="get_by_id_topic"),  
    path('topic-group/', CreateTopicGroupView.as_view(), name="create_topic_group"),  
    path('get-by-id-topic-group/<int:id>/', GetByIdTopicGroup.as_view(), name="get_by_id_topic_group"),  
    path('generate-token/',Generatetoken.as_view(), name='generate-token'),

    path('topic/<int:topic_id>/like/', LikeTopicAPIView.as_view(), name='like_topic_api'),
    path('topic/<int:topic_id>/join/', JoinTopicAPIView.as_view(), name='join_topic_api'),
]