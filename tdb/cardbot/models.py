import sqlalchemy

from tdb.cardbot import database


class Job(database.BaseDatabase.base):
    __tablename__ = 'jobs'

    job_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    job_type = sqlalchemy.Column(sqlalchemy.String, index=True)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime, index=True)
    end_time = sqlalchemy.Column(sqlalchemy.DateTime)
    status = sqlalchemy.Column(sqlalchemy.String)
    results = sqlalchemy.Column(sqlalchemy.JSON)
