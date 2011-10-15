"FormPump - It fills up forms"

import cgi
import logging
from random import Random
import string

log = logging.getLogger('formpump')

class Form(object):
    def __init__(self, name, name_key, ctx_key, attrs, default_action, form_vars, form_errors):
        self.name = name
        self.name_key = name_key
        self.ctx_key = ctx_key
        self.attrs = attrs
        self.form_vars = form_vars
        self.form_errors = form_errors
        self.inputless_labels = {}
        self.labeless_inputs = {}

        log.debug("Form Name: %s", self.name)
        log.debug("Form Vars: %s", self.form_vars)
        log.debug("Form Errors: %s", self.form_errors)
        self.attrs.setdefault('method', 'post')
        self.attrs.setdefault('action', default_action() if callable(default_action) else default_action)


    def build_tag(self, tag, attrs, close=True, label=True):
        if label and attrs.get('name', None) is not None and not 'id' in attrs:
            name = attrs['name']
            if len(self.inputless_labels.get(name,[])) != 0:
                html_id = self.inputless_labels[name].pop(0)
            else:
                html_id = self.html_id()
                self.labeless_inputs.setdefault(name, [])
                self.labeless_inputs[name].append(html_id)
            attrs['id'] = html_id

        tag = '<' + cgi.escape(tag)
        for k,v in attrs.items():
            tag += ' %s="%s"' % (cgi.escape(k), cgi.escape(unicode(v if v is not None else '')))

        if close:
            return tag +' />'
        return tag + '>'

    def change_context(self, ctx_name, attrs):
        self.name = ctx_name
        if self.ctx_key or 'name' in attrs:
            attrs.setdefault('type', 'hidden')
            attrs.setdefault('name', self.ctx_key)
            attrs.setdefault('value', ctx_name)

            return self.build_tag('input', attrs)

        return ''

    def check_tag(self, attrs):
        name = attrs.get('name', None)
        attrs.setdefault('value', '1')
        true_values = ('1', 't', 'true', 'y', 'yes', 'on')
        if name is not None:
            value = self.form_vars.get(self.name, {}).get(name, '')
            if value == attrs['value'] or unicode(value).lower() in true_values and unicode(attrs['value']).lower() in true_values:
                attrs['checked'] = 'checked'
            else:
                attrs.pop('checked', None)

            error = self.form_errors.get(self.name, {}).get(name, None)
            if error:
                if 'class' in attrs:
                    attrs['class'] = 'error ' + attrs['class']
                else:
                    attrs['class'] = 'error'

        return self.build_tag('input', attrs)

    def end_label_tag(self):
        return '</label>'

    def end_tag(self):
        return '</form>'

    def error_tag(self, attrs, error_renderers):
        error = self.form_errors.get(self.name, {}).get(name, None)
        if not error:
            return ''

        attrs.setdefault('render', 'default')
        if attrs['render'] == 'default':
            renderer = error_renderers.get('default') or self._default_error
        else:
            renderer = error_renderers.get(attrs['render'])
        if renderer is None:
            raise ValueError('Unknown error renderer: %s' % attrs['render'])

        attrs.pop('render', None)

        return renderer(error, attrs)

    def html_id(self):
        source = string.letters+string.digits
        return u''.join( [Random().sample(source, 1)[0] for x in range(0, 32)] )

    def input_tag(self, attrs):
        html_id = self._assign_label_to_tag(attrs)
        if html_id is not None:
            attrs['id'] = html_id

        name = attrs.get('name', None)
        if name is not None:
            attrs['value'] = self.form_vars.get(self.name, {}).get(name, attrs.get('value', ''))
            error = self.form_errors.get(self.name, {}).get(name, None)
            if error is not None:
                if 'class' in attrs:
                    attrs['class'] = 'error ' + attrs['class']
                else:
                    attrs['class'] = 'error'

        return self.build_tag('input', attrs)

    def label_tag(self, label_for, attrs):
        for_id = self._assign_tag_to_label(label_for, attrs)
        if for_id is not None:
            attrs['for'] = for_id

        return self.build_tag('label', attrs, close=False)

    def quick_select_tag(self, attrs):
        options = attrs.pop('options', [])[:]
        prompt = attrs.pop('prompt', None)
        name = attrs.get('name', None)
        error = self.form_errors.get(self.name, {}).get(name, None)
        if error is not None:
            if 'class' in attrs:
                attrs['class'] = 'error ' + attrs['class']
            else:
                attrs['class'] = 'error'

        ret = self.build_tag('select', attrs, close=False)
        if prompt:
            options.insert(0, (None, prompt))

        value = self.form_vars.get(self.name, {}).get(name, '')
        for opt in options:
            attrs = {'value': opt[0]}
            if unicode(value) == unicode(opt[0]):
                attrs['selected'] = 'selected'
            ret += self.build_tag('option', attrs, close=False) + cgi.escape(opt[1]) + '</option>'

        return ret + '</select>'

    def radio_tag(self, attrs):
        name = attrs.get('name', None)
        if name is not None:
            value = self.form_vars.get(self.name, {}).get(name, '')
            if value == attrs.get('value', None):
                attrs['checked'] = 'checked'
            else:
                attrs.pop('checked', None)

            error = self.form_errors.get(self.name, {}).get(name, None)
            if error:
                if 'class' in attrs:
                    attrs['class'] = 'error ' + attrs['class']
                else:
                    attrs['class'] = 'error'

        return self.build_tag('input', attrs)

    def start_tag(self):
        ret = self.build_tag('form', self.attrs, close=False)

        if self.name is not None and self.name_key is not None:
            return ret + self.build_tag('input', {'type': 'hidden',
                                                  'name': self.name_key,
                                                  'value': self.name}, label=False)
        return ret

    def textarea_tag(self, attrs):
        html_id = self._assign_label_to_tag(attrs)
        if html_id is not None:
            attrs['id'] = html_id

        name = attrs.get('name', None)
        value = ''
        if name is not None:
            value = self.form_vars.get(self.name, {}).get(name, '')
            error = self.form_errors.get(self.name, {}).get(name, None)
            if error is not None:
                if 'class' in attrs:
                    attrs['class'] = 'error ' + attrs['class']
                else:
                    attrs['class'] = 'error'

        return '%s%s</textarea>' % (self.build_tag('textarea', attrs, close=False), cgi.escape(value or ''))


    def _assign_label_to_tag(self, attrs):
        if attrs.get('name', None) is not None and not 'id' in attrs:
            name = attrs['name']
            if len(self.inputless_labels.get(name,[])) != 0:
                html_id = self.inputless_labels[name].pop(0)
            else:
                html_id = self.html_id()
                self.labeless_inputs.setdefault(name, [])
                self.labeless_inputs[name].append(html_id)
            return html_id

        return None

    def _assign_tag_to_label(self, label_for, attrs):
        if label_for is not None and not 'id' in attrs :
            if len(self.labeless_inputs.get(label_for, [])) != 0:
                for_id = self.labeless_inputs[label_for].pop(0)
            else:
                for_id = self.html_id()
                self.inputless_labels.setdefault(label_for, [])
                self.inputless_labels[label_for].append(for_id)
            return for_id

        return None

class StubForm(Form):
    def __init__(self):
        Form.__init__(self, '', '', '', {}, '', {}, {})

class FormContext(object):
    def __init__(self, name):
        self.name = name

