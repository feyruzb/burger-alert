from flask import Flask , render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from typing import Dict, List
import random

from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db = SQLAlchemy(app)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    order = db.Column(db.String(200), nullable=False)
    mode = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Order %r>' % self.id

@app.route("/")
def index_page():
    return render_template('index.html')

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    order = request.form.get("order")
    mode = request.form.get("mode")

    order = Orders(name=name,
                   order=order,
                   mode = mode
                   )

    try:
        db.session.add(order)
        db.session.commit()
        return render_template("confirmation.html",
                            name=name,
                            order=order)
    except:
        return render_template("failed.html")

@app.route("/today_orders")
def return_todays_orders():
    start_of_today = datetime.combine(date.today(), time.min)
    end_of_today = datetime.combine(date.today(), time.max)

    orders = Orders.query.filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today
    ).order_by(Orders.date_created).all()

    return render_template("today_orders.html", orders=orders)

@app.route("/car_distribution")
def return_car_distribution():
    start_of_today = datetime.combine(date.today(), time.min)
    end_of_today = datetime.combine(date.today(), time.max)


    people_with_cars = list(set([ order.name for order in Orders.query.filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.mode =="Has a car and will drive people from office"
    ).order_by(Orders.name).all() ]))

    people_without_cars = list(set([ order.name for order in Orders.query.filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.mode =="Want to be driven by someone from office"
    ).order_by(Orders.name).all()]))
    # print(people_with_cars)
    # print(people_without_cars)

    # random.shuffle(people_without_cars)

    list_of_distributes: Dict[str, List[str]] = {}

    for driver in people_with_cars:
        list_of_distributes[driver] = list()

    driver_cnt = 0
    for walker in people_without_cars:
        list_of_distributes[people_with_cars[driver_cnt]].append(walker)
        driver_cnt = (driver_cnt + 1) % len(people_with_cars)

    print("list of distributors", list_of_distributes.items())
    list_of_distributes = list(list_of_distributes.items())


    return render_template("car_distribution.html", list_of_distributes=list_of_distributes)

@app.route('/hello')
def hello():
    return 'Hello, World'

if __name__ == "__main__":
    app.run(debug=True)




