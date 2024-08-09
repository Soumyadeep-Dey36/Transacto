from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import socket
import psutil
import uuid  # Importing the uuid module for get_mac_address function
from smtplib import *
import datetime as dt

app = Flask(__name__)
app.config.from_object('config.Config')

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
def send_email(client_email_id, mac_address, flag):
    host_email_id = "kapxdesanta36@gmail.com"
    password = app.config['PASS']
    
    present_time = dt.datetime.now()
    
    with SMTP(host="smtp.gmail.com",port=587) as connection:
        connection.starttls()
        connection.login(user=host_email_id, password=password)
        # Email content
        subject = "Failed transaction attempt!"
        if flag == True:
            body = f"There has been a failed transaction attempt from your card at {present_time}, due to an unknown device having MAC address {mac_address}."
        else:
            body = f"There has been a failed transaction attempt from your card at {present_time}, due to incorrect password through a device having MAC address {mac_address}."
        message = f"Subject: {subject}\n\n{body}"
        connection.sendmail(from_addr=host_email_id, to_addrs=client_email_id, msg=message)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    email_id = request.form['email_id']
    card_no = request.form['card_no']
    password = request.form['password']
    mac_address = get_mac_address('Wi-Fi')

    conn = get_db_connection()
    if conn is None:
        flash('Database connection error. Please try again later.', 'danger')
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor()
        # Use parameterized query to avoid SQL injection
        cursor.execute('''INSERT INTO user_info (email_id, card_no, pw, mac_address) VALUES (%s, %s, %s, %s)
        ''', (email_id, card_no, password, mac_address))
        conn.commit()
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        # flash('An error occurred while registering. Please try again.', 'danger')
        print("An error occurred while registering. Please try again")
        
    else:
        # flash('Registration successful!', 'success')
        print("Registration successful")
        cursor.close()
        
    finally:
        conn.close()

    return redirect(url_for('transaction'))

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if request.method == 'POST':
        card_no = request.form['card_no']
        password = request.form['password']
        mac_address = get_mac_address('Wi-Fi')

        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('transaction'))

        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_info WHERE card_no = %s', (card_no,))
            user = cursor.fetchone()

            if user:
                stored_password = user[2]  # Adjust index based on your table schema
                user_email = user[0]
                if stored_password == password:  # Direct comparison for plain text
                    allowed_mac = user[3]
                    print(f"Allowed MAC address : {allowed_mac}")
                    print(f"Current MAC address : {mac_address}")
                    if user[3] == mac_address:  # Adjust index based on your table schema
                        flash('Transaction Successful!', 'success')
                        print("Transaction Successful")
                    else:
                        send_email(user_email, mac_address, True)
                        flash('Transaction Failed: Invalid MAC address.', 'danger')
                        print("Transaction Failed: Invalid MAC address")
                else:
                    send_email(user_email, mac_address, False)
                    flash('Invalid Password.', 'danger')
                    print("Invalid Password")
            else:
                flash('Invalid Card No', 'danger')
                print("Invalid Card No")

        except mysql.connector.Error as err:
            print(f"Database error: {err}")
            flash('An error occurred while processing the transaction. Please try again.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('transaction.html')

def get_mac_address(interface_name):
    addrs = psutil.net_if_addrs()
    if interface_name in addrs:
        for addr in addrs[interface_name]:
            if addr.family == psutil.AF_LINK:
                return addr.address

if __name__ == '__main__':
    app.run(debug=True)
