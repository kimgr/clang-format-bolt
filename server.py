import os
import yaml
import cherrypy
import subprocess


CONF = {
    '/': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.getcwd(),
        'tools.staticdir.index': 'index.html'
    },
    'global': {
        'server.socket_host': '0.0.0.0'
    }
}


def yaml_to_dict(yml):
    y = yaml.load(yml)
    y = str(y)
    y = y.replace("False", "false")
    y = y.replace("True", "true")
    return y


def run(command, input=None, *args):
    cmd = [command] + list(args)
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE if input else None,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    output, _ = p.communicate(input=input)
    return output


class ClangFormatBolt(object):
    @cherrypy.expose
    @cherrypy.expose
    def format(self, source, style=None, clang_format=None):
        clang_format = clang_format or 'clang-format'

        style = style or 'LLVM'
        if '\n' in style:
            style = yaml_to_json(style)

        output = run(clang_format, source, '-style=' + style)
        return "<pre>%s</pre>" % output


cherrypy.quickstart(ClangFormatBolt(), '/', CONF)
