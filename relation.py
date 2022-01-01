from sqlalchemy import Column, String, JSON, Boolean, Integer
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass

db = SQLAlchemy()

@dataclass
class Dept(db.Model):
    __tablename__ = 'dept'

    id: str
    name: str
    abber: str

    id = Column(String, primary_key=True)
    name = Column(String)
    abber = Column(String)


@dataclass
class College(db.Model):
    __tablename__ = 'college'

    id: int
    name: str
    depts: JSON

    id = Column(Integer, primary_key=True)
    name = Column(String)
    depts = Column(JSON)

@dataclass
class Course(db.Model):
    __tablename__ = 'course'

    id: str #課程碼 in 1st td (starting from 0)
    deptName : str #系所名 in 0th td
    name: str #科目名稱 in 4th td
    link: str #課綱連結 in 4th td
    mandatoriness = bool #選必修 in 5th td

    id = Column(String, primary_key=True)
    deptName = Column(String)
    name = Column(String)
    link = Column(String)
    mandatoriness = Column(Boolean)

'''
if __name__ == '__main__':
    engine = create_engine("sqlite+pysqlite:///db.sqlite", echo=True, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    with Session() as s:
        s.add(Dept(id='A1', name='外語中心', aber='FLC'))
        s.commit()
'''
