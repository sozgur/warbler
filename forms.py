from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired(), Length(max=40)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), 
        EqualTo('confirm'), Length(min=6)])
    confirm  = PasswordField('Confirm Password')
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserEditForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired(), Length(max=40)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    image_url = StringField('Image URL')
    header_image_url = StringField('Header Image URL')
    bio = TextAreaField("Bio")
    location = StringField("Location")

