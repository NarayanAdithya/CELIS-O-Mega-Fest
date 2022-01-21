from app import app,forms,db,socketio,mail
from flask_socketio import emit,leave_room,join_room
from flask_login import current_user,login_required
from flask import render_template, redirect, url_for, get_flashed_messages, flash, request
from app.models import thread,post,Courses,enrolled
from app.auth.models import User
from app.forms import add_course_form
from werkzeug.urls import url_parse
from wtforms.validators import ValidationError
from flask_mail import Message
from threading import Thread
import pickle
import pandas as pd
import numpy as np
from app.utils import send_async_email

@app.route('/')
@app.route('/index')
def index():
    return render_template('celis.html',title='Home',data_footer_aos="fade-left",data_aos_footer_delay=100,data_aos_header="fade-left",data_header_aos_delay=100)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error500.html'), 500


@app.route('/course/<course_code>/students')
@login_required
def view_students(course_code):
    if current_user.user_role=='Instructor':
        c=Courses.query.filter_by(course_code=course_code).first()
        students=c.students_enrolled.all()
        return render_template('view_students.html',students=students,course=c)
    return redirect(url_for('index'))

@app.route('/enroll_course/<course_code>')
@login_required
def enroll_course(course_code):
    if current_user.user_role=='Student':
        c=Courses.query.filter_by(course_code=course_code).first()
        c.add_student(current_user)
        db.session.commit()
        flash('Enrolled Successfully',category='success')
        return redirect(url_for('view_course',course_code=course_code))
    else:
        return redirect(url_for('index'))

@app.route('/view_course/<course_code>')
@login_required
def view_course(course_code):
    c=Courses.query.filter_by(course_code=course_code).first()
    i=User.query.filter_by(id=c.Instructor_id).first()
    if c and i:
        return render_template('view_course.html',course=c,i=i)

@app.route('/edit_course_page/<username>/<course>',methods=['POST','GET'])
@login_required
def edit_course_page(username,course):
    if current_user.is_authenticated and current_user.user_role=='Instructor':
        c=Courses.query.filter_by(course_code=course).first()
        if request.method=='POST':
            c=Courses.query.filter_by(course_code=course).first()
            c.Course_Description=request.form['interests']
            c.resources_link=request.form['resources_link']
            db.session.commit()
            print(c.Course_Description)
            flash('Successfully Saved',category='success')
            return redirect(url_for('profile',username=current_user.username))
        return render_template('edit_course.html',course=c)
    else:
        return redirect(url_for('profiel',username=current_user.username))

@app.route('/mailform', methods=["POST"])
@login_required
def mailform():
    first_name=request.form.get("first_name")
    last_name=request.form.get("last_name")
    tel=request.form.get("tel")
    email=request.form.get("email")
    body_to_admins=request.form.get('feedback')
    message= "Thanks for contacting CELIS. We will reach out to you soon!"
    #server=smtplib.SMTP("smpt.gmail.com",465)
    #server.starttls()
    msg = Message('Your Issue/Request has been notified',
                  sender="celis.students@gmail.com",
                  recipients=[email])
    msg_admins=Message('Issue/Feedback/Request from'+email,sender="celis.students@gmail.com",recipients=['narayanadithya1234@gmail.com','aravindharinarayanan111@gmail.com'])
    msg.body = f'''Your recent feedback/issue/request has been sent to our admins. Actions will be taken soon.
'''
    msg_admins.body="Hey you have a message from user {} {}".format(current_user.username,body_to_admins)
    Thread(target=send_async_email,args=(app,msg)).start()
    Thread(target=send_async_email,args=(app,msg_admins)).start()
    return redirect(url_for('index'))
    

@app.route('/add_course',methods=['GET','POST'])
@login_required
def add_course():
    if(current_user.user_role=="Instructor"):
        form=add_course_form()
        if form.validate_on_submit():
            c=Courses(course_code=form.Course_Code.data,Course_name=form.Course_Name.data,Course_Description=form.Course_description.data,resources_link=form.resources_link.data,Instructor_id=current_user.id)
            db.session.add(c)
            db.session.commit()
            flash('Course Added Successfully',category='success')
            return redirect(url_for('profile',username=current_user.username))
        return render_template('add_course.html',form=form)
    else:
        return redirect(url_for('profile',username=current_user.username))



@app.route('/courses')
@login_required
def course():
    c=Courses.query.all()
    with open('app//AI.pickle', 'rb') as handle:
        ai_courses = pickle.load(handle)
    with open('app//appdev.pickle', 'rb') as handle:
        appdev_courses = pickle.load(handle)
    with open('app//webdev.pickle', 'rb') as handle:
        webdev_courses = pickle.load(handle)
    return render_template('courses.html',title='Courses',courses=c,ai=ai_courses,len_ai=len(ai_courses['Title']),web=webdev_courses,len_web=len(webdev_courses['Title']),app=appdev_courses,len_app=len(appdev_courses['Reviews']))


