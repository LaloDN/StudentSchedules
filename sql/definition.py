from sqlalchemy import create_engine, Column, String, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event

Base = declarative_base()

engine = create_engine('sqlite:///sql/school.db', echo=True)

class Student(Base):
    __tablename__ = 'Students'
    id = Column(Integer, primary_key=True,autoincrement=True)
    firstName = Column(String(50),nullable=False)
    secondName = Column(String(50),nullable=False)
    studentId = Column(Integer,nullable=False,unique=True)
    birthday = Column(Date,nullable=False)
    semester = Column(Integer,nullable=False)
    gpa = Column(Float,nullable=False)
    carrerId = Column(Integer,ForeignKey('Carrers.id', ondelete='CASCADE', onupdate='CASCADE'),nullable=False)
    

class Asignature(Base):
    __tablename__ = 'Asignatures'
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(80),nullable=False,unique=True)
    semester = Column(Integer,nullable=False)
    carrerId = Column(Integer,ForeignKey('Carrers.id', ondelete='CASCADE', onupdate='CASCADE'), nullable = False)


class Teacher(Base):
    __tablename__ = 'Teachers'
    id = Column(Integer, primary_key=True,autoincrement=True)
    employeeId = Column(Integer, nullable = False, unique = True)
    firstName = Column(String(50), nullable = False)
    secondName = Column(String(50), nullable = False)

class Carrer(Base):
    __tablename__ = 'Carrers'
    id = Column(Integer, primary_key=True,autoincrement=True)
    name = Column(String(40), nullable = False)
    students = relationship('Student', backref='carrer')
    asignatures = relationship('Asignature', backref='carrer')

class StudentAsignature(Base):
    __tablename__ = 'StudentAsignatures'
    id = Column(Integer, primary_key=True,autoincrement=True)
    idStudent = Column(Integer,ForeignKey('Students.id', ondelete='CASCADE', onupdate='CASCADE'),nullable = False)
    idAsignature = Column(Integer,ForeignKey('Asignatures.id', ondelete='CASCADE', onupdate='CASCADE') ,nullable = False)

class TeacherAsignature(Base):
    __tablename__ = 'TeacherAsignatures'
    id = Column(Integer, primary_key=True,autoincrement=True)
    hour = Column(String(30),nullable = False)
    groupNo = Column(Integer, nullable = False, unique = True)
    idTeacher = Column(Integer,ForeignKey('Teachers.id', ondelete='CASCADE', onupdate='CASCADE'),nullable = False)
    idAsignature = Column(Integer,ForeignKey('Asignatures.id', ondelete='CASCADE', onupdate='CASCADE'),nullable = False)


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
#event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))
