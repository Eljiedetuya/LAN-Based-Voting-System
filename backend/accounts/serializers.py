from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from .models import User
from elections.models import Election

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'student_id', 'display_name', 'course', 'year_level', 'role', 'is_active', 'must_change_password']

class CurrentUserSerializer(UserSummarySerializer):
    can_create_admin = serializers.SerializerMethodField()
    class Meta(UserSummarySerializer.Meta):
        fields = UserSummarySerializer.Meta.fields + ['can_create_admin']
    def get_can_create_admin(self, obj):
        return bool(obj.is_superuser)

class StudentCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    course = serializers.ChoiceField(choices=User.Course.choices, required=True)
    year_level = serializers.ChoiceField(choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4')], required=True)
    election = serializers.PrimaryKeyRelatedField(queryset=Election.objects.filter(status=Election.Status.DRAFT), required=False, allow_null=True, write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'student_id', 'display_name', 'course', 'year_level', 'password', 'is_active', 'election']
        read_only_fields = ['id']

    def validate_student_id(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Student ID is required.')
        return value.strip()

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('election', None)
        return User.objects.create_user(password=password, role=User.Role.STUDENT,
            must_change_password=True, **validated_data)

class StaffCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    role = serializers.ChoiceField(choices=[(User.Role.MONITOR, 'Election Monitor'), (User.Role.ADMIN, 'Administrator')])
    class Meta:
        model = User
        fields = ['id', 'username', 'display_name', 'role', 'password']
        read_only_fields = ['id']
    def validate_password(self, value):
        validate_password(value)
        return value
    def validate(self, attrs):
        if attrs['role'] == User.Role.ADMIN and not self.context['request'].user.is_superuser:
            raise PermissionDenied('Only the primary administrator can create administrator accounts.')
        return attrs
    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data['role']
        return User.objects.create_user(password=password, must_change_password=True,
            is_staff=(role == User.Role.ADMIN), **validated_data)

class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError({'current_password': 'Current password is incorrect.'})
        if attrs['current_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password': 'Choose a password different from the temporary password.'})
        validate_password(attrs['new_password'], user=user)
        return attrs

class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['display_name', 'course', 'year_level', 'is_active']
