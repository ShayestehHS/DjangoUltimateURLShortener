from urls.models import Url, UrlUsage, UrlUser
from rest_framework import serializers
from django.contrib.auth.models import User


class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = ["id","url", "token", "expiration_date"]

class UrlSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = ["url"]


class UrlUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlUser
        fields = ["url", "user"]


class UrlUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlUsage
        fields = ["url", "seen"]


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            "password": {"write_only": True},
        }
    def create(self, validated_data):
        # Create the user and hash the password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [ 'username', 'email']
       
    
