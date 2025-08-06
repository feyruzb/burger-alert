from datetime import datetime, date, time
from flask import Flask , render_template, request
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from typing import Dict, List
from sqlalchemy import and_
from collections import defaultdict
from sqlalchemy import distinct

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db = SQLAlchemy(app)
# ordering modes table
# Has a car and will drive people from office. = 1
# Want to be driven by someone from office. = 2
# I will come by myself. = 3

# GLOBAL VARIABLES
MAX_PASSENGER_CNT = 4

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    order = db.Column(db.String(200), nullable=False)
    mode = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Order %r>' % self.id

if not Path('instance/orders.db').exists():
    with app.app_context():
        db.create_all()

def is_now_burger_time():
    return app.debug or datetime.now().hour > 10 and \
        datetime.now().hour < 12 and \
        datetime.now().weekday() == 3

@app.route("/")
def index_page():
    disabled = not is_now_burger_time()
    return render_template('index.html', disabled=disabled)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    order = request.form.get("order")[:200]
    mode = request.form.get("mode")

    if not is_now_burger_time():
        return render_template("failed.html", error_msg = "not burger ordering time")

    order = Orders(name=name, order=order, mode = mode)

    try:
        db.session.add(order)
        db.session.commit()
        return render_template("confirmation.html", name=name, order=order)
    except:
        return render_template("failed.html")

@app.route("/today_orders")
def return_todays_orders():
    today = date.today()
    start_of_today = datetime.combine(today, time.min)
    end_of_today = datetime.combine(today, time.max)

    orders = Orders.query.filter(
        and_(
            Orders.date_created >= start_of_today,
            Orders.date_created <= end_of_today
        )
    ).order_by(Orders.date_created).all()

    sorted_orders = defaultdict(list)
    for order in orders:
        sorted_orders[order.name].append(order.order)

    sorted_orders_mega = {
        name: ", ".join(item_list)
        for name, item_list in sorted_orders.items()
    }

    return render_template("today_orders.html", orders=sorted_orders_mega)


@app.route("/car_distribution")
def return_car_distribution():
    start_of_today = datetime.combine(date.today(), time.min)
    end_of_today = datetime.combine(date.today(), time.max)

    # get list of people with car
    people_with_cars = list(set([ order.name for order in Orders.query.filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.mode == 1
    ).order_by(Orders.date_created).all() ]))

    names = db.session.query(Orders.name).filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.mode == 2
    ).distinct().order_by(Orders.date_created).all()

    people_without_cars = [name[0] for name in names]

    list_of_distributes: Dict[str, List[str]] = {}
    list_of_extra = []
    # Fill dict of drivers with passengers
    for driver in people_with_cars:
        list_of_distributes[driver] = list()

    driver_cnt = 0

    for ind, walker in enumerate(people_without_cars):
        if ind+1 > (len(people_with_cars) * MAX_PASSENGER_CNT):
            list_of_extra.append(walker)
        else:
            list_of_distributes[people_with_cars[driver_cnt]].append(walker)
            driver_cnt = (driver_cnt + 1) % len(people_with_cars)

    list_of_distributes = list(list_of_distributes.items())

    return render_template("car_distribution.html",
                           list_of_distributes=list_of_distributes,
                           list_of_extra=list_of_extra)

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=80,
            debug=True)
