from rest_framework.viewsets import GenericViewSet
from django_filters import FilterSet, filters
from django_filters.rest_framework import DjangoFilterBackend

from api import models
from api.serializers.news import NewsSerializer,IndexSerializer
from api.extension.filter import SelfFilterBackend
from api.extension.mixins import DigCreateModelMixin, DigListModelMixin
from api.extension.auth import UserAnonTokenAuthentication
from api.extension.throttle import NewsCreateRateThrottle


class NewsFilterSet(FilterSet):
    lasted_id = filters.NumberFilter(field_name='id', lookup_expr='lt')

    class Meta:
        model = models.News
        fields = ['lasted_id']


class NewsView(DigListModelMixin, DigCreateModelMixin, GenericViewSet):
    filter_backends = [SelfFilterBackend, DjangoFilterBackend]
    filterset_class = NewsFilterSet
    queryset = models.News.objects.filter(deleted=False).order_by('-id')
    serializer_class = NewsSerializer
    throttle_obj = [NewsCreateRateThrottle(), ]

    def perform_create(self, serializer):
        # 1.创建新闻资讯
        # 2.自己对自己的内容做推荐
        #       - 推荐数量+1
        #       - 推荐记录  用户&资讯
        serializer.save(user=self.request.user)
        for throttle in self.throttle_obj:
            throttle.done()

    def get_throttles(self):
        if self.request.method == 'POST':
            return self.throttle_obj
        return []


class IndexFilterSet(FilterSet):
    latest_id = filters.NumberFilter(field_name='id', lookup_expr='lt')

    class Meta:
        model = models.News
        fields = ["latest_id", 'zone']
        # ?zone=1
        # ?latest_id=99&limit=10


class IndexView(DigListModelMixin, GenericViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = IndexFilterSet

    authentication_classes = [UserAnonTokenAuthentication, ]

    # queryset = models.News.objects.filter(deleted=False, status=2).order_by('-id')
    queryset = models.News.objects.filter(deleted=False).order_by('-id')
    serializer_class = IndexSerializer
