import json
import datetime
class Orders():
    orders = []

    def __init__(self):
        try:
            with open('orders.json') as file:
                self.orders = json.loads(file.read())
                print("Checked existance of orders")
        except OSError as ex:
            print("File doesn't exist, creating new orders file")
            with open('orders.json', 'w') as file:
                file.write(json.dumps(self.orders))

    def save_orders(self):
        with open('orders.json', 'w') as f:
            f.write(json.dumps(self.orders))
