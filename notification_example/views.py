import asyncio

from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.http import HttpResponse

from notification_example.models import Notification
from sse.response import ServerSideEventHttpResponse


@sync_to_async
def get_user(request):
    # user = request.user

    # for example we use one user
    user, _ = User.objects.get_or_create(username='test')
    if user.is_authenticated and user.is_active:
        return user


@sync_to_async
def send_notification(notification):
    if notification:
        notification.sent = True
        notification.save()


@sync_to_async
def get_notification(user):
    return Notification.objects.filter(
        sent=False, user=user
    ).only('text').first()


async def notifications(request):
    # https://docs.djangoproject.com/en/3.1/topics/http/views/#async-views
    delay = 5

    async def notifications_stream():
        for i in range(12):
            user = await get_user(request)
            if not user:
                return

            notification = await get_notification(user)
            if notification:
                yield notification.text
                await send_notification(notification)
            else:
                yield ''
            await asyncio.sleep(delay)

    return ServerSideEventHttpResponse(notifications_stream(), event_type='message')


def create_message(request):
    user, _ = User.objects.get_or_create(username='test')
    Notification.objects.create(
        user=user,
        text=request.GET.get('message', '')
    )
    return HttpResponse()
