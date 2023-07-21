from django.urls import path
from .views import logout, register, flushtoken, delete_user
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout, name='logout'),
    path('flushtokens/', flushtoken, name='flushtoken'),
    path('delete_user/', delete_user, name='delete_user'),
]
