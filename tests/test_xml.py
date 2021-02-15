from datetime import datetime

from django.utils import timezone
from django.utils.encoding import smart_str
from mock import mock

from modeltranslation_rosetta.export_translation import collect_queryset_translations, export_xlsx, \
    export_xml
from modeltranslation_rosetta.import_translation import parse_xlsx, parse_xml
from tests.fixtures import ArticleFactory
from tests.models import Article


def test_generic_export():
    a = ArticleFactory()
    translations = list(collect_queryset_translations(qs=Article.objects.all()))
    dt = timezone.now()
    with mock.patch('django.utils.timezone.now') as tz_now:
        tz_now.side_effect = [dt]
        xml = smart_str(export_xml(translations=translations, merge_trans=False).read())
    assert xml.strip() == (
        f"""
<root created="{dt.isoformat()}">
  <Objects>
    <Object comment="Tests::article:Article object ({a.id}) [{a.id}]" id="tests.article.{a.id}">
      <Title field="title">
        <Lang code="en"><![CDATA[{a.title_en}]]></Lang>
        <Lang code="de"><![CDATA[]]></Lang>
      </Title>
      <Body field="body">
        <Lang code="en"><![CDATA[{a.body_en}]]></Lang>
        <Lang code="de"><![CDATA[]]></Lang>
      </Body>
    </Object>
  </Objects>
</root>
""".strip('\n')
    )


def test_export_merge_trans():
    a = ArticleFactory()
    translations = list(collect_queryset_translations(qs=Article.objects.all()))
    dt = timezone.now()
    with mock.patch('django.utils.timezone.now') as tz_now:
        tz_now.side_effect = [dt]
        xml = smart_str(export_xml(translations=translations, merge_trans=True).read())
    assert xml.strip('\n') == (
        f"""
<root created="{dt.isoformat()}">
  <Objects>
    <Object comment="Tests::article:Article object ({a.id}) [{a.id}]" id="tests.article.title.{a.id}">
      <Lang code="en"><![CDATA[{a.title_en}]]></Lang>
      <Lang code="de"><![CDATA[]]></Lang>
    </Object>
    <Object comment="Tests::article:Article object ({a.id}) [{a.id}]" id="tests.article.body.{a.id}">
      <Lang code="en"><![CDATA[{a.body_en}]]></Lang>
      <Lang code="de"><![CDATA[]]></Lang>
    </Object>
  </Objects>
</root>
""".strip('\n')
    )


def test_generic_import():
    article = ArticleFactory()
    translations = list(collect_queryset_translations(qs=Article.objects.all()))
    stream = export_xml(translations=translations, merge_trans=False)
    dataset = list(parse_xml(stream))
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

def test_generic_import_merge_trans():
    article = ArticleFactory()
    translations = list(collect_queryset_translations(qs=Article.objects.all()))
    stream = export_xml(translations=translations, merge_trans=True)
    dataset = list(parse_xml(stream))
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
