from djoser.serializers import UserCreateSerializer as BaseUserCreateSerialzer, UserSerializer as BaseUserSerializer


class UserCreateSerializer(BaseUserCreateSerialzer):
    class Meta(BaseUserCreateSerialzer.Meta):
        fields = ["id", "username", "password",
                  "email", "first_name", "last_name"]


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ["id", "username", "email", "first_name", "last_name"]
