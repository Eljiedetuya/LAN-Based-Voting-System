from django.db import models
from django.db.models import Q
import uuid


def candidate_photo_path(instance, filename):
    """Store uploads under opaque names; never trust the submitted filename."""
    extension = getattr(instance, '_photo_extension', '.jpg')
    return f'candidates/{uuid.uuid4().hex}{extension}'

class Election(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    # NULL on other statuses means MySQL permits multiple non-open rows.
    open_slot = models.PositiveSmallIntegerField(null=True, blank=True, unique=True, editable=False)

    def __str__(self):
        return self.title

class Position(models.Model):
    election = models.ForeignKey(Election, on_delete=models.PROTECT, related_name='positions')
    name = models.CharField(max_length=100)
    display_order = models.PositiveIntegerField()

    class Meta:
        ordering = ['display_order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['election', 'name'], name='uniq_position_name'),
            models.UniqueConstraint(fields=['election', 'display_order'], name='uniq_position_order'),
        ]

class Candidate(models.Model):
    position = models.ForeignKey(Position, on_delete=models.PROTECT, related_name='candidates')
    name = models.CharField(max_length=150)
    biography = models.TextField(blank=True)
    platform = models.TextField(blank=True)
    photo_path = models.ImageField(max_length=255, blank=True, upload_to=candidate_photo_path)

    def __str__(self):
        return self.name
