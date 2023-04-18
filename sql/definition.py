from sqlalchemy import create_engine, Column, String, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine('sqlite:///school.db', echo=True)

class Student(Base):
    __tablename__ = 'Students'
    id = Column(Integer, primary_key=True)
    firstName = Column(String(50),nullable=False)
    secondName = Column(String(50),nullable=False)
    studentId = Column(Integer,nullable=False,unique=True)
    birthday = Column(Date,nullable=False)
    semester = Column(Integer,nullable=False)
    gpa = Column(Float,nullable=False)
    carrerId = Column(Integer,ForeignKey('Carrers.id'),nullable=False)

class Asignature(Base):
    __tablename__ = 'Asignatures'
    id = Column(Integer, primary_key=True)
    name = Column(String(80),nullable=False,unique=True)
    semester = Column(Integer,nullable=False)
    carrerId = Column(Integer,ForeignKey('Carrers.id'), nullable = False)


class Teacher(Base):
    __tablename__ = 'Teachers'
    id = Column(Integer, primary_key=True)
    employeeId = Column(Integer, nullable = False, unique = True)
    firstName = Column(String(50), nullable = False)
    secondName = Column(String(50), nullable = False)

class Carrer(Base):
    __tablename__ = 'Carrers'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable = False)
    students = relationship('Student', backref='carrer')
    asignatures = relationship('Asignature', backref='carrer')

class StudentAsignature(Base):
    __tablename__ = 'StudentAsignatures'
    id = Column(Integer, primary_key=True)
    idStudent = Column(Integer,ForeignKey('Students.id'),nullable = False)
    idAsignature = Column(Integer,ForeignKey('Asignatures.id') ,nullable = False)

class TeacherAsignature(Base):
    __tablename__ = 'TeacherAsignatures'
    id = Column(Integer, primary_key=True)
    hour = Column(String(30),nullable = False)
    groupNo = Column(Integer, nullable = False, unique = True)
    idTeacher = Column(Integer,ForeignKey('Teachers.id'),nullable = False)
    idAsignature = Column(Integer,ForeignKey('Asignatures.id'),nullable = False)


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
