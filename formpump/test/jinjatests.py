import jinja2
import re
import unittest

import formpump

class JinjaPumpTests(unittest.TestCase):
    def setUp(self):
        self.env = jinja2.Environment(extensions=[formpump.JinjaPump])

    def stripID(self, val):
        return re.sub(r' id="[^"]*"', '', val, 1)

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
        
if __name__ == "__main__":
    unittest.main()

loader = unittest.TestLoader()
#print loader.getTestCaseNames(JinjaPumpFormTests)
#suite = unittest.TestLoader().loadTestsFromNames(['test.jinjatests.JinjaPumpFormTests'])
suite = unittest.TestSuite()
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpFormTests))
suite.addTest(loader.loadTestsFromTestCase(JinjaPumpInputTests))
#suite = unittest.TestSuite([JinjaPumpFormTests(),
#                            JinjaPumpInputTests(),
#                            ])
