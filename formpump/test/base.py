from HTMLParser import HTMLParser
import logging
import re
import unittest

from formpump import makopump

class FormPumpTests(unittest.TestCase):
    def setUp(self):
        #self.env = jinja2.Environment(extensions=[formpump.JinjaPump])
        pass

    def stripID(self, val):
        return re.sub(r' (id|for)="[^"]*"', '', val)

    def runTemplate(self, tpl, strip_id=True, **kwargs):
        pass

    def assertHTMLEqual(self, html_a, html_b):
        parser_a = HTMLQueueParser()
        parser_b = HTMLQueueParser()
        parser_a.feed(unicode(html_a))
        parser_b.feed(unicode(html_b))
        if parser_a != parser_b:
            raise AssertionError("%s != %s" % (html_a, html_b))

    def get_tags(self, html):
        parser = HTMLQueueParser()
        parser.feed(unicode(html))
        return parser.tags

class HTMLQueueParser(HTMLParser):
    START_TAG    = 0
    END_TAG      = 1
    STARTEND_TAG = 2

    def __init__(self):
        HTMLParser.__init__(self)
        self.tags = []
        
    def handle_starttag(self, tag, attrs):
        self.tags.append({'type': self.START_TAG, 
                          'tag': tag, 
                          'attrs': self.attrs_to_dict(attrs)})

    def handle_endtag(self, tag):
        self.tags.append({'type': self.END_TAG, 
                          'tag': tag, 
                          'attrs': {}})
                              
    def handle_startendtag(self, tag, attrs):
        self.tags.append({'type': self.STARTEND_TAG, 
                          'tag': tag, 
                          'attrs': self.attrs_to_dict(attrs)})
        
    @classmethod
    def attrs_to_dict(cls, attrs):
        return {k:v for (k,v) in attrs}

    def __eq__(self, other):
        return self.tags == other.tags

    def __ne__(self, other):
        return self.tags != other.tags
