Voici toutes les étapes nécessaires pour configurer le projet Flask avec Docker, MySQL et l'initialisation automatisée de la base de données. Les mots de passe des utilisateurs seront encodés en base64.

### Étape 1 : Créer l'arborescence du projet

Créez la structure de dossiers suivante :

```
flask_mysql_crud/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── templates/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── products.html
│   │   └── home.html
│   └── static/
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
├── init-db.sql
└── docker-compose.yml
```

### Étape 2 : Configuration des fichiers du projet

#### 1. Fichier `__init__.py`

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@db/flask_app'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

from app import routes
```

#### 2. Fichier `models.py`

```python
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
```

#### 3. Fichier `routes.py`

```python
from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.models import User, Product
from flask_login import login_user, current_user, logout_user, login_required
import base64

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
        if user and base64.b64decode(user.password.encode()).decode() == password:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
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
```

#### 4. Fichiers HTML (templates)

##### `login.html`

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Login</title>
</head>
<body>
    <h2>Login</h2>
    <form method="POST">
        <input type="email" name="email" placeholder="Email">
        <input type="password" name="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
</body>
</html>
```

##### `register.html`

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Register</title>
</head>
<body>
    <h2>Register</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="Username">
        <input type="email" name="email" placeholder="Email">
        <input type="password" name="password" placeholder="Password">
        <button type="submit">Register</button>
    </form>
</body>
</html>
```

##### `products.html`

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Products</title>
</head>
<body>
    <h2>Products</h2>
    <form method="POST">
        <input type="text" name="name" placeholder="Product Name">
        <input type="text" name="description" placeholder="Product Description">
        <input type="number" step="0.01" name="price" placeholder="Price">
        <button type="submit">Add Product</button>
    </form>
    <ul>
        {% for product in products %}
        <li>{{ product.name }} - {{ product.description }} - ${{ product.price }}</li>
        {% endfor %}
    </ul>
</body>
</html>
```

##### `home.html`

```html
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Home</title>
</head>
<body>
    <h2>Home</h2>
    <a href="{{ url_for('login') }}">Login</a>
    <a href="{{ url_for('register') }}">Register</a>
    <a href="{{ url_for('products') }}">Products</a>
    <a href="{{ url_for('logout') }}">Logout</a>
</body>
</html>
```

#### 5. Fichier `Dockerfile`

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0"]
```

#### 6. Fichier `entrypoint.sh`

```bash
#!/bin/bash

flask db init
flask db migrate -m "Initial migration."
flask db upgrade

exec "$@"
```

Rendez le fichier exécutable :

```bash
chmod +x entrypoint.sh
```

#### 7. Fichier `requirements.txt`

```
Flask
Flask-SQLAlchemy
Flask-Bcrypt
Flask-Login
Flask-Migrate
PyMySQL
```

#### 8. Fichier `init-db.sql`

```sql
USE flask_app;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(200) NOT NULL,
    price FLOAT NOT NULL,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO user (username, email, password) VALUES
('user1', 'user1@example.com', 'dXNlcjFwYXNz'),  -- password: user1pass
('user2', 'user2@example.com', 'dXNlcjJwYXNz'),  -- password: user2pass
('user3', 'user3@example.com', 'dXNlcjNwYXNz');  -- password: user3pass
```

#### 9. Fichier `docker-compose.yml`

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      FLASK_APP: app
      FLASK_ENV: development
    depends_on:
      - db

  db:
    image: mysql:5

.7
    restart: always
    environment:
      MYSQL_DATABASE: flask_app
      MYSQL_USER: root
      MYSQL_PASSWORD: password
      MYSQL_ROOT_PASSWORD: password
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

volumes:
  mysql-data:
```

### Étape 3 : Construire et démarrer les conteneurs Docker

Rebuild et démarrez les conteneurs Docker :

```bash
docker-compose up --build
```

### Conclusion

Cette configuration va construire et démarrer les conteneurs Docker pour une application Flask et une base de données MySQL. Lors du démarrage, les utilisateurs spécifiés dans le fichier `init-db.sql` seront insérés automatiquement dans la base de données, et la base de données sera initialisée grâce à `Flask-Migrate`. Les mots de passe des utilisateurs sont encodés en base64 pour simplifier les tests de sécurité.