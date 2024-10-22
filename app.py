from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']=environ.get['DB_URL']
db=SQLAlchemy(app)


class User(db.Model):
    __tablename__='users'
    
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(80), unique=True, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    
    # def __init__(self, username, email):
    #     self.username=username
    #     self.email=email
        
    def json(self):
        return{'id':id, 'username':self.username, 'email':self.email}
    
db.create_all()

    
@app.route('/run', methods=['GET'])
def Fetch():
    return make_response(jsonify({'message':'test route'}),200)

@app.route('/add', methods=['POST'])
def add_user():
    try:
        data=request.get_json()
        newUser=User(username=data['username'],email=data['email'])
        db.session.add(newUser)
        db.session.commit()
        return make_response(jsonify({'message':'user added'}),201)
    except:
        return make_response(jsonify({'message':'Error user adding'}),500)

