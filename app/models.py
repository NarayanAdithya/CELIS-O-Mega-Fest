from app import db
from app import login
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin
from datetime import datetime
from app import app


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


enrolled=db.Table('Enrolled',
    db.Column('user_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('course_id',db.Integer,db.ForeignKey('courses.id'))
)

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),index=True,unique=True)
    email=db.Column(db.String(120),index=True,unique=True)
    user_role=db.Column(db.String(20))
    Region=db.Column(db.String(20))
    password_hash=db.Column(db.String(128))
    threads=db.relationship('thread',backref='creator',lazy='dynamic')
    posts=db.relationship('post',backref='Author',lazy='dynamic')
    last_seen=db.Column(db.DateTime,default=datetime.utcnow)
    twitter=db.Column(db.String(120),default="N/A")
    facebook=db.Column(db.String(120),default="N/A")
    instagram=db.Column(db.String(120),default="N/A")
    birthdate=db.Column(db.String(120),default="N/A")
    Interests=db.Column(db.String(200),default="N/A")
    provides_course=db.relationship('Courses',backref="Teacher",lazy='dynamic')
    def __repr__(self):
        return '<Role:{} Name:{} Id:{}>'.format(self.user_role,self.username,self.id)
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    def get_reset_token(self, expires_sec=1800):
         s = Serializer(app.config['SECRET_KEY'], expires_sec)
         return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['id']
        except:
            return None
        return User.query.get(user_id)


class thread(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    subject=db.Column(db.String(50))
    description=db.Column(db.String(100))
    created=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    posts=db.relationship('post',backref='BelongsTo',lazy='dynamic')
    def __repr__(self):
        return '<Thread by {}>'.format(self.user_id,self.created)

class post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    message=db.Column(db.String(150))
    time=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    thread_id=db.Column(db.Integer,db.ForeignKey('thread.id'))
    def __repr__(self):
        return '<Post in thread {} by {}>'.format(self.thread_id,self.user_id)

class Courses(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    course_code=db.Column(db.String(10),unique=True)
    Course_name=db.Column(db.String(100))
    Course_Description=db.Column(db.String(250))
    resources_link=db.Column(db.String(250))
    created=db.Column(db.DateTime,default=datetime.utcnow)
    Instructor_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    students_enrolled=db.relationship('User',secondary=enrolled,backref="Courses_enrolled",lazy='dynamic')
    def __repr__(self):
        return '<Course {} made by {}>'.format(self.course_code,self.Instructor_id)
    def add_student(self, user):
        if not self.is_student(user):
            self.students_enrolled.append(user)

    def remove_student(self, user):
        if self.is_student(user):
            self.students_enrolled.remove(user)

    def is_student(self, user):
        return self.students_enrolled.filter(
            enrolled.c.user_id == user.id).count() > 0
