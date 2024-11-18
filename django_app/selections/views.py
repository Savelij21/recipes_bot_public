
from rest_framework.viewsets import ModelViewSet

from .models import ProductsSelection
from .serializers import ProductsSelectionSerializer


class ProductsSelectionModelViewSet(ModelViewSet):
    queryset = ProductsSelection.objects.all().order_by('num')
    serializer_class = ProductsSelectionSerializer
