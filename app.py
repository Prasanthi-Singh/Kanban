# from crypt import methods
# from curses import flash
from flask import flash
from enum import unique
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use('Agg')


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pkanban.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'abc'

db = SQLAlchemy(app)


class User(db.Model):
    tablename = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(15), nullable=False, unique=True)
    emailid = db.Column(db.String(50), nullable=False)
    passw = db.Column(db.String, nullable=False)


class List(db.Model):
    tablename = 'list'
    list_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    l_name = db.Column(db.String(15), nullable=False)
    l_description = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id'), nullable=False)


class Card(db.Model):
    tablename = 'card'
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_name = db.Column(db.String(15), nullable=False)
    c_description = db.Column(db.String(150), nullable=False)
    p_rate = db.Column(db.String(15), nullable=False)
    deadline = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id'), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'list.list_id'), nullable=False)


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(user_name=name).first()
        if user is None:

            user_detail = User(
                user_name=name, emailid=email, passw=password)
            db.session.add(user_detail)
            db.session.commit()

            userid = User.query.with_entities(
                User.user_id).filter_by(user_name=name).first()
            uid = User.query.filter_by(user_id=userid.user_id).first()

            return render_template('dashboard.html', users=uid)
        else:
            msg = "Username already Exists! Kindly try different username !"
            return render_template('signup.html', msg=msg)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        name1 = request.form['name']
        password = request.form['password']

        userid = User.query.with_entities(
            User.user_id).filter_by(user_name=name1).first()
        if(userid):

            uid = User.query.filter_by(user_id=userid.user_id).first()
            list = List.query.filter_by(user_id=uid.user_id).all()
            card = Card.query.filter_by(user_id=uid.user_id).all()
            if uid is None:
                msg = "wrong username"
                return render_template('login.html', mag=msg)
            else:
                if uid.passw != password:
                    msg = "Credentials are not matching!please enter correct credentials"
                    return render_template('login.html', msg=msg)
                else:
                    return redirect(url_for('dashboard', user_id=uid.user_id))
        else:

            # flash("Enter Correct Details!")
            msg = "Enter correct details"
            return render_template('signup.html', msg=msg)


@app.route('/<int:user_id>/dashboard')
def dashboard(user_id):
    print(user_id)
    users = User.query.filter_by(user_id=user_id).first()
    list = List.query.filter_by(user_id=user_id).all()
    card = Card.query.filter_by(user_id=user_id).all()
    return render_template('dashboard1.html', cards=card, lists=list, users=users)


@app.route('/list/<int:user_id>', methods=['POST', 'GET'])
def list(user_id):
    if request.method == 'GET':
        users = User.query.filter_by(user_id=user_id).first()
        return render_template('list.html', users=users)
    elif request.method == 'POST':
        name1 = request.form['name']
        descr = request.form['description']

        list_detail = List(
            l_name=name1, l_description=descr, user_id=user_id)
        db.session.add(list_detail)
        db.session.commit()

        return redirect(url_for('dashboard', user_id=user_id))


@app.route('/card/<int:list_id>', methods=['POST', 'GET'])
def card(list_id):
    if request.method == 'GET':
        list = List.query.filter_by(list_id=list_id).first()
        user = User.query.filter_by(user_id=list.user_id).first()
        return render_template('card.html', l_name=list.l_name, user_name=user.user_name, l_id=list.list_id)
    elif request.method == 'POST':
        name1 = request.form['task']
        descr = request.form['desc']
        progress = request.form.getlist('progress')
        deadline = request.form['deadline']
        for pro in progress:

            if pro == 'progress_1':
                pid = 'Completed'
            elif pro == 'progress_2':
                pid = 'In progress'
            elif pro == 'progress_3':
                pid = 'Not started'

        l = List.query.filter_by(list_id=list_id).first()
        card_detail = Card(
            c_name=name1, c_description=descr, p_rate=pid, deadline=deadline, user_id=l.user_id, list_id=l.list_id)
        db.session.add(card_detail)
        db.session.commit()
        enrolls = List.query.with_entities(
            List.user_id).filter_by(list_id=list_id).first()
        user_id = enrolls.user_id
        return redirect(url_for('dashboard', user_id=user_id))


@app.route('/list/<int:list_id>/update', methods=['GET', 'POST'])
def update(list_id):
    if request.method == 'GET':  # check id
        record = List.query.filter_by(list_id=list_id).first()
        enroll = List.query.with_entities(
            List.user_id).filter_by(list_id=list_id).first()
        uid = User.query.filter_by(user_id=enroll.user_id).first()
        return render_template('updatelist.html', list=record, users=uid)

    elif request.method == 'POST':
        name1 = request.form['name']
        descr = request.form['description']

        print(name1)
        # store course
        s = List.query.filter_by(list_id=list_id).update(
            dict(l_name=name1, l_description=descr))                #
        db.session.commit()
        enroll = List.query.with_entities(
            List.user_id).filter_by(list_id=list_id).first()
        user_id = enroll.user_id
        # return redirect(f'/{user_id}/dashboard')
        return redirect(url_for('dashboard', user_id=user_id))


