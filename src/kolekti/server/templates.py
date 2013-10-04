from jinja2 import Environment, FileSystemLoader
import os

apppath = os.path.dirname(os.path.dirname(os.path.realpath( __file__ )))

templatesdirs=[os.path.join(apppath, 'web', 'templates')]

jinjaenv = Environment(loader = FileSystemLoader(templatesdirs))

def render(template,context={}, encoding="utf-8"):
    print templatesdirs
    template = jinjaenv.get_template(template+'.html')
    print "render context : ", context
    return template.render(**context).encode(encoding)


