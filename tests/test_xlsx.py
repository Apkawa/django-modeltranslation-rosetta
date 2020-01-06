import shutil

from modeltranslation_rosetta.export_translation import collect_queryset_translations, export_xlsx
from modeltranslation_rosetta.import_translation import parse_xlsx
from tests.fixtures import ArticleFactory
from tests.models import Article


def test_generic_export():
    ArticleFactory()
    translations = list(collect_queryset_translations(qs=Article.objects.all()))
    stream = export_xlsx(translations=translations)
    with open('/tmp/test.xlsx', 'wb')  as f:
        shutil.copyfileobj(stream, f)


def test_generic_import():
    article = ArticleFactory()
    translations = list(collect_queryset_translations(qs=Article.objects.all()))
    stream = export_xlsx(translations=translations)
    dataset = list(parse_xlsx(stream))
    assert len(dataset) == 2
    assert list(sorted(dataset, key=lambda r: r['field'], reverse=True)) == [
        {
            'model_key': 'tests.article', 'field': 'title', 'object_id': str(article.id),
            'app_name': 'tests', 'model_name': 'article', 'model': Article,
            'from_lang': 'en', 'to_lang': 'de', 'en': article.title_en,
            'de': None
        },
        {
            'model_key': 'tests.article', 'field': 'body', 'object_id': str(article.id),
            'app_name': 'tests', 'model_name': 'article', 'model': Article,
            'from_lang': 'en', 'to_lang': 'de',
            'en': article.body_en,
            'de': None
        }]
