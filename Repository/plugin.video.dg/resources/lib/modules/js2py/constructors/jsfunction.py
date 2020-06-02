from ..base import *
try:
    from ..translators.translator import translate_js
except:
    pass


@Js
def Function():
    a = [e.to_string().value for e in arguments.to_list()]
    body = ';'
    args = ()
    if len(a):
        body = '%s;' % a[-1]
        args = a[:-1]
    js_func = '(function (%s) {%s})' % (','.join(args), body)
    py_func =  translate_js(js_func, '')
    globals()['var'] = PyJs.GlobalObject
    temp = executor(py_func, globals())
    temp.source = '{%s}'%body
    temp.func_name = 'anonymous'
    return temp

def executor(f, glob):
    exec(f, globals())
    return globals()['PyJs_anonymous_0_']

Function.create = Function


fill_in_props(FunctionPrototype, {'constructor':Function}, default_attrs)

Function.define_own_property('prototype', {'value': FunctionPrototype,
                                         'enumerable': False,
                                         'writable': False,
                                         'configurable': False})
Function.own['length']['value'] = Js(1)

