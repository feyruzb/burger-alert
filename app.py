from datetime import datetime, date, time
from os import getenv
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from typing import Dict, List
from sqlalchemy import and_
from collections import defaultdict
from sqlalchemy import distinct
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db = SQLAlchemy(app)
# ordering modes table
# Has a car and will drive people from office. = 1
# Want to be driven by someone from office. = 2
# I will come by myself. = 3

# GLOBAL VARIABLES
MAX_PASSENGER_CNT = 4
START_HOUR_OF_DAY = 1
END_HOUR_OF_DAY = 13
NO_TIME_CONSTRAINT = getenv("NO_TIME_CONSTRAINT") in ["true", "1"]
# despite the name there is supposed to be only 1 driver
APP_VERSION = os.getenv("APP_VERSION", "v0.0.0")

@app.context_processor
def inject_version():
    return dict(app_version=APP_VERSION)

class UserOrder:
    def __init__(self, name,
                 order=None,
                 lipoti=None,
                 takeout=None,
                 t_mode=None):

        self.name = name
        self.order = order
        self.lipoti = lipoti
        self.takeout = takeout
        self.t_mode = t_mode

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    order = db.Column(db.String(200), nullable=False)
    lipoti_d = db.Column(db.Integer, nullable=False)
    lipoti = db.Column(db.Integer, nullable=False)
    takeout = db.Column(db.Integer, nullable=False)
    t_mode = db.Column(db.Integer, nullable=False)

    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Order %r>' % self.id

if not Path('instance/orders.db').exists():
    with app.app_context():
        db.create_all()

def get_people_with_cars():
    """
    Returns a list of people that are drivers.
    """
    start_of_today = datetime.combine(date.today(), time.min)
    end_of_today = datetime.combine(date.today(), time.max)

    names_wc = db.session.query(Orders.name).filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.t_mode == 1
    ).distinct().order_by(Orders.date_created).all()
    return [name[0] for name in names_wc]

def get_list_of_lipoti_drivers():
    """
    Returns a list of people that want to be drivers for LIPÓTI.
    """
    start_of_today = datetime.combine(date.today(), time.min)
    end_of_today = datetime.combine(date.today(), time.max)

    names_wc = db.session.query(Orders.name).filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.lipoti_d == 1
    ).distinct().order_by(Orders.date_created).all()
    return [name[0] for name in names_wc]

def is_now_burger_time():
    if app.debug or NO_TIME_CONSTRAINT:
        return True
    return datetime.now().hour > START_HOUR_OF_DAY and \
        datetime.now().hour < END_HOUR_OF_DAY and \
        datetime.now().weekday() == 3

@app.route("/")
def index_page():
    disabled = not is_now_burger_time()
    return render_template('index.html', disabled=disabled)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "Placeholder")
    order = request.form.get("order", "Placeholder")[:200]
    lipoti_d = request.form.get("lipoti_d", 0)
    lipoti = request.form.get("lipoti", "Placeholder")
    takeout = request.form.get("takeout", "Placeholder")

    # if it is a takeout order, set mode to 0 if not set to mode
    if takeout == "takeout":
        takeout = 1
        t_mode = 0
    else:
        takeout = 0
        t_mode = request.form.get("mode", 0)

    if not is_now_burger_time():
        return render_template("failed.html",
                               error_msg = "not burger ordering time")

    order = Orders(name=name,
                   order=order,
                   lipoti_d=lipoti_d,
                   lipoti=lipoti,
                   takeout=takeout,
                   t_mode=t_mode)

    try:
        db.session.add(order)
        db.session.commit()
        return render_template("confirmation.html", name=name, order=order)
    except:
        return render_template("failed.html")

@app.route("/orders/delete", methods=["POST"])
def delete_order():
    name = request.form.get("name")
    if not name:
        return render_template("failed.html",
                               error_msg="No such name exists in database")


    try:
        db.session.query(Orders).filter(
            Orders.name == name
            ).delete()

        db.session.commit()
    except:
        return render_template("failed.html")

    return redirect("/today_orders")


