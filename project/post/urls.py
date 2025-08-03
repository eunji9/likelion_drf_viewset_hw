from django.urls import path, include
from rest_framework import routers
from .views import PostViewSet, CommentViewSet, PostCommentViewSet, TagViewSet
from .views import *

from django.conf.urls.static import static
from django.conf import settings

app_name = "post"

default_router = routers.DefaultRouter(trailing_slash=False)
default_router.register("posts", PostViewSet, basename="posts")

comment_router = routers.DefaultRouter(trailing_slash=False)
comment_router.register("comments", CommentViewSet, basename="comments")

post_comment_router = routers.DefaultRouter(trailing_slash=False)
post_comment_router.register("comments", PostCommentViewSet, basename="comments")

tag_router = routers.DefaultRouter(trailing_slash=False)
tag_router.register("tags", TagViewSet, basename="tags")

post_list_view = PostViewSet.as_view({'get': 'list'})

urlpatterns = [
    path("", post_list_view, name="root-post-list"),
    path("", include(default_router.urls)), 
    path("", include(comment_router.urls)),
    path("posts/<int:post_id>/", include(post_comment_router.urls)),
    path("", include(tag_router.urls)),
] +static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)