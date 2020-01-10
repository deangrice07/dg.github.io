# -*- coding: UTF-8 -*-


# Addon Name: Laplaza
# Addon id: plugin.video.laplaza
# Addon Provider: Cy4Root

from utils import *
from jsparser import *

def exps_translator(js):
    ass = assignment_translator(js)



def assignment_translator(js):
    sep = js.split(',')
    res = sep[:]
    for i, e in enumerate(sep):
        if '=' not in e: 
            continue
        res[i] = bass_translator(e)
    return ','.join(res)


def bass_translator(s):
    if '(' in s or '[' in s:
        converted = ''
        for e in bracket_split(s, ['()','[]'], strip=False):
            if e[0]=='(':
                converted += '(' + bass_translator(e[1:-1])+')'
            elif e[0]=='[':
                converted += '[' + bass_translator(e[1:-1])+']'
            else:
                converted += e
        s = converted
    if '=' not in s:
        return s
    ass = reversed(s.split('='))
    last = ass.next()
    res = last
    for e in ass:
        op = ''
        if e[-1] in OP_METHODS: 
            op = ', "'+e[-1]+'"'
            e = e[:-1]
        cand = e.strip('() ')  
        if not is_property_accessor(cand): 
            if not is_lval(cand) or is_internal(cand):
                raise SyntaxError('Invalid left-hand side in assignment')
            res = 'var.put(%s, %s%s)'%(cand.__repr__(), res, op)
        elif cand[-1]==']': 
            c = list(bracket_split(cand, ['[]'], strip=False))
            meth, prop = ''.join(c[:-1]).strip(), c[-1][1:-1].strip() 
                                                                     
            res =  '%s.put(%s, %s%s)'%(meth, prop, res, op)
        else:  
            c = cand.rfind('.')
            meth, prop = cand[:c].strip(), cand[c+1:].strip('() ')
            if not is_lval(prop):
                raise SyntaxError('Invalid left-hand side in assignment')
            res =  '%s.put(%s, %s%s)'%(meth, prop.__repr__(), res, op)
    return res

if __name__=='__main__':
    print bass_translator('3.ddsd = 40')
