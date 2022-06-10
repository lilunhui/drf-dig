import datetime
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from django_filters import FilterSet, filters
from django_filters.rest_framework import DjangoFilterBackend

from api import models
from api.serializers.comment import CreateCommentSerializer, ListCommentSerializer
from api.extension.filter import SelfFilterBackend
from api.extension.mixins import DigCreateModelMixin, DigListModelMixin, DigDestroyModelMixin, DigUpdateModelMixin
from api.extension.auth import UserAnonTokenAuthentication, TokenAuthentication
from api.extension import return_code


class CommentFilterSet(FilterSet):
    news = filters.NumberFilter(field_name='news', required=True)
    latest_id = filters.DateTimeFilter(field_name='descendant_update_datetime', lookup_expr='lte')

    class Meta:
        model = models.Comment
        fields = ["latest_id", 'news']



"""
1.先根据后代的更新时间，进行排序，获取根评论 10。
2.这些根评论关联的子评论，并构造父子关系。
"""
class CommentView(DigListModelMixin, DigCreateModelMixin, GenericViewSet):
    """ 评论 """
    filter_backends = [DjangoFilterBackend]
    filterset_class = CommentFilterSet

    authentication_classes = [TokenAuthentication, ]

    # ?news=2  ->  news=2
    # 获取某条新闻资讯的 根评论（根据后代更新时间排序）
    queryset = models.Comment.objects.filter(depth=0).order_by("-descendant_update_datetime")
    serializer_class = CreateCommentSerializer

    def perform_create(self, serializer):
        reply = serializer.validated_data.get('reply')
        if not reply:
            # 如果是根评论 'news', "reply", "content"
            instance = serializer.save(user=self.request.user)
        else:
            # 如果子评论

            # 1.获取根评论
            if not reply.root:
                # 给根评论回复
                root = reply
            else:
                root = reply.root
            # 创建评论
            instance = serializer.save(user=self.request.user, depth=reply.depth + 1, root=root)

            # 根评论的最新更新时间
            root.descendant_update_datetime = datetime.datetime.now()
            root.save()
        instance.news.comment_count += 1
        instance.news.save()


    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListCommentSerializer
        return CreateCommentSerializer

    def get_authenticators(self):
        if self.request.method == "POST":
            return super().get_authenticators()
        return []
