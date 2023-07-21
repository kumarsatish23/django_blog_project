from django.urls import path
from .views import AllPostsView, UserPostsView, UserPostDetailView

urlpatterns = [
    path('allposts/', AllPostsView.as_view(), name='allposts'),
    path('userposts/', UserPostsView.as_view(), name='userposts'),
    path('userposts/<uuid:post_uuid>/', UserPostDetailView.as_view(), name='userpost-detail'),
]
