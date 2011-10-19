from HTMLParser import HTMLParser
import logging
import re
import unittest

from formpump import makopump

def skipIfUndef(attr):
    def wrapper(func):
        def test(self):
            if not callable(getattr(self, attr, None)):
                return self.skipTest('%s is undefined or not callable.' % (attr, ))
            return func(self)
        return test
    return wrapper

class FormPumpTests(unittest.TestCase):
    def setUp(self):
        pass

    def stripID(self, val):
        return re.sub(r' (id|for)="[^"]*"', '', val)

    def run_template(self, tpl, **kwargs):
        raise Exception('run_template must be overriden in a subclass')

    def _run_template(self, tpl, strip_id=True, **kwargs):
        tpl = self.run_template(tpl, **kwargs)
        if strip_id:
            return self.stripID(tpl)
        return tpl

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

class FormTests(object):
    @skipIfUndef('form')
    def test_form(self):
        tpl = self._run_template(self.form())
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')
 
    @skipIfUndef('form_name')
    def test_form_name(self): 
        tpl = self._run_template(self.form_name())
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    @skipIfUndef('form_attrs')
    def test_form_attrs(self):
        tpl = self._run_template(self.form_attrs())
        self.assertHTMLEqual(tpl, '<form action="x" class="y" method="post">ok</form>')

    @skipIfUndef('form_name_key')
    def test_form_name_key(self):
        prev_form_name_key = self.set_form_name_key('_')
        tpl = self._run_template(self.form_name_key())
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input type="hidden" name="_" value="test" />ok</form>')
        self.set_form_name_key(prev_form_name_key)

class InputTests(object):
    @skipIfUndef('text')
    def test_text(self):
        tpl = self._run_template(self.text())
        self.assertHTMLEqual(tpl, '<input type="text" />')

    @skipIfUndef('name')
    def test_name(self):
        tpl = self._run_template(self.name())
        self.assertHTMLEqual(tpl, '<input type="text" name="test" value="" />')

    @skipIfUndef('dynamic_name')
    def test_dynamic_name(self):
        tpl = self._run_template(self.dynamic_name(), 
                               var="est")
        self.assertHTMLEqual(tpl, '<input type="text" name="test" value="" />')

    @skipIfUndef('attrs')
    def test_attrs(self):
        tpl = self._run_template(self.attrs(),
                               var="est")
        self.assertHTMLEqual(tpl, '<input name="test" title="x" value="" class="y" type="text" />')
    
    @skipIfUndef('email')
    def test_email(self):
        tpl = self._run_template(self.email())
        self.assertHTMLEqual(tpl, '<input type="email" name="test" value="" />')

