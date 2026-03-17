from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, Course, Task

class AMSTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Test1234'
        )
        self.client.force_authenticate(user=self.user)

    def test_user_registration(self):
        """Test user registration"""
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/register', {
            'email': 'newuser@example.com',
            'password': 'NewPass123'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        """Test user login"""
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/login', {
            'email': 'test@example.com',
            'password': 'Test1234'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_creation(self):
        """Test course creation and retrieval"""
        response = self.client.post('/api/courses', {'name': 'Math'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Math')

    def test_task_creation(self):
        """Test task creation with deadline"""
        course = Course.objects.create(name='Science', user=self.user)
        deadline = (timezone.now() + timedelta(days=3)).isoformat()
        response = self.client.post('/api/tasks', {
            'title': 'Lab Report',
            'course_id': course.id,
            'deadline': deadline,
            'status': 'todo'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_task_status_update(self):
        """Test updating task status"""
        course = Course.objects.create(name='History', user=self.user)
        task = Task.objects.create(
            title='Essay',
            course=course,
            user=self.user,
            deadline=timezone.now() + timedelta(days=2),
            status='todo'
        )
        response = self.client.patch(f'/api/tasks/{task.id}/status', {'status': 'done'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'done')

    def test_dashboard(self):
        """Test dashboard returns courses and upcoming tasks"""
        response = self.client.get('/api/dashboard')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('courses', response.data)
        self.assertIn('upcoming_tasks', response.data)