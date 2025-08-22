from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scheduler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ------------------- Database Model ------------------- #
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    task = db.Column(db.String(200), nullable=False)
    backlog = db.Column(db.String(200))
    process = db.Column(db.String(200))
    done = db.Column(db.String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "task": self.task,
            "backlog": self.backlog,
            "process": self.process,
            "done": self.done
        }

# ------------------- Routes ------------------- #
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('muluma schedular.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    data = request.json
    new_task = Task(
        name=data['name'],
        surname=data['surname'],
        task=data['task'],
        backlog=data.get('backlog', ''),
        process=data.get('process', ''),
        done=data.get('done', '')
    )
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict())

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})

@app.route('/edit/<int:id>', methods=['PUT'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    data = request.json
    task.name = data['name']
    task.surname = data['surname']
    task.task = data['task']
    task.backlog = data['backlog']
    task.process = data['process']
    task.done = data['done']
    db.session.commit()
    return jsonify(task.to_dict())

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
