from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from voting.models import VoterParticipation
from core.permissions import IsAdmin, IsStudent
from audit.utils import record
from .models import Election, Position, Candidate
from .serializers import ElectionSerializer, PositionSerializer, CandidateSerializer, PublicCandidateSerializer, BulkEligibilityFilterSerializer
from .services import ensure_draft, open_election, close_election

class AdminElectionList(ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = ElectionSerializer
    queryset = Election.objects.order_by('-id')
    def perform_create(self, serializer):
        election = serializer.save()
        record(self.request.user, 'ELECTION_CREATED', 'ELECTION', election.id)

class AdminElectionDetail(RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = ElectionSerializer
    queryset = Election.objects.all()
    http_method_names = ['get', 'patch', 'head', 'options']
    @transaction.atomic
    def perform_update(self, serializer):
        election = Election.objects.select_for_update().get(pk=serializer.instance.pk)
        ensure_draft(election)
        serializer.instance = election
        updated = serializer.save()
        record(self.request.user, 'ELECTION_UPDATED', 'ELECTION', updated.id)

class ElectionLifecycle(APIView):
    permission_classes = [IsAdmin]
    def post(self, request, pk, action):
        get_object_or_404(Election, pk=pk)
        if action == 'open': election = open_election(pk, request.user)
        elif action == 'close': election = close_election(pk, request.user)
        else: raise ValidationError('Invalid lifecycle action.')
        return Response(ElectionSerializer(election).data)

class PositionListCreate(ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = PositionSerializer
    def get_queryset(self):
        return Position.objects.filter(election_id=self.kwargs['election_id'])
    @transaction.atomic
    def perform_create(self, serializer):
        election = get_object_or_404(Election.objects.select_for_update(), pk=self.kwargs['election_id'])
        ensure_draft(election)
        item = serializer.save(election=election)
        record(self.request.user, 'POSITION_CREATED', 'POSITION', item.id)

class PositionDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = PositionSerializer
    queryset = Position.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    @transaction.atomic
    def perform_update(self, serializer):
        election = Election.objects.select_for_update().get(pk=serializer.instance.election_id)
        item = Position.objects.select_for_update().get(pk=serializer.instance.pk)
        ensure_draft(election)
        serializer.instance = item
        serializer.save(election=election)
        record(self.request.user, 'POSITION_UPDATED', 'POSITION', item.id)
    @transaction.atomic
    def perform_destroy(self, instance):
        election = Election.objects.select_for_update().get(pk=instance.election_id)
        ensure_draft(election)
        if instance.candidates.exists():
            raise ValidationError('Remove candidates before deleting this position.')
        record(self.request.user, 'POSITION_DELETED', 'POSITION', instance.id)
        instance.delete()

class CandidateListCreate(ListCreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = CandidateSerializer
    def get_queryset(self):
        q = Candidate.objects.select_related('position__election').order_by('id')
        election = self.request.query_params.get('election_id')
        return q.filter(position__election_id=election) if election and election.isdecimal() else q
    @transaction.atomic
    def perform_create(self, serializer):
        position = serializer.validated_data['position']
        election = Election.objects.select_for_update().get(pk=position.election_id)
        ensure_draft(election)
        candidate = serializer.save()
        record(self.request.user, 'CANDIDATE_CREATED', 'CANDIDATE', candidate.id)

class CandidateDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    serializer_class = CandidateSerializer
    queryset = Candidate.objects.all()
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    @transaction.atomic
    def perform_update(self, serializer):
        source_election = Election.objects.select_for_update().get(pk=serializer.instance.position.election_id)
        candidate = Candidate.objects.select_for_update().get(pk=serializer.instance.pk)
        ensure_draft(source_election)
        new_position = serializer.validated_data.get('position', candidate.position)
        if new_position.election_id != source_election.id:
            raise ValidationError({'position': 'Changing a candidate to a different election is not supported.'})
        serializer.instance = candidate
        serializer.save()
        record(self.request.user, 'CANDIDATE_UPDATED', 'CANDIDATE', candidate.id)
    @transaction.atomic
    def perform_destroy(self, instance):
        election = Election.objects.select_for_update().get(pk=instance.position.election_id)
        ensure_draft(election)
        record(self.request.user, 'CANDIDATE_DELETED', 'CANDIDATE', instance.id)
        instance.delete()

class PublishedElections(APIView):
    permission_classes = [IsStudent]
    def get(self, request):
        ids = VoterParticipation.objects.filter(user=request.user).values_list('election_id', flat=True)
        qs = Election.objects.filter(pk__in=ids, status=Election.Status.OPEN)
        return Response(ElectionSerializer(qs, many=True).data)

class PublishedCandidates(APIView):
    permission_classes = [IsStudent]
    def get(self, request, pk):
        election = get_object_or_404(Election, pk=pk, status=Election.Status.OPEN)
        get_object_or_404(VoterParticipation, election=election, user=request.user)
        items = Candidate.objects.filter(position__election=election).order_by('position__display_order', 'id')
        positions = list(Position.objects.filter(election=election).values('id', 'name', 'display_order'))
        return Response({'positions': positions, 'candidates': PublicCandidateSerializer(items, many=True).data})

class EligibilityListCreate(APIView):
    permission_classes = [IsAdmin]
    def get(self, request, pk):
        get_object_or_404(Election, pk=pk)
        qs = VoterParticipation.objects.filter(election_id=pk).select_related('user').order_by('user_id')
        return Response([{
            'user_id': x.user_id,
            'student_id': x.user.student_id,
            'display_name': x.user.display_name,
            'course': x.user.course,
            'year_level': x.user.year_level,
            'has_voted': x.has_voted,
        } for x in qs])
    @transaction.atomic
    def post(self, request, pk):
        election = get_object_or_404(Election.objects.select_for_update(), pk=pk)
        ensure_draft(election)
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, pk=user_id, role=User.Role.STUDENT, is_active=True)
        item, created = VoterParticipation.objects.get_or_create(election=election, user=user)
        if created: record(request.user, 'ELIGIBILITY_ADDED', 'ELECTION', election.id)
        return Response({'user_id': user.id, 'election_id': election.id, 'eligible': True}, status=201 if created else 200)
    @transaction.atomic
    def delete(self, request, pk):
        election = get_object_or_404(Election.objects.select_for_update(), pk=pk)
        ensure_draft(election)
        user_id = request.data.get('user_id')
        deleted, _ = VoterParticipation.objects.filter(election=election, user_id=user_id).delete()
        if deleted: record(request.user, 'ELIGIBILITY_REMOVED', 'ELECTION', election.id)
        return Response(status=204)

def matching_students(filters):
    qs = User.objects.filter(role=User.Role.STUDENT, is_active=True,
        course__in=['BSIT', 'BIT'], year_level__in=[1, 2, 3, 4])
    if filters['course'] != 'ALL':
        qs = qs.filter(course=filters['course'])
    if filters.get('year_level') is not None:
        qs = qs.filter(year_level=filters['year_level'])
    return qs

def eligibility_preview(election, filters):
    students = matching_students(filters)
    matched = students.count()
    already_eligible = VoterParticipation.objects.filter(election=election, user__in=students).count()
    return {
        'matching_students': matched,
        'already_eligible': already_eligible,
        'will_be_added': matched - already_eligible,
        'course': filters['course'],
        'year_level': filters.get('year_level'),
    }

class EligibilityBulkPreview(APIView):
    permission_classes = [IsAdmin]
    def post(self, request, pk):
        election = get_object_or_404(Election, pk=pk)
        ensure_draft(election)
        serializer = BulkEligibilityFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(eligibility_preview(election, serializer.validated_data))

class EligibilityBulkAssign(APIView):
    permission_classes = [IsAdmin]
    @transaction.atomic
    def post(self, request, pk):
        election = get_object_or_404(Election.objects.select_for_update(), pk=pk)
        ensure_draft(election)
        serializer = BulkEligibilityFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        filters = serializer.validated_data
        students = matching_students(filters).only('id').order_by('id')
        before = VoterParticipation.objects.filter(election=election, user__in=students).count()
        batch = []
        for student in students.iterator(chunk_size=1000):
            batch.append(VoterParticipation(election=election, user_id=student.id))
            if len(batch) == 1000:
                VoterParticipation.objects.bulk_create(batch, ignore_conflicts=True, batch_size=1000)
                batch.clear()
        if batch:
            VoterParticipation.objects.bulk_create(batch, ignore_conflicts=True, batch_size=1000)
        after = VoterParticipation.objects.filter(election=election, user__in=students).count()
        added = after - before
        if added:
            record(request.user, 'ELIGIBILITY_BULK_ADDED', 'ELECTION', election.id)
        result = eligibility_preview(election, filters)
        result['added'] = added
        return Response(result)
