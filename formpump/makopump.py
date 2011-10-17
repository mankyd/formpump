"FormPump - It fills up forms"

import cgi
from mako.runtime import supports_caller
from random import Random
import string
import threading

from base import Form, StubForm

_mako_local = threading.local()
_mako_local.form = StubForm()
_mako_local.name_key = None
_mako_local.ctx_key = None
_mako_local.default_form_action = None
_mako_local.value_dict_name = 'form_vars'
_mako_local.error_dict_name = 'form_errors'

def set_form_name_key(name_key):
    _mako_local.name_key = name_key

def get_form_name_key():
    return _mako_local.name_key

def set_form_ctx_key(ctx_key):
    _mako_local.ctx_key = ctx_key

def get_form_ctx_key():
    return _mako_local.ctx_key

## Tags
def checkbox(context, **kwargs):
    return _mako_local.form.checkbox_tag(kwargs)

def email(context, **kwargs):
    return _mako_local.form.email_tag(kwargs)

@supports_caller
def form(context, **kwargs):
    name = kwargs.pop('name', None)
    
    form, _mako_local.form = _mako_local.form, Form(name,
                                                    _mako_local.name_key,
                                                    _mako_local.ctx_key,
                                                    kwargs,
                                                    _mako_local.default_form_action,
                                                    context.get(_mako_local.value_dict_name, {}),
                                                    context.get(_mako_local.error_dict_name, {}))
    context.write(_mako_local.form.start_tag())
    context['caller'].body()
    context.write(_mako_local.form.end_tag())
    return ''

def form_ctx(context, **kwargs):
    return _mako_local.form.context_tag(kwargs)
    
def hidden(context, **kwargs):
    return _mako_local.form.hidden_tag(kwargs)

@supports_caller
def label(context, **kwargs):
    context.write(_mako_local.form.label_tag(kwargs))
    context['caller'].body()
    context.write(_mako_local.form.end_label_tag())
    return ''



def password(context, **kwargs):
    return _mako_local.form.password_tag(kwargs)

def radio(context, **kwargs):
    return _mako_local.form.radio_tag(kwargs)

def submit(context, **kwargs):
    return _mako_local.form.submit_tag(kwargs)

def text(context, **kwargs):
    return _mako_local.form.text_tag(kwargs)

def textarea(context, **kwargs):
    return _mako_local.form.textarea_tag(kwargs)

