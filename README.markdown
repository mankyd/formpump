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
(Examples shown in this README are shown in Jinja2. Other templating languages
will have similar usage.)

    >>> from formpump import JinjaPump
    >>> from jinja2 import Environment
    >>> env = Environment(extensions=[JinjaPump])
    >>> tpl = env.from_string('''
    ... {% form "example" class="simple-form" %}
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


In the above example, we see a simple template object being created that
contains one form. When rendered without any arguments, it simply prints out the
form with no information filled in. When the special "form_vars" dict is
provided, it fills any values it can find into the form as it generates it.

You may also notice the long, ugly id attributes that were set. These are
required so that FormPump can associate labels with inputs; FormPump makes them
up as it goes. You are free to override them yourself by simply providing your
own `id` and `for` attributes on your elements. FormPump automatically keeps
track of the labels and inputs in the template and attempts to intelligently
associate them with one another, but only when the inputs do not have `id`'s
specified, and labels don't have `for`'s specified.

Filling in Forms
----------------
FormPump fills in forms by looking up input values in designated template
variable. This variable defaults to `form_vars` but can be configured by setting
the `values_dict_name` property of the extension (for Jinja2, set this on the
environment: `env.values_dict_name`). 

`form_vars` is a dictionary of dictionaries. Top level keys are the
_form context_ identifiers, explained in more detail below. Each _form context_
refers to another dictionary which is a simple set of key-value pairs that
FormPump uses to lookup values for the form. The keys refer to the input name.
The values are become the value attribute* for the input, converted to unicode.

*note: For inputs like a radio button, where the values are predetermined,
FormPump uses the `form_vars` value to determine which radio button to preselect,
if any.

### Form Context's
FormPump allows you to have more than one form in your template. Each form can
have overlapping input names. The forms are disambiguated by what FormPump calls
the _form context_. The example above shows a form context set to "example" - it
is the string immediately following the `form` keyword. The string _must_ be a
constant string, not a variable or other dynamic expression, (there is a way
around this covered below).

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

Form contexts actually serve a dual purpose. A common obstacle with having
multiple HTML forms on a single page is that can be difficult to determine
_which_ form was submitted if both forms have the same `action` attribute. Form
contexts can help.

With the default settings, as shown thus far, they have no direct effect on the
output. However, if you set the `form_name_key` property on the extension,
FormPump will automatically insert a hidden input that contains the form context
value as its name, (for Jinja2, set this on the environment).

    >>> env.form_name_key = '__'
    >>> tpl = env.from_string('''
    ... {% form "example" %}
    ... {% endform %}
    ... ''')
    >>> print tpl.render()
    
    <form action="" method="post"><input type="hidden" name="__" value="example" />
    </form>

The submitted value can then be used to easily identify the submitted form on
the server.

_But_, using this feature brings up one more complication! Say we want to have
one form repeated multiple times on a single page. With each repetition of the
form, we want to change the variables that are prefilled. For instance, say you
have a list of people in a company, and you want to be able to edit and submit
updates to the phone number for each one. You therefore want the _same_
form_name submitted back to the server, but a _different_ form context when
filling in the form. Enter the `form_ctx` function, which allows you to change
the context where FormPump looks up values from on the fly. The `form_ctx`
function also allows you to assign dynamic context names to your forms, which
the standard form function does not:

    >>> tpl = env.from_string('''
    ... <ul>
    ... {% for person in people %}
    ...     <li>
    ...         {% form "person" %}
    ...             {% form_ctx "person.%d" % person['id'] %}
    ...             {% hidden "id" %}
    ...             {% label "phone" %}{{ person['name'] }}{% endlabel %}
    ...             {% text "phone" %}
    ...         {% endform %}
    ...     </li>
    ... {% endfor %}
    ... </ul>
    ... ''')
    >>> people = [{'id': 1, 'name': 'Bill B.', 'phone': '555-123-4567'},
    ...           {'id': 2, 'name': 'Chris C.', 'phone': '555-7654-321'}]
    >>> print tpl.render(people=people,
    ...                  form_vars=dict([('person.%d' % person['id'], person) for person in people]))

    <ul>

        <li>
            <form action="" method="post"><input type="hidden" name="__" value="person" />
           
                <input type="hidden" name="id" value="1" id="SnX73O3VCSqGdKKfk14UL5W2riTZwuVq" />
                <label for="weiOPnfowyRnF2tKTM9dGCVTUjmS7NZM">Bill B.</label>
                <input type="text" name="phone" value="555-123-4567" id="weiOPnfowyRnF2tKTM9dGCVTUjmS7NZM" />
            </form>
        </li>

        <li>
            <form action="" method="post"><input type="hidden" name="__" value="person" />
           
                <input type="hidden" name="id" value="2" id="TXyn6Vos37ixMPsNBsu8G10n9NlZrnlV" />
                <label for="2EKjdwWOY1GdtCVK20dtZYAqBSs4Bo9i">Chris C.</label>
                <input type="text" name="phone" value="555-7654-321" id="2EKjdwWOY1GdtCVK20dtZYAqBSs4Bo9i" />
            </form>
        </li>

    </ul>

If you look above, you will see two forms, both with the same form name, but
with different values filled in thanks to the dynamic `form_ctx`. The `form_ctx`
function affects all inputs that come _after_ it. You can specify multiple
`form_ctx`'s in a form if you want, each one pre-empting the previous. Note
however that his may become stylistically confusing.

Form Errors
-----------
Form errors work much like `form_vars`. You use the `error` function in your
template to indicate where errors should go, and then specify `form_error` as a
nested dictionary of dictionaries containing any and all error messages you'd
like to put in. Any `error` that does not find a corresponding value in the
`form_error` lookup will be left out of the final output.

    >>> tpl = env.from_string('''
    ... {% form "example" %}
    ...     {% error "field_A" %}
    ...     {% text "field_A" %}
    ...     {% error "field_B" %}
    ...     {% text "field_B" %}
    ... {% endform %}
    ... ''')
    >>> print tpl.render(form_vars={"example": {"field_A": "val A", "field_B": "val B"}},
    ...                  form_errors={"example": {"field_B": "error B"}})

    <form action="" method="post"><input type="hidden" name="__" value="example" />
    
        <input type="text" name="field_A" value="val A" id="XkWRXAE0w18j0N6c1mHmtEsSCMPJZWRn" />
        <div class="error-message">error B</div>
        <input class="error" type="text" name="field_B" value="val B" id="rP5RGqTnitBwA3oP8BZNcQ9oz3pFp0BC" />
    </form>

Note also that any inputs that find an error will have the "error" css class added to them.

Error messages by default are output like above &mdash; in a div with the class
"error-message". You can specify your own error message style by assigning
functions to its `error_renderers` dictionary and then specifying the `renderer`
attribute in the template: `{% error renderer="custom" %}`. By default, all
errors use the "default" renderer which you are free to override.