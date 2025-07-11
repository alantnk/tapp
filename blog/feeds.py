from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from markdown import markdown

from .models import Post


class LatestPostsFeed(Feed):
    title = 'Py Blog'
    link = reverse_lazy('blog:post_list')
    description = 'New posts of Py Blog.'

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(markdown(item.body), 30)

    def item_pubdate(self, item):
        return item.publish
