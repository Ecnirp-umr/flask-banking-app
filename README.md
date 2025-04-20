# flask-banking-app

This project is a simple **Flask-based RESTful API** for managing banking operations such as customer creation, balance check, deposits, withdrawals, and admin-level actions like editing user info or deleting accounts.

## 📌 Features

- Create customer accounts (user or admin)
- Check balance by customer ID
- Deposit and withdraw money
- Admin-only:
  - View senior citizens (60+ years)
  - View customers by city
  - Change customer's DOB and name
  - Delete a user account

## 🛠️ Technologies Used

- Python 3
- Flask
- SQLAlchemy
- SQLite
- Postman



📝 Notes

DOB format: YYYY-MM-DD

SQLite database will be created as customers.db in the project folder

Admin access is required for certain sensitive operations
