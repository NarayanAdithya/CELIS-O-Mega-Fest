from app import db
from datetime import datetime
from app import app


enrolled=db.Table('Enrolled',
    db.Column('user_id',db.Integer,db.ForeignKey('user.id')),
    db.Column('course_id',db.Integer,db.ForeignKey('courses.id'))
)


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
