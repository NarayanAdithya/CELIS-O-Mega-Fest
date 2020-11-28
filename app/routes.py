from app import app,socketio
from flask import request,redirect,url_for,render_template,flash,get_flashed_messages
from flask_login import current_user,login_user,logout_user,login_required
from app.models import User,thread,post,Courses,enrolled
from app.forms import LoginForm,RegisterForm,add_course_form,RequestResetForm, ResetPasswordForm
from werkzeug.urls import url_parse
from wtforms.validators import ValidationError
from datetime import datetime
import pickle


@app.route('/')
@app.route('/index')
def index():
    return render_template('celis.html',title='Home',data_footer_aos="fade-left",data_aos_footer_delay=100,data_aos_header="fade-left",data_header_aos_delay=100)


@app.route('/courses')
@login_required
def course():
    c=Courses.query.all()
    #Pickle Files Here for Course List Display
    # with open('app//AI.pickle', 'rb') as handle:
    #     ai_courses = pickle.load(handle)
    # with open('app//appdev.pickle', 'rb') as handle:
    #     appdev_courses = pickle.load(handle)
    # with open('app//webdev.pickle', 'rb') as handle:
    #     webdev_courses = pickle.load(handle)
    return render_template('courses.html',title='Courses',courses=c,ai=ai_courses,len_ai=len(ai_courses['Title']),web=webdev_courses,len_web=len(webdev_courses['Title']),app=appdev_courses,len_app=len(appdev_courses['Reviews']))


@app.route('/logout')
def logout():
    current_user.last_seen=datetime.utcnow()
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


    
@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Email or Password',category="danger")
            return redirect(url_for('login'))
        login_user(user,remember=form.remember_me.data)
        next_page=request.args.get('next')
        if not next_page or url_parse(next_page).netloc!='':
            next_page=url_for('index')
        return redirect(next_page)
    return render_template('signinpage.html',title='SignIn',form=form)

@app.route('/register',methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=forms.RegisterForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,email=form.email.data,user_role=form.user_role.data,Region=form.Region.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Successfully Registered',category="success")
        msg = Message('Welcome to CELIS',
                  sender="celis.students@gmail.com",
                  recipients=[user.email])
        msg.body="Hey There, We are happy that you have decided to join our community, We look forward to working with you. If you have any issues do notify us in our contact us section"
        Thread(target=send_async_email,args=(app,msg)).start()
        print(form.password.data)
        print(form.user_role.data)
        print(form.Region.data)
        return redirect(url_for('login'))
    return render_template('signuppage.html',form=form,title='Register')

@app.route('/contact')
@login_required
def contactus():
    return render_template('contactus.html',title='Contact Us')


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender="celis.students@gmail.com",
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        
        password=(form.password.data)
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

