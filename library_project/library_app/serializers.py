from rest_framework import serializers
from .models import Book, Author, Favorite
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from typing import Any, Dict


class RegisterSerializer(serializers.ModelSerializer):
    email: serializers.EmailField = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password: serializers.CharField = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2: serializers.CharField = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> User:
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    author: serializers.PrimaryKeyRelatedField = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())

    class Meta:
        model = Book
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}  # The user is set automatically, so this is read-only
        }

    def create(self, validated_data: Dict[str, Any]) -> Favorite:
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)
