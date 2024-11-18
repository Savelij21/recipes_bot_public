
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import TgUsers
from .serializers import TgUsersSerializer


class TgUsersModelViewSet(ModelViewSet):
    queryset = TgUsers.objects.all().order_by('-created_at')
    serializer_class = TgUsersSerializer

    lookup_field = 'tg_id'

    def create(self, request, *args, **kwargs):
        try:
            user: TgUsers = TgUsers.objects.get(tg_id=request.data.get('tg_id'))
            if user.subscribed:
                return Response(
                    status=status.HTTP_200_OK,
                    data={'detail': f'Пользователь [{user.tg_id}#{user.username}] уже существует в БД и подписан'}
                )
            else:
                user.subscribed = True
                user.save()
                return Response(
                    status=status.HTTP_200_OK,
                    data={'detail': f'Пользователь [{user.tg_id}#{user.username}] уже существует в БД, '
                                    f'но был заново подписан'}
                )
        except TgUsers.DoesNotExist:
            return super().create(request, *args, **kwargs)

    @action(methods=['GET'], detail=False)
    def get_active_tg_ids(self, request):
        ids = TgUsers.objects.filter(subscribed=True).values_list('tg_id', flat=True)
        return Response(status=status.HTTP_200_OK, data={'tg_ids': ids})

    @action(methods=['PATCH'], detail=True)
    def unsubscribe_user(self, request, tg_id: int):
        try:
            user: TgUsers = TgUsers.objects.get(tg_id=tg_id)
            user.subscribed = False
            user.save()
            return Response(
                status=status.HTTP_200_OK,
                data={'detail': f'Подписка для ТГ Пользователя {user.id}#{user.username} отменена'}
            )
        except TgUsers.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={'detail': 'Пользователь не найден'}
            )

    @action(methods=['GET'], detail=False)
    def get_users_stats(self, request):
        all_users = TgUsers.objects.all()
        return Response(
            status=status.HTTP_200_OK,
            data={
                'all': all_users.count(),
                'subscribed': all_users.filter(subscribed=True).count(),
                'unsubscribed': all_users.filter(subscribed=False).count()
            }
        )
