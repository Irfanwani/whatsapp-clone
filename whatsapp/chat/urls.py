from django.urls import path, include
from .views import LoginView, ValidateOtp, CreateRoomView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login', LoginView.as_view()),
    path('validate', ValidateOtp.as_view()),
    path('api', include('knox.urls')),
    path('createroom', CreateRoomView.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)