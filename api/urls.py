from rest_framework import routers
from django.urls import path, include
from api.views import account, comment, collect, recommend, topic,news

router = routers.SimpleRouter()
router.register(r'register', account.RegisterView,'register')
router.register(r'topic',topic.TopicView)
router.register(r'news',news.NewsView)
router.register(r'index',news.IndexView)
router.register(r'collect',collect.CollectView)
router.register(r'recommend', recommend.RecommendView)
# 评论
router.register(r'comment', comment.CommentView)

urlpatterns = [
    path('auth/',account.AuthView.as_view()),
]
urlpatterns += router.urls