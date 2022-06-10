from rest_framework import serializers
from api import models


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Topic
        fields = ['id', 'title', 'is_hot']
        extra_kwargs = {
            'is_hot': {'read_only': True}
        }
