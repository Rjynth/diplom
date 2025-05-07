from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from easy_thumbnails.files import get_thumbnailer

from core.models import Profile

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Пользователь с таким email уже зарегистрирован."
            )
        ]
    )
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        # Берём email как username
        email = validated_data['email']
        validated_data['username'] = email

        return User.objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    avatar_small = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('avatar', 'avatar_small', 'default_contact')

    def get_avatar_small(self, obj):
        if not obj.avatar:
            return None
        thumb = get_thumbnailer(obj.avatar).get_thumbnail('avatar_small')
        return thumb.url