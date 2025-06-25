from functools import partial

from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from blog.models import Post
from .forms import EmailPostForm, CommentForm


class PostListView(View):
    _post_list = Post.published.all()

    def get(self, request, *args, **kwargs):
        paginator = Paginator(self._post_list, 3)
        page_number = request.GET.get('page', 1)

        try:
            posts = paginator.page(page_number)
        except (EmptyPage, PageNotAnInteger):
            raise Http404()
        return render(
            request,
            'blog/post/list.html',
            {'posts': posts}
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
        return render(
            request,
            'blog/post/detail.html',
            {
                'post': post,
                'comments': comments,
                'form': form
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
