from flask import Flask , render_template, request
from flask_sqlalchemy import SQLAlchemy
import orders
from datetime import datetime, date, time

from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
db = SQLAlchemy(app)
requests = orders.Orders()

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    order = db.Column(db.String(200), nullable=False)
    mode = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Order %r>' % self.id

@app.route("/today_orders")
def return_todays_orders():
    start_of_today = datetime.combine(date.today(), time.min)
    end_of_today = datetime.combine(date.today(), time.max)

    orders = Orders.query.filter(
        Orders.date_created >= start_of_today,
        Orders.date_created <= end_of_today
    ).order_by(Orders.date_created).all()

    return render_template("today_orders.html", orders=orders)

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

@app.route('/hello')
def hello():
    return 'Hello, World'

if __name__ == "__main__":
    app.run(debug=True)




