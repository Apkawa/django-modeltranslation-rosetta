from django.db import models


class Article(models.Model):
    title = models.CharField(verbose_name="Title", max_length=100)
    body = models.TextField(verbose_name="Body")

    def __str__(self):
        return "Article"
