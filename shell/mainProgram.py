# encoding: utf-8

from sqlalchemy import Column, String, create_engine
from sqlalchemy import Enum
from sqlalchemy.exc import StatementError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, request, jsonify, g, wrappers
from flask_restful import Api, Resource, abort, url_for
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.orm import scoped_session
from models import User, UserRole, db_session, Shell, Song, ShellTag, Notice, Tag
import common
from random import choice

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

def generate_return_info(code, message):
    return {
        "code": code,
        "message": message
    }


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
            return False
    g.user = user
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
    token = get_auth_token()
    code = 1
    message = "登录成功"
    if type(token) != unicode:
        token = ""
        code = 0
        message = "登录失败"
    return jsonify({
        'user': {'token': token},
        'info': generate_return_info(code, message)
    })


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
    return jsonify(shell.to_json())


# 添加标签
@app.route('/shell/tag', methods=['POST'])
def add_tag():
    shell_id = request.json.get("shell_id")
    tag_ids = request.json.get("tag_id")
    session = db_session()
    session.query(ShellTag).filter(ShellTag.shell_id == shell_id).delete(synchronize_session=False)
    for tag_id in tag_ids:
        session.add(ShellTag(shell_id=shell_id, tag_id=tag_id))
    shell = session.query(Shell).filter(Shell.id == shell_id).first()
    try:
        session.commit()
    finally:
        session.close()
    info = generate_return_info(1, "操作成功")
    return jsonify({
        "shell": shell.to_json(),
        "info": info})


# 根据歌曲/tag查看海螺，未完成
@app.route('/shell', methods=['GET'])
def all_shell():
    type = request.args.get("type")
    song_name = request.args.get("song_name")
    tag = request.args.get("tag")
    session = db_session()
    songs = session.query(Song).filter(Song.name == song_name).all()
    # if type == "all":
    shells_result = []
    for song in songs:
        shells_tmp = session.query(Shell).filter(Shell.song_id == song.id).all()
        for shell in shells_tmp:
            shells_result.append(shell)
    shells = []
    if type == "all":
        shells = [shell.to_json() for shell in shells_result]
    elif type == "random":
        shells = choice(shells_result).to_json()
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
        user.compaint += 1
        session.commit()
    finally:
        session.close()
    user = session.merge(user)
    return jsonify(user.to_json())


# 关注海螺作者
# @app.route('/user/id/follow')


# 查看我的收藏列表
@app.route('/favorate', methods=['GET'])
def my_collection():
    pass


# 查看我的喜欢列表
@app.route('/like', methods=['GET'])
def my_like():
    pass


# 测试程序
@app.route('/test/<int:id>', methods=['GET'])
def test(id):
    session = db_session()
    # tags = [tag.content for tag in [session.query(Tag).filter(Tag.id == tag_id).all() for tag_id in
    #         session.query(ShellTag).filter(ShellTag.shell_id == id).all()]]
    # tag_ids = session.query(ShellTag.tag_id).filter(ShellTag.shell_id == id).all()
    tags_result = [session.query(Tag.content).filter(Tag.id == tag_id[0]).first() for tag_id in
                   session.query(ShellTag.tag_id).filter(ShellTag.shell_id == id).all()]
    session.close()
    tags = []
    for tag in tags_result:
        tags.append(tag[0])
    print tags
    return jsonify({"tags": tags})


if __name__ == '__main__':
    app.run(debug=True)
