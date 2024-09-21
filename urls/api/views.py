from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from urls.models import Url, UrlUser, UrlUsage
from drf_spectacular.utils import extend_schema
from django.contrib.auth.models import User
from urls import tasks
from rest_framework.response import Response
from .serializers import (
    UrlSerializer,
    UrlUsageSerializer,
    UrlUserSerializer,
    UserCreateSerializer,
    UserEditSerializer,
    UrlSerializerCreate,
)
from django import shortcuts


class UserView(viewsets.ViewSet):
    def get_queryset(self):
        return User.objects.all()

    @extend_schema(
        request=UserCreateSerializer,
        responses={201: UserCreateSerializer},
        description="Endpoint for user registration",
    )
    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            User.objects.create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        data = self.get_queryset()
        serilizer = UserCreateSerializer(data, many=True)
        return Response(serilizer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        data = self.get_queryset()
        user = shortcuts.get_object_or_404(data, pk=pk)
        serilizer = UserCreateSerializer(user)
        return Response(serilizer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserEditSerializer,
        responses={201: UserEditSerializer},
        description="edit user",
    )
    def update(self, request, pk=None):
        data = self.get_queryset()
        user = shortcuts.get_object_or_404(data, pk=pk)
        update_serilizer = UserEditSerializer(
            instance=user, data=request.data, partial=True
        )
        if update_serilizer.is_valid():
            update_serilizer.save()
            return Response(update_serilizer.data, status=status.HTTP_200_OK)
        return Response(update_serilizer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        data = self.get_queryset()
        user = shortcuts.get_object_or_404(data, pk=pk)
        if user:
            user.delete()
            return Response("user deleted", status=status.HTTP_200_OK)
        return Response("user not found", status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["get"])
    def return_all_url_for_one_user(self, request, pk):
        data = self.get_queryset()
        user = shortcuts.get_object_or_404(data, pk=pk)
        urls = UrlUser.objects.filter(user=user)
        serializer = UrlSerializer(urls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RedirectAPIView(viewsets.ViewSet):
    authorization_classes = []

    def get_queryset(self):
        return Url.objects.all()

    def list(self, request):
        data = self.get_queryset()
        serilizer = UrlSerializer(data, many=True)
        return Response(serilizer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def get_data(self, request, *args, **kwargs):
        token = self.kwargs.get("pk")
        if len(token) != settings.URL_SHORTENER_MAXIMUM_URL_CHARS:
            raise NotFound({"token": "Given token not found."})

        url_obj = Url.objects.all_actives().filter(token=token).only("url").first()
        if not url_obj:
            return HttpResponseRedirect(redirect_to=settings.URL_SHORTENER_404_PAGE)

        tasks.log_the_url_usages.delay(
            url_obj.pk, now().strftime("%Y-%m-%d %H:%M:%S %z'")
        )
        return HttpResponseRedirect(redirect_to=url_obj.url)

    @action(detail=False, methods=["get"])
    def get_short_url_data(self, short_url):
        pass

    @action(detail=False, methods=["get"])
    def short_url_to_general_page(self, short_url):
        pass

    @extend_schema(
        request=UrlUserSerializer,
        responses={201: UrlUserSerializer},
        description="Endpoint for creating a URL user entry",
    )
    def create(self, request):
        serializer = UrlUserSerializer(data=request.data)
        # long_url = request.data.get("long_url")
        # user = request.data.get("user_id")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=UrlSerializerCreate,
        responses={201: UrlSerializer},
        description="generate short url",
    )
    @action(detail=False, methods=["post"])
    def generate_token(self, request):
        serializer = UrlSerializerCreate(data=request.data)
        if serializer.is_valid():
            calculation = serializer.save()
            tasks.generate_token.delay(
                calculation.id,
            )
            response_serilizer = UrlSerializer(calculation)
            return Response(response_serilizer.data, status=status.HTTP_201_CREATED)
        return Response(response_serilizer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["put"])
    def change_short_url_with_long(self, request):
        pass

    @action(detail=True, methods=["put"])
    def change_short_url_with_short(self, request):
        pass

    @action(detail=True, methods=["delete"])
    def delete_short_url_with_short(self, request):
        pass

    @action(detail=True, methods=["delete"])
    def delete_short_url_with_long(self, request):
        pass
