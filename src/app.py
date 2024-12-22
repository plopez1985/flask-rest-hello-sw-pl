"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Vehicle, Favorites
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

users_favorites = {
    1: {"planets": [], "vehicles": [], "characters": []},
    2: {"planets": [], "vehicles": [], "characters": []},
}

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_all_user():
    all_users = User.query.all()  # Consulta todos los usuarios
    result = [user.serialize() for user in all_users]  # Serializa los datos
    return jsonify(result), 200

@app.route('/people', methods=['GET'])
def get_all_people():
    all_people = Character.query.all()
    result = [people.serialize() for people in all_people]  # Serializa los datos
    return jsonify(result), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    all_planets = Planet.query.all()
    result = [planets.serialize() for planets in all_planets]  # Serializa los datos
    return jsonify(result), 200

@app.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    all_vehicles = Vehicle.query.all()
    result = [vehicles.serialize() for vehicles in all_vehicles]  # Serializa los datos
    return jsonify(result), 200

@app.route('/planet/<int:id>', methods=['GET'])
def get_one_planet(id):
    one_planet = Planet.query.get(id)
    if one_planet is None: 
        return "Planeta no encontrado", 400
    result = one_planet.serialize() 
    return jsonify(result), 200

@app.route('/vehicle/<int:id>', methods=['GET'])
def get_one_vehicle(id):
    one_vehicle = Vehicle.query.get(id)
    if one_vehicle is None: 
        return "Vehiculo no encontrado", 400
    result = one_vehicle.serialize() 
    return jsonify(result), 200

@app.route('/character/<int:id>', methods=['GET'])
def get_one_character(id):
    one_character = Character.query.get(id)
    if one_character is None: 
        return "Personaje no encontrado", 400
    result = one_character.serialize() 
    return jsonify(result), 200

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    # Obtener todos los favoritos del usuario específico
    favoritos = Favorites.query.filter_by(user_id=user_id).all()
    
    # Verificar si se encontraron favoritos para ese usuario
    if not favoritos:
        return jsonify({"error": "No se encontraron favoritos para este usuario"}), 404
    
    # Serializar los resultados
    result = [fav.serialize() for fav in favoritos]
    
    return jsonify(result), 200

# @app.route('/favorite/planet/<int:id>', methods=['POST'])
# def get_one_planet(id):
#     one_planet = Planet.query.get(id)
#     if one_planet is None: 
#         return "Planeta no encontrado", 400
#     result = one_planet.serialize() 
#     return jsonify(result), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')

    if user_id not in users_favorites:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if planet_id in users_favorites[user_id]["planets"]:
        return jsonify({"message": "El planeta ya está en los favoritos"}), 400

    users_favorites[user_id]["planets"].append(planet_id)
    return jsonify({"message": f"Planeta {planet_id} agregado a los favoritos"}), 200

@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['POST'])
def add_favorite_vehicle(vehicle_id):
    user_id = request.json.get('user_id')

    if user_id not in users_favorites:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if vehicle_id in users_favorites[user_id]["vehicles"]:
        return jsonify({"message": "El vehiculo ya está en los favoritos"}), 400

    users_favorites[user_id]["vehicles"].append(vehicle_id)
    return jsonify({"message": f"Vehiculo {vehicle_id} agregado a los favoritos"}), 200

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    user_id = request.json.get('user_id')

    if user_id not in users_favorites:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if character_id in users_favorites[user_id]["characters"]:
        return jsonify({"message": "El Personaje ya está en los favoritos"}), 400

    users_favorites[user_id]["characters"].append(character_id)
    return jsonify({"message": f"Personaje {character_id} agregado a los favoritos"}), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')

    if user_id not in users_favorites:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if planet_id not in users_favorites[user_id]["planets"]:
        return jsonify({"message": "El planeta no esta en los favoritos"}), 400

    users_favorites[user_id]["planets"].remove(planet_id)
    return jsonify({"message": f"Planeta {planet_id} eliminado de los favoritos"}), 200

@app.route('/favorite/vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_favorite_vehicle(vehicle_id):
    user_id = request.json.get('user_id')

    if user_id not in users_favorites:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if vehicle_id not in users_favorites[user_id]["vehicles"]:
        return jsonify({"message": "El vehiculo no esta en los favoritos"}), 400

    users_favorites[user_id]["vehicles"].remove(vehicle_id)
    return jsonify({"message": f"Vehiculo {vehicle_id} eliminado de los favoritos"}), 200

@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    user_id = request.json.get('user_id')

    if user_id not in users_favorites:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if character_id not in users_favorites[user_id]["characters"]:
        return jsonify({"message": "El personaje no esta en los favoritos"}), 400

    users_favorites[user_id]["characters"].remove(character_id)
    return jsonify({"message": f"Personaje {character_id} eliminado de los favoritos"}), 200


# @app.route('/users/favorites', methods=['GET'])
# def get_all_favorites():
#     all_favorites = Favorites.query.all()
#     result = [favorites.serialize() for favorites in all_favorites]  
#     return jsonify(result), 200

    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
