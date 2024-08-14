from rest_framework import serializers
from .models import MyUser, Post, Image

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'image_120x120', 'image_400x400', 'image_800x800']

class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'text', 'user', 'created_at', 'updated_at', 'images']
