
from rest_framework import serializers
from .models import User, Course, Task
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password validation rules."""
    class Meta:
        model = User
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("The password length must be at least eight characters.")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("The password must contain at least one capital letter.")
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("The password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("The password must contain at least one digit.")
        return value


    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'name', 'created_at')

class TaskSerializer(serializers.ModelSerializer):
    """Serializer for task CRUD with course ownership verification."""
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source='course', write_only=False
    )

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'deadline', 'status', 'course_id', 'course_name', 'created_at', 'updated_at')

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("The title of the task cannot be left blank.")
        return value.strip()

    def create(self, validated_data):
        # We need to inject the user from the context
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
             raise serializers.ValidationError("User context missing")
        user = request.user
        
        # Verify course belongs to user
        course = validated_data.get('course')
        if course.user != user:
             raise serializers.ValidationError("Invalid course_id or course does not belong to user")
        
        validated_data['user'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Check course ownership if changing course
        if 'course' in validated_data:
            course = validated_data['course']
            if course.user != instance.user:
                 raise serializers.ValidationError("Invalid course_id or course does not belong to user")
        return super().update(instance, validated_data)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("The password length must be at least eight characters.")
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("The password must contain at least one capital letter.")
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("The password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("The password must contain at least one digit.")
        return value

