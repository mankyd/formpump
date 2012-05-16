"FormPump - It fills up forms"

import cgi
from mako.runtime import supports_caller
from random import Random
import string

from base import Form, StubForm

class MakoSettings(object):
    def __init__(self):
        self.form = StubForm()
        self.name_key = None
        self.ctx_key = None
        self.default_form_action = None
        self.value_dict_name = 'form_vars'
        self.error_dict_name = 'form_errors'
        self.error_renderers = {}
        
_mako_settings = MakoSettings()

def set_form_name_key(name_key):
    _name_key = _mako_settings.name_key
    _mako_settings.name_key = name_key
    return _name_key

def get_form_name_key():
    return _mako_settings.name_key

def set_form_ctx_key(ctx_key):
    _ctx_key = _mako_settings.ctx_key
    _mako_settings.ctx_key = ctx_key
    return _ctx_key

def get_form_ctx_key():
    return _mako_settings.ctx_key

def add_error_renderer(name, callback):
    _mako_settings.error_renderers[name] = callback

def remove_error_renderer(name):
    _mako_settings.error_renderers.pop(name, None)

## Tags
def checkbox(context, **kwargs):
    context.write(_mako_settings.form.checkbox_tag(kwargs))
    return ''

def email(context, **kwargs):
    context.write(_mako_settings.form.email_tag(kwargs))
    return ''

def error(context, name, **kwargs):
    context.write(_mako_settings.form.error_tag(name, kwargs, _mako_settings.error_renderers))
    return ''

def file(context, **kwargs):
    context.write(_mako_settings.form.file_tag(kwargs))
    return ''
    
@supports_caller
def form(context, **kwargs):
    name = kwargs.pop('name', None)
    
    form, _mako_settings.form = _mako_settings.form, Form(name,
                                                    _mako_settings.name_key,
                                                    _mako_settings.ctx_key,
                                                    kwargs,
                                                    _mako_settings.default_form_action,
                                                    context.get(_mako_settings.value_dict_name, {}),
                                                    context.get(_mako_settings.error_dict_name, {}))
    context.write(_mako_settings.form.start_tag())
    context['caller'].body()
    context.write(_mako_settings.form.end_tag())
    return ''

def form_ctx(context, **kwargs):
    context.write(_mako_settings.form.context_tag(kwargs))
    return ''
    
def hidden(context, **kwargs):
    context.write(_mako_settings.form.hidden_tag(kwargs))
    return ''

@supports_caller
def iferror(context, name):
    if _mako_settings.form.if_error(name):
        context['caller'].body()
    return ''

@supports_caller
def ifnoterror(context, name):
    if _mako_settings.form.if_not_error(name):
        context['caller'].body()
    return ''

@supports_caller
def label(context, **kwargs):
    context.write(_mako_settings.form.label_tag(kwargs))
    context['caller'].body()
    context.write(_mako_settings.form.end_label_tag())
    return ''

def password(context, **kwargs):
    context.write(_mako_settings.form.password_tag(kwargs))
    return ''

def radio(context, **kwargs):
    context.write(_mako_settings.form.radio_tag(kwargs))
    return ''

def submit(context, **kwargs):
    context.write(_mako_settings.form.submit_tag(kwargs))
    return ''

def text(context, **kwargs):
    context.write(_mako_settings.form.text_tag(kwargs))
    return ''

def textarea(context, **kwargs):
    context.write(_mako_settings.form.textarea_tag(kwargs))
    return ''

