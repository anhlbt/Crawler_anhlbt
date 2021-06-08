# -*- coding: utf-8 -*-

from scrapy.exporters import CsvItemExporter


class CsvCustomSeperator(CsvItemExporter):
    def __init__(self, *args, **kwargs):
        kwargs['encoding'] = 'utf-8'
        kwargs['delimiter'] = '|'
        if args[0].tell() > 0:
            kwargs['include_headers_line'] = False
            
        super(CsvCustomSeperator, self).__init__(*args, **kwargs)
