from datetime import datetime, date, time
from flask import Flask , render_template, request
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from typing import Dict, List
from sqlalchemy import and_
from collections import defaultdict

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

    # Get the latest order per person to determine their current transportation mode
    from sqlalchemy import desc
    latest_orders = db.session.query(Orders).filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today
    ).order_by(Orders.name, desc(Orders.date_created)).all()
    
    # Keep only the latest order per person
    latest_orders_per_person = {}
    for order in latest_orders:
        if order.name not in latest_orders_per_person:
            latest_orders_per_person[order.name] = order

    people_with_cars = [
        name for name, order in latest_orders_per_person.items()
        if order.mode == "Has a car and will drive people from office"
    ]

    people_without_cars = [
        name for name, order in latest_orders_per_person.items()
        if order.mode == "Want to be driven by someone from office"
    ]

    list_of_distributes: Dict[str, List[str]] = {}

    for driver in people_with_cars:
        list_of_distributes[driver] = list()

    if people_with_cars:  # Only distribute if there are drivers
        driver_cnt = 0
        for walker in people_without_cars:
            list_of_distributes[people_with_cars[driver_cnt]].append(walker)
            driver_cnt = (driver_cnt + 1) % len(people_with_cars)

    print("list of distributors", list_of_distributes.items())
    list_of_distributes = list(list_of_distributes.items())

    return render_template("car_distribution.html", list_of_distributes=list_of_distributes)

if __name__ == "__main__":
    app.run(debug=True)
