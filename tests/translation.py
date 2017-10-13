# coding: utf-8
from __future__ import unicode_literals
from modeltranslation.translator import translator, TranslationOptions
from .models import (
    Article
)


class ArticleTranslation(TranslationOptions):
    fields = ('title', 'body')


translator.register(Article, ArticleTranslation)


