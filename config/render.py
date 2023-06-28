"""
yaml is a libaray which gives functions to deal with .yaml files 
"""
import yaml
"""
Jinja2 is  python module which proves functions to deal with .j2 files.
Template is an jinja2 object, used here as a variables template for python dictionary object creation.
"""
from jinja2 import Template

with open('/home/hardik/seminar-project/config/config.yaml') as f:
    config_data = yaml.safe_load(f)

with open('/home/hardik/seminar-project/config/config_template.j2') as f:
    template = Template(f.read())

rendered_config = template.render(config=config_data)

with open('/home/hardik/seminar-project/config/config.py', 'w') as f:
    f.write(rendered_config)

print("Configuration file generated for server successfully!")
