# -*- coding: UTF-8 -*-


# Addon Name: Mirrorv2
# Addon id: plugin.video.mirrorv2
# Addon Provider: Cy4Root

import re

def detect(source):
    """Detects whether `source` is P.A.C.K.E.R. coded."""
    source = source.replace(' ', '')
    if re.search('eval\(function\(p,a,c,k,e,(?:r|d)', source): return True
    else: return False

def unpack(source):
    """Unpacks P.A.C.K.E.R. packed js code."""
    payload, symtab, radix, count = _filterargs(source)

    if count != len(symtab):
        raise UnpackingError('Malformed p.a.c.k.e.r. symtab.')

    try:
        unbase = Unbaser(radix)
    except TypeError:
        raise UnpackingError('Unknown p.a.c.k.e.r. encoding.')

    def lookup(match):
        """Look up symbols in the synthetic symtab."""
        word = match.group(0)
        return symtab[unbase(word)] or word

    source = re.sub(r'\b\w+\b', lookup, payload)
    return _replacestrings(source)

def _filterargs(source):
    """Juice from a source file the four args needed by decoder."""
    argsregex = (r"}\s*\('(.*)',\s*(.*?),\s*(\d+),\s*'(.*?)'\.split\('\|'\)")
    args = re.search(argsregex, source, re.DOTALL).groups()

    try:
        payload, radix, count, symtab = args
        radix = 36 if not radix.isdigit() else int(radix)
        return payload, symtab.split('|'), radix, int(count)
    except ValueError:
        raise UnpackingError('Corrupted p.a.c.k.e.r. data.')

def _replacestrings(source):
    """Strip string lookup table (list) and replace values in source."""
    match = re.search(r'var *(_\w+)\=\["(.*?)"\];', source, re.DOTALL)

    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = '%s[%%d]' % varname
        for index, value in enumerate(lookup):
            source = source.replace(variable % index, '"%s"' % value)
        return source[startpoint:]
    return source


