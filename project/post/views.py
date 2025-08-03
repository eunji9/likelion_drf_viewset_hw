from django.shortcuts import render
from rest_framework import viewsets, mixins
from .models import Post , Tag, Comment
from .serializers import PostSerializer, TagSerializer, CommentSerializer, PostListSerializer

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from django.views.generic import RedirectView

import re

from django.shortcuts import get_object_or_404
# Create your views here.
class TagViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "name"
    lookup_url_kwarg = "tags_name"

    def retrieve(self, request, *args, **kwargs):
        tags_name = kwargs.get("tags_name")
        tags = get_object_or_404(Tag, name=tags_name)
        posts = Post.objects.filter(tags=tags)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    # serializer_class = PostSerializer
    def get_serializer_class(self):
        if self.action in ["list", "recommend"]: #지피티 수정
            return PostListSerializer
        return PostSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        post = serializer.instance
        self.handle_tags(post)

        return Response(serializer.data)
    
    def perform_update(self, serializer):
        post = serializer.save()
        post.tags.clear()
        self.handle_tags(post)

    def handle_tags(self, post): #지피티 추가 
        import re
        words = re.split(r'[\s,]+', post.content.strip())
        tag_list = []

        for w in words:
            if len(w) > 0:
                if w[0] == '#':
                    tag_list.append(w[1:])
        for t in tag_list:
            tag, _ = Tag.objects.get_or_create(name=t)
            post.tags.add(tag)
        post.save()

    @action(methods=["GET"], detail=False)
    def recommend(self, request):
        ran_post = self.get_queryset().order_by("?").first()
        serializer = self.get_serializer(ran_post) #gpt 수정
        return Response(ran_post_serializer.data)
    
    @action(methods=["GET"], detail=False)
    def test(self, request, pk=None):
        test_post = self.get_object()
        test_post.click_num += 1
        test_post.save(update_fields=["click_num"])
        return Response()

class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class PostCommentViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    # queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        post = self.kwargs.get("post_id")
        queryset = Comment.objects.filter(post_id=post)
        return queryset

    # def list(self, request, post_id=None):
    #     post = get_object_or_404(Post, id=post_id)
    #     queryset = self.filter_queryset(self.get_queryset().filter(post=post))
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    def create(self, request, post_id=None):
        post = get_object_or_404(Post, id=post_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data)
    
