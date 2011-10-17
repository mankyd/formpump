import logging
from mako.template import Template
import re
import unittest

from base import FormPumpTests
from formpump import makopump


class MakoPumpTests(FormPumpTests):
    def runTemplate(self, tpl, strip_id=True, **kwargs):
        tpl = '<%namespace name="fp" module="formpump.makopump" />' + tpl

        tpl= Template(tpl)
        tpl = tpl.render(**kwargs)
        if strip_id:
            return self.stripID(tpl)
        return tpl

class MakoPumpFormTests(MakoPumpTests):
    def test_form(self):
        tpl = self.runTemplate('<%fp:form>ok</%fp:form>')
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    def test_form_name(self): 
        tpl = self.runTemplate('<%fp:form name="test">ok</%fp:form>')
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    def test_form_attrs(self):
        tpl = self.runTemplate('<%fp:form name="test" action="x" class_="y">ok</%fp:form>')
        self.assertHTMLEqual(tpl, '<form action="x" class="y" method="post">ok</form>')

    def test_form_name_key(self):
        form_name_key = makopump.get_form_name_key()
        makopump.set_form_name_key('_')
        tpl = self.runTemplate('<%fp:form name="test">ok</%fp:form>')
        self.assertHTMLEqual(tpl, '<form action="" method="post"><input type="hidden" name="_" value="test" />ok</form>')
        makopump.set_form_name_key(form_name_key)

class MakoPumpInputTests(MakoPumpTests):
    def test_text(self):
        tpl = self.runTemplate('<%fp:text />')
        self.assertHTMLEqual(tpl, '<input type="text" />')

    def test_name(self):
        tpl = self.runTemplate('<%fp:text name="test" />')
        self.assertHTMLEqual(tpl, '<input type="text" name="test" value="" />')

    def test_dynamic_name(self):
        tpl = self.runTemplate('<%fp:text name="${\'t\'+var}" />', var='est')
        self.assertHTMLEqual(tpl, '<input type="text" name="test" value="" />')

    def test_attrs(self):
        tpl = self.runTemplate('<%fp:text name="test" class_="y" title="x" />')
        self.assertHTMLEqual(tpl, '<input name="test" title="x" value="" class="y" type="text" />')
    
    def test_email(self):
        tpl = self.runTemplate('<%fp:email name="test" />')
        self.assertHTMLEqual(tpl, '<input type="email" name="test" value="" />')

class MakoPumpFillTests(MakoPumpTests):
    def test_checkbox_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:checkbox name="var_a" /><%fp:checkbox name="var_b" /><%fp:checkbox name="var_c" value="c" /></%fp:form>', 
                               form_vars={'test':{'var_a':True, 'var_c':'c'}})
        self.assertHTMLEqual(tpl, 
                         '<form action="" method="post"><input checked="checked" type="checkbox" name="var_a" value="1" /><input type="checkbox" name="var_b" value="1" /><input checked="checked" type="checkbox" name="var_c" value="c" /></form>')

    def test_email_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:email name="var" /></%fp:form>', 
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                             '<form action="" method="post"><input type="email" name="var" value="val" /></form>')

    def test_hidden_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:hidden name="var" /></%fp:form>',
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl,
                             '<form action="" method="post"><input type="hidden" name="var" value="val" /></form>')

    def test_password_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:password name="var" /></%fp:form>',
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                             '<form action="" method="post"><input type="password" name="var" value="val" /></form>')

    def test_radio_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:radio name="var" value="a" /><%fp:radio name="var" value="b" /><%fp:radio name="var" value="c" /></%fp:form>',
                               form_vars={'test':{'var': 'b'}})
        self.assertHTMLEqual(tpl, 
                             '<form action="" method="post"><input type="radio" name="var" value="a" /><input checked="checked" type="radio" name="var" value="b" /><input type="radio" name="var" value="c" /></form>')

    def test_submit_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:submit name="var" /></%fp:form>',
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl,
                             '<form action="" method="post"><input type="submit" name="var" value="val" /></form>')

    def test_text_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:text name="var" /></%fp:form>',
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                             '<form action="" method="post"><input type="text" name="var" value="val" /></form>')

    def test_textarea_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:textarea name="var" /></%fp:form>',
                               form_vars={'test':{'var':'val'}})
        self.assertHTMLEqual(tpl, 
                             '<form action="" method="post"><textarea name="var">val</textarea></form>')


