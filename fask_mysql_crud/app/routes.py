from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import User, Product
from flask_login import login_user, current_user, logout_user, login_required
import base64
import logging

logging.basicConfig(level=logging.DEBUG)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        encoded_password = base64.b64encode(password.encode()).decode('utf-8')
        user = User(username=username, email=email, password=encoded_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            decoded_password = base64.b64decode(user.password.encode()).decode()
            if decoded_password == password:
                login_user(user)
                next_page = request.args.get('next')
                flash('Login Successful', 'success')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Incorrect password.', 'danger')
        else:
            flash('Login Unsuccessful. User not found.', 'danger')
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/products", methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        product = Product(name=name, description=description, price=price)
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')
