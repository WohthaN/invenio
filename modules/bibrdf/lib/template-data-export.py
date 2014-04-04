from jinja2 import FileSystemLoader, Environment
from datadicts.record import *


env = Environment(loader=FileSystemLoader('./config/orcid/'), auto_reload=True)
orcid = env.get_template('orcid.xml')


print orcid.render({'records':[Record(1234),Record(1235)]})
