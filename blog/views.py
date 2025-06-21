from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from blog.models import Post


class PostListView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        posts = Post.published.all()
        return render(
            request,
            'blog/post/list.html',
            {'posts': posts}
        )

class PostDetailView(View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            id=kwargs['pk'],
            status=Post.Status.PUBLISHED
        )
        return render(
            request,
            'blog/post/detail.html',
            {'post': post}
        )