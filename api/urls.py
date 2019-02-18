from django.urls import path
from . import views


# SET THE NAMESPACE!
app_name = 'api'

urlpatterns = [
    path('register/',views.register,name='register'),
    path('user_login/',views.user_login,name='user_login'),
    path('face/recognition', views.verify_face_recognition, name='verify_face_recognition')
]