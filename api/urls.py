
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, LoginView, dashboard, CourseViewSet, TaskViewSet, change_password, user_profile, task_stats

router = DefaultRouter(trailing_slash=False)
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('dashboard', dashboard, name='dashboard'),
    path('change-password', change_password, name='change-password'),
    path('profile', user_profile, name='profile'),
    path('stats', task_stats, name='task-stats'),
    path('', include(router.urls)),   
]
