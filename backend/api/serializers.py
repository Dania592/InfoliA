from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password, check_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['pseudo', 'password', 'is_admin']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class LoginSerializer(serializers.Serializer):
    pseudo = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(pseudo=data['pseudo'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Identifiants invalides")

        if not check_password(data['password'], user.password):
            raise serializers.ValidationError("Identifiants invalides")

        return user
