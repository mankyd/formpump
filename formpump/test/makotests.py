import logging
from mako.template import Template
import re
import unittest

import base
from formpump import makopump


class MakoPumpTests(base.FormPumpTests):
    def run_template(self, tpl, strip_id=True, **kwargs):
        tpl = '<%namespace name="fp" module="formpump.makopump" />' + tpl

        tpl= Template(tpl)
        tpl = tpl.render(**kwargs)
        if strip_id:
            return self.stripID(tpl)
        return tpl

    def set_form_name_key(self, form_name_key):
        return makopump.set_form_name_key(form_name_key)

    def set_form_ctx_key(self, form_ctx_key):
        return makopump.set_form_ctx_key(form_ctx_key)

class MakoPumpFormTests(MakoPumpTests, base.FormTests):
    def form(self):
        return '<%fp:form>ok</%fp:form>'

    def form_name(self): 
        return '<%fp:form name="test">ok</%fp:form>'

    def form_attrs(self):
        return '<%fp:form name="test" action="x" class_="y">ok</%fp:form>'

    def form_name_key(self):
        return '<%fp:form name="test">ok</%fp:form>'

class MakoPumpInputTests(MakoPumpTests, base.InputTests):
    def text(self):
        return '<%fp:text />'

    def name(self):
        return '<%fp:text name="test" />'

    def dynamic_name(self):
        return '<%fp:text name="${\'t\'+var}" />'

    def attrs(self):
        return '<%fp:text name="test" class_="y" title="x" />'
    
    def email(self):
        return '<%fp:email name="test" />'

class MakoPumpFillTests(MakoPumpTests, base.FillTests):
    def checkbox_fill(self):
        return '<%fp:form name="test"><%fp:checkbox name="var_a" /><%fp:checkbox name="var_b" /><%fp:checkbox name="var_c" value="c" /></%fp:form>'

    def email_fill(self):
        return '<%fp:form name="test"><%fp:email name="var" /></%fp:form>'

    def hidden_fill(self):
        return '<%fp:form name="test"><%fp:hidden name="var" /></%fp:form>'

    def password_fill(self):
        return '<%fp:form name="test"><%fp:password name="var" /></%fp:form>'

    def radio_fill(self):
        return '<%fp:form name="test"><%fp:radio name="var" value="a" /><%fp:radio name="var" value="b" /><%fp:radio name="var" value="c" /></%fp:form>'

    def submit_fill(self):
        return '<%fp:form name="test"><%fp:submit name="var" /></%fp:form>'

    def text_fill(self):
        return '<%fp:form name="test"><%fp:text name="var" /></%fp:form>'

    def textarea_fill(self):
        return '<%fp:form name="test"><%fp:textarea name="var" /></%fp:form>'

class MakoPumpFormContextTests(MakoPumpTests, base.FormContextTests):
    def form_context(self):
        return '<%fp:form><%fp:form_ctx name="ctx" />ok</%fp:form>'

    def form_context_key(self):
        return '<%fp:form name="test"><%fp:form_ctx name="ctx" />ok</%fp:form>'

    def form_context_attrs(self):
        return '<%fp:form name="test"><%fp:form_ctx name="ctx" var="val" />ok</%fp:form>'

    def form_context_fill(self):
        return '<%fp:form name="test"><%fp:form_ctx name="ctx" /><%fp:text name="var" /></%fp:form>'

class MakoPumpLabelTests(MakoPumpTests, base.LabelTests):
    def label(self):
        return '<%fp:form><%fp:label name="var">ok</%fp:label></%fp:form>'

    def label_attrs(self):
        return '<%fp:form><%fp:label name="var" var="val">ok</%fp:label></%fp:form>'

    def label_match_forward(self):
        return '<%fp:form><%fp:label name="var">ok</%fp:label><%fp:text name="var" /></%fp:form>'

    def label_match_back(self):
        return '<%fp:form><%fp:text name="var" /><%fp:label name="var">ok</%fp:label></%fp:form>'

    def label_match_forward_multi(self):
        return '<%fp:form><%fp:label name="var">ok</%fp:label><%fp:text name="var" /><%fp:label name="var">ok</%fp:label><%fp:text name="var" /></%fp:form>'

    def label_match_back_multi(self):
        return '<%fp:form><%fp:text name="var" /><%fp:label name="var">ok</%fp:label><%fp:text name="var" /><%fp:label name="var">ok</%fp:label></%fp:form>'

if __name__ == "__main__":
    unittest.main()

loader = unittest.TestLoader()
suite = unittest.TestSuite()
suite.addTest(loader.loadTestsFromTestCase(MakoPumpFillTests))
suite.addTest(loader.loadTestsFromTestCase(MakoPumpFormContextTests))
suite.addTest(loader.loadTestsFromTestCase(MakoPumpFormTests))
suite.addTest(loader.loadTestsFromTestCase(MakoPumpInputTests))
