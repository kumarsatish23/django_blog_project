from rest_framework import serializers
from postapp.models import Post
from userapp.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

class PostSerializers(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)  # Include user details (email and username)

    class Meta:
        model = Post
        fields = "__all__"

    def create(self, validated_data):
        return Post.objects.create(**validated_data)
