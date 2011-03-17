"FormPump - It fills up forms"

import cgi
from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension
from random import Random
import string

def pumpwidget(func):
    @environmentfunction
    def wrap(*args, **kwargs):
        args = list(args)
        env_index = 0
        if len(args) > 1 and not isinstance(args[env_index], Environment):
            env_index = 1
        env = args[env_index]
        
        jinjapump = None

        for ext in env.extensions.values():
            if  isinstance(ext, JinjaPump):
                jinjapump = ext
                break
            if jinjapump is None:
                raise Exception('Could not find JinjaPump in extensions')
        args[env_index] = jinjapump
        return func(*args, **kwargs)
    
    return wrap

class JinjaPump(Extension):
    # a set of names that trigger the extension.
    tags = set(['checkbox', 'email', 'error', 'form', 'form_ctx', 'hidden', 'label', 'password', 'quickselect', 'radio', 'submit', 'text', 'textarea'])

    def __init__(self, environment):
        Extension.__init__(self, environment)
        environment.extend(
            default_form_action = '',
            error_renderers = {'default': self._default_error},
            form_vars = {},
            form_errors = {},
            form_name_key = None,
            )
        self.form_name = None
        self.inputless_labels = {}
        self.labeless_inputs = {}

    def parse(self, parser):
        tag = parser.stream.next()

        if tag.value == 'form':
            return self._form(parser, tag)
        elif tag.value == 'form_ctx':
            return self._form_ctx(parser, tag)
        elif tag.value in ( 'email', 'hidden', 'password', 'text'):
            return self._input(parser, tag)
        elif tag.value == 'checkbox':
            return self._check(parser, tag)
        elif tag.value == 'radio':
            return self._radio(parser, tag)
        elif tag.value == 'submit':
            return self._submit(parser, tag)
        elif tag.value == 'label':
            return self._label(parser, tag)
        elif tag.value == 'quickselect':
            return self._quick_select(parser, tag)
        elif tag.value == 'textarea':
            return self._text_area(parser, tag)
        elif tag.value == 'error':
            return self._field_error(parser)

    def html_id(self):
        source = string.letters+string.digits
        return u''.join( [Random().sample(source, 1)[0] for x in range(0, 32)] )

    def build_tag(self, tag, attrs, close=True):
        if attrs.get('name', None) is not None and not 'id' in attrs:
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

    def _parse_attrs(self, parser, add_id=True):
        name = None
        if parser.stream.current.test('string'):
            name = parser.parse_expression(with_condexpr=False)

        attrs = {}
        while parser.stream.current.type != 'block_end':
            node = parser.parse_assign_target(with_tuple=False)

            if parser.stream.skip_if('assign'):
                attrs[node.name] = parser.parse_expression()
            else:
                attrs[node.name] = nodes.Const(node.name)

        return (name, attrs)

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

    def _form(self, parser, tag):
        form_name, attrs = self._parse_attrs(parser)

        form_name = form_name or nodes.Const(None)
        
        body = parser.parse_statements(['name:endform'], drop_needle=True)

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])
        return [nodes.Output([self.call_method('form_tag', args=[form_name, attrs])]),
                nodes.CallBlock(self.call_method('_form_block', args=[form_name]),
                                [], [], body).set_lineno(tag.lineno),
                nodes.Output([nodes.MarkSafe(nodes.Const('</form>'))])]

    def form_tag(self, form_name, attrs):
        attrs.setdefault('method', 'post')
        attrs.setdefault('action', self.environment.default_form_action() if callable(self.environment.default_form_action) else self.environment.default_form_action)
        ret = self.build_tag('form', attrs, close=False)

        if form_name is not None and self.environment.form_name_key is not None:
            return ret + '<input type="hidden" name="%s" value="%s" />' % (cgi.escape(self.environment.form_name_key), cgi.escape(form_name))

        return ret

    def _form_block(self, form_name, caller):
        form_name, self.form_name = self.form_name, form_name
        il, self.inputless_labels = self.inputless_labels, {}
        li, self.labeless_inputs = self.labeless_inputs, {}
        ret = caller()
        self.form_name = form_name
        self.inputless_labels = il
        self.labeless_inputs = li

        return ret

    def _form_ctx(self, parser, tag):
        form_name = parser.parse_expression()

        return [nodes.ExprStmt(self.call_method('_switch_form_name', args=[form_name]))]

    def _switch_form_name(self, form_name):
        self.form_name = form_name

    def _input(self, parser, tag, method_name='input_tag'):
        name, attrs = self._parse_attrs(parser)
        if name is not None:
            attrs['name'] = name

        attrs['type'] = nodes.Const(tag.value)
        
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method(method_name, args=[attrs])])

    def input_tag(self, attrs):
        html_id = self._assign_label_to_tag(attrs)
        if html_id is not None:
            attrs['id'] = html_id

        name = attrs.get('name', None)
        if name is not None:
            attrs['value'] = self.environment.form_vars.get(self.form_name, {}).get(name, '')
            error = self.environment.form_errors.get(self.form_name, {}).get(name, None)
            if error is not None:
                if 'class' in attrs:
                    attrs['class'] = 'error ' + attrs['class']
                else:
                    attrs['class'] = 'error'

        return self.build_tag('input', attrs)

    def _check(self, parser, tag):
        return self._input(parser, tag, method_name='check_tag')

    def check_tag(self, attrs):
        name = attrs.get('name', None)
        attrs.setdefault('value', '1')
        true_values = ('1', 't', 'true', 'y', 'yes', 'on')
        if name is not None:
            value = self.environment.form_vars.get(self.form_name, {}).get(name, '')
            if value == attrs['value'] or unicode(value).lower() in true_values and unicode(attrs['value']).lower() in true_values:
                attrs['checked'] = 'checked'
            else:
                attrs.pop('checked', None)

        return self.build_tag('input', attrs)

    def _radio(self, parser, tag):
        return self._input(parser, tag, method_name='radio_tag')

    def radio_tag(self, attrs):
        name = attrs.get('name', None)
        if name is not None:
            value = self.environment.form_vars.get(self.form_name, {}).get(name, '')
            if value == attrs.get('value', None):
                attrs['checked'] = 'checked'
            else:
                attrs.pop('checked', None)

        return self.build_tag('input', attrs)

    def _submit(self, parser, tag):
        name, attrs = self._parse_attrs(parser)
        if name is not None:
            attrs['value'] = name

        attrs['type'] = nodes.Const(tag.value)

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method('input_tag', args=[attrs])])

    def _label(self, parser, tag):
        label_for, attrs = self._parse_attrs(parser)

        if label_for is None and 'name' in attrs:
            label_for = attrs['name']
            del attrs['name']
            
        body = parser.parse_statements(['name:endlabel'], drop_needle=True)
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return [nodes.Output([self.call_method('label_tag', args=[label_for, attrs])])] + body + [nodes.Output([nodes.MarkSafe(nodes.Const('</label>'))])]

    def label_tag(self, label_for, attrs):
        for_id = self._assign_tag_to_label(label_for, attrs)
        if for_id is not None:
            attrs['for'] = for_id

        return self.build_tag('label', attrs, close=False)

    def _quick_select(self, parser, tag):
        name, attrs = self._parse_attrs(parser)
        if name is not None:
            attrs['name'] = name

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return [nodes.Output([self.call_method('quick_select_tag', args=[attrs])])]

    def quick_select_tag(self, attrs):
        options = attrs.pop('options', [])[:]
        prompt = attrs.pop('prompt', None)
        name = attrs.get('name', None)
        error = self.environment.form_errors.get(self.form_name, {}).get(name, None)
        if error is not None:
            if 'class' in attrs:
                attrs['class'] = 'error ' + attrs['class']
            else:
                attrs['class'] = 'error'

        ret = self.build_tag('select', attrs, close=False)
        if prompt:
            options.insert(0, (None, prompt))

        value = self.environment.form_vars.get(self.form_name, {}).get(name, '')
        for opt in options:
            attrs = {'value': opt[0]}
            if unicode(value) == unicode(opt[0]):
                attrs['selected'] = 'selected'
            ret += self.build_tag('option', attrs, close=False) + cgi.escape(opt[1]) + '</option>'

        return ret + '</select>'

    def _text_area(self, parser, tag):
        name, attrs = self._parse_attrs(parser)
        if name is not None:
            attrs['name'] = name

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])
        return [nodes.Output([self.call_method('text_area_tag', args=[attrs])])]

    def text_area_tag(self, attrs):
        html_id = self._assign_label_to_tag(attrs)
        if html_id is not None:
            attrs['id'] = html_id

        name = attrs.get('name', None)
        value = ''
        if name is not None:
            value = self.environment.form_vars.get(self.form_name, {}).get(name, '')
            error = self.environment.form_errors.get(self.form_name, {}).get(name, None)
            if error is not None:
                if 'class' in attrs:
                    attrs['class'] = 'error ' + attrs['class']
                else:
                    attrs['class'] = 'error'

        return '%s%s</textarea>' % (self.build_tag('textarea', attrs, close=False), cgi.escape(value or ''))

    def _field_error(self, parser):
        name, attrs = self._parse_attrs(parser)
        name = name or attrs.get('name', None)
        if name is None:
            raise ValueError('First argument of error tag must be a string')

        attrs.setdefault('render', nodes.Const('default'))

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method('field_error_tag', args=[name, attrs])])

    def field_error_tag(self, name, attrs):
        error = self.environment.form_errors.get(self.form_name, {}).get(name, None)
        if not error:
            return ''

        renderer = self.environment.error_renderers.get(attrs['render'], None)
        if renderer is None:
            raise ValueError('Unknown error renderer: %s' % attrs['render'])

        attrs.pop('render', None)

        return renderer(error, attrs)

    def _default_error(self, error, attrs):
        if 'class' in attrs:
            attrs['class'] = 'error-message '+attrs['class']
        else:
            attrs['class'] = 'error-message'

        return self.build_tag('div', attrs, close=False) + unicode(error) + '</div>'

