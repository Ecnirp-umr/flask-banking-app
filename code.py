from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)  

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Welcome to the banking service"

@app.route('/create_customer', methods=['POST'])
def create_customer():
    try:
        data = request.json

        required_keys = {"name", "dob", "city", "account_number", "balance", "password", "role"}
        if not required_keys.issubset(data.keys()):
            return jsonify({"error": "Invalid request, check your input keys."}), 400

        if data['role'] not in ['admin', 'user']:
            return jsonify({"error": "Invalid role. Must be 'admin' or 'user'."}), 400

        new_customer = Customer(
            name=data['name'],
            dob=datetime.strptime(data['dob'], "%Y-%m-%d").date(),
            city=data['city'],
            account_number=data['account_number'],
            balance=data['balance'],
            password=data['password'],
            role=data['role']
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({"message": "Customer created successfully!"})
    except Exception as e:
        return jsonify({"error": "Something went wrong.", "details": str(e)}), 500

@app.route('/balance/<int:customer_id>', methods=['GET'])
def get_balance(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify({"balance": customer.balance})
    except Exception:
        return jsonify({"error": "Invalid endpoint or incorrect URL."}), 400

@app.route('/deposit/<int:customer_id>', methods=['POST'])
def deposit_money(customer_id):
    try:
        data = request.json
        if 'amount' not in data:
            return jsonify({"error": "Invalid request, check your input keys."}), 400
       
        amount = data.get('amount')
        if not isinstance(amount, (int, float)):
            return jsonify({"error": "Invalid request, 'amount' must be a number."}), 400
       
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        customer.balance += amount
        db.session.commit()
        return jsonify({"message": "Deposit successful", "New Balance": customer.balance})
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500

@app.route('/withdraw/<int:customer_id>', methods=['POST'])
def withdraw_money(customer_id):
    try:
        data = request.json
        if 'amount' not in data:
            return jsonify({"error": "Invalid request, check your input keys."}), 400
       
        amount = data.get('amount')
        if amount is None or not isinstance(amount, (int, float)):
            return jsonify({"error": "Invalid request, 'amount' must be a number."}), 400

        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        if amount > customer.balance:
            return jsonify({"error": "Insufficient funds"}), 400

        customer.balance -= amount
        db.session.commit()
        return jsonify({"message": "Withdrawal successful", "New Balance": customer.balance})
    except Exception as e:
        return jsonify({"error": "Something went wrong.", "details": str(e)}), 500

@app.route('/senior_citizens', methods=['GET'])
def get_senior_citizens():
    try:
        admin_id = request.args.get('admin_id')
        admin = Customer.query.get(admin_id)
       
        if not admin or admin.role != 'admin':
            return jsonify({"error": "Access denied. Only admins can fetch senior citizens data."}), 403
       
        senior_cutoff = date.today().replace(year=date.today().year - 60)
        senior_customers = Customer.query.filter(Customer.dob <= senior_cutoff).all()
       
        return jsonify({"Senior Citizens": [{
            "CustomerId": c.id,
            "CustomerName": c.name,
            "DOB": c.dob.strftime('%Y-%m-%d'),
            "City": c.city,
            "AccountNumber": c.account_number
        } for c in senior_customers]})
    except Exception:
        return jsonify({"error": "Invalid request or unauthorized access."}), 400

@app.route('/customers/city/<string:city>', methods=['GET'])
def get_customers_by_city(city):
    try:
        admin_id = request.args.get('admin_id')
        admin = Customer.query.get(admin_id)
       
        if not admin or admin.role != 'admin':
            return jsonify({"error": "Access denied. Only admins can fetch city-based customer data."}), 403
       
        city_customers = Customer.query.filter_by(city=city).all()
        return jsonify({"Customers in City": [{
            "CustomerId": c.id,
            "CustomerName": c.name,
            "DOB": c.dob.strftime('%Y-%m-%d'),
            "City": c.city,
            "AccountNumber": c.account_number
        } for c in city_customers]})
    except Exception:
        return jsonify({"error": "Invalid request or unauthorized access."}), 400

@app.route('/admin/change_dob/<int:user_id>', methods=['PUT'])
def change_dob(user_id):
    try:
        data = request.json

        if 'admin_id' not in data or 'dob' not in data:
            return jsonify({"error": "Invalid request, check your input keys."}), 400
           
        admin_id = data.get('admin_id')
        new_dob = data.get('dob')
       
        admin = Customer.query.get(admin_id)
        if not admin or admin.role != 'admin':
            return jsonify({"error": "Access denied. Only admins can change DOB."}), 403
       
        user = Customer.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
       
        user.dob = datetime.strptime(new_dob, "%Y-%m-%d").date()
        db.session.commit()
        return jsonify({"message": "DOB updated successfully."})
    except Exception as e:
        return jsonify({"error": "Something went wrong.", "details": str(e)}), 500

@app.route('/admin/change_name/<int:user_id>', methods=['PUT'])
def change_name(user_id):
    try:
        data = request.json
        if 'admin_id' not in data or 'name' not in data:
            return jsonify({"error": "Invalid request, check your input keys."}), 400

        admin_id = data.get('admin_id')
        new_name = data.get('name')
       
        admin = Customer.query.get(admin_id)
        if not admin or admin.role != 'admin':
            return jsonify({"error": "Access denied. Only admins can change names."}), 403
       
        user = Customer.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
       
        user.name = new_name
        db.session.commit()
        return jsonify({"message": "Name updated successfully."})
    except Exception as e:
        return jsonify({"error": "Something went wrong.", "details": str(e)}), 500
   
@app.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        data = request.json
        if 'admin_id' not in data:
            return jsonify({"error": "Invalid request, check your input keys."}), 400
       
        admin_id = data.get('admin_id')
       
        admin = Customer.query.get(admin_id)
        if not admin or admin.role != 'admin':
            return jsonify({"error": "Access denied. Only admins can delete users."}), 403
       
        user = Customer.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
       
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted successfully."})
    except Exception as e:
        return jsonify({"error": "Something went wrong.", "details": str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "This URL does not exist"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
