from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "current_password"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def create(self, validated_data):
        validated_data.pop("current_password", None)
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        current_password = validated_data.pop("current_password", None)
        new_password = validated_data.pop("password", None)

        if not current_password:
            raise serializers.ValidationError({"current_password": "Current password is required to make changes."})
        if not instance.check_password(current_password):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})

        if new_password:
            instance.set_password(new_password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user_id"] = self.user.id
        data["email"] = self.user.email
        data["username"] = self.user.username
        return data