@app.route("/today_orders")
def return_todays_orders():
    today = date.today()
    start_of_today = datetime.combine(today, time.min)
    end_of_today = datetime.combine(today, time.max)
    # limit of people that can go by cars
    top_limit = len(get_people_with_cars()) * 5

    orders = Orders.query.filter(
        and_(
            Orders.date_created >= start_of_today,
            Orders.date_created <= end_of_today
        )
    ).order_by(Orders.date_created).all()

    def squash_orders(name):
        items = [order.order for order in orders if order.name == name]
        result = ", ".join(items)
        return result

    users_orders = []
    for order in orders:
        if not any(uo.name == order.name for uo in users_orders):
            user_order = UserOrder(
                name=order.name,
                order=squash_orders(order.name),
                takeout=order.takeout,
                t_mode=order.t_mode
            )
            users_orders.append(user_order)

    buckets = [[], []]  # index 0 -> dine-in, index 1 -> takeout

    cnt = 0
    for uo in users_orders:
        if uo.t_mode == 3:
            buckets[0].append(uo)
        elif uo.takeout or cnt >= top_limit:
            buckets[1].append(uo)
        else:
            buckets[0].append(uo)
            cnt+=1

    return render_template("today_orders.html",
                           dinein_orders=buckets[0],
                           takeout_orders=buckets[1] )

@app.route("/car_distribution")
def return_car_distribution():
    start_of_today = datetime.combine(date.today(), time.min)
    end_of_today = datetime.combine(date.today(), time.max)

    lipoti_drivers = get_list_of_lipoti_drivers()

    people_with_cars = get_people_with_cars()

    names_nc = db.session.query(Orders.name).filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.t_mode == 2
    ).distinct().order_by(Orders.date_created).all()
    people_without_cars = [name[0] for name in names_nc]

    # lipoti priority
    names_lipoti = db.session.query(Orders.name).filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.lipoti == 1
    ).distinct().order_by(Orders.date_created).all()
    lipoti_passengers = [name[0] for name in names_lipoti]

    # people that get in by themselves
    names_self_d = db.session.query(Orders.name).filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today,
        Orders.t_mode == 3
    ).distinct().order_by(Orders.date_created).all()
    names_self_passengers = [name[0] for name in names_self_d]

    if people_with_cars:

        list_of_distributes: Dict[str, List[str]] = {}
        # Fill dict of drivers with driver's names
        for driver in people_with_cars:
            list_of_distributes[driver] = list()

        # Fill priority with people that want to go in lipoti
        try:
            lipoti_driver_set = set(lipoti_drivers)
        except Exception as e:
            print(f"Error parsing lipoti_drivers: {e}")
            lipoti_driver_set = set()

        for walker in lipoti_passengers:
            for driver in people_with_cars:
                if driver in lipoti_driver_set and len(list_of_distributes[driver]) < MAX_PASSENGER_CNT:
                    if walker not in list_of_distributes[driver]:
                        list_of_distributes[driver].append(walker)
                    break


        list_of_extra = []
        driver_cnt = 0
        already_assigned = {p for riders in list_of_distributes.values() for p in riders}

        for walker in people_without_cars:
            if walker in already_assigned:
                continue

            got_place = False
            for _ in range(len(people_with_cars)):
                driver = people_with_cars[driver_cnt]
                if len(list_of_distributes[driver]) < MAX_PASSENGER_CNT:
                    list_of_distributes[driver].append(walker)
                    already_assigned.add(walker)
                    got_place = True
                    driver_cnt = (driver_cnt + 1) % len(people_with_cars)
                    break
                driver_cnt = (driver_cnt + 1) % len(people_with_cars)

            if not got_place:
                list_of_extra.append(walker)
                driver_cnt = (driver_cnt + 1) % len(people_with_cars)

        list_of_distributes = list(list_of_distributes.items())

        return render_template("car_distribution.html",
                            list_of_distributes=list_of_distributes,
                            list_of_extra=list_of_extra,
                            names_self_passengers=names_self_passengers)
    return render_template("failed.html",
                               error_msg = "Unfortunately there are no drivers")

if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=80,
            debug=True)
