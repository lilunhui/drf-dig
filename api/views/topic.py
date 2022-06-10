from api.serializers.topic import TopicSerializer
from api.extension.filter import SelfFilterBackend
from api.extension.mixins import DigCreateModelMixin, DigDestroyModelMixin, DigListModelMixin, DigUpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import filters, FilterSet
from api import models


class TopicFilterSet(FilterSet):
    lasted_id = filters.NumberFilter(field_name='id', lookup_expr='lt')

    class Meta:
        model = models.Topic
        fields = ['lasted_id']


class TopicView(DigUpdateModelMixin, DigListModelMixin, DigDestroyModelMixin, DigCreateModelMixin, GenericViewSet):
    filter_backends = [SelfFilterBackend,DjangoFilterBackend]
    filterset_class = TopicFilterSet

    queryset = models.Topic.objects.filter(deleted=False).order_by('-id')
    serializer_class = TopicSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()
