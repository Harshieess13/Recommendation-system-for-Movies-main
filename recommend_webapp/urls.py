from django.contrib import admin
from django.urls import path,include
from recommend_webapp import views
urlpatterns = [
    path('',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('webapp/',views.webapp,name='webapp'),
]