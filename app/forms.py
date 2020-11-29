#Auto Rendered Flask Forms Here

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,RadioField,SelectField,TextAreaField
from wtforms.fields.html5 import EmailField,URLField,DateField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,URL,Length
from app.models import User,Courses
from flask_login import current_user,login_user,logout_user,login_required
class RegisterForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired()],render_kw={'class':'form-control form-group'})
    email=EmailField('Email',validators=[DataRequired(),Email()],render_kw={'class':'form-control form-group'})
    password=PasswordField('Password',validators=[DataRequired()],render_kw={'class':'form-control form-group'})
    conpassword=PasswordField('Re-Enter Password',validators=[DataRequired(),EqualTo('password')],render_kw={'class':'form-control form-group'})#('values','label')
    user_role=RadioField('User Role',validators=[DataRequired()],choices=[('Student','Student'),('Instructor','Instructor')],render_kw={'class':'form-check form-check-input','style':'list-style:none;'})
    Region=SelectField('Select Region',validators=[(DataRequired())],choices=[('America','America'),('Africa','Africa'),('Asia','Asia'),('Europe','Europe')],render_kw={'class':'form-group col-md-4 form-control '})
    # remember_me=BooleanField('Keep Me Signed In')
    submit=SubmitField('Sign In',render_kw={'class':'btn btn-info btn-pill','style':'height : 50px;'})
    def validate_username(self,username):
        user=User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please Use a Different Username.')
    def validate_email(self,email):
        user=User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please Use A different Email Address')
class LoginForm(FlaskForm):
    email=EmailField('Email',validators=[DataRequired(),Email()],render_kw={'class':'form-control form-group'})
    password=PasswordField('Password',validators=[DataRequired()],render_kw={'class':'form-control form-group'})
    remember_me=BooleanField('Keep Me Signed In')
    submit=SubmitField('Sign In',render_kw={'class':'btn btn-info btn-pill','style':'height : 50px;'})



class add_course_form(FlaskForm):
    Course_Code=StringField('Course Code',validators=[DataRequired(),Length(min=5,max=10),],render_kw={'class':'form-control form-group'})
    Course_Name=StringField('Course Name',validators=[DataRequired(),Length(min=10,max=100)],render_kw={'class':'form-control form-group'})
    Course_description=TextAreaField('Enter Description',[DataRequired()],render_kw={'class':'form-control form-group'})
    resources_link=StringField('Resources Link',render_kw={'class':'form-control form-group'})
    submit=SubmitField('Add Course',render_kw={'class':'btn btn-info btn-pill','style':'height : 50px;'})
    def validate_Course_Code(self,Course_Code):
        c=Courses.query.filter_by(course_code=Course_Code.data).first()
        if c is not None:
            raise ValidationError('Please Use a Different Code')
    def validate_Course_Name(self,Course_Name):
        c=Courses.query.filter_by(Course_name=Course_Name.data).first()
        if c is not None:
            raise ValidationError('Please Use a Different Course Name')   

class RequestResetForm(FlaskForm):
    email = EmailField('Email',
                        validators=[DataRequired(), Email()],render_kw={'class':'form-control form-group'})
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()],render_kw={'class':'form-control form-group'})
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')],render_kw={'class':'form-control form-group'})
    submit = SubmitField('Reset Password')