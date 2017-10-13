# coding: utf-8
from __future__ import unicode_literals

import factory


class ArticleFixture(factory.django.DjangoModelFactory):
    class Meta:
        model = 'tests.Article'

    title = 'Example article'
    body = 'Example body article'