@app.route('/card/<int:card_id>/update', methods=['GET', 'POST'])
def update1(card_id):
    if request.method == 'GET':  # check id
        record = Card.query.filter_by(card_id=card_id).first()
        print(record.p_rate)
        enroll = Card.query.with_entities(
            Card.user_id).filter_by(card_id=card_id).first()
        print(enroll)
        uid = User.query.filter_by(user_id=enroll.user_id).first()
        print(uid)
        ld = List.query.filter_by(user_id=enroll.user_id).all()

        return render_template('updatecard.html', card=record, users=uid, p=record.p_rate, lists=ld)

    elif request.method == 'POST':
        new_list_name = request.form.getlist('lname')[0]
        name1 = request.form['task']
        descr = request.form['desc']
        progress = request.form.getlist('progress')
        deadline = request.form['deadline']
        for pro in progress:

            if pro == 'progress_1':
                pid = 'Completed'
            elif pro == 'progress_2':
                pid = 'In progress'
            elif pro == 'progress_3':
                pid = 'Not started'

        # store course

        s = Card.query.filter_by(card_id=card_id).update(dict(list_id=new_list_name,
                                                              c_name=name1, c_description=descr, p_rate=pid, deadline=deadline,))                #
        db.session.commit()
        enroll = Card.query.with_entities(
            Card.user_id).filter_by(card_id=card_id).first()
        user_id = enroll.user_id

    # return redirect(f'/{user_id}/dashboard')
    return redirect(url_for('dashboard', user_id=user_id))


@app.route('/summary/<int:user_id>')
def summary(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    list = List.query.filter_by(user_id=user_id).all()

    id = []
    overall = []
    t = dt.today()
    for i in list:
        id.append(i.list_id)
    status = []
    deadline = []
    for j in id:
        date = []
        status_ = []
        card = Card.query.filter_by(list_id=j).all()
        for k in card:
            date.append(k.deadline)
            status_.append(k.p_rate)
        status.append(status_)
        deadline.append(date)
    # print(status)
    # print(deadline)
    image = []
    for i in range(len(status)):
        all = []
        S = 0
        C = 0
        I = 0
        passed = 0
        left = 0
        for j in deadline[i]:
            if dt.strptime(j, "%Y-%m-%d") > t:
                left += 1
            else:
                passed += 1
        for elem in status[i]:
            if elem == 'Completed':
                C += 1
            else:
                S += 1
        all.append(C)
        # all.append(I)
        all.append(S)
        all.append(passed)
        overall.append(all)
    print(overall)

    for i in range(len(overall)):
        x = ['Completed', 'In Progress', 'deadline passed']
        y = overall[i]
        plt.clf()
        plt.bar(x, y, color=['green',  'blue', 'red'], width=0.4)
        plt.ylabel("Number of Task")
        plt.title("Summary of Task")
        plt.savefig(f'Kanban/static/images/hist{y}.png')
        image.append(f'/static/images/hist{y}.png')

    return render_template('summary.html', images=image, users=user, list=list, overall=overall)


@app.route('/list/<int:list_id>/<int:user_id>/delete')
def delete(list_id, user_id):
    record = List.query.filter_by(list_id=list_id).first()
    return render_template('l_confirmation.html', list=record, list_id_d=list_id, user_id_d=user_id)


@app.route('/list/<int:list_id>/<int:user_id>/delete/confirm')
def confirm_l(list_id, user_id):
    l = List.query.filter_by(list_id=list_id).first()
    c = Card.query.filter_by(list_id=list_id).all()
    for i in c:
        db.session.delete(i)

    db.session.delete(l)
    db.session.commit()

    # return redirect(f'/{user_id}/dashboard')
    return redirect(url_for('dashboard', user_id=user_id))


@app.route('/delete/<int:card_id>/<int:user_id>')
def delete1(card_id, user_id):
    record = Card.query.filter_by(card_id=card_id).first()
    return render_template('c_confirmation.html', card=record, card_id_d=card_id, user_id_d=user_id)


@app.route('/card/<int:card_id>/<int:user_id>/delete/confirm')
def confirm_c(card_id, user_id):
    card = Card.query.filter_by(card_id=card_id).first()
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('dashboard', user_id=user_id))


@app.route('/cancel/<int:user_id>')
def cancel(user_id):
    return redirect(url_for('dashboard', user_id=user_id))
    # return redirect(f'/{user_id}/dashboard')


@app.route('/logout')
def logout():
    return redirect('/')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
