
from django.urls import path

from .views import TgUsersModelViewSet


urlpatterns = [

    path('users/', TgUsersModelViewSet.as_view({
            'get': 'list',
            'post': 'create',
    })),
    path('users/active_tg_ids/', TgUsersModelViewSet.as_view({
            'get': 'get_active_tg_ids',
    })),
    path('users/<int:tg_id>/', TgUsersModelViewSet.as_view({
            'get': 'retrieve',
    })),
    path('users/<int:tg_id>/unsubscribe/', TgUsersModelViewSet.as_view({
            'patch': 'unsubscribe_user',
    })),
    path('users/stats/', TgUsersModelViewSet.as_view({
            'get': 'get_users_stats',
    })),

]



