from rest_framework.serializers import ModelSerializer
from .models import TgUsers


class TgUsersSerializer(ModelSerializer):
    class Meta:
        model = TgUsers
        fields = '__all__'


