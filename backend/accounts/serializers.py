from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                "This username is already taken."
            )

        return username

    def create(self, validated_data):
        # >>> IMPORTANT: create_user() hashes the password correctly.
        # Using User.objects.create(**validated_data) directly would
        # store the password in plain text — a real security bug.
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )