from rest_framework import serializers
from django.db import transaction
from PIL import Image, UnidentifiedImageError
from .models import Election, Position, Candidate

MAX_CANDIDATE_PHOTO_BYTES = 2 * 1024 * 1024
MAX_CANDIDATE_PHOTO_PIXELS = 25_000_000
IMAGE_EXTENSIONS = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp'}

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ['id', 'election', 'name', 'display_order']
        read_only_fields = ['id', 'election']

class BulkEligibilityFilterSerializer(serializers.Serializer):
    course = serializers.ChoiceField(choices=[('ALL', 'All Students'), ('BSIT', 'BSIT'), ('BIT', 'BIT')])
    year_level = serializers.IntegerField(required=False, allow_null=True, min_value=1, max_value=4, default=None)

class CandidateSerializer(serializers.ModelSerializer):
    election_id = serializers.IntegerField(source='position.election_id', read_only=True)
    photo_path = serializers.ImageField(required=False, allow_null=True)
    remove_photo = serializers.BooleanField(write_only=True, required=False, default=False)

    def validate_photo_path(self, photo):
        if photo is None:
            return photo
        if photo.size > MAX_CANDIDATE_PHOTO_BYTES:
            raise serializers.ValidationError('Image must be 2 MB or smaller.')
        try:
            photo.seek(0)
            with Image.open(photo) as image:
                image_format = image.format
                width, height = image.size
                image.verify()
            if image_format not in IMAGE_EXTENSIONS:
                raise serializers.ValidationError('Use a JPG, PNG, or WebP image.')
            if width * height > MAX_CANDIDATE_PHOTO_PIXELS:
                raise serializers.ValidationError('Image dimensions are too large.')
            photo.seek(0)
            photo._candidate_image_extension = IMAGE_EXTENSIONS[image_format]
            return photo
        except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
            raise serializers.ValidationError('The uploaded file is not a valid JPG, PNG, or WebP image.')

    def create(self, validated_data):
        validated_data.pop('remove_photo', None)
        photo = validated_data.get('photo_path')
        candidate = Candidate(**validated_data)
        if photo:
            candidate._photo_extension = photo._candidate_image_extension
        candidate.save()
        return candidate

    def update(self, instance, validated_data):
        remove_photo = validated_data.pop('remove_photo', False)
        old_photo = instance.photo_path
        if remove_photo:
            validated_data['photo_path'] = ''
        photo = validated_data.get('photo_path')
        if photo:
            instance._photo_extension = photo._candidate_image_extension
        updated = super().update(instance, validated_data)
        if old_photo and (remove_photo or 'photo_path' in validated_data):
            storage, old_name = old_photo.storage, old_photo.name
            transaction.on_commit(lambda: storage.delete(old_name))
        return updated

    class Meta:
        model = Candidate
        fields = ['id', 'position', 'election_id', 'name', 'biography', 'platform', 'photo_path', 'remove_photo']
        read_only_fields = ['id']

class ElectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Election
        fields = ['id', 'title', 'description', 'status', 'created_at', 'opened_at', 'closed_at']
        read_only_fields = ['id', 'status', 'created_at', 'opened_at', 'closed_at']

class PublicCandidateSerializer(serializers.ModelSerializer):
    position_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Candidate
        fields = ['id', 'position_id', 'name', 'biography', 'platform', 'photo_path']
