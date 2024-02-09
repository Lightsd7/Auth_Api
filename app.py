import json
from flask import Flask, request, jsonify
from models.user import User, Meal
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
#mysql://username:password@host:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:3306/db'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/login', methods=["POST"])
def login():
  data = request.get_json()
  username = data.get("username")
  password = data.get("password")

  if username and password:
    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
      login_user(user)
      return jsonify({"message": "Autenticação realizada com sucesso."})

  return jsonify({"message": "Credenciais inválidas."}), 400

@app.route('/logout', methods=['GET'])
@login_required
def logout():
  logout_user()
  return jsonify({"message":"Logout realizado com sucesso."})

@app.route('/user', methods=["POST"])
def create_user():
  data = request.get_json()
  username = data.get("username")
  password = data.get("password")

  if username and password:
    user = User.query.filter_by(username=username).first()
    if not user:
      new_user = User(username=username, password=password)
      db.session.add(new_user)
      db.session.commit()
      return jsonify({"message": "Usuário cadastrado com sucesso."})

  return jsonify({"message": "Dados inválidos."}), 400

@app.route("/user/<int:id_user>", methods=["GET"])
@login_required
def get_user(id_user):
  user = User.query.get(id_user)
  if user:
    return {"username": user.username}

  return jsonify({"message": "Usuário não encontrado."}), 404

@app.route('/user', methods=["GET"])
@login_required
def get_users():
  users = User.query.all()
  users_list = [{"id": user.id,"username": user.username} for user in users]
  return jsonify({
    "users": users_list,
    "total_tasks": len(users_list)
  })

@app.route("/user/<int:id_user>", methods=["PUT"])
@login_required
def update_user(id_user):
  user = User.query.get(id_user)

  data = request.get_json()

  if user and data.get("password"):
    user.password = data.get("password")
    db.session.commit()
    return jsonify({"message": f"Usuário {id_user} atualizado com sucesso."})

  return jsonify({"message": "Dados inválidos."}), 400

@app.route("/user/<int:id_user>", methods=["DELETE"])
@login_required
def delete_user(id_user):
  user = User.query.get(id_user)
  if id_user == current_user.id:
    return jsonify({"message": "Deleção não permitida."}), 403

  if user:
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Usuário deletado com sucesso."})

  return jsonify({"message": "Usuário não encontrado."}), 404

@app.route('/meal', methods=["POST"])
@login_required
def create_meal():
  data = request.get_json()
  name = data.get("name")
  description = data.get("description", "")
  date_time = data.get("date_time")
  is_on_diet = data.get("is_on_diet")

  # time_new = datetime.strptime(date_time, '%d/%m/%Y %H:%M:%s')

  if name and date_time:
    user_id = current_user.id
    new_meal = Meal(name=name, description=description, date_time=date_time, is_on_diet=is_on_diet, user_id=user_id)
    db.session.add(new_meal)
    db.session.commit()
    return jsonify({"message": "Refeição cadastrada com sucesso."})

  return jsonify({"message": "Dados inválidos."}), 400

@app.route('/meal/user/<int:id_user>', methods=["GET"])
@login_required
def get_meals_by_user(id_user):
  meals = Meal.query.filter(Meal.user_id==id_user).all()
  if meals:
    meals_list = [{"name": meal.name, "date_time": meal.date_time, "is_on_diet": meal.is_on_diet} for meal in meals]
    return jsonify({
      "meals": meals_list,
      "total_meals": len(meals_list)
    })

  return jsonify({"message": "Usuário não encontrado."}), 404

@app.route("/meal/<int:id_meal>", methods=["GET"])
@login_required
def get_meal(id_meal):
  meal = Meal.query.get(id_meal)
  if meal:
    return {"name": meal.name, "date_time": meal.date_time, "is_on_diet": meal.is_on_diet}

  return jsonify({"message": "Refeição não encontrada."}), 404

@app.route("/meal/<int:id_meal>", methods=["PUT"])
@login_required
def update_meal(id_meal):
  meal = Meal.query.get(id_meal)

  data = request.get_json()

  if meal:
    meal.name = data.get("name", meal.name)
    meal.description = data.get("description", meal.description)
    meal.date_time = data.get("date_time", meal.date_time)
    meal.is_on_diet = data.get("is_on_diet", meal.is_on_diet)
    db.session.commit()
    return jsonify({"message": f"Refeição {id_meal} atualizada com sucesso."})

  return jsonify({"message": "Dados inválidos."}), 400

@app.route("/meal/<int:id_meal>", methods=["DELETE"])
@login_required
def delete_meal(id_meal):
  meal = Meal.query.get(id_meal)
  if id_meal == current_user.id:
    return jsonify({"message": "Deleção não permitida."}), 403

  if meal:
    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": f"Refeição deletada com sucesso."})

  return jsonify({"message": "Refeição não encontrada."}), 404

if __name__ == "__main__":
  app.run(debug=True)