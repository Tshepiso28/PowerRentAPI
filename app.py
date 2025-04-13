from flask import Flask, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager, create_access_token
from models import User
from database import db, init_db
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

init_db(app)

jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = '1017300'


with app.app_context():
    db.create_all()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if role not in ['renter', 'lender']:
        return jsonify({"error": "Invalid role"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(full_name=full_name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        dashboard_url = f"/dashboard/{user.role}"
        return jsonify({"message": "Login successful", "dashboard": dashboard_url, "token": access_token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/dashboard/<role>', methods=['GET'])
@jwt_required()
def dashboard(role):
    identity = get_jwt_identity()
    if identity["role"] !=role:
        return jsonify({"error": "Unauthorized for this dashboard"}), 403
    return jsonify({"message": f"Welcome to the {role} dashboard!"})

if __name__ == '__main__':
    app.run(debug=True)
