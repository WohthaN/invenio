from jinja2 import FileSystemLoader, Environment


def export(datadicts_list, template_file):

    env = Environment(loader=FileSystemLoader('./templates/'), auto_reload=True)
    template = env.get_template(template_file)
    return template.render({'records': datadicts_list})