class FillTests(object):
    @skipIfUndef('checkbox_fill')
    def test_checkbox_fill(self):
        tpl = self._run_template(self.checkbox_fill(),
                               form_vars={'test':{'var_a':True, 'var_c':'c'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input checked="checked" type="checkbox" name="var_a" value="1" /><input type="checkbox" name="var_b" value="1" /><input checked="checked" type="checkbox" name="var_c" value="c" /></form>')

    @skipIfUndef('email_fill')
    def test_email_fill(self):
        tpl = self._run_template(self.email_fill(),
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="email" name="var" value="val" /></form>')

    @skipIfUndef('hidden_fill')
    def test_hidden_fill(self):
        tpl = self._run_template(self.hidden_fill(),
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="hidden" name="var" value="val" /></form>')

    @skipIfUndef('password_fill')
    def test_password_fill(self):
        tpl = self._run_template(self.password_fill(),
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="password" name="var" value="val" /></form>')

    @skipIfUndef('radio_fill')
    def test_radio_fill(self):
        tpl = self._run_template(self.radio_fill(),
                               form_vars={'test':{'var': 'b'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="radio" name="var" value="a" /><input checked="checked" type="radio" name="var" value="b" /><input type="radio" name="var" value="c" /></form>')

    @skipIfUndef('submit_fill')
    def test_submit_fill(self):
        tpl = self._run_template(self.submit_fill(),
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="submit" name="var" value="val" /></form>')

    @skipIfUndef('text_fill')
    def test_text_fill(self):
        tpl = self._run_template(self.text_fill(),
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="text" name="var" value="val" /></form>')

    @skipIfUndef('textarea_fill')
    def test_textarea_fill(self):
        tpl = self._run_template(self.textarea_fill(),
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><textarea name="var">val</textarea></form>')

class FormContextTests(object):
    @skipIfUndef('form_context')
    def test_form_context(self):
        tpl = self._run_template(self.form_context())
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    @skipIfUndef('form_context_key')
    def test_form_context_key(self):
        form_ctx_key = self.set_form_ctx_key('_')
        tpl = self._run_template(self.form_context_key())
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input type="hidden" name="_" value="ctx" />ok</form>')
        self.set_form_ctx_key(form_ctx_key)

    @skipIfUndef('form_context_attrs')
    def test_form_context_attrs(self):
        form_ctx_key = self.set_form_ctx_key('_')
        tpl = self._run_template(self.form_context_attrs())
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input var="val" type="hidden" name="_" value="ctx" />ok</form>')
        self.set_form_ctx_key(form_ctx_key)

    @skipIfUndef('form_context_fill')
    def test_form_context_fill(self):
        tpl = self._run_template(self.form_context_fill(),
                               form_vars={'test': {'var': 'test'},
                                          'ctx' : {'var': 'ctx'},
                                          })
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input type="text" name="var" value="ctx" /></form>')

class LabelTests(object):
    @skipIfUndef('label')
    def test_label(self):
        tpl = self._run_template(self.label())
        self.assertHTMLEqual(tpl, '<form action="" method="post"><label>ok</label></form>')

    @skipIfUndef('label_attrs')
    def test_label_attrs(self):
        tpl = self._run_template(self.label_attrs())
        self.assertHTMLEqual(tpl, '<form action="" method="post"><label var="val">ok</label></form>')

    @skipIfUndef('label_match_forward')
    def test_label_match_forward(self):
        tpl = self._run_template(self.label_match_forward(),
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><label>ok</label><input type="text" name="var" value="" /></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[1]['attrs']['for'], 
                         tags[4]['attrs']['id'])

    @skipIfUndef('label_match_back')
    def test_label_match_back(self):
        tpl = self._run_template(self.label_match_back(),
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><input type="text" name="var" value="" /><label>ok</label></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[2]['attrs']['for'], 
                         tags[1]['attrs']['id'])

    @skipIfUndef('label_match_forward_multi')
    def test_label_match_forward_multi(self):
        tpl = self._run_template(self.label_match_forward_multi(),
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><label>ok</label><input type="text" name="var" value="" /><label>ok</label><input type="text" name="var" value="" /></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[1]['attrs']['for'], 
                         tags[4]['attrs']['id'])
        self.assertEqual(tags[5]['attrs']['for'], 
                         tags[8]['attrs']['id'])

    @skipIfUndef('label_match_back_multi')
    def test_label_match_back_multi(self):
        tpl = self._run_template(self.label_match_back_multi(),
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><input type="text" name="var" value="" /><label>ok</label><input type="text" name="var" value="" /><label>ok</label></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[2]['attrs']['for'], 
                         tags[1]['attrs']['id'])
        self.assertEqual(tags[6]['attrs']['for'], 
                         tags[5]['attrs']['id'])


class ErrorTests(object):
    @skipIfUndef('error')
    def test_error(self):
        tpl = self._run_template(self.error())
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

        tpl = self._run_template(self.error(),
                                 form_errors={'test': {'a': 'a'}}
                                 )
        self.assertHTMLEqual(tpl, '<form action="" method="post"><span class="error">a</span>ok</form>')

    @skipIfUndef('multi_error')
    def test_multi_error(self):
        tpl = self._run_template(self.multi_error(),
                                 form_errors={'test': {'a': 'a'}}
                                 )
        self.assertHTMLEqual(tpl, '<form action="" method="post"><span class="error">a</span>ok</form>')
        tpl = self._run_template(self.multi_error(),
                                 form_errors={'test': {'b': 'b'}}
                                 )
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok<span class="error">b</span></form>')
        tpl = self._run_template(self.multi_error(),
                                 form_errors={'test': {'a': 'a', 'b':'b'}}
                                 )
        self.assertHTMLEqual(tpl, '<form action="" method="post"><span class="error">a</span>ok<span class="error">b</span></form>')
        tpl = self._run_template(self.multi_error(),
                                 form_errors={'test': {}}
                                 )
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    @skipIfUndef('error_renderer')
    def test_error_renderer(self):
        def renderer(error, attrs):
            return '<div class="error">'+error+'</div>'

        with self.assertRaises(ValueError):
            tpl = self._run_template(self.error_renderer(),
                                     form_errors={'test': {'a': 'a'}}
                                     )
        
        self.add_renderer('test', renderer)
        tpl = self._run_template(self.error_renderer(),
                                 form_errors={'test': {'a': 'a'}}
                                 )
        self.assertHTMLEqual(tpl, '<form action="" method="post"><div class="error">a</div>ok</form>')
        self.remove_renderer('test')

        with self.assertRaises(ValueError):
            tpl = self._run_template(self.error_renderer(),
                                     form_errors={'test': {'a': 'a'}}
                                     )

    @skipIfUndef('error')
    def test_default_error_renderer(self):
        def renderer(error, attrs):
            return '<div class="error">'+error+'</div>'

        self.add_renderer('default', renderer)
        tpl = self._run_template(self.error(),
                                 form_errors={'test': {'a': 'a'}}
                                 )
        self.assertHTMLEqual(tpl, '<form action="" method="post"><div class="error">a</div>ok</form>')
        self.remove_renderer('default')
        tpl = self._run_template(self.error(),
                                 form_errors={'test': {'a': 'a'}}
                                 )
        self.assertHTMLEqual(tpl, '<form action="" method="post"><span class="error">a</span>ok</form>')

class HTMLQueueParser(HTMLParser):
    START_TAG    = 0
    END_TAG      = 1
    STARTEND_TAG = 2
    DATA         = 3

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
        
    def handle_data(self, data):
        self.tags.append({'type': self.DATA,
                          'tag': data,
                          'attrs': {}})
    @classmethod
    def attrs_to_dict(cls, attrs):
        return {k:v for (k,v) in attrs}

    def __eq__(self, other):
        return self.tags == other.tags

    def __ne__(self, other):
        return self.tags != other.tags
