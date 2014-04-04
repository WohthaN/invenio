from jinja2 import FileSystemLoader, Environment

def export(datadicts_list, template_file, output_file='/tmp/data.xml'):

    env = Environment(loader=FileSystemLoader('./templates/'), auto_reload=True)
    template = env.get_template(template_file)
    with open(output_file, 'w') as dest:
        dest.writelines(template.render({'records':datadicts_list}))
