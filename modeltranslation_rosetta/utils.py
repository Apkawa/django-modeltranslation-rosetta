# coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict

from modeltranslation.translator import translator


def build_model_name(model):
    return "%s.%s" % (model._meta.app_label, model._meta.model_name)


def get_model(model_name):
    return get_models()[model_name]


def get_models():
    models_map = OrderedDict()
    models = translator.get_registered_models(abstract=False)
    for model in models:
        opts = translator.get_options_for_model(model)
        model_name = build_model_name(model)
        models_map[model_name] = {
            'model': model,
            'meta': model._meta,
            'opts': opts,
        }

    return models_map
