from flask import Flask, render_template,request
from model import db, User  
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SECRET_KEY"] = "HARSH123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/c',methods =['GET','POST'])
def home():
    if request.method == 'POST':
        name = request.form ['name']
        email = request.form['email']
        age = request.form['age']

        new_user = User(name = 'name' , email = 'email ' , age = 'age')

        db.session.add(new_user)
        db.session.commit()
    return render_template("index.html")

@app.route('/a')
def home1():
    return render_template("form.html")

@app.route('/b')
def home2():
    return render_template("base.html")

@app.route('/xyz')
def home3():
    return render_template("xyz.html")

if __name__ == "__main__":
    app.run(debug=True)