class MakoPumpFormContextTests(MakoPumpTests):
    def test_form_context(self):
        tpl = self.runTemplate('<%fp:form><%fp:form_ctx name="ctx" />ok</%fp:form>')
        self.assertHTMLEqual(tpl, '<form action="" method="post">ok</form>')

    def test_form_ctx_key(self):
        form_ctx_key = makopump.get_form_ctx_key()
        makopump.set_form_ctx_key('_')
        tpl = self.runTemplate('<%fp:form name="test"><%fp:form_ctx name="ctx" />ok</%fp:form>')
        self.assertHTMLEqual(tpl, 
                             '<form action="" method="post"><input type="hidden" name="_" value="ctx" />ok</form>')
        makopump.set_form_ctx_key(form_ctx_key)

    def test_form_ctx_attrs(self):
        form_ctx_key = makopump.get_form_ctx_key()
        makopump.set_form_ctx_key('_')
        tpl = self.runTemplate('<%fp:form name="test"><%fp:form_ctx name="ctx" var="val" />ok</%fp:form>')
        self.assertHTMLEqual(tpl, 
                             '<form action="" method="post"><input var="val" type="hidden" name="_" value="ctx" />ok</form>')
        makopump.set_form_ctx_key(form_ctx_key)

    def test_form_context_fill(self):
        tpl = self.runTemplate('<%fp:form name="test"><%fp:form_ctx name="ctx" /><%fp:text name="var" /></%fp:form>',
                               form_vars={
                'test': {'var': 'test'},
                'ctx' : {'var': 'ctx'},
                })
        self.assertHTMLEqual(tpl, 
                             '<form action="" method="post"><input type="text" name="var" value="ctx" /></form>')

class MakoPumpLabelTests(MakoPumpTests):
    def test_label(self):
        tpl = self.runTemplate('<%fp:form><%fp:label name="var">ok</%fp:label></%fp:form>')
        self.assertHTMLEqual(tpl, '<form action="" method="post"><label>ok</label></form>')

    def test_label_attrs(self):
        tpl = self.runTemplate('<%fp:form><%fp:label name="var" var="val">ok</%fp:label></%fp:form>')
        self.assertHTMLEqual(tpl, '<form action="" method="post"><label var="val">ok</label></form>')

    def test_label_match_forward(self):
        tpl = self.runTemplate('<%fp:form><%fp:label name="var">ok</%fp:label><%fp:text name="var" /></%fp:form>',
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><label>ok</label><input type="text" name="var" value="" /></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[1]['attrs']['for'], 
                         tags[3]['attrs']['id'])

    def test_label_match_back(self):
        tpl = self.runTemplate('<%fp:form><%fp:text name="var" /><%fp:label name="var">ok</%fp:label></%fp:form>',
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><input type="text" name="var" value="" /><label>ok</label></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[2]['attrs']['for'], 
                         tags[1]['attrs']['id'])

    def test_label_match_forward_multi(self):
        tpl = self.runTemplate('<%fp:form><%fp:label name="var">ok</%fp:label><%fp:text name="var" /><%fp:label name="var">ok</%fp:label><%fp:text name="var" /></%fp:form>',
                               strip_id=False)
        self.assertHTMLEqual(self.stripID(tpl), '<form action="" method="post"><label>ok</label><input type="text" name="var" value="" /><label>ok</label><input type="text" name="var" value="" /></form>')
        tags = self.get_tags(tpl)
        self.assertEqual(tags[1]['attrs']['for'], 
                         tags[3]['attrs']['id'])
        self.assertEqual(tags[4]['attrs']['for'], 
                         tags[6]['attrs']['id'])

    def test_label_match_back_multi(self):
        tpl = self.runTemplate('<%fp:form><%fp:text name="var" /><%fp:label name="var">ok</%fp:label><%fp:text name="var" /><%fp:label name="var">ok</%fp:label></%fp:form>',
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
suite.addTest(loader.loadTestsFromTestCase(MakoPumpFillTests))
suite.addTest(loader.loadTestsFromTestCase(MakoPumpFormContextTests))
suite.addTest(loader.loadTestsFromTestCase(MakoPumpFormTests))
suite.addTest(loader.loadTestsFromTestCase(MakoPumpInputTests))
