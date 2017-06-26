# coding: utf-8
from __future__ import unicode_literals

from django.http import HttpResponse

from django.utils.encoding import smart_str


class FileResponse(HttpResponse):
    """
    DRF Response to render data as a PDF File.
    kwargs:
        - pdf (byte array). The PDF file content.
        - file_name (string). The default downloaded file name.
    """

    def __init__(self, file_content, file_name, download=True, content_type=None, *args, **kwargs):
        disposition = b'filename="{}"'.format(smart_str(file_name))
        if download:
            disposition = b'attachment; ' + disposition

        headers = {
            'Content-Disposition': disposition,
            'Content-Length': len(file_content),
        }

        super(FileResponse, self).__init__(
            file_content,
            content_type=content_type or 'application/octet-stream',
            *args,
            **kwargs
        )

        for h, v in headers.items():
            self[h] = v
