from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.secret_key = 'hi'
db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return '<Task %r>' % self.id

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    last_password = db.Column(db.String(200))
    name = db.Column(db.String(200), nullable=False)
    surname = db.Column(db.String(200), nullable=False)
    age = db.Column(db.String(200), nullable=False)
    tasks_ids = db.relationship('Todo', backref='user')

    def __str__(self):
        return f'User: {self.name} {self.surname}'

@app.route('/user_page/', methods=['GET', 'POST'])
def user_page():
    if request.method == 'POST':
        del session['email']
        return redirect('/login/')
    else:
        if 'email' not in session or not session['email']:
            return redirect('/login/')
        return render_template('user_page.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']
        get_user = Users.query.filter_by(email=user_email, password=user_password).first()
        if get_user:
            session['email'] = user_email
            return redirect('/user_page/')
        else:
            return render_template('user_login.html', login_failed=True)
    else:
        if 'email' in session and session['email']:
            return redirect('/user_page/')
        return render_template('user_login.html')

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        current_user = session['email'] if 'email' in session and session['email'] else False
        if current_user:
            new_task = Todo(content=task_content, user_id=Users.query.filter_by(email=session['email']).first().id)
        else:
            new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an error!'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        session_email = session['email'] if 'email' in session and session['email'] else 'logged_id'
        return render_template('index.html', tasks=tasks, session_email=session_email)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was an error!'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an error!'
    else:
        return render_template('update.html', task=task)

if __name__ == '__main__':
    app.run(debug=True)
