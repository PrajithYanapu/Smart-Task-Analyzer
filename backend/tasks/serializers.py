from rest_framework import serializers
from datetime import datetime
from dateutil.parser import parse as parse_date

class TaskInputSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)  # optional client-provided id
    title = serializers.CharField()
    due_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_hours = serializers.FloatField(required=False)
    importance = serializers.IntegerField(required=False)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False)

    def validate_due_date(self, value):
        if value in (None, ''):
            return None
        try:
            d = parse_date(value).date()
            return d.isoformat()
        except Exception as e:
            raise serializers.ValidationError("Invalid due_date format. Use YYYY-MM-DD.") from e

    def validate_importance(self, value):
        if value is None:
            return 5
        if not (1 <= value <= 10):
            raise serializers.ValidationError("importance must be 1-10")
        return value

    def validate_estimated_hours(self, value):
        if value is None:
            return 1.0
        if value <= 0:
            raise serializers.ValidationError("estimated_hours must be positive")
        return value
