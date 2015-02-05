'''
Created on May 18, 2014

@author: sergio
'''

from web import form
import re

project = form.Form(form.Button('Create',value="Create"),
                        form.Button('Find',value="Find"))

create_project = form.Form( 
    form.Textbox("Name", form.notnull),
    form.Textarea('Description'),
    form.Textbox("Date", form.notnull,
        form.Validator('Format: dd/mm/yyyy', lambda x:validate_date(x))),
    form.Button('Create',value="Create") )

find_project = form.Form( 
    form.Textbox("Name", form.notnull),
    form.Textbox("Date from", form.notnull,
        form.Validator('Format: dd/mm/yyyy', lambda x:validate_date(x))),
    form.Textbox("to", form.notnull,
        form.Validator('Format: dd/mm/yyyy', lambda x:validate_date(x))),
    form.Button('Find',value="Find") )

create_individual = form.Form(
    form.Textbox("Name", form.notnull),
    form.Textarea('Description'),
    form.Textbox("Birth Date", form.notnull,
        form.Validator('Format: dd/mm/yyyy', lambda x:validate_date(x))),
    form.File(name = 'Picture'),
    form.Button('Create',value="Create") )

find_individual = form.Form( 
    form.Textbox("Name", form.notnull),
    form.Textbox("Birth Date from", form.notnull,
        form.Validator('Format: dd/mm/yyyy', lambda x:validate_date(x))),
    form.Textbox("to", form.notnull,
        form.Validator('Format: dd/mm/yyyy', lambda x:validate_date(x))),
    form.Button('Find',value="Find") )


def validate_date(date):
    match = re.match('(^\d{1,2}[\/|-]\d{1,2}[\/|-]\d{4}$)', date)
    if match:
        return True
    else:
        return False

if __name__ == '__main__':
    pass