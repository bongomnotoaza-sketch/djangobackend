from rest_framework import serializers
from .models import Updates
from django.utils import timezone


class UpdatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Updates
        fields = [
            "id",
            "initials",
            "heading",
            "subject",
            "senddate",
            "category",
            "body",
        ]
        read_only_fields = ["id", "senddate"]
        
class UpdatesGetSerializer(serializers.ModelSerializer):
    senddate = serializers.SerializerMethodField()

    class Meta:
        model = Updates
        fields = [
            "id",
            "initials",
            "heading",
            "subject",
            "senddate",
            "category",
            "body",
        ]

    def get_senddate(self, obj):
        now = timezone.now()
        difference = now - obj.senddate

        seconds = int(difference.total_seconds())

        if seconds < 60:
            return "just now"

        minutes = seconds // 60

        if minutes < 60:
            return f"{minutes} min ago" if minutes == 1 else f"{minutes} mins ago"

        hours = minutes // 60

        if hours < 24:
            return f"{hours} h ago"

        days = hours // 24

        if days < 7:
            return f"{days} d ago"

        weeks = days // 7

        if weeks < 4:
            return f"{weeks} wk ago"

        return obj.senddate.strftime("%d %b %Y")
