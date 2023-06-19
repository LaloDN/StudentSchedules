from sqlalchemy import create_engine, Column, String, Integer, Date, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event

Base = declarative_base()

engine = create_engine('sqlite:///sql/school.db', echo=True)

class Student(Base):
    __tablename__ = 'Students'
    id = Column(Integer, primary_key=True)
    firstName = Column(String(50),nullable=False)
    secondName = Column(String(50),nullable=False)
    studentId = Column(Integer,nullable=False,unique=True)
    birthday = Column(Date,nullable=False)
    semester = Column(Integer,nullable=False)
    gpa = Column(Float,nullable=False)
    careerId = Column(Integer,ForeignKey('Careers.id', ondelete='CASCADE', onupdate='CASCADE'),nullable=False)
    __table_args__ = (
        CheckConstraint(studentId >= 10000, name='studentId_format'),
    )
    __table_args__ = (
        CheckConstraint(semester.between(1,10), name='number_semesters'),
    )
    __table_args__ = (
        CheckConstraint(semester.between(1,100), name='gpa_range'),
    )

class Asignature(Base):
    __tablename__ = 'Asignatures'
    id = Column(Integer, primary_key=True)
    name = Column(String(80),nullable=False,unique=True)
    semester = Column(Integer,nullable=False)
    careerId = Column(Integer,ForeignKey('Careers.id', ondelete='CASCADE', onupdate='CASCADE'), nullable = False)
    __table_args__ = (
        CheckConstraint(semester.between(1,10), name='number_semesters'),
    )

class Teacher(Base):
    __tablename__ = 'Teachers'
    id = Column(Integer, primary_key=True)
    employeeId = Column(Integer, nullable = False, unique = True)
    firstName = Column(String(50), nullable = False)
    secondName = Column(String(50), nullable = False)
    __table_args__ = (
        CheckConstraint(employeeId >= 1000, name='employeeId_format'),
    )

class Career(Base):
    __tablename__ = 'Careers'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable = False, unique=True)
    students = relationship('Student', backref='career')
    asignatures = relationship('Asignature', backref='career')

class StudentClass(Base):
    __tablename__ = 'StudentClasses'
    id = Column(Integer, primary_key=True)
    idStudent = Column(Integer,ForeignKey('Students.id', ondelete='CASCADE', onupdate='CASCADE'),nullable = False)
    idClass = Column(Integer,ForeignKey('Classes.id', ondelete='CASCADE', onupdate='CASCADE') ,nullable = False)

class Class(Base):
    __tablename__ = 'Classes'
    id = Column(Integer, primary_key=True)
    hour = Column(String(30),nullable = False)
    groupNo = Column(Integer, nullable = False, unique = True)
    idTeacher = Column(Integer,ForeignKey('Teachers.id', ondelete='CASCADE', onupdate='CASCADE'),nullable = False)
    idAsignature = Column(Integer,ForeignKey('Asignatures.id', ondelete='CASCADE', onupdate='CASCADE'),nullable = False)
    

#Base.metadata.drop_all(engine)
#Base.metadata.create_all(engine)
#event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))
