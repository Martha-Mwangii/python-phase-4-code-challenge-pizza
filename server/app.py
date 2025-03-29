#!/usr/bin/env python3

from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os
from models import db, Restaurant, RestaurantPizza, Pizza  # Import RestaurantPizza and Pizza

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# ✅ Get all restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address
    } for restaurant in restaurants]), 200

# ✅ Get a restaurant by ID (with restaurant_pizzas)
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)  # Fix for SQLAlchemy 2.0 warning
    if restaurant:
        return jsonify({
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients,
                    }
                }
                for rp in restaurant.restaurant_pizzas  # Assuming relationship is defined
            ]
        }), 200
    return jsonify({"error": "Restaurant not found"}), 404  # Return 404 if not found

@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def get_or_delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    if request.method == "DELETE":
        db.session.delete(restaurant)
        db.session.commit()
        return "", 204  # No Content response
    
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {"id": rp.id, "price": rp.price, "pizza_id": rp.pizza_id}
            for rp in restaurant.restaurant_pizzas
        ],
    })
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients
    } for pizza in pizzas]), 200

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    try:
        # Validate price range
        if not (1 <= data["price"] <= 30):
         return jsonify({"errors": ["validation errors"]}), 400


        new_restaurant_pizza = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"],
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        return jsonify({
            "id": new_restaurant_pizza.id,
            "price": new_restaurant_pizza.price,
            "pizza_id": new_restaurant_pizza.pizza_id,
            "restaurant_id": new_restaurant_pizza.restaurant_id,
            "pizza": {
                "id": new_restaurant_pizza.pizza.id,
                "name": new_restaurant_pizza.pizza.name,
                "ingredients": new_restaurant_pizza.pizza.ingredients
            },
            "restaurant": {
                "id": new_restaurant_pizza.restaurant.id,
                "name": new_restaurant_pizza.restaurant.name,
                "address": new_restaurant_pizza.restaurant.address
            }
        }), 201

    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400  # ✅ Fix: Ensure "errors" key exists





if __name__ == "__main__":
    app.run(port=5555, debug=True)



'''from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)'''
