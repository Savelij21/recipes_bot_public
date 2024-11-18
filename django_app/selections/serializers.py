from rest_framework.serializers import ModelSerializer
from .models import ProductsSelection


class ProductsSelectionSerializer(ModelSerializer):
    class Meta:
        model = ProductsSelection
        fields = '__all__'


