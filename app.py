from flask import Flask, render_template as rt, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta, date
import hashlib
from instance.Utils import *


app = Flask(__name__)
app.secret_key = "secret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Todo(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    done = db.Column(db.Boolean)
    created = db.Column(db.String)
    dueDate = db.Column(db.String)
    userId = db.Column(db.Integer, db.ForeignKey('users.userId'), nullable=False)
    
class Users(db.Model):
    userId = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(20))
    salt = db.Column(db.String(10))


@app.route('/')
def home():
    if session:
        todo_list=getUserTodos(session['userId'])
        lateTodos=getLateList(todo_list)
        user = session['user']
    else:
        todo_list = None
        user = None 
        lateTodos = None
    return rt('base.html',todo_list=todo_list, user=user, lateTodos=lateTodos)

@app.route('/login', methods=["GET","POST"])
def login():
        if request.method == "POST":
            username = request.form.get('email')
            password = request.form.get('password')

            if validateLogin(username, password):
                session['user'] = username
                session['userId'] = getUserId(username)[0]
                return redirect(url_for("home"))
            else:
                return rt("login.html", error="Invalid Login")
         
        return rt("login.html")       

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route('/register', methods=["GET","POST"])
def register():
        if request.method == "POST":
            username = request.form.get('email')
            password = request.form.get('password')
            if validateEmail(username):
                #salt the password
                salt = saltShaker()
                hashPass = hashlib.sha256((password+salt).encode('utf-8')).hexdigest()
                
                new_user = Users(username=username, password=hashPass, salt=salt)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("login"))
            return redirect(url_for("register"))

         
        return rt("register.html")    

@app.route('/add',methods=['POST'])
def add():
    name = request.form.get("name")
    dueIn = request.form.get("dueDate")
    dayCreated = date.today()
    if dueIn != None:
        dueDate = dayCreated + timedelta(days=int(dueIn))
    else:
        dueDate = None
    new_task=Todo(name=name,done=False, userId=session['userId'], created=dayCreated, dueDate=dueDate)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo= Todo.query.get(todo_id)
    if session['userId'] == todo.userId:
        todo.done=not todo.done
        db.session.commit()
    return redirect(url_for("home"))


@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo= Todo.query.get(todo_id)
    if session['userId'] == todo.userId:
        db.session.delete(todo)
        db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True)