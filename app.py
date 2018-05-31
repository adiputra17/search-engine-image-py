# create by : eepis-fire 
# !/usr/bin/python3

# how to run flask without restart :
# a) export FLASK_APP=app.py
# b) export FLASK_DEBUG=1
# c) python3 -m flask run

# tuorial link :
# https://www.tutorialspoint.com/flask/flask_templates.htm
# https://stackoverflow.com/questions/12867140/python-mysqldb-get-the-result-of-fetchall-in-a-list?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

from flask import Flask, render_template, request
from PIL import Image
import pymysql

app = Flask(__name__, static_url_path = "/images", static_folder = "images")

# databse mysql
db      = pymysql.connect("localhost","root","","python3" )
cursor  = db.cursor()

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('result.html')

    elif request.method =='POST':
        keyword = request.form['keyword']

        # cursor.execute("SELECT DISTINCT id_image_data FROM keyword_image WHERE keyword LIKE '%"+keyword+"%'")
        cursor.execute("SELECT url FROM image_data WHERE id IN (SELECT DISTINCT id_image_data FROM keyword_image WHERE keyword LIKE '%["+keyword+"]%')")
        # data = cursor.fetchall()

        data = [item[0] for item in cursor.fetchall()]
        sum_data = len(data)

        print('URL IMAGE : '+str(data))

        return render_template('result.html', keyword=keyword, data=data, sum_data=sum_data)

        db.close()

    else:
        return('<center>404 Not Found</center>')


# run app
if __name__ == "__main__":
    app.run()