class Unbaser(object):
    """Functor for a given base. Will efficiently convert
    strings to natural numbers."""
    ALPHABET = {
        62: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        95: (' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
             '[\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
    }

    def __init__(self, base):
        self.base = base


        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            if base < 62:
                self.ALPHABET[base] = self.ALPHABET[62][0:base]
            elif 62 < base < 95:
                self.ALPHABET[base] = self.ALPHABET[95][0:base]
            try:
                self.dictionary = dict((cipher, index) for index, cipher in enumerate(self.ALPHABET[base]))
            except KeyError:
                raise TypeError('Unsupported base encoding.')

            self.unbase = self._dictunbaser

    def __call__(self, string):
        return self.unbase(string)

    def _dictunbaser(self, string):
        """Decodes a  value to an integer."""
        ret = 0
        for index, cipher in enumerate(string[::-1]):
            ret += (self.base ** index) * self.dictionary[cipher]
        return ret

class UnpackingError(Exception):
    """Badly packed source or general error. Argument is a
    meaningful description."""
    pass


if __name__ == "__main__":
    test='''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}(';k N=\'\',2c=\'1T\';1P(k i=0;i<12;i++)N+=2c.V(C.K(C.H()*2c.E));k 2j=8,33=5O,2H=5Z,2e=5Y,36=B(t){k o=!1,i=B(){z(q.1k){q.2g(\'2Q\',e);D.2g(\'29\',e)}P{q.2A(\'2v\',e);D.2A(\'24\',e)}},e=B(){z(!o&&(q.1k||5V.38===\'29\'||q.2F===\'2n\')){o=!0;i();t()}};z(q.2F===\'2n\'){t()}P z(q.1k){q.1k(\'2Q\',e);D.1k(\'29\',e)}P{q.2u(\'2v\',e);D.2u(\'24\',e);k n=!1;2N{n=D.54==5I&&q.27}2R(a){};z(n&&n.2i){(B r(){z(o)F;2N{n.2i(\'16\')}2R(e){F 5v(r,50)};o=!0;i();t()})()}}};D[\'\'+N+\'\']=(B(){k t={t$:\'1T+/=\',5r:B(e){k d=\'\',l,a,i,s,c,r,n,o=0;e=t.e$(e);1b(o<e.E){l=e.14(o++);a=e.14(o++);i=e.14(o++);s=l>>2;c=(l&3)<<4|a>>4;r=(a&15)<<2|i>>6;n=i&63;z(2O(a)){r=n=64}P z(2O(i)){n=64};d=d+U.t$.V(s)+U.t$.V(c)+U.t$.V(r)+U.t$.V(n)};F d},13:B(e){k n=\'\',l,c,d,s,a,i,r,o=0;e=e.1x(/[^A-5l-5o-9\\+\\/\\=]/g,\'\');1b(o<e.E){s=U.t$.1F(e.V(o++));a=U.t$.1F(e.V(o++));i=U.t$.1F(e.V(o++));r=U.t$.1F(e.V(o++));l=s<<2|a>>4;c=(a&15)<<4|i>>2;d=(i&3)<<6|r;n=n+O.T(l);z(i!=64){n=n+O.T(c)};z(r!=64){n=n+O.T(d)}};n=t.n$(n);F n},e$:B(t){t=t.1x(/;/g,\';\');k n=\'\';1P(k o=0;o<t.E;o++){k e=t.14(o);z(e<1C){n+=O.T(e)}P z(e>5x&&e<5J){n+=O.T(e>>6|5F);n+=O.T(e&63|1C)}P{n+=O.T(e>>12|2E);n+=O.T(e>>6&63|1C);n+=O.T(e&63|1C)}};F n},n$:B(t){k o=\'\',e=0,n=5E=1B=0;1b(e<t.E){n=t.14(e);z(n<1C){o+=O.T(n);e++}P z(n>4V&&n<2E){1B=t.14(e+1);o+=O.T((n&31)<<6|1B&63);e+=2}P{1B=t.14(e+1);2o=t.14(e+2);o+=O.T((n&15)<<12|(1B&63)<<6|2o&63);e+=3}};F o}};k r=[\'6m==\',\'6w\',\'6F=\',\'6y\',\'6j\',\'5X=\',\'5U=\',\'6b=\',\'68\',\'69\',\'3b=\',\'6l=\',\'48\',\'49\',\'47=\',\'46\',\'43=\',\'44=\',\'45=\',\'4a=\',\'4b=\',\'4g=\',\'4h==\',\'4f==\',\'4e==\',\'4c==\',\'4d=\',\'42\',\'41\',\'3Q\',\'3R\',\'3P\',\'3O\',\'3L==\',\'3M=\',\'3N=\',\'3S=\',\'3T==\',\'3Z=\',\'40\',\'3Y=\',\'3X=\',\'3U==\',\'3V=\',\'3W==\',\'4i==\',\'4j=\',\'4G=\',\'4H\',\'4F==\',\'4E==\',\'4B\',\'4C==\',\'4D=\'],y=C.K(C.H()*r.E),W=t.13(r[y]),b=W,M=1,p=\'#4I\',a=\'#4J\',g=\'#4O\',w=\'#4P\',Q=\'\',Y=\'4N!\',v=\'4M 4K 4L 4A\\\'4z 4p 4q 2I 2W. 3K\\\'s 4n.  4k 4l\\\'t?\',f=\'4m 4r 4s-4x, 4y 4w\\\'t 4v 4t U 4u 4Q.\',s=\'I 3A, I 3a 3j 3i 2I 2W.  3e 3g 3h!\',o=0,u=1,n=\'3c.3d\',l=0,L=e()+\'.2V\';B h(t){z(t)t=t.1Q(t.E-15);k n=q.2K(\'34\');1P(k o=n.E;o--;){k e=O(n[o].1J);z(e)e=e.1Q(e.E-15);z(e===t)F!0};F!1};B m(t){z(t)t=t.1Q(t.E-15);k e=q.3f;x=0;1b(x<e.E){1o=e[x].1R;z(1o)1o=1o.1Q(1o.E-15);z(1o===t)F!0;x++};F!1};B e(t){k o=\'\',e=\'1T\';t=t||30;1P(k n=0;n<t;n++)o+=e.V(C.K(C.H()*e.E));F o};B i(o){k i=[\'3J\',\'3C==\',\'3B\',\'3k\',\'35\',\'3y==\',\'3z=\',\'3D==\',\'3E=\',\'3I==\',\'3H==\',\'3G==\',\'3F\',\'3x\',\'3w\',\'35\'],a=[\'2P=\',\'3p==\',\'3o==\',\'3n==\',\'3l=\',\'3m\',\'3q=\',\'3r=\',\'2P=\',\'3v\',\'3u==\',\'3t\',\'3s==\',\'4o==\',\'5L==\',\'6a=\'];x=0;1K=[];1b(x<o){c=i[C.K(C.H()*i.E)];d=a[C.K(C.H()*a.E)];c=t.13(c);d=t.13(d);k r=C.K(C.H()*2)+1;z(r==1){n=\'//\'+c+\'/\'+d}P{n=\'//\'+c+\'/\'+e(C.K(C.H()*20)+4)+\'.2V\'};1K[x]=26 1V();1K[x].23=B(){k t=1;1b(t<7){t++}};1K[x].1J=n;x++}};B Z(t){};F{2B:B(t,a){z(66 q.J==\'1U\'){F};k o=\'0.1\',a=b,e=q.1c(\'1s\');e.1m=a;e.j.1i=\'1I\';e.j.16=\'-1h\';e.j.X=\'-1h\';e.j.1u=\'2d\';e.j.11=\'67\';k d=q.J.2L,r=C.K(d.E/2);z(r>15){k n=q.1c(\'2a\');n.j.1i=\'1I\';n.j.1u=\'1q\';n.j.11=\'1q\';n.j.X=\'-1h\';n.j.16=\'-1h\';q.J.6c(n,q.J.2L[r]);n.1d(e);k i=q.1c(\'1s\');i.1m=\'2M\';i.j.1i=\'1I\';i.j.16=\'-1h\';i.j.X=\'-1h\';q.J.1d(i)}P{e.1m=\'2M\';q.J.1d(e)};l=6h(B(){z(e){t((e.1X==0),o);t((e.1W==0),o);t((e.1O==\'2X\'),o);t((e.1N==\'2z\'),o);t((e.1E==0),o)}P{t(!0,o)}},21)},1S:B(e,m){z((e)&&(o==0)){o=1;o$.6g([\'6f\',\'6d\',\'6e\',1U,1U,!0]);D[\'\'+N+\'\'].1r();D[\'\'+N+\'\'].1S=B(){F}}P{k f=t.13(\'62\'),c=q.61(f);z((c)&&(o==0)){z((33%3)==0){k d=\'5R=\';d=t.13(d);z(h(d)){z(c.1G.1x(/\\s/g,\'\').E==0){o=1;D[\'\'+N+\'\'].1r()}}}};k p=!1;z(o==0){z((2H%3)==0){z(!D[\'\'+N+\'\'].2C){k l=[\'5S==\',\'5Q==\',\'4R=\',\'5P=\',\'5N=\'],s=l.E,a=l[C.K(C.H()*s)],n=a;1b(a==n){n=l[C.K(C.H()*s)]};a=t.13(a);n=t.13(n);i(C.K(C.H()*2)+1);k r=26 1V(),u=26 1V();r.23=B(){i(C.K(C.H()*2)+1);u.1J=n;i(C.K(C.H()*2)+1)};u.23=B(){o=1;i(C.K(C.H()*3)+1);D[\'\'+N+\'\'].1r()};r.1J=a;z((2e%3)==0){r.24=B(){z((r.11<8)&&(r.11>0)){D[\'\'+N+\'\'].1r()}}};i(C.K(C.H()*3)+1);D[\'\'+N+\'\'].2C=!0};D[\'\'+N+\'\'].1S=B(){F}}}}},1r:B(){z(u==1){k M=2w.5W(\'2D\');z(M>0){F!0}P{2w.6B(\'2D\',(C.H()+1)*21)}};k c=\'6x==\';c=t.13(c);z(!m(c)){k h=q.1c(\'6C\');h.1Z(\'6D\',\'6H\');h.1Z(\'38\',\'1l/6G\');h.1Z(\'1R\',c);q.2K(\'6E\')[0].1d(h)};6v(l);q.J.1G=\'\';q.J.j.19+=\'S:1q !17\';q.J.j.19+=\'1p:1q !17\';k Q=q.27.1W||D.32||q.J.1W,y=D.6k||q.J.1X||q.27.1X,r=q.1c(\'1s\'),b=e();r.1m=b;r.j.1i=\'2t\';r.j.16=\'0\';r.j.X=\'0\';r.j.11=Q+\'1z\';r.j.1u=y+\'1z\';r.j.2G=p;r.j.1Y=\'6q\';q.J.1d(r);k d=\'<a 1R="6t://6s.6r" j="G-1e:10.6I;G-1n:1j-1g;1f:6u;">6n 6i 5M 5b-5a 34</a>\';d=d.1x(\'59\',e());d=d.1x(\'57\',e());k i=q.1c(\'1s\');i.1G=d;i.j.1i=\'1I\';i.j.1y=\'1H\';i.j.16=\'1H\';i.j.11=\'5c\';i.j.1u=\'5d\';i.j.1Y=\'2h\';i.j.1E=\'.6\';i.j.2p=\'2k\';i.1k(\'5i\',B(){n=n.5h(\'\').5g().5e(\'\');D.2f.1R=\'//\'+n});q.1L(b).1d(i);k o=q.1c(\'1s\'),R=e();o.1m=R;o.j.1i=\'2t\';o.j.X=y/7+\'1z\';o.j.56=Q-55+\'1z\';o.j.4W=y/3.5+\'1z\';o.j.2G=\'#4S\';o.j.1Y=\'2h\';o.j.19+=\'G-1n: "4T 4X", 1w, 1t, 1j-1g !17\';o.j.19+=\'4Y-1u: 53 !17\';o.j.19+=\'G-1e: 52 !17\';o.j.19+=\'1l-1v: 1A !17\';o.j.19+=\'1p: 4Z !17\';o.j.1O+=\'2T\';o.j.37=\'1H\';o.j.51=\'1H\';o.j.5j=\'2s\';q.J.1d(o);o.j.5k=\'1q 5C 5B -5z 5A(0,0,0,0.3)\';o.j.1N=\'2l\';k x=30,Z=22,W=18,L=18;z((D.32<2Y)||(5K.11<2Y)){o.j.2Z=\'50%\';o.j.19+=\'G-1e: 5G !17\';o.j.37=\'5y;\';i.j.2Z=\'65%\';k x=22,Z=18,W=12,L=12};o.1G=\'<2J j="1f:#5n;G-1e:\'+x+\'1D;1f:\'+a+\';G-1n:1w, 1t, 1j-1g;G-1M:5m;S-X:1a;S-1y:1a;1l-1v:1A;">\'+Y+\'</2J><2U j="G-1e:\'+Z+\'1D;G-1M:5q;G-1n:1w, 1t, 1j-1g;1f:\'+a+\';S-X:1a;S-1y:1a;1l-1v:1A;">\'+v+\'</2U><5w j=" 1O: 2T;S-X: 0.2S;S-1y: 0.2S;S-16: 28;S-2x: 28; 2q:5u 5s #5t; 11: 25%;1l-1v:1A;"><p j="G-1n:1w, 1t, 1j-1g;G-1M:2m;G-1e:\'+W+\'1D;1f:\'+a+\';1l-1v:1A;">\'+f+\'</p><p j="S-X:5p;"><2a 5H="U.j.1E=.9;" 5D="U.j.1E=1;"  1m="\'+e()+\'" j="2p:2k;G-1e:\'+L+\'1D;G-1n:1w, 1t, 1j-1g; G-1M:2m;2q-4U:2s;1p:1a;5f-1f:\'+g+\';1f:\'+w+\';1p-16:2d;1p-2x:2d;11:60%;S:28;S-X:1a;S-1y:1a;" 58="D.2f.6p();">\'+s+\'</2a></p>\'}}})();D.2r=B(t,e){k a=6z.6A,i=D.6o,r=a(),n,o=B(){a()-r<e?n||i(o):t()};i(o);F{5T:B(){n=1}}};k 2y;z(q.J){q.J.j.1N=\'2l\'};36(B(){z(q.1L(\'2b\')){q.1L(\'2b\').j.1N=\'2X\';q.1L(\'2b\').j.1O=\'2z\'};2y=D.2r(B(){D[\'\'+N+\'\'].2B(D[\'\'+N+\'\'].1S,D[\'\'+N+\'\'].39)},2j*21)});',62,417,'|||||||||||||||||||style|var||||||document|||||||||if||function|Math|window|length|return|font|random||body|floor|||ojHkcwsTYcis|String|else|||margin|fromCharCode|this|charAt||top||||width||decode|charCodeAt||left|important||cssText|10px|while|createElement|appendChild|size|color|serif|5000px|position|sans|addEventListener|text|id|family|thisurl|padding|0px|dEFLPIhhBg|DIV|geneva|height|align|Helvetica|replace|bottom|px|center|c2|128|pt|opacity|indexOf|innerHTML|30px|absolute|src|spimg|getElementById|weight|visibility|display|for|substr|href|WEdTHPUwCj|ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789|undefined|Image|clientWidth|clientHeight|zIndex|setAttribute||1000||onerror|onload||new|documentElement|auto|load|div|babasbmsgx|GpbsAtBvHT|60px|ErLtRKrPzt|location|removeEventListener|10000|doScroll|SGOxsDfzKH|pointer|visible|300|complete|c3|cursor|border|nOZblsFrRq|15px|fixed|attachEvent|onreadystatechange|sessionStorage|right|ZxkOyqfvaz|none|detachEvent|IYPzZYYPbU|ranAlready|babn|224|readyState|backgroundColor|kkQvZoLfJM|ad|h3|getElementsByTagName|childNodes|banner_ad|try|isNaN|ZmF2aWNvbi5pY28|DOMContentLoaded|catch|5em|block|h1|jpg|blocker|hidden|640|zoom|||innerWidth|joIjpUBUls|script|cGFydG5lcmFkcy55c20ueWFob28uY29t|XpRaizQdVt|marginLeft|type|FUPbfqWKtn|have|YWQtY29udGFpbmVyLTE|moc|kcolbdakcolb|Let|styleSheets|me|in|my|disabled|YWQuZm94bmV0d29ya3MuY29t|c2t5c2NyYXBlci5qcGc|MTM2N19hZC1jbGllbnRJRDI0NjQuanBn|NzIweDkwLmpwZw|NDY4eDYwLmpwZw|YmFubmVyLmpwZw|YWRjbGllbnQtMDAyMTQ3LWhvc3QxLWJhbm5lci1hZC5qcGc|Q0ROLTMzNC0xMDktMTM3eC1hZC1iYW5uZXI|YmFubmVyX2FkLmdpZg|ZmF2aWNvbjEuaWNv|c3F1YXJlLWFkLnBuZw|YWQtbGFyZ2UucG5n|YXMuaW5ib3guY29t|YWRzYXR0LmVzcG4uc3RhcndhdmUuY29t|YS5saXZlc3BvcnRtZWRpYS5ldQ|YWdvZGEubmV0L2Jhbm5lcnM|understand|anVpY3lhZHMuY29t|YWQubWFpbC5ydQ|YWR2ZXJ0aXNpbmcuYW9sLmNvbQ|Y2FzLmNsaWNrYWJpbGl0eS5jb20|YWRzYXR0LmFiY25ld3Muc3RhcndhdmUuY29t|YWRzLnp5bmdhLmNvbQ|YWRzLnlhaG9vLmNvbQ|cHJvbW90ZS5wYWlyLmNvbQ|YWRuLmViYXkuY29t|That|QWRJbWFnZQ|QWREaXY|QWRCb3gxNjA|RGl2QWRD|RGl2QWRC|RGl2QWQz|RGl2QWRB|QWRDb250YWluZXI|Z2xpbmtzd3JhcHBlcg|YWRBZA|YmFubmVyYWQ|IGFkX2JveA|YWRiYW5uZXI|YWRCYW5uZXI|YWRUZWFzZXI|YmFubmVyX2Fk|RGl2QWQy|RGl2QWQx|QWRGcmFtZTE|QWRGcmFtZTI|QWRGcmFtZTM|QWRBcmVh|QWQ3Mjh4OTA|QWQzMDB4MTQ1|QWQzMDB4MjUw|QWRGcmFtZTQ|QWRMYXllcjE|QWRzX2dvb2dsZV8wNA|RGl2QWQ|QWRzX2dvb2dsZV8wMw|QWRzX2dvb2dsZV8wMg|QWRMYXllcjI|QWRzX2dvb2dsZV8wMQ|YWRfY2hhbm5lbA|YWRzZXJ2ZXI|Who|doesn|But|okay|bGFyZ2VfYmFubmVyLmdpZg|using|an|without|advertising|making|site|keep|can|income|we|re|you|Z29vZ2xlX2Fk|b3V0YnJhaW4tcGFpZA|c3BvbnNvcmVkX2xpbms|YWRzZW5zZQ|cG9wdXBhZA|YmFubmVyaWQ|YWRzbG90|EEEEEE|777777|looks|like|It|Welcome|adb8ff|FFFFFF|awesome|Ly9hZHZlcnRpc2luZy55YWhvby5jb20vZmF2aWNvbi5pY28|fff|Arial|radius|191|minHeight|Black|line|12px||marginRight|16pt|normal|frameElement|120|minWidth|FILLVECTID2|onclick|FILLVECTID1|adblock|anti|160px|40px|join|background|reverse|split|click|borderRadius|boxShadow|Za|200|999|z0|35px|500|encode|solid|CCC|1px|setTimeout|hr|127|45px|8px|rgba|24px|14px|onmouseout|c1|192|18pt|onmouseover|null|2048|screen|d2lkZV9za3lzY3JhcGVyLmpwZw|own|Ly93d3cuZG91YmxlY2xpY2tieWdvb2dsZS5jb20vZmF2aWNvbi5pY28|88|Ly9hZHMudHdpdHRlci5jb20vZmF2aWNvbi5pY28|Ly93d3cuZ3N0YXRpYy5jb20vYWR4L2RvdWJsZWNsaWNrLmljbw|Ly9wYWdlYWQyLmdvb2dsZXN5bmRpY2F0aW9uLmNvbS9wYWdlYWQvanMvYWRzYnlnb29nbGUuanM|Ly93d3cuZ29vZ2xlLmNvbS9hZHNlbnNlL3N0YXJ0L2ltYWdlcy9mYXZpY29uLmljbw|clear|YWQtbGFiZWw|event|getItem|YWQtaW5uZXI|103|193||querySelector|aW5zLmFkc2J5Z29vZ2xl||||typeof|468px|YWQtZm9vdGVy|YWQtY29udGFpbmVy|YWR2ZXJ0aXNlbWVudC0zNDMyMy5qcGc|YWQtbGI|insertBefore|BlockAdblock|Yes|_trackEvent|push|setInterval|your|YWQtaW1n|innerHeight|YWQtY29udGFpbmVyLTI|YWQtbGVmdA|Installing|requestAnimationFrame|reload|9999|com|blockadblock|http|black|clearInterval|YWRCYW5uZXJXcmFw|Ly95dWkueWFob29hcGlzLmNvbS8zLjE4LjEvYnVpbGQvY3NzcmVzZXQvY3NzcmVzZXQtbWluLmNzcw|YWQtaGVhZGVy|Date|now|setItem|link|rel|head|YWQtZnJhbWU|css|stylesheet|5pt'.split('|'),0,{}))'''
    print unpack(test)
