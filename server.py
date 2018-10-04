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


class ClangFormatBolt(object):
    @cherrypy.expose
    def format(self, source, style=None):
        style = style or 'LLVM'
        if '\n' in style:
            style = yaml_to_dict(style)

        p = subprocess.Popen(['clang-format', '-style=' + style],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        o, _ = p.communicate(input=source)
        return "<pre>" + o + "</pre>"


cherrypy.quickstart(ClangFormatBolt(), '/', CONF)
