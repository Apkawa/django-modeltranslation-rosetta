# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from unittest import TestCase

from babel.messages.pofile import read_po, write_po
from io import BytesIO

from modeltranslation_rosetta.export_translation import (
    export_po,
    collect_model_translations,
    collect_queryset_translations,
    collect_models,
)

from modeltranslation_rosetta.import_translation import (
    load_translation,
    load_same_rows,
    group_dataset,
    parse_po
)

from .models import Article
from .fixtures import ArticleFixture


class GenericTestCase(TestCase):
    def setUp(self):
        self.article = ArticleFixture()

    def test_collect_models_all(self):
        models = list(collect_models())

        self.assert_(models)
        self.assertDictEqual(models[0],
            {
                'fields': {u'body': {'ru': 'body_ru', 'en': 'body_en'},
                           u'title': {'ru': 'title_ru', 'en': 'title_en'}},
                'model': Article, 'model_name': 'article',
                'model_key': u'tests.article', 'app_label': 'tests'
            })

    def test_collect_translation(self):
        model_opts = {
            'fields': {u'body': {'ru': 'body_ru', 'en': 'body_en'},
                       u'title': {'ru': 'title_ru', 'en': 'title_en'}},
            'model': Article, 'model_name': 'article',
            'model_key': u'tests.article', 'app_label': 'tests'
        }
        translations = list(collect_model_translations(model_opts))
        self.assert_(translations)
        for tr in translations:
            self.assertDictEqual(tr,
                {'field': tr['field'], 'obj': self.article,
                 'translated_data': {
                     'ru': getattr(self.article, tr['field'] + '_ru') or '',
                     'en': getattr(self.article, tr['field'] + '_en')
                 },
                 'model_key': u'tests.article',
                 'model': Article,
                 'model_name': 'article',
                 'object_id': str(self.article.id)}
            )

    def test_collect_translation_from_queryset(self):
        translations = list(collect_queryset_translations(qs=Article.objects.all()))
        self.assert_(translations)
        for tr in translations:
            self.assertDictEqual(tr,
                {'field': tr['field'], 'obj': self.article,
                 'translated_data': {
                     'ru': getattr(self.article, tr['field'] + '_ru') or '',
                     'en': getattr(self.article, tr['field'] + '_en')
                 },
                 'model_key': u'tests.article',
                 'model': Article,
                 'model_name': 'article',
                 'object_id': str(self.article.id)}
            )

    def test_export_po(self):
        translations = list(collect_queryset_translations(qs=Article.objects.all()))
        stream = export_po(translations=translations)
        po_file = read_po(stream)
        self.assertEqual(len(po_file), 2)

        message = po_file[self.article.title_en]
        self.assertEqual(message.auto_comments[0],
            'Tests->article:{a} [{a.id}]'.format(a=self.article))

        self.assertEqual(message.locations[0][0],
            'tests.article.title.{a.id}'.format(a=self.article))
        self.assertEqual(message.id, self.article.title_en)
        self.assertEqual(message.string, self.article.title_ru or '')

    def test_import_po(self):
        translated_string = 'Пример статьи'
        # Preparations
        translations = list(collect_queryset_translations(qs=Article.objects.all()))
        self.assertEqual(len(translations), 2)
        stream = export_po(translations=translations)
        po_file = read_po(stream)
        message = po_file[str(self.article.title_en)]
        message.string = translated_string
        stream = BytesIO()
        write_po(stream, po_file)
        stream.seek(0)

        # Process import

        flatten_dataset = list(parse_po(stream))

        row = [r for r in flatten_dataset if r['field'] == 'title'][0]
        self.assertDictEqual(row,
            {
                u'app_name': u'tests',
                u'from_lang': self.article.title_en,
                u'object_id': str(self.article.id),
                u'to_lang': translated_string,
                u'field': u'title', u'model_key': u'tests.article',
                u'model': Article, u'model_name': u'article'
            }
        )
        _grouped_dataset = list(group_dataset(flatten_dataset))
        self.assertEqual(len(_grouped_dataset), 1)
        result = load_translation(_grouped_dataset)
        self.assertDictEqual(result,
            {
                u'stat': {
                    u'fail': 0,
                    u'skip': 0,
                    u'total': 1,
                    u'update': 1
                }, u'fail_rows': []})

        result = load_translation(_grouped_dataset)
        self.assertDictEqual(result,
            {u'stat': {
                u'fail': 0,
                u'skip': 1,
                u'total': 1,
                u'update': 0
            }, u'fail_rows': []})

        article = Article.objects.get()
        self.assertEqual(article.title_ru, translated_string)
