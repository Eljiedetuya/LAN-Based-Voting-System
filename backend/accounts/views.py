from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.db import transaction
from elections.models import Election
from elections.services import ensure_draft
from voting.models import VoterParticipation
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, PermissionDenied
from .models import User
from .serializers import (UserSummarySerializer, CurrentUserSerializer, StudentCreateSerializer,
    StudentUpdateSerializer, StaffCreateSerializer, PasswordChangeSerializer)
from core.permissions import IsAdmin
from audit.utils import record

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def get(self, request):
        return Response({'message': 'CSRF cookie issued'})

@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        if not isinstance(username, str) or not isinstance(password, str):
            raise ValidationError({'credentials': 'Invalid credentials.'})
        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_active:
            # Authentication failures intentionally reveal no account-existence details.
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed('Invalid credentials.')
        login(request, user)
        return Response({'user': CurrentUserSerializer(user).data})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out'})

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)

@method_decorator(csrf_protect, name='dispatch')
class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.must_change_password = False
        user.save(update_fields=['password', 'must_change_password'])
        update_session_auth_hash(request, user)
        return Response(CurrentUserSerializer(user).data)

class SmallPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class StudentListCreateView(ListCreateAPIView):
    permission_classes = [IsAdmin]
    pagination_class = SmallPagination
    def get_queryset(self):
        qs = User.objects.filter(role=User.Role.STUDENT).order_by('id')
        if self.request.query_params.get('include_inactive') != 'true':
            qs = qs.filter(is_active=True)
        q = self.request.query_params.get('search', '').strip()[:100]
        return qs.filter(Q(username__icontains=q) | Q(student_id__icontains=q) | Q(display_name__icontains=q)) if q else qs
    def get_serializer_class(self):
        return StudentCreateSerializer if self.request.method == 'POST' else UserSummarySerializer
    def perform_create(self, serializer):
        election = serializer.validated_data.get('election')
        with transaction.atomic():
            if election:
                election = Election.objects.select_for_update().get(pk=election.pk)
                ensure_draft(election)
            student = serializer.save()
            if election:
                VoterParticipation.objects.get_or_create(election=election, user=student)
                record(self.request.user, 'ELIGIBILITY_ADDED', 'ELECTION', election.id)
        record(self.request.user, 'STUDENT_CREATED', 'USER', student.id)

class StudentDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]
    http_method_names = ['get', 'patch', 'head', 'options']
    def get_queryset(self):
        return User.objects.filter(role=User.Role.STUDENT)
    def get_serializer_class(self):
        return StudentUpdateSerializer if self.request.method == 'PATCH' else UserSummarySerializer
    def perform_update(self, serializer):
        if 'is_active' in serializer.validated_data and not serializer.validated_data['is_active']:
            if VoterParticipation.objects.filter(user=serializer.instance, election__status=Election.Status.OPEN).exists():
                raise ValidationError({'is_active': 'Cannot deactivate an eligible voter during an open election.'})
        student = serializer.save()
        record(self.request.user, 'STUDENT_UPDATED', 'USER', student.id)

class StaffAccountListCreateView(ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = UserSummarySerializer
    def get_queryset(self):
        return User.objects.filter(role__in=[User.Role.ADMIN, User.Role.MONITOR]).order_by('id')
    def get_serializer_class(self):
        return StaffCreateSerializer if self.request.method == 'POST' else UserSummarySerializer
    def perform_create(self, serializer):
        staff = serializer.save()
        record(self.request.user, 'STAFF_ACCOUNT_CREATED', 'USER', staff.id)
