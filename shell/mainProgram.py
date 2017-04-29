# encoding: utf-8

from sqlalchemy import Column, String, create_engine
from sqlalchemy import Enum
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, request, jsonify, g
from flask_restful import Api, Resource, abort, url_for
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm import scoped_session
from models import User, UserRole, db_session, Shell, Song, ShellTag, Notice
import common

app = Flask(__name__)
api = Api(app)

auth = HTTPBasicAuth()


# @app.before_request
# def init_session():
#     g.session = db_session()
#
#
# @app.teardown_request
# def close_session(exception):
#     try:
#         g.session.commit()
#     except:
#         print "oops!"
#         g.session.rollback()
#     finally:
#         print "aha close!"
#         g.session.close()


@auth.login_required
def get_auth_token():
    print "get auth token"
    token = g.user.generate_auth_token()
    return token.decode('ascii')


@auth.verify_password
def verify_password(email_or_token, password):
    print "verify password"
    print email_or_token, password
    user = User.verify_auth_token(email_or_token)
    if not user:
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.verity_password(password):
            print 'false'
            return False
    g.user = user
    print 'true'
    return True


# 注册
@app.route('/user', methods=['POST'])
def new_user():
    username = request.json.get('name')
    pwd = request.json.get('password')
    email = request.json.get('email')
    print username, pwd, email
    if username is None or pwd is None or email is None:
        abort(400)
    if User.query.filter_by(email=email).first() is not None:
        print "existed user"
        abort(400)
    common.send_mail(email)
    user = User(name=username, password=pwd, email=email)
    session = db_session()
    session.add(user)
    session.commit()
    session.close()
    user = session.merge(user)
    return jsonify(user.to_json())


# 登录
@app.route('/token', methods=['GET'])
def login():
    # email = request.json.get('email')
    # password = request.json.get('password')
    return jsonify({'token': get_auth_token})


# 获取歌曲
@app.route('/song')
def get_song():
    name = request.args.get('name')
    singer = request.args.get('singer_name')
    session = db_session
    result = []
    songs = session.query(Song).filter(Song.name == name, singer == None or Song.singer == singer).all()
    if (songs != None):
        result = [song.to_json() for song in songs]
    session.close()
    return jsonify(result)


# 新建歌曲
@app.route('/song', methods=['POST'])
@auth.login_required
def new_song():
    name = request.json.get('name')
    singer = request.json.get('singer')
    url = request.json.get('url')
    print name, singer, url
    song = Song(name=name, singer=singer, url=url)
    session = db_session()
    session.add(song)
    session.commit()
    session.close()
    song = session.merge(song)
    return jsonify(song.to_json())


# 创建海螺
@app.route('/shell', methods=['POST'])
@auth.login_required
def new_shell():
    user_name = g.user.name
    song_id = request.json.get('song_id')
    content = request.json.get('content')
    shell = Shell(user_id=g.user.id, song_id=song_id, content=content)
    session = db_session
    song = session.query(Song).filter(Song.id == song_id).first()
    session.add(shell)
    session.commit()
    session.close()
    shell = session.merge(shell)
    song = session.merge(song)
    return jsonify({
        'id': shell.id,
        'user_name': user_name,
        'song_id': song_id,
        "song_name": song.name,
        'singer_name': song.singer,
        'url': song.url,
        'content': shell.content
    })


# 打标签
@app.route('/shell/tag', methods=['POST'])
def set_tag():
    # shell_id=request.json.get("shell_id")
    # tag_id=request.json.get("tag_id")
    # session = db_session()
    # shell_tag = ShellTag(shell_id=shell_id,tag_id=tag_id)
    pass


# 根据歌曲/tag查看海螺，未完成
@app.route('/shell', methods=['GET'])
def all_shell():
    type = request.json.get("type")
    song_name = request.json.get("song_name")
    tag = request.json.get("tag")
    session = db_session()
    songs = session.query(Song).filter(Song.name == song_name).all()
    if type == "all":
        shells = [session.query(Shell).filter(Shell.song_id == song.id).all() for song in songs]
    shells = [shell.to_json() for shell in session.query(Song).all()]
    session.close()
    return jsonify(shells)


# 喜欢,，未完成
@app.route('/shell/like', methods=['POST'])
@auth.login_required
def like_shell():
    session = db_session()
    shell_id = request.json.get("shell_id")
    receiver_id = session.query(Shell).filter(Shell.id == shell_id).first().user_id
    type = 'like'
    sender_id = g.user.id
    notice = Notice(sender_id=sender_id, receiver_id=receiver_id, type=type)
    session.add(notice)
    try:
        session.commit()
    except StatementError, e:
        print e.message
        session.rollback()
    finally:
        session.close()
    return jsonify({"aa": "aa"})


# 举报
@app.route('/user/<int:id>/complain', methods=['PATCH'])
def comlain_user(id):
    session = db_session
    try:
        user = session.query(User).filter(User.id == id).first()
        user.compaint+=1
        session.commit()
    finally:
        session.close()
    user = session.merge(user)
    return jsonify(user.to_json())

#关注海螺作者
# @app.route('/user/id/follow')


# 查看我的收藏列表
@app.route('/favorate', methods=['GET'])
def my_collection():
    pass


# 查看我的喜欢列表
@app.route('/like', methods=['GET'])
def my_like():
    pass


if __name__ == '__main__':
    app.run(debug=True)
