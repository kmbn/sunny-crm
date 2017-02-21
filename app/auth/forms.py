import re
from flask import session, Markup, Blueprint
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import Required, Length, Email, EqualTo
from app.db import get_db
from . import pwd_context


# Custom validators
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


class RegistrationForm(Form):
    email = StringField('Enter your email: (required)', \
        validators=[Required(), is_new_user, Length(1, 64), Email()])
    password = PasswordField('Create a password: \
        (minimum 8 characters, must include a number and a special character)', \
        validators=[Required(), has_digits, has_special_char, Length(min=8)])
    submit = SubmitField('Create account')


class PasswordCorrect(object):
    '''Verify email/password combo before validating form.'''
    def __init__(self, fieldname):
        self.fieldname = fieldname

    def __call__(self, form, field):
        try:
            email = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") \
                % self.fieldname)
        db = get_db()
        cur = db.execute('select password from users \
            where email is ?', (email.data,))
        row = cur.fetchone()
        if row is not None:
            db_password = row[0]
            if not pwd_context.verify(field.data, db_password):
                raise ValidationError('The email or password you entered \
                    were not found.')
        else:
            raise ValidationError('Could not log in—\
                have you already registered?.')


class LoginForm(Form):
    email = StringField('Email address:', \
        validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password:', validators=[Required(), \
        PasswordCorrect('email')])
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
        validators=[Required()])
    new_password = PasswordField('Your new password: \
        (minimum 8 characters, must include a number and a special character)', \
        validators=[Required(), Length(min=8), has_digits, \
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
    new_password = PasswordField('Your new password: \
        (minimum 8 characters, must include a number and a special character)', \
        validators=[Required(), Length(min=8), has_digits, has_special_char, \
        EqualTo('verify_password', \
        message='Passwords must match')])
    verify_password = PasswordField('Re-enter new password:', \
        validators=[Required()])
    submit = SubmitField('Use new password')