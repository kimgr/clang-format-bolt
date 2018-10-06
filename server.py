import os
import re
import yaml
import cherrypy
import subprocess


CONF = {
    '/': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.getcwd(),
        'tools.staticdir.index': 'golden.html'
    },
    'global': {
        'server.socket_host': '0.0.0.0'
    }
}


def flatten_json(json):
    return json.replace('\n', '')


def yaml_to_json(yml):
    y = yaml.load(yml)
    y = str(y)
    y = y.replace("False", "false")
    y = y.replace("True", "true")
    return flatten_json(y)


def build_style_arg(style):
    """ Returns a list of a single --style=X argument or an empty list """
    if not style:
        return []

    if '{' in style:
        style = flatten_json(style)
    elif '\n' in style:
        style = yaml_to_json(style)

    return ["-style=" + style]


def run(command, input=None, *args):
    cmd = [command] + list(args)
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE if input else None,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    output, _ = p.communicate(input=input)
    return output


def find_pattern_on_path(pattern):
    for path in os.environ.get("PATH", "").split(os.pathsep):
        for fname in os.listdir(path):
            if re.match(pattern, fname):
                return fname


def collect_clang_formats():
    clang_formats = []
    patterns = [r'clang-format$',
                r'clang-format-\d$',
                r'clang-format-\d.\d$']
    for pattern in patterns:
        found = find_pattern_on_path(pattern)
        if found:
            clang_formats.append(found)

    return set(clang_formats)


class ClangFormatBolt(object):
    def __init__(self):
        self.clang_formats = collect_clang_formats()

    def check_executable(self, executable):
        if not executable in self.clang_formats:
            raise Exception("Invalid clang-format executable: %s" % executable)

    @cherrypy.expose
    def version(self, clang_format=None):
        clang_format = clang_format or 'clang-format'
        self.check_executable(clang_format)
        return run(clang_format, None, '--version')

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def clang_formats(self):
        return sorted(self.clang_formats)

    @cherrypy.expose
    def format(self, source, style=None, clang_format=None):
        clang_format = clang_format or 'clang-format'
        self.check_executable(clang_format)

        style = build_style_arg(style)
        output = run(clang_format, source, *style)

        return output


cherrypy.quickstart(ClangFormatBolt(), '/', CONF)
