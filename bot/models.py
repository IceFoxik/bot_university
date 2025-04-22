from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class DaysOfTheWeek(Base):
    __tablename__ = 'days_of_the_week'
    id = Column(Integer, primary_key=True)
    day_of_the_week = Column(String(15), nullable=False)

class Couples(Base):
    __tablename__ = 'couples'
    id = Column(Integer, primary_key=True)
    pair_number = Column(Integer, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

class Groups(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    group_name = Column(String(7), nullable=False)

class TypesOfActivities(Base):
    __tablename__ = 'types_of_activities'
    id = Column(Integer, primary_key=True)
    type = Column(String(30), nullable=False)

class Audiences(Base):
    __tablename__ = 'audiences'
    id = Column(Integer, primary_key=True)
    audience = Column(String(5), nullable=False)

class Teachers(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

class Disciplines(Base):
    __tablename__ = 'disciplines'
    id = Column(Integer, primary_key=True)
    discipline = Column(String(50), nullable=False)

class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    day_of_the_week_id = Column(Integer, ForeignKey('days_of_the_week.id'))
    discipline_id = Column(Integer, ForeignKey('disciplines.id'))
    audience_id = Column(Integer, ForeignKey('audiences.id'))
    couples_id = Column(Integer, ForeignKey('couples.id'))
    groups_id = Column(Integer, ForeignKey('groups.id'))
    teacher_id = Column(Integer, ForeignKey('teachers.id'))
    type_id = Column(Integer, ForeignKey('types_of_activities.id'))

    day_of_the_week = relationship("DaysOfTheWeek")
    discipline = relationship("Disciplines")
    audience = relationship("Audiences")
    couples = relationship("Couples")
    groups = relationship("Groups")
    teacher = relationship("Teachers")
    type = relationship("TypesOfActivities")