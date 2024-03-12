from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task_db.db'
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(50), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


def create_table():
    if os.path.exists('task_db.db'):
        os.remove('task_db.db')

    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Created 'task' table.")


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # Handle form submission to add new task
        task_content = request.form['content']
        priority = request.form['priority']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d') if request.form['due_date'] else None

        new_task = Task(content=task_content, priority=priority, due_date=due_date)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        # Render index page with list of tasks
        tasks = Task.query.order_by(Task.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    # Handle task deletion
    task_to_delete = Task.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    # Handle task update
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        task.priority = request.form['priority']
        task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d') if request.form['due_date'] else None

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)


if __name__ == "__main__":
    create_table()
    app.run(debug=True)
