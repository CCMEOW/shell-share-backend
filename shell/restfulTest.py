from flask import Flask,request
from flask_restful import Resource,Api

app = Flask(__name__)
api = Api(app)

todos = {}

class HelloWorld(Resource):
    def get(self):
        return {'hello':'world'}

class TodoSimple(Resource):
    def get(self,todoId):
        return {todoId:todos[todoId]}

    def put(self,todoId):
        print request.form['data']
        todos[todoId] = request.form['data']
        return {todoId:todos[todoId]}

api.add_resource(TodoSimple,'/<string:todoId>')
api.add_resource(HelloWorld,'/')

if(__name__) == '__main__':
    app.run(debug=True)