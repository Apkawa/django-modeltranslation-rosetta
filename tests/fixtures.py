# coding: utf-8
from __future__ import unicode_literals

import factory


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'tests.Article'

    title = factory.Faker('sentence')
    body = factory.Faker('text')
