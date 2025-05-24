from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
create_access_token, get_jwt_identity, jwt_required
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///backwise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

# Bind all extensions here (before any model)
db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
CORS(app)

class User(db.Model):
    ...
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class StretchPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pain_point = db.Column(db.String(100))
    stretches = db.Column(db.Text)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class StretchPlanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StretchPlan

user_schema = UserSchema()
stretch_plan_schema = StretchPlanSchema()
stretch_plan_schemas = StretchPlanSchema(many=True)

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # <-- Add this after your app definition

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify(message="Missing username or password"), 400

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify(message="User registered"), 201

    except Exception as e:
        return jsonify(message="Error", error=str(e)), 500
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        token = create_access_token(identity=user.id)
        return jsonify(access_token=token), 200
    return jsonify(message='Invalid credentials'), 401

@app.route('/create_plan', methods=['POST'])
@jwt_required()
def create_plan():
    user_id = get_jwt_identity()
    pain_point = request.json['pain_point']
    stretches = request.json['stretches']
    plan = StretchPlan(user_id=user_id, pain_point=pain_point, stretches=stretches)
    db.session.add(plan)
    db.session.commit()
    return stretch_plan_schema.jsonify(plan), 201

@app.route('/my_plans', methods=['GET'])
@jwt_required()
def get_plans():
    user_id = get_jwt_identity()
    plans = StretchPlan.query.filter_by(user_id=user_id).all()
    return jsonify(stretch_plan_schemas.dump(plans)), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
