FormPump - It fills your forms.
===============================

The FormPump is a collection of Python template engine extensions written to 
make HTML forms much easier to work with. It directly tackles the problems 
related to filling in values into your inputs, applying labels to your inputs
and displaying error messages in a quick way. It does this by introducing a set
of tags/functions into your template that create forms elements in an intuitive
and natural way that is quick to adapt into existing code.

At present, FormPump supports Jinja2.

An Introductory [Jinja2] Example
--------------------------------
(Examples shown in this README are shown in Jinja2. Other templating languages will have similar usage.)

    >>> from formpump import JinjaPump
    >>> from jinja2 import Environment
    >>> env = Environment(extensions=[JinjaPump])
    >>> tpl = env.from_string('''
    {% form "example" class="simple-form" %}
    ...    {% label 'inp'}Enter a value:{% endlabel %}
    ...    {% text "inp" %}
    ... {% endform %}
    ... ''')
    >>> print tpl.render()
    
    <form action="" class="simple-form" method="post">
        <label for="6GiCLEkUToekNy8xuN8AnT2esddU8MG8">Enter a value:</label>
        <input type="text" name="inp" value="" id="6GiCLEkUToekNy8xuN8AnT2esddU8MG8" />
    </form>
    
    >>> print tpl.render(form_vars={'example':{'inp': 123}})
    
    <form action="" class="simple-form" method="post">
        <label for="pnBP2IoFmfExTQdDZe44GKsFN6wrVOPu">Enter a value:</label>
        <input type="text" name="inp" value="" id="pnBP2IoFmfExTQdDZe44GKsFN6wrVOPu" />
    </form>


In the above example, we see a simple template object being created that contains one form. When rendered without any arguments, it simply prints out the form with no information filled in. When the special "form_vars" dict is provided, it fills any values it can find into the form as it generates it.

You may also notice the long, ugly id attributes that were set. These are required so that FormPump can associate labels with inputs; FormPump makes them up as it goes. You are free to override them yourself by simply providing your own `id` and `for` attributes on your elements. FormPump automatically keeps track of the labels and inputs in the template and attempts to intelligently associate them with one another, but only when the inputs do not have `id`'s specified, and labels don't have `for`'s specified.

Filling in Forms
----------------
FormPump fills in forms by looking up input values in designated template variable. This variable defaults to `form_vars` but can be configured by setting the `values_dict_name` property of the extension (for Jinja2, set this on the environment: `env.values_dict_name`). 

`form_vars` is a dictionary of dictionaries. Top level keys are the _form context_ identifiers, explained in more detail below. Each _form context_ refers to another dictionary which is a simple set of key-value pairs that FormPump uses to lookup values for the form. The keys refer to the input name. The values are become the value attribute* for the input, converted to unicode.

*note: For inputs like a radio button, where the values are predetermined, FormPump uses the `form_vars` value to determine which radio button to preselect, if any.

### Form Context's
FormPump allows you to have more than one form in your template. Each form can have overlapping input names. The forms are disambiguated by what FormPump calls the _form context_. The example above shows a form context set to "example" - it is the string immediately following the `form` keyword.

A simple example should clarify their usage:

    >>> tpl = env.from_string('''
    ... {% form "a" %}
    ...     {% text "inp" %}
    ... {% endform %}
    ... {% form "b" %}
    ...     {% text "inp" %}
    ... {% endform %}
    ... ''')
    >>> print tpl.render(form_vars={'a': {'inp': 'A'}, 'b': {'inp': 'B'}})
    <form action="" method="post">
        <input type="text" name="inp" value="A" id="TCpYQKe8Dsx3jvRLqUCKRtUfsDGmDIxu" />
    </form>
    <form action="" method="post">
        <input type="text" name="inp" value="B" id="8qXe3PUDgmDPAD3SOdQp6xEq3dYokLyU" />
    </form>

Form contexts actually serve a dual purpose. A common obstacle with having multiple HTML forms on a single page is that can be difficult to determine _which_ form was submitted if both forms have the same `action` attribute. Form contexts can help.

With the default settings, as shown thus far, they have no direct effect on the output. However, if you set the `form_name_key` property on the extension, FormPump will automatically insert a hidden input that contains the form context value as its name, (for Jinja2, set this on the environment).

    >>> env.form_name_key = '__'
    >>> tpl = env.from_string('''
    ... {% form "example" %}
    ... {% endform %}
    ... ''')
    >>> print tpl.render()
    
    <form action="" method="post"><input type="hidden" name="__" value="example" />
    </form>

The submitted value can then be used to easily identify the submitted form on the server.