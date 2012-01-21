"FormPump - It fills up forms"

from jinja2 import Environment, environmentfunction, nodes
from jinja2.ext import Extension

from base import Form, StubForm

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
    tags = set(['checkbox', 'email', 'error', 'file', 'form', 'form_ctx', 'hidden', 'iferror', 'label', 'password', 'quickselect', 'radio', 'submit', 'text', 'textarea'])

    def __init__(self, environment):
        Extension.__init__(self, environment)
        environment.extend(
            default_form_action = '',
            error_renderers     = {},
            value_dict_name     = 'form_vars',
            error_dict_name     = 'form_errors',
            form_name_key       = None,
            form_ctx_key        = None,
            )
        self.form = StubForm()

    def _form_vars_node(self):
        return nodes.Or(nodes.Name(self.environment.value_dict_name, 'load'), nodes.Dict([]))
    
    def _form_errors_node(self):
        return nodes.Or(nodes.Name(self.environment.error_dict_name, 'load'), nodes.Dict([]))

    def parse(self, parser):
        tag = parser.stream.next()

        if tag.value == 'form':
            return self._form(parser, tag)
        elif tag.value == 'form_ctx':
            return self._form_ctx(parser, tag)
        elif tag.value in ( 'email', 'file', 'hidden', 'password', 'text'):
            return self._input(parser, tag)
        elif tag.value == 'checkbox':
            return self._check(parser, tag)
        elif tag.value == 'iferror':
            return self._iferror(parser, tag)
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

    def _form(self, parser, tag):
        form_name, attrs = self._parse_attrs(parser)

        form_name = form_name or nodes.Const(None)
        
        body = parser.parse_statements(['name:endform'], drop_needle=True)

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])
        return [nodes.CallBlock(self.call_method('_form_block', args=[form_name, attrs, self._form_vars_node(), self._form_errors_node()]),
                                [], [], body).set_lineno(tag.lineno)]

    def _form_block(self, form_name, attrs, form_vars, form_errors, caller):
        form = Form(form_name, 
                    self.environment.form_name_key, 
                    self.environment.form_ctx_key,
                    attrs, 
                    self.environment.default_form_action,
                    form_vars,
                    form_errors)
        form, self.form = self.form, form
        ret = caller()
        form, self.form = self.form, form
        return form.start_tag() + ret + form.end_tag()

    def _form_ctx(self, parser, tag):
        name, attrs = self._parse_attrs(parser)

        if name is not None:
            attrs['name'] = name

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method('_switch_form_ctx', args=[attrs])])

    def _switch_form_ctx(self, attrs):
        return self.form.context_tag(attrs)

    def _input(self, parser, tag, method_name='input_tag'):
        name, attrs = self._parse_attrs(parser)
        if name is not None:
            attrs['name'] = name

        attrs['type'] = nodes.Const(tag.value)
        
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method(method_name, args=[attrs])])

    def input_tag(self, attrs):
        return self.form.input_tag(attrs)

    def _check(self, parser, tag):
        return self._input(parser, tag, method_name='checkbox_tag')

    def checkbox_tag(self, attrs):
        return self.form.checkbox_tag(attrs)

    def _radio(self, parser, tag):
        return self._input(parser, tag, method_name='radio_tag')

    def radio_tag(self, attrs):
        return self.form.radio_tag(attrs)

    def _iferror(self, parser, tag):
        name, attrs = self._parse_attrs(parser)
        name = name or attrs.get('name', None)
        if name is None:
            raise ValueError('First argument of error tag must be a string')
            
        body = parser.parse_statements(['name:endiferror'], drop_needle=True)

        return [nodes.CallBlock(self.call_method('_iferror_block', args=[name]),
                                [], [], body).set_lineno(tag.lineno)]


    def _iferror_block(self, attrs, caller):
        if self.form.if_error(name):
            return caller()
        return ''

    def _submit(self, parser, tag):
        name, attrs = self._parse_attrs(parser)
        if name is not None:
            attrs['name'] = name

        attrs['type'] = nodes.Const(tag.value)

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method('input_tag', args=[attrs])])

    def _label(self, parser, tag):
        name, attrs = self._parse_attrs(parser)

        if name is not None:
            attrs['name'] = name
            
        body = parser.parse_statements(['name:endlabel'], drop_needle=True)
        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return [nodes.CallBlock(self.call_method('_label_block', args=[attrs]),
                                [], [], body).set_lineno(tag.lineno)]


    def _label_block(self, attrs, caller):
        return self.form.label_tag(attrs) + caller() + self.form.end_label_tag()

    def _quick_select(self, parser, tag):
        name, attrs = self._parse_attrs(parser)
        if name is not None:
            attrs['name'] = name

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return [nodes.Output([self.call_method('quick_select_tag', args=[attrs])])]

    def quick_select_tag(self, attrs):
        return self.form.quick_select_tag(attrs)

    def _text_area(self, parser, tag):
        name, attrs = self._parse_attrs(parser)
        if name is not None:
            attrs['name'] = name

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])
        return [nodes.Output([self.call_method('text_area_tag', args=[attrs])])]

    def text_area_tag(self, attrs):
        return self.form.textarea_tag(attrs)

    def _field_error(self, parser):
        name, attrs = self._parse_attrs(parser)
        name = name or attrs.get('name', None)
        if name is None:
            raise ValueError('First argument of error tag must be a string')

        attrs.setdefault('render', nodes.Const('default'))

        attrs = nodes.Dict([nodes.Pair(nodes.Const(k), v) for k,v in attrs.items()])

        return nodes.Output([self.call_method('field_error_tag', args=[name, attrs])])

    def field_error_tag(self, name, attrs):
        return self.form.error_tag(name, attrs, self.environment.error_renderers)
