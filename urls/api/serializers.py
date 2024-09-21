from urls.models import Url, UrlUsage
from rest_framework import serializers
from django.contrib.auth.models import User


class UrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = ["id", "user", "url","new_url", "token", "expiration_date"]



class UrlSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Url
        fields = ["user", "url"]

    def validate(self, attrs):
        user = self.context['request'].user 
        if Url.objects.filter(user=user, url=attrs).exists():
            raise serializers.ValidationError("This URL already exists for this user.")
        return attrs


class UrlUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlUsage
        fields = ["url", "seen"]


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        # Create the user and hash the password
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]
