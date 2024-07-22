import sqlalchemy
from .db_session import SqlAlchemyBase


class Level(SqlAlchemyBase):
    __tablename__ = 'levels'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name_game = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name_math = sqlalchemy.Column(sqlalchemy.String, nullable=True)



class Module(SqlAlchemyBase):
    __tablename__ = 'modules'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    level_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("levels.id"))
    name_game = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name_math = sqlalchemy.Column(sqlalchemy.String, nullable=True)



class Progress(SqlAlchemyBase):
    __tablename__ = 'progress'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    level_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("levels.id"))
    module_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("modules.id"))
    task_id = sqlalchemy.Column(sqlalchemy.Integer)
    text_task = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    completed = sqlalchemy.Column(sqlalchemy.String, default='unblocked')
