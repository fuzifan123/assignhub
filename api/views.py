
from rest_framework import generics, viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render

from .models import User, Course, Task
from .serializers import UserSerializer, LoginSerializer, CourseSerializer, TaskSerializer

# Auth Views
class RegisterView(generics.CreateAPIView):
    """Handles user registration and returns JWT token on success."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate token immediately
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "token": str(refresh.access_token),
            "id": user.id,
            "email": user.email
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    """Authenticates user credentials and returns JWT token."""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "token": str(refresh.access_token),
            "id": user.id,
            "email": user.email
        }, status=status.HTTP_200_OK)

# Dashboard View
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """Returns user's courses and tasks due within the next 24 hours."""
    user = request.user
    
    # Courses
    courses = Course.objects.filter(user=user)
    courses_data = CourseSerializer(courses, many=True).data
    
    # Upcoming Tasks (Next 24h, not done)
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    
    upcoming_tasks = Task.objects.filter(
        user=user,
        deadline__gte=now,
        deadline__lte=tomorrow
    ).exclude(status='done')
    
    upcoming_tasks_data = TaskSerializer(upcoming_tasks, many=True).data
    
    return Response({
        "courses": courses_data,
        "upcoming_tasks": upcoming_tasks_data
    })

# Course ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Task ViewSet
class TaskViewSet(viewsets.ModelViewSet):
    """CRUD operations for tasks with filtering by course, status, and deadline."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)
        
        # Filtering
        course_id = self.request.query_params.get('course_id')
        status_param = self.request.query_params.get('status')
        due_within_days = self.request.query_params.get('due_within_days')
        sort_by = self.request.query_params.get('sort_by', 'deadline')
        order = self.request.query_params.get('order', 'asc')

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if due_within_days:
            try:
                days = int(due_within_days)
                target_date = timezone.now() + timedelta(days=days)
                queryset = queryset.filter(deadline__lte=target_date)
            except ValueError:
                pass
        
        # Sorting
        if sort_by in ['deadline', 'created_at']:
            if order == 'desc':
                sort_by = f'-{sort_by}'
            queryset = queryset.order_by(sort_by)
            
        return queryset

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ['todo', 'doing', 'done']:
            return Response({"detail": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = new_status
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    from .serializers import ChangePasswordSerializer
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    if not user.check_password(serializer.validated_data['old_password']):
        return Response({"detail": "The original password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(serializer.validated_data['new_password'])
    user.save()
    return Response({"detail": "Password modification successful."})

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    if request.method == 'GET':
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })
    elif request.method == 'PUT':
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.save()
        return Response({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_stats(request):
    user = request.user
    from django.utils import timezone

    all_tasks = Task.objects.filter(user=user)
    total = all_tasks.count()
    todo = all_tasks.filter(status='todo').count()
    doing = all_tasks.filter(status='doing').count()
    done = all_tasks.filter(status='done').count()
    overdue = all_tasks.filter(deadline__lt=timezone.now()).exclude(status='done').count()

    course_stats = []
    courses = Course.objects.filter(user=user)
    for course in courses:
        course_tasks = all_tasks.filter(course=course)
        course_total = course_tasks.count()
        course_done = course_tasks.filter(status='done').count()
        course_stats.append({
            'name': course.name,
            'total': course_total,
            'done': course_done,
            'percent': round(course_done / course_total * 100) if course_total > 0 else 0
        })

    return Response({
        'total': total,
        'todo': todo,
        'doing': doing,
        'done': done,
        'overdue': overdue,
        'done_percent': round(done / total * 100) if total > 0 else 0,
        'course_stats': course_stats
    })

def index_view(request):
    return render(request, 'index.html')
