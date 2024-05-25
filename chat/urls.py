from django.urls import path, include
from .API import urls, views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat/', views.chat_main, name='chat'),
    path('profile/', views.profile, name='profile'),
    path('<int:pk>/', views.chat, name='chat_id'),
    path('api/', include('chat.API.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

