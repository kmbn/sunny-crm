import re
from flask import session
from flask_wtf import Form
from wtforms import PasswordField, StringField, SubmitField, TextAreaField, \
    ValidationError
from wtforms.validators import Required, Length, Email, EqualTo
from datetime import datetime
from .parse import Days
from .db import get_db


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


def has_digits(form, field):
    if not bool(re.search(r'\d', field.data)):
        raise ValidationError('Your password must contain at least one \
            number.')


def has_special_char(form, field):
    if not bool(re.search(r'[^\w\*]', field.data)):
        raise ValidationError('Your password must contain at least one \
            special character.')


def is_new_user(form, field):
    db = get_db()
    cur = db.execute('select id from users where email is ?', (field.data,))
    user_exists = cur.fetchone()
    if user_exists:
        raise ValidationError('That email is already in use.')


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
    submit = SubmitField('Go')


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


class RegistrationForm(Form):
    email = StringField('Enter your email:', \
        validators=[Required(), is_new_user, Length(1, 64), Email()])
    password = PasswordField('Create a password:', \
        validators=[Required(), has_digits, has_special_char, Length(1, 64)])
    submit = SubmitField('Create account')


class LoginForm(Form):
    email = StringField('Email address:', \
        validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password:', validators=[Required()])
    submit = SubmitField('Log in')


class NewEmailForm(Form):
    new_email = StringField('New email address:', validators=[Required(), \
        Length(1, 64), Email(), EqualTo('verify_email', \
            message='Email addresses must match.')])
    verify_email = StringField('Re-enter new email address:', \
                               validators=[Required(), Email()])
    submit = SubmitField('Change email')


class ChangePasswordForm(Form):
    current_password = PasswordField('Your current password:', \
        validators=[Required(), Length(1, 64)])
    new_password = PasswordField('Your new password:', \
        validators=[Required(), Length(1, 64), has_digits, \
        has_special_char, EqualTo('verify_password', \
        message='New passwords must match.')])
    verify_password = PasswordField('Re-enter new password:', \
        validators=[Required()])
    submit = SubmitField('Change password')


class RequestPasswordResetForm(Form):
    email = StringField('Your email address: ', validators=[Required(), \
        Length(1, 64), Email()])
    submit = SubmitField('Request password reset link')


class SetNewPasswordForm(Form):
    new_password = PasswordField('Your new password:', \
        validators=[Required(), Length(1, 64), has_digits, has_special_char, \
        EqualTo('verify_password', \
        message='Passwords must match')])
    verify_password = PasswordField('Re-enter new password:', \
        validators=[Required()])
    submit = SubmitField('Use new password')


class RingTheBellForm(Form):
    achievement = StringField('What did you achieve?', \
        validators=[Required()])
    submit = SubmitField('Ring the bell')