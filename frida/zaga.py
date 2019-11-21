import frida, sys
import struct
import sys
from ida2frida import prepare as _prepare


def b2f(a):
    a = "%08x"%a
    s = [0,0,0,0]
    s[0] = chr(int(a[0:2],16))
    s[1] = chr(int(a[2:4],16))
    s[2] = chr(int(a[4:6],16))
    s[3] = chr(int(a[6:8],16))
    s = "%s%s%s%s"%(s[3],s[2],s[1],s[0])
    a = struct.pack('4s',s)
    b = struct.unpack('f',a)[0]
    return b

def _on_message(message, data):
    if message['type'] == 'send':
        msg = message['payload']
        if data == 'float':
            b = int(msg,16)
            print('float:',b2f(b))
        elif data == 'stderr':
            sys.stderr.write("[*] {0}\n".format(message['payload']))
        else:
            print("[*] {0}".format(message['payload']))
    else:
        print(message)


headerline = 200

def run(jsname, on_message=None, prepare=False):
    global headerline
    if prepare:
        _prepare()
    if not on_message :
        on_message = _on_message
    procname = 'com.nintendo.zaga'
    process = frida.get_usb_device().attach(procname)
    commonjs = open('common/utils.js').read()
    symboljs = open('common/symbol.js').read()
    lines = 0
    for i in commonjs:
        if i == '\n':
            lines +=1
    for i in symboljs:
        if i == '\n':
            lines +=1
    padding = '\n'*(headerline - lines - 1)
    padding += 'var __padding__ = 0;\n'


    jscode = open(jsname).read()
    
    jscode = commonjs + symboljs + padding + jscode

 #   print(jscode)
 #   ln = 0;
 #   for i in jscode.split('\n'):
 #       ln += 1
 #       print ln, i
 #   exit()
    script = process.create_script(jscode)
    script.on('message', on_message)
    sys.stderr.write('[*] Running %s\n==============================\n'%jsname)
    script.load()
    sys.stdin.read()


if __name__ == '__main__':
    _prepare()
