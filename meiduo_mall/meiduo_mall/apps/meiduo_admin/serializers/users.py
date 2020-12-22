import re

from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
            }
        }

    def validate_mobile(self, value):
        if not re.match(r'1[3-9]\d{9}', value):
            raise serializers.ValidationError('手机格式不对')
        return value

    def create(self, validated_data):
        # 方案一
        # user = super().create(validated_data)
        # user.set_password(validated_data['password'])
        # user.save()

        # 方案二
        user = User.objects.create(**validated_data)  # 会自动对password加密
        return user
