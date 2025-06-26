from functools import partial

from django.contrib.postgres.search import (
    TrigramSimilarity
)
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from taggit.models import Tag

from blog.models import Post
from .forms import EmailPostForm, CommentForm, SearchForm


class PostListView(View):
    _post_list = Post.published.all()

    def get(self, request, *args, **kwargs):
        tag_slug = kwargs.get('tag_slug', None)
        tag = None
        if tag_slug:
            tag = get_object_or_404(Tag, name=tag_slug)
            self._post_list = self._post_list.filter(tags__in=[tag])
        paginator = Paginator(self._post_list, 3)
        page_number = request.GET.get('page', 1)

        try:
            posts = paginator.page(page_number)
        except (EmptyPage, PageNotAnInteger):
            raise Http404()
        return render(
            request,
            'blog/post/list.html',
            {
                'posts': posts,
                'tag': tag
            }
        )


class PostDetailView(View):

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            status=Post.Status.PUBLISHED,
            slug=kwargs['post'],
            publish__year=kwargs['year'],
            publish__month=kwargs['month'],
            publish__day=kwargs['day']
        )

        comments = post.comments.filter(active=True)
        # Form for users to comment
        form = CommentForm()
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(
            same_tags=Count('tags')
        ).order_by('-same_tags', '-publish')[:4]
        return render(
            request,
            'blog/post/detail.html',
            {
                'post': post,
                'comments': comments,
                'form': form,
                'similar_posts': similar_posts,
            },
        )


class PostShareView(View):
    _form = None
    _post = None
    _sent = False

    def get(self, request, *args, **kwargs):
        self._form = EmailPostForm()
        lazy_render = kwargs['_lazy_render']

        return lazy_render(context={'post': self._post, 'form': self._form, 'sent': self._sent})

    def post(self, request, *args, **kwargs):
        self._form = EmailPostForm(request.POST)
        if self._form.is_valid():
            cd = self._form.cleaned_data
            post_url = request.build_absolute_uri(
                self._post.get_absolute_url()
            )
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {self._post.title}"
            )
            message = (
                f"Read {self._post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )

            self._sent = True
        lazy_render = kwargs['_lazy_render']
        return lazy_render(context={'post': self._post, 'form': self._form, 'sent': self._sent})

    def dispatch(self, request, *args, **kwargs):
        self._post = get_object_or_404(
            Post,
            id=kwargs['post_id'],
            status=Post.Status.PUBLISHED,
        )
        kwargs['_lazy_render'] = partial(render, self.request, 'blog/post/share.html')
        return super().dispatch(request, *args, **kwargs)


class PostCommentView(View):
    def post(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            id=kwargs['post_id'],
            status=Post.Status.PUBLISHED
        )
        comment = None
        # A comment was posted
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            # Assign the post to the comment
            comment.post = post
            # Save the comment to the database
            comment.save()
        return render(
            request,
            'blog/post/comment.html',
            {
                'post': post,
                'form': form,
                'comment': comment
            }
        )


class PostSearchView(View):
    _form = SearchForm()
    _query = None
    _results = []

    def get(self, request, *args, **kwargs):
        if 'query' in request.GET:
            self._form = SearchForm(request.GET)
        if self._form.is_valid():
            self._query = self._form.cleaned_data['query']

            self._results = (
                Post.published.annotate(
                    similarity=TrigramSimilarity('title', self._query),
                )
                .filter(similarity__gt=0.1)
                .order_by('-similarity')
            )
        return render(
            request,
            'blog/post/search.html',
            {
                'form': self._form,
                'query': self._query,
                'results': self._results
            }
        )
