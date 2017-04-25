# encoding: utf-8

from sqlalchemy import Column,String,create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask,request,jsonify,g
from flask_restful import Api,Resource,abort,url_for
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm import scoped_session
from models import User,UserRole,db_session,Shell,Song
import common

app = Flask(__name__)
api = Api(app)

auth = HTTPBasicAuth()


@app.before_request
def before_request():
    pass

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    print "get auth token"
    token = g.user.generate_auth_token()
    print token
    return jsonify({'token':token.decode('ascii')})


@auth.verify_password
def verify_password(email_or_token,password):
    print "verify password"
    print email_or_token,password
    user = User.verify_auth_token(email_or_token)
    if not user:
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.verity_password(password):
            return False
        g.user = user
        print 'true'
        return True


@app.route('/user',methods=['POST'])
def new_user():
    username = request.json.get('username')
    pwd = request.json.get('password')
    email = request.json.get('email')
    print username,pwd,email
    if username is None or pwd is None or email is None:
        print "none element"
        abort(400)
    if User.query.filter_by(email=email).first() is not None:
        print "existed user"
        abort(400)
    common.send_mail(email)
    user =User(name=username,password=pwd,email=email)
    session = db_session()
    session.add(user)
    session.commit()
    session.close()
    return jsonify({'username':user.name}),201

@app.route('/session',methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    get_auth_token()

# 新建歌曲
@app.route('/song',methods=['POST'])
def new_song():
    name = request.json.get('name')
    singer = request.json.get('singer')
    url = request.json.get('url')
    print name,singer,url
    song = Song(name=name,singer=singer,url=url)
    session = db_session()
    session.add(song)
    session.commit()
    session.close()
    song = session.merge(song)
    return jsonify({'name':song.name})


# 扔海螺
@app.route('/shell',methods=['POST'])
def throw():
    pass

# 查看所有海螺
@app.route('/shell',methods=['GET'])
def all_shell():
    session = db_session()
    shells = session.query(Shell).all()
    session.close()
    return jsonify(shells)

# 查看我的收藏列表
@app.route('/favorate',methods=['GET'])
def my_collection():
    pass

# 查看我的喜欢列表
@app.route('/like',methods=['GET'])
def my_like():
    pass

if __name__=='__main__':
    app.run(debug=True)




