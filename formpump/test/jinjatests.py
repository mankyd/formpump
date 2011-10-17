import jinja2
import logging
import re
import unittest

from base import FormPumpTests
import formpump

class JinjaPumpTests(FormPumpTests):
    def setUp(self):
        self.env = jinja2.Environment(extensions=[formpump.JinjaPump])

    def runTemplate(self, tpl, strip_id=True, **kwargs):
        tpl = self.env.from_string(tpl).render(**kwargs)
        if strip_id:
            return self.stripID(tpl)
        return tpl

class JinjaPumpFormTests(JinjaPumpTests):
    def test_form(self):
        tpl = self.runTemplate('{% form %}ok{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    def test_form_name(self): 
        tpl = self.runTemplate('{% form "test" %}ok{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    def test_form_attrs(self):
        tpl = self.runTemplate('{% form "test" action="x" class="y" %}ok{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="x" class="y" method="post">ok</form>')

    def test_form_name_key(self):
        form_name_key, self.env.form_name_key = self.env.form_name_key, '_'
        tpl = self.runTemplate('{% form "test" %}ok{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input type="hidden" name="_" value="test" />ok</form>')
        self.env.form_name_key = form_name_key

class JinjaPumpInputTests(JinjaPumpTests):
    def test_text(self):
        tpl = self.runTemplate('{% text %}')
        self.assertHTMLEqual(tpl, '<input type="text" />')

    def test_name(self):
        tpl = self.runTemplate('{% text "test" %}')
        self.assertHTMLEqual(tpl, '<input type="text" name="test" value="" />')

    def test_dynamic_name(self):
        tpl = self.runTemplate('{% text name="t"~var %}', 
                                  var="est")
        self.assertHTMLEqual(tpl, '<input type="text" name="test" value="" />')

    def test_attrs(self):
        tpl = self.runTemplate('{% text "test" class="y" title="x" %}',
                                  var="est")
        self.assertHTMLEqual(tpl, '<input name="test" title="x" value="" class="y" type="text" />')
    
    def test_email(self):
        tpl = self.runTemplate('{% email "test" %}')
        self.assertHTMLEqual(tpl, '<input type="email" name="test" value="" />')

class JinjaPumpFillTests(JinjaPumpTests):
    def test_checkbox_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% checkbox "var_a" %}{% checkbox "var_b" %}{% checkbox "var_c" value="c" %}{% endform %}',
                                  form_vars={'test':{'var_a':True, 'var_c':'c'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input checked="checked" type="checkbox" name="var_a" value="1" /><input type="checkbox" name="var_b" value="1" /><input checked="checked" type="checkbox" name="var_c" value="c" /></form>')

    def test_email_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% email "var" %}{% endform %}',
                                  form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="email" name="var" value="val" /></form>')

    def test_hidden_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% hidden "var" %}{% endform %}',
                                  form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="hidden" name="var" value="val" /></form>')

    def test_password_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% password "var" %}{% endform %}',
                                  form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="password" name="var" value="val" /></form>')

    def test_radio_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% radio "var" value="a" %}{% radio "var" value="b" %}{% radio "var" value="c" %}{% endform %}',
                                  form_vars={'test':{'var': 'b'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="radio" name="var" value="a" /><input checked="checked" type="radio" name="var" value="b" /><input type="radio" name="var" value="c" /></form>')

    def test_submit_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% submit "var" %}{% endform %}',
                                  form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="submit" name="var" value="val" /></form>')


    def test_text_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% text "var" %}{% endform %}',
                                  form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input type="text" name="var" value="val" /></form>')

    def test_textarea_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% textarea "var" %}{% endform %}',
                                  form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><textarea name="var">val</textarea></form>')


class JinjaPumpFormContextTests(JinjaPumpTests):
    def test_form_context(self):
        tpl = self.runTemplate('{% form %}{% form_ctx "ctx" %}ok{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    def test_form_ctx_key(self):
        form_ctx_key, self.env.form_ctx_key = self.env.form_ctx_key, '_'
        tpl = self.runTemplate('{% form "test" %}{% form_ctx "ctx" %}ok{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input type="hidden" name="_" value="ctx" />ok</form>')
        self.env.form_ctx_key = form_ctx_key

    def test_form_ctx_attrs(self):
        form_ctx_key, self.env.form_ctx_key = self.env.form_ctx_key, '_'
        tpl = self.runTemplate('{% form "test" %}{% form_ctx "ctx" var="val" %}ok{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input var="val" type="hidden" name="_" value="ctx" />ok</form>')
        self.env.form_ctx_key = form_ctx_key

    def test_form_context_fill(self):
        tpl = self.runTemplate('{% form "test" %}{% form_ctx "ctx" %}{% text "var" %}{% endform %}',
                                  form_vars={'test': {'var': 'test'},
                                             'ctx' : {'var': 'ctx'},
                                             })
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input type="text" name="var" value="ctx" /></form>')

class JinjaPumpLabelTests(JinjaPumpTests):
    def test_label(self):
        tpl = self.runTemplate('{% form %}{% label name="var" %}ok{% endlabel %}{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="" method="post"><label>ok</label></form>')

    def test_label_attrs(self):
        tpl = self.runTemplate('{% form %}{% label name="var" var="val" %}ok{% endlabel %}{% endform %}')
        self.assertHTMLEqual(tpl, '<form action="" method="post"><label var="val">ok</label></form>')

    def test_label_match_forward(self):
        tpl = self.runTemplate('{% form %}{% label name="var" %}ok{% endlabel %}{% text name="var" %}{% endform %}',
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><label>ok</label><input type="text" name="var" value="" /></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[1]['attrs']['for'], 
                         tags[3]['attrs']['id'])

    def test_label_match_back(self):
        tpl = self.runTemplate('{% form %}{% text name="var" %}{% label name="var" %}ok{% endlabel %}{% endform %}',
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><input type="text" name="var" value="" /><label>ok</label></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[2]['attrs']['for'], 
                         tags[1]['attrs']['id'])

    def test_label_match_forward_multi(self):
        tpl = self.runTemplate('{% form %}{% label name="var" %}ok{% endlabel %}{% text name="var" %}{% label name="var" %}ok{% endlabel %}{% text name="var" %}{% endform %}',
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><label>ok</label><input type="text" name="var" value="" /><label>ok</label><input type="text" name="var" value="" /></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[1]['attrs']['for'], 
                         tags[3]['attrs']['id'])
        self.assertEqual(tags[4]['attrs']['for'], 
                         tags[6]['attrs']['id'])

    def test_label_match_back_multi(self):
        tpl = self.runTemplate('{% form %}{% text name="var" %}{% label name="var" %}ok{% endlabel %}{% text name="var" %}{% label name="var" %}ok{% endlabel %}{% endform %}',
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><input type="text" name="var" value="" /><label>ok</label><input type="text" name="var" value="" /><label>ok</label></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[2]['attrs']['for'], 
                         tags[1]['attrs']['id'])
        self.assertEqual(tags[5]['attrs']['for'], 
                         tags[4]['attrs']['id'])




if __name__ == "__main__":
    unittest.main()

loader = unittest.TestLoader()
suite = unittest.TestSuite()
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFillTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFormContextTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFormTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpInputTests))
