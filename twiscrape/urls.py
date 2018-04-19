from django.urls import path
from .import views


urlpatterns = [
    path('list_messages/<int:project_id>', views.TweetsList.as_view(), name='messages_list')
]
