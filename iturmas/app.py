import json

from flask import Flask

import config
from iturmas.myemail import mail


app = Flask(__name__)
app.config.from_pyfile('../config.py')
mail.init_app(app)


@app.context_processor
def utility_processor():
    def my_json_parse(data):
        try:
            r = json.loads(data)
        except json.decoder.JSONDecodeError:
            r = [data]
        return r

    return dict(parse_json=my_json_parse)


@app.template_filter('print_dict')
def print_dict(s):
    print(s)
    if s == 'NULL':
        return s
    obj = json.loads(s)
    return '\n'.join([str(key).upper() + ': ' + str(obj[key]) for key in obj])


@app.template_filter('properties2show')
def properties_filter(s, domain=''):
    try:
        obj = json.loads(s)
    except json.decoder.JSONDecodeError:
        return s

    props = list()
    for name in config.REQUIRED_PROPERTIES[domain]:
        props.append(obj.get(name, f'{name}?'))

    return '; '.join(props)
