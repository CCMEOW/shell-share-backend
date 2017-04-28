# coding: utf-8
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text, text,create_engine
from sqlalchemy.orm import relationship,scoped_session,sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask import Flask,g

engine = create_engine('mysql+pymysql://root:root@localhost:3306/conch?charset=utf8')
db_session = scoped_session(sessionmaker(autocommit=False,
                                     autoflush=False,
                                     bind=engine))
app = Flask(__name__)
Base = declarative_base()
Base.query = db_session.query_property()
metadata = Base.metadata

class Notice(Base):
    __tablename__ = 'notice'

    id = Column(Integer, primary_key=True)
    type = Column(Enum(u'like', u'collection', u'follow'), nullable=False)
    receiver_id = Column(ForeignKey(u'user.id'), nullable=False, index=True)
    sender_id = Column(ForeignKey(u'user.id'), nullable=False, index=True)

    receiver = relationship(u'User', primaryjoin='Notice.receiver_id == User.id')
    sender = relationship(u'User', primaryjoin='Notice.sender_id == User.id')


class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    content = Column(Enum(u'admin', u'user'), nullable=False)


class Shell(Base):
    __tablename__ = 'shell'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'user.id'), nullable=False, index=True)
    song_id = Column(ForeignKey(u'song.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)

    song = relationship(u'Song')
    user = relationship(u'User')


class ShellTag(Base):
    __tablename__ = 'shell_tag'

    id = Column(Integer, primary_key=True)
    shell_id = Column(ForeignKey(u'shell.id'), nullable=False, index=True)
    tag_id = Column(ForeignKey(u'tag.id'), nullable=False, index=True)

    shell = relationship(u'Shell')
    tag = relationship(u'Tag')


class Song(Base):
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    singer = Column(String(45), nullable=False)
    url = Column(String(100))

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'singer_name':self.singer,
            'url':self.url
        }


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    content = Column(String(45), nullable=False)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    password = Column(String(20), nullable=False)
    email = Column(String(45), nullable=False)
    compaint = Column(Integer, nullable=False, server_default=text("'0'"))

    def to_json(self):
        return {
            'id':self.id,
            'name':self.name,
            'email':self.email,
            'complaint':self.compaint
        }

    def generate_auth_token(self,expiration = 600):
        s = Serializer('SECRET_KEY', expires_in = expiration)
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        print "verify_auth_token"
        s = Serializer('SECRET_KEY')
        try:
            data = s.loads(token)
        except SignatureExpired:
            print 'signature expired'
            return None
        except BadSignature:
            print 'bad signature'
            return  None
        user = User.query.get(data['id'])
        return user

    def verity_password(self,password):
        return password==self.password

class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'user.id'), index=True)
    role_id = Column(ForeignKey(u'role.id'), index=True)

    role = relationship(u'Role')
    user = relationship(u'User')


class UserShellRelationship(Base):
    __tablename__ = 'user_shell_relationship'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey(u'user.id'), nullable=False, index=True)
    shell_id = Column(ForeignKey(u'shell.id'), nullable=False, index=True)
    like = Column(Integer, nullable=False, server_default=text("'0'"))
    collection = Column(Integer, nullable=False, server_default=text("'0'"))

    shell = relationship(u'Shell')
    user = relationship(u'User')
