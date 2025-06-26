from django.urls import path

from .feeds import LatestPostsFeed
from .views import PostListView, PostDetailView, PostShareView, PostCommentView

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path(
        'tag/<slug:tag_slug>/', PostListView.as_view(), name='post_list_by_tag'
    ),
    path(
        '<int:year>/<int:month>/<int:day>/<slug:post>/',
        PostDetailView.as_view(),
        name='post_detail'
    ),
    path('<int:post_id>/share/', PostShareView.as_view(), name='post_share'),
    path(
        '<int:post_id>/comment/', PostCommentView.as_view(), name='post_comment'
    ),
    path('feed/', LatestPostsFeed(), name='post_feed'),
]
