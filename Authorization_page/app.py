from flask import Flask, jsonify, request, render_template, url_for, redirect, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
from flask_mysqldb import MySQL  

app = Flask(__name__)
mysql = MySQL(app)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MYSQL_HOST'] = 'localhost'  
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Xplx@2104'
app.config['MYSQL_DB'] = 'flasksql'


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email already in use. Please choose a different one.')

class loginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    

@app.route('/')
def Home():
    return render_template('index.html')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.username.data
        email = form.email.data
        password = form.password.data

        # Check if email already exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Email already in use
            return render_template('register.html', form=form, message="Email already exists.")
        
        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Store user in the database
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Check if email already exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        cursor.close()
        
        if existing_user and bcrypt.checkpw(password.encode('utf-8'), existing_user[3].encode('utf-8')):
            session['user_id'] = existing_user[0]
            return redirect(url_for('dash'))
        else:
            flash("Invalid email or password.","danger")
            return redirect(url_for('login'))

        
    return render_template('login.html', form=form)


@app.route('/dashboard')
def dash():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()  # Fetch the first (and only) user from the query
        cursor.close()

        if user:
            # Instead of using index-based access, use field names
            return render_template('dashboard.html', user=user)

    flash('You must be logged in to view the dashboard.', 'warning')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)  
    flash("You have been logged out.")  
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

