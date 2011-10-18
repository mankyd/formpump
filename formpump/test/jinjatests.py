import jinja2
import logging
import re
import unittest

import base
import formpump

class JinjaPumpTests(base.FormPumpTests):
    def setUp(self):
        self.env = jinja2.Environment(extensions=[formpump.JinjaPump])

    def run_template(self, tpl, strip_id=True, **kwargs):
        tpl = self.env.from_string(tpl).render(**kwargs)
        if strip_id:
            return self.stripID(tpl)
        return tpl

    def set_form_name_key(self, form_name_key):
        form_name_key, self.env.form_name_key = self.env.form_name_key, form_name_key
        return form_name_key

    def set_form_ctx_key(self, form_ctx_key):
        form_ctx_key, self.env.form_ctx_key = self.env.form_ctx_key, form_ctx_key
        return form_ctx_key

class JinjaPumpFormTests(JinjaPumpTests, base.FormTests):
    def form(self):
        return '{% form %}ok{% endform %}'

    def form_name(self): 
        return '{% form "test" %}ok{% endform %}'

    def form_attrs(self):
        return '{% form "test" action="x" class="y" %}ok{% endform %}'

    def test_form_name_key(self):
        return '{% form "test" %}ok{% endform %}'

class JinjaPumpInputTests(JinjaPumpTests, base.InputTests):
    def text(self):
        return '{% text %}'

    def name(self):
        return '{% text "test" %}'

    def dynamic_name(self):
        return '{% text name="t"~var %}'

    def attrs(self):
        return '{% text "test" class="y" title="x" %}'
    
    def email(self):
        return '{% email "test" %}'

class JinjaPumpFillTests(JinjaPumpTests, base.FillTests):
    def checkbox_fill(self):
        return '{% form "test" %}{% checkbox "var_a" %}{% checkbox "var_b" %}{% checkbox "var_c" value="c" %}{% endform %}'

    def email_fill(self):
        return '{% form "test" %}{% email "var" %}{% endform %}'

    def hidden_fill(self):
        return '{% form "test" %}{% hidden "var" %}{% endform %}'

    def password_fill(self):
        return '{% form "test" %}{% password "var" %}{% endform %}'

    def radio_fill(self):
        return '{% form "test" %}{% radio "var" value="a" %}{% radio "var" value="b" %}{% radio "var" value="c" %}{% endform %}'

    def submit_fill(self):
        return '{% form "test" %}{% submit "var" %}{% endform %}'

    def text_fill(self):
        return '{% form "test" %}{% text "var" %}{% endform %}'

    def textarea_fill(self):
        return '{% form "test" %}{% textarea "var" %}{% endform %}'

class JinjaPumpFormContextTests(JinjaPumpTests, base.FormContextTests):
    def form_context(self):
        return '{% form %}{% form_ctx "ctx" %}ok{% endform %}'

    def form_context_key(self):
        return '{% form "test" %}{% form_ctx "ctx" %}ok{% endform %}'

    def form_context_attrs(self):
        return '{% form "test" %}{% form_ctx "ctx" var="val" %}ok{% endform %}'

    def form_context_fill(self):
        return '{% form "test" %}{% form_ctx "ctx" %}{% text "var" %}{% endform %}'

class JinjaPumpLabelTests(JinjaPumpTests, base.LabelTests):
    def label(self):
        return '{% form %}{% label name="var" %}ok{% endlabel %}{% endform %}'

    def label_attrs(self):
        return '{% form %}{% label name="var" var="val" %}ok{% endlabel %}{% endform %}'

    def label_match_forward(self):
        return '{% form %}{% label name="var" %}ok{% endlabel %}{% text name="var" %}{% endform %}'

    def label_match_back(self):
        return '{% form %}{% text name="var" %}{% label name="var" %}ok{% endlabel %}{% endform %}'

    def label_match_forward_multi(self):
        return '{% form %}{% label name="var" %}ok{% endlabel %}{% text name="var" %}{% label name="var" %}ok{% endlabel %}{% text name="var" %}{% endform %}'

    def label_match_back_multi(self):
        return '{% form %}{% text name="var" %}{% label name="var" %}ok{% endlabel %}{% text name="var" %}{% label name="var" %}ok{% endlabel %}{% endform %}'

if __name__ == "__main__":
    unittest.main()

loader = unittest.TestLoader()
suite = unittest.TestSuite()
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFillTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFormContextTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFormTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpInputTests))
