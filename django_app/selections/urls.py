
from django.urls import path

from .views import ProductsSelectionModelViewSet


urlpatterns = [

    path('selections/', ProductsSelectionModelViewSet.as_view({
            'get': 'list',
    })),
    path('selections/<int:pk>/', ProductsSelectionModelViewSet.as_view({
            'get': 'retrieve',
    })),

]



