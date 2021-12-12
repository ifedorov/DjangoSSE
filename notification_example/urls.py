from django.urls import path
from django.views.generic import TemplateView

from notification_example import views

urlpatterns = [
    path('notifications/', views.notifications, name='notifications'),
    path('create/', views.create_message, name='create_message'),
    path('', TemplateView.as_view(template_name="notification.html"), name='notification'),
]
