import jinja2
import logging
import re
import unittest

import formpump

class JinjaPumpTests(unittest.TestCase):
    def setUp(self):
        self.env = jinja2.Environment(extensions=[formpump.JinjaPump])

    def stripID(self, val):
        return re.sub(r' id="[^"]*"', '', val)

class JinjaPumpFormTests(JinjaPumpTests):
    def test_form(self):
        tpl = self.env.from_string('{% form %}ok{% endform %}')
        self.assertEqual(tpl.render(), '<form action="" method="post">ok</form>')

    def test_form_name(self): 
        tpl = self.env.from_string('{% form "test" %}ok{% endform %}')
        self.assertEqual(tpl.render(), '<form action="" method="post">ok</form>')

    def test_form_attrs(self):
        tpl = self.env.from_string('{% form "test" action="x" class="y" %}ok{% endform %}')
        self.assertEqual(tpl.render(), '<form action="x" class="y" method="post">ok</form>')

    def test_form_name_key(self):
        form_name_key, self.env.form_name_key = self.env.form_name_key, '_'
        tpl = self.env.from_string('{% form "test" %}ok{% endform %}')
        self.assertEqual(tpl.render(), '<form action="" method="post"><input type="hidden" name="_" value="test" />ok</form>')
        self.env.form_name_key = form_name_key

class JinjaPumpInputTests(JinjaPumpTests):
    def test_text(self):
        tpl = self.env.from_string('{% text %}')
        self.assertEqual(tpl.render(), '<input type="text" />')

    def test_name(self):
        tpl = self.env.from_string('{% text "test" %}')
        self.assertEqual(self.stripID(tpl.render()), '<input type="text" name="test" value="" />')

    def test_dynamic_name(self):
        tpl = self.env.from_string('{% text name="t"~var %}')
        self.assertEqual(self.stripID(tpl.render(var="est")), '<input type="text" name="test" value="" />')

    def test_attrs(self):
        tpl = self.env.from_string('{% text "test" class="y" title="x" %}')
        self.assertEqual(self.stripID(tpl.render(var="est")), '<input name="test" title="x" value="" class="y" type="text" />')
    
    def test_email(self):
        tpl = self.env.from_string('{% email "test" %}')
        self.assertEqual(self.stripID(tpl.render()), '<input type="email" name="test" value="" />')

class JinjaPumpFillTests(JinjaPumpTests):
    def test_checkbox_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% checkbox "var_a" %}{% checkbox "var_b" %}{% checkbox "var_c" value="c" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={'test':{'var_a':True, 'var_c':'c'}})), 
                         '<form action="" method="post"><input checked="checked" type="checkbox" name="var_a" value="1" /><input type="checkbox" name="var_b" value="1" /><input checked="checked" type="checkbox" name="var_c" value="c" /></form>')

    def test_email_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% email "var" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={'test':{'var':'val'}})), 
                         '<form action="" method="post"><input type="email" name="var" value="val" /></form>')

    def test_hidden_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% hidden "var" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={'test':{'var':'val'}})), 
                         '<form action="" method="post"><input type="hidden" name="var" value="val" /></form>')

    def test_password_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% password "var" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={'test':{'var':'val'}})), 
                         '<form action="" method="post"><input type="password" name="var" value="val" /></form>')

    def test_radio_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% radio "var" value="a" %}{% radio "var" value="b" %}{% radio "var" value="c" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={'test':{'var': 'b'}})), 
                         '<form action="" method="post"><input type="radio" name="var" value="a" /><input checked="checked" type="radio" name="var" value="b" /><input type="radio" name="var" value="c" /></form>')

    def test_submit_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% submit "var" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={'test':{'var':'val'}})), 
                         '<form action="" method="post"><input type="submit" value="var" /></form>')


    def test_text_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% text "var" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={'test':{'var':'val'}})), 
                         '<form action="" method="post"><input type="text" name="var" value="val" /></form>')

    def test_textarea_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% textarea "var" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={'test':{'var':'val'}})), 
                         '<form action="" method="post"><textarea name="var">val</textarea></form>')


class JinjaPumpFormContextTests(JinjaPumpTests):
    def test_form_context(self):
        tpl = self.env.from_string('{% form %}{% form_ctx "ctx" %}ok{% endform %}')
        self.assertEqual(tpl.render(), '<form action="" method="post">ok</form>')

    def test_form_ctx_key(self):
        form_ctx_key, self.env.form_ctx_key = self.env.form_ctx_key, '_'
        tpl = self.env.from_string('{% form "test" %}{% form_ctx "ctx" %}ok{% endform %}')
        self.assertEqual(self.stripID(tpl.render()), '<form action="" method="post"><input type="hidden" name="_" value="ctx" />ok</form>')
        self.env.form_ctx_key = form_ctx_key

    def test_form_ctx_attrs(self):
        form_ctx_key, self.env.form_ctx_key = self.env.form_ctx_key, '_'
        tpl = self.env.from_string('{% form "test" %}{% form_ctx "ctx" var="val" %}ok{% endform %}')
        self.assertEqual(self.stripID(tpl.render()), '<form action="" method="post"><input var="val" type="hidden" name="_" value="ctx" />ok</form>')
        self.env.form_ctx_key = form_ctx_key

    def test_form_context_fill(self):
        tpl = self.env.from_string('{% form "test" %}{% form_ctx "ctx" %}{% text "var" %}{% endform %}')
        self.assertEqual(self.stripID(tpl.render(form_vars={
                    'test': {'var': 'test'},
                    'ctx' : {'var': 'ctx'},
                    })), '<form action="" method="post"><input type="text" name="var" value="ctx" /></form>')

if __name__ == "__main__":
    unittest.main()

loader = unittest.TestLoader()
suite = unittest.TestSuite()
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFillTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFormContextTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFormTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpInputTests))