@app.route('/recommend',methods=['POST','GET'])
def recommend():
    df=pd.read_csv('app//tag_gen.csv')
    if request.method=='POST':
        user_courses=[]
        course1=request.form['course1']
        user_courses.append(course1)
        course2=request.form['course2']
        user_courses.append(course2)
        course3=request.form['course3']
        user_courses.append(course3)
        print(course1,course2,course3)
        df['tags_str'] = [','.join(map(str, l)) for l in df['Tags_fin']]
        course_tags_list=df[['Title','tags_str','Tags_fin']].copy()
        model=pickle.load(open('app//recommender_model','rb'))
        course_tags_vectors = model.docvecs.vectors_docs
        user_course_vector = np.zeros(shape = course_tags_vectors.shape[1])
        for course in user_courses:
            course_index = df[df["Title"] == course].index.values[0]  
            user_course_vector += course_tags_vectors[course_index]
        user_course_vector /= len(user_courses)  
        # print(user_course_vector)
        #  find courses similar to user vector to generate course recommendations
        sims = model.docvecs.most_similar(positive = [user_course_vector], topn = 30)
        nu=[]
        for i,j in sims:
            print(i,j)
            course_sim = course_tags_list.loc[int(i),'Title'].strip()
            
            if course_sim not in user_courses:
                nu.append(int(i))
                print(course_sim)
        return render_template('recommender.html',options=df,indices=nu)

    return render_template('recommender.html',options=df)
    


@app.route('/profile/<username>')
@login_required
def profile(username):
    print(username)
    user=User.query.filter_by(username=username).first()
    if user:
        if user.user_role=="Instructor":
            posts=post.query.filter_by(user_id=user.id).all()
            no_posts=len(posts)
            c=user.provides_course.all()
            return render_template('profile_instructor.html',title='Profile',user=user,no_posts=no_posts,posts=posts,courses=c)
        elif user.user_role=="Student" :
            posts=post.query.filter_by(user_id=user.id).all()
            no_posts=len(posts)
            courses=user.Courses_enrolled
            return render_template('profile_student.html',title='Profile',user=user,no_posts=no_posts,posts=posts,courses=courses)
    return redirect(url_for('profile',username=current_user.username))

@app.route('/unenroll/<coursecode>')
@login_required
def remove(coursecode):
    c=Courses.query.filter_by(course_code=coursecode).first()
    if(c.is_student(current_user)):
        c.remove_student(current_user)
        db.session.commit()
        flash('Successfully Unenrolled',category='success')
        return redirect(url_for('profile',username=current_user.username))
    else:    
        return redirect(url_for('profile',username=current_user.username))

@app.route('/edit_profile',methods=['POST','GET'])
@login_required
def edit_profile():
    if current_user.is_authenticated:
        if request.method=='POST':
            twitter_link=request.form['twitter_link']
            facebook_link=request.form['linkedin_link']
            instagram_link=request.form['github_link']
            birthdate=request.form['birthdate']
            about=request.form['interests']
            user=User.query.filter_by(id=current_user.id).first()
            user.twitter=twitter_link
            user.facebook=facebook_link
            user.instagram=instagram_link
            user.birthdate=birthdate
            user.Interests=about
            db.session.commit()
            flash('Changes Saved Successfully',category='success')
            return redirect(url_for('profile',username=user.username))
        return render_template('edit_profile.html',)
    else:
        return redirect(url_for('index'))


@app.route('/basetemplate')
def base():
    return render_template('template.html',title='template')


@app.route('/forum')
@login_required
def forum():
    threads=thread.query.all()
    return render_template('forumhome.html',title='Forum',threads=threads)

@app.route('/thread/<int:thread_id>',methods=['POST','GET'])
@login_required
def forum_(thread_id):
        posts=post.query.filter_by(thread_id=thread_id).order_by(post.time.asc())
        thread_name=thread.query.filter_by(id=thread_id).first().subject
        return render_template('forum.html',title='Forum',posts=posts,room=thread_name)

@app.route('/contact')
@login_required
def contactus():
    return render_template('contactus.html',title='Contact Us')

#socket events

@socketio.on('join')
def join_room_(data):
    join_room(data['room'])
    socketio.emit('status',data,room=data['room'],dif_user=0)

@socketio.on('leave')
def leave_room_(data):
    leave_room(data['room'])
    print('User gonna leave')
    socketio.emit('left_room_announcement',data,room=data['room'],dif_user=0)

@socketio.on('send_message')
def send_message(data):
    user_=User.query.filter_by(username=data['username']).first()
    thread_=thread.query.filter_by(subject=data['room']).first()
    p=post(message=data['message'],user_id=user_.id,thread_id=thread_.id)
    db.session.add(p)
    db.session.commit()
    p=post.query.filter_by(message=data['message'],user_id=user_.id,thread_id=thread_.id).first()
    socketio.emit('received_message',{'room':data['room'],'user_id':p.user_id,'username':user_.username,'msg':p.message,'post_id':p.id,'thread_id':thread_.id},room=data['room'],dif_user=p.user_id)

@socketio.on('remove')
def remove_post(data):
    id=int(data['post_id'].split('f')[1])
    post_=post.query.filter_by(id=id).first()
    db.session.delete(post_)
    db.session.commit()
    socketio.emit('confirm_remove',{"id":data['post_id']},room=data['room'])
