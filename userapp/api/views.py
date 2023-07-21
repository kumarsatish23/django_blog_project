from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken , RefreshToken
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


User = get_user_model()

@swagger_auto_schema(method='post', request_body=UserSerializer)  # Add this line
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])  # Requires admin user to access this endpoint
def flushtoken(request):
    try:
        # Use `timezone.now()` instead of `datetime.now()` for correct timezone handling
        OutstandingToken.objects.filter(expires_at__lt=timezone.now()).delete()
        BlacklistedToken.objects.filter(blacklisted_at__lt=timezone.now()).delete()
        return Response({'message': 'Outdated tokens are flushed'}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # Requires authenticated user to access this endpoint
def delete_user(request):
    user_id = request.user.id
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({"message": "User was deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
    }),
    responses={
        status.HTTP_204_NO_CONTENT: openapi.Response(description="User was logged out successfully"),
        status.HTTP_400_BAD_REQUEST: openapi.Response(description="Invalid refresh token"),
        status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(description="Internal server error"),
    }
)
@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            # Blacklist both access and refresh tokens
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)