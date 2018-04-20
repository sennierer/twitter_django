from django.urls import path
from .import views


urlpatterns = [
    path('messages/list/<int:project_id>', views.TweetsList.as_view(), name='messages_list'),
    path('accounts/detail/<int:pk>', views.AccountDetail.as_view(), name='account-detail'),
]
