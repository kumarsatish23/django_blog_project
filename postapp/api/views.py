from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from postapp.models import Post
from .serializers import PostSerializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView
from PIL import Image
from io import BytesIO

class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        operation_description="Get access token",
        responses={status.HTTP_200_OK: "Access token and refresh token"}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class BaseUserPostsView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

class AllPostsView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializers(posts, many=True)
        return Response(serializer.data)

class UserPostsView(BaseUserPostsView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get user's posts",
        responses={status.HTTP_200_OK: PostSerializers(many=True)},
        security=[{"Bearer": []}]
    )
    def get(self, request):
        posts = self.get_queryset()
        serializer = PostSerializers(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new post",
        responses={status.HTTP_201_CREATED: PostSerializers},
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(name="title", in_=openapi.IN_FORM, required=True, type=openapi.TYPE_STRING),
            openapi.Parameter(name="content", in_=openapi.IN_FORM, required=True, type=openapi.TYPE_STRING),
            openapi.Parameter(name="images", in_=openapi.IN_FORM, required=False, type=openapi.TYPE_FILE),
        ],
    )
    def post(self, request):
        serializer = PostSerializers(data=request.data)
        if serializer.is_valid():
            # Compress the image and save as PNG only if 'images' key is present in request.FILES
            image_file = request.FILES.get('images')
            if image_file:
                compressed_image = self.compress_image(image_file)
                serializer.validated_data['images'] = compressed_image

            # Set the author field to the authenticated user
            serializer.validated_data['author'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def compress_image(self, image_file):
        image = Image.open(image_file)

        # Convert the image to RGB mode if it's not already in that mode
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Perform quantization to reduce the number of colors and optimize the PNG format
        quantized_image = image.quantize(method=2)

        # Save the quantized image to a file-like object
        output_io = BytesIO()
        quantized_image.save(output_io, format='PNG', optimize=True)

        return output_io.getvalue()

class UserPostDetailView(BaseUserPostsView):
    @swagger_auto_schema(
        operation_description="Delete a post",
        responses={status.HTTP_204_NO_CONTENT: "Post deleted successfully"},
        security=[{"Bearer": []}]
    )
    def delete(self, request, post_uuid):
        try:
            post = self.get_queryset().get(id=post_uuid)
        except Post.DoesNotExist:
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Update a post",
        responses={status.HTTP_200_OK: PostSerializers},
        security=[{"Bearer": []}],
        manual_parameters=[
            openapi.Parameter(name="title", in_=openapi.IN_FORM, required=True, type=openapi.TYPE_STRING),
            openapi.Parameter(name="content", in_=openapi.IN_FORM, required=True, type=openapi.TYPE_STRING),
            openapi.Parameter(name="images", in_=openapi.IN_FORM, required=False, type=openapi.TYPE_FILE),
        ],
    )
    def put(self, request, post_uuid):
        try:
            post = self.get_queryset().get(id=post_uuid)
        except Post.DoesNotExist:
            return Response("Post not found", status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializers(post, data=request.data)

        if serializer.is_valid():
            # Perform image compression and save as PNG only if 'images' key is present in request.FILES
            image_file = request.FILES.get('images')
            if image_file:
                compressed_image = self.compress_image(image_file)
                serializer.validated_data['images'] = compressed_image

            # Set the author field to the authenticated user
            serializer.validated_data['author'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
