from rest_framework import serializers

from core.models import User


class EmailAuthorizationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password')
