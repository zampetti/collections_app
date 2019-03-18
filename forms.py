from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(Form):
    first_name = StringField('First Name', validators=[DataRequired("Please enter your first name.")])
    last_name = StringField('Last Name', validators=[DataRequired("Please enter your last name.")])
    email = StringField('Email', validators=[DataRequired("Please enter your email."), 
                                             Email("Please enter a valid email.")])
    password = PasswordField('Password', validators=[DataRequired("Please create a password."), 
                                                     Length(min=6, message="Passwords must be at least 6 characters in length.")])
    submit = SubmitField('Sign up')
    
class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired("Please enter your email address."), Email("Please enter a valid email.")])
    password = PasswordField('Password', validators=[DataRequired("Please enter your password.")])
    submit = SubmitField("Sign in")
    
class UploadForm(Form):
    upload = FileField('image', validators=[
        FileRequired(),
        FileAllowed(['jpg'], 'JPEG Images only!')
    ])
    collection_path = StringField('Collection path', validators=[DataRequired("Please enter the collection path.")])
    target_file_dir = StringField('Path to desired target file directory', validators=[DataRequired("Please enter a path for the target file directory.")])
    submit = SubmitField("Run Locator")