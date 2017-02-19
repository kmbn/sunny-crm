import re
from flask import session
from flask_wtf import Form
from wtforms import PasswordField, StringField, SubmitField, TextAreaField, \
    ValidationError
from wtforms.validators import Required, Length, Email, EqualTo
from datetime import datetime
from app.parse import Days
from app.db import get_db


# Custom validators
def is_date(form, field):
    if field.data not in Days.days and field.data not in Days.next_days \
    and field.data not in Days.terms:
        try:
            datetime.strptime(field.data, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('Enter a date like "2017-12-31" \
                or a word like "today" or "tommorow", or a weekday like \
                Monday", or "next Monday".')


def is_new_contact(form, field):
    db = get_db()
    cur = db.execute('select id from contacts where name is ? \
        and creator_id is ?', (field.data, session.get('current_user')))
    contact_exists = cur.fetchone()
    if contact_exists:
        raise ValidationError('A contact with that name already exists.')


class AddContactForm(Form):
    name = StringField('Contact name: (required)', validators=[Required(), \
        is_new_contact])
    note = TextAreaField('Note: (optional)')
    next_action = StringField("What's the next step? (optional)")
    checkin = StringField('When do you need to do it? (optional)', \
        validators=[is_date])
    submit = SubmitField('Add contact')


class QuickNavForm(Form):
    query = StringField('Search for a contact:', validators=[Required()])
    submit = SubmitField('Search')


class AddUpdateForm(Form):
    update_text = StringField('What happenned? (required)', \
        validators=[Required()])
    next_action = StringField("What's the next step? (optional)")
    checkin_text = StringField('When do you need to do it? (optional)', \
        validators=[is_date])
    submit = SubmitField('Add update')


class EditContactNameForm(Form):
    new_name = StringField('Enter new name:', validators=[Required(), \
        is_new_contact])
    submit = SubmitField('Save new name')


class EditNoteForm(Form):
    new_note = TextAreaField('Enter new note:', validators=[Required()])
    submit = SubmitField('Save edited note')


class EditCheckinForm(Form):
    new_checkin = StringField('Enter new check-in date:', \
        validators=[Required(), is_date])
    new_next_action = StringField('Enter new next action:')
    submit = SubmitField('Save new checkin')


class AddCheckinForm(Form):
    checkin = StringField('Check in on:', validators=[Required(), is_date])
    submit = SubmitField('Schedule check-in')


class EditContactForm(Form):
    new_name = StringField('Enter new name: (optional)', \
        validators=[Required(), is_new_contact])
    new_note = TextAreaField('Enter new note: (optional)')
    new_next_action = StringField('Enter new next action: (optional)')
    new_checkin = StringField('Enter new check-in date: (optional)', \
        validators=[is_date])
    submit = SubmitField('Update contact')


class RingTheBellForm(Form):
    achievement = StringField('What did you achieve?', \
        validators=[Required()])
    submit = SubmitField('Ring the bell')