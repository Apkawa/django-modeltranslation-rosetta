# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO
from unittest import TestCase

from babel.messages.pofile import read_po, write_po

from modeltranslation.translator import translator

from modeltranslation_rosetta.export_translation import (
    build_comment,
    export_po,
    collect_model_translations,
    collect_queryset_translations,
    collect_models,
)
from modeltranslation_rosetta.import_translation import (
    load_translation,
    group_dataset,
    parse_po,
)
from .fixtures import ArticleFactory
from .models import Article


class GenericTestCase(TestCase):
    maxDiff = None

    def setUp(self):
        self.article = ArticleFactory()
        self.opts = translator.get_options_for_model(Article)

    def test_collect_models_all(self):
        models = list(collect_models())

        assert models
        self.assertDictEqual(
            models[0],
            {
                "fields": {
                    "body": {"de": "body_de", "en": "body_en"},
                    "title": {"de": "title_de", "en": "title_en"},
                },
                "model": Article,
                "model_name": "article",
                "model_key": "tests.article",
                "app_label": "tests",
                "opts": self.opts,
            },
        )

    def test_collect_translation(self):
        model_opts = {
            "fields": {
                "body": {"de": "body_de", "en": "body_en"},
                "title": {"de": "title_de", "en": "title_en"},
            },
            "model": Article,
            "model_name": "article",
            "model_key": "tests.article",
            "app_label": "tests",
            "opts": self.opts,
        }
        translations = list(collect_model_translations(model_opts))
        assert translations
        for tr in translations:
            self.assertDictEqual(
                tr,
                {
                    "field": tr["field"],
                    "obj": self.article,
                    "translated_data": {
                        "de": getattr(self.article, tr["field"] + "_de") or "",
                        "en": getattr(self.article, tr["field"] + "_en"),
                    },
                    "model_key": "tests.article",
                    "model": Article,
                    "model_name": "article",
                    "object_id": str(self.article.id),
                    "comment": build_comment(self.article),
                    "context": None,
                },
            )

    def test_collect_translation_from_queryset(self):
        translations = list(collect_queryset_translations(qs=Article.objects.all()))
        assert translations
        for tr in translations:
            self.assertDictEqual(
                tr,
                {
                    "field": tr["field"],
                    "obj": self.article,
                    "translated_data": {
                        "de": getattr(self.article, tr["field"] + "_de") or "",
                        "en": getattr(self.article, tr["field"] + "_en"),
                    },
                    "model_key": "tests.article",
                    "model": Article,
                    "model_name": "article",
                    "object_id": str(self.article.id),
                    "comment": build_comment(self.article),
                    "context": None,
                },
            )

    def test_export_po(self):
        translations = list(collect_queryset_translations(qs=Article.objects.all()))
        stream = export_po(translations=translations)
        po_file = read_po(stream)
        self.assertEqual(len(po_file), 2)

        message = po_file[self.article.title_en]
        self.assertEqual(
            message.auto_comments[0],
            "Tests::article:{a} [{a.id}]".format(a=self.article),
        )

        self.assertEqual(
            message.locations[0][0], "tests.article.title.{a.id}".format(a=self.article)
        )
        self.assertEqual(message.id, self.article.title_en)
        self.assertEqual(message.string, self.article.title_de or "")

    def test_import_po(self):
        translated_string = "Пример статьи"
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

        row = [r for r in flatten_dataset if r["field"] == "title"][0]
        self.assertDictEqual(
            row,
            {
                "app_name": "tests",
                "de": translated_string,
                "en": self.article.title_en,
                "from_lang": "en",
                "object_id": str(self.article.id),
                "to_lang": "de",
                "field": "title",
                "model_key": "tests.article",
                "model": Article,
                "model_name": "article",
            },
        )
        _grouped_dataset = list(group_dataset(flatten_dataset))
        self.assertEqual(len(_grouped_dataset), 1)
        result = load_translation(_grouped_dataset)
        self.assertDictEqual(
            result,
            {"stat": {"fail": 0, "skip": 0, "total": 1, "update": 1}, "fail_rows": []},
        )

        result = load_translation(_grouped_dataset)
        self.assertDictEqual(
            result,
            {"stat": {"fail": 0, "skip": 1, "total": 1, "update": 0}, "fail_rows": []},
        )

        article = Article.objects.get()
        self.assertEqual(article.title_de, translated_string)

    def test_group_dataset(self):
        flatten_dataset = [
            {
                "model_key": "tests.article",
                "field": "title",
                "object_id": "1",
                "app_name": "tests",
                "model_name": "article",
                "model": Article,
                "from_lang": "en",
                "to_lang": "de",
                "en": "Improve street someone history fund thought.",
                "de": "Пример статьи",
            },
            {
                "model_key": "tests.article",
                "field": "body",
                "object_id": "1",
                "app_name": "tests",
                "model_name": "article",
                "model": Article,
                "from_lang": "en",
                "to_lang": "de",
                "en": "Nor record media main watch. Right up travel these enjoy. Sport her cause might place himself people.",
                "de": "",
            },
        ]
        grouped_ds = list(group_dataset(flatten_dataset))
        assert grouped_ds == [
            {
                "model_key": "tests.article",
                "object_id": "1",
                "app_name": "tests",
                "model_name": "article",
                "model": Article,
                "fields": [
                    {
                        "field": "title",
                        "from_lang": "en",
                        "to_lang": "de",
                        "en": "Improve street someone history fund thought.",
                        "de": "Пример статьи",
                    },
                    {
                        "field": "body",
                        "from_lang": "en",
                        "to_lang": "de",
                        "en": "Nor record media main watch. Right up travel these enjoy. Sport her cause might place himself people.",
                        "de": "",
                    },
                ],
            }
        ]
