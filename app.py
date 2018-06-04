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
from PIL import Image, ImageChops
from functools import reduce
from operator import itemgetter
import pymysql
import math, operator

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
        cursor.execute("SELECT url FROM image_data WHERE id IN (SELECT DISTINCT id_image_data FROM keyword_image WHERE keyword LIKE '%"+keyword+"%')")
        # data = cursor.fetchall()

        data = [item[0] for item in cursor.fetchall()]
        sum_data = len(data)

        # print('URL IMAGE : '+str(data))        

        return render_template('result.html', keyword=keyword, data=data, sum_data=sum_data)

        db.close()

    else:
        return('<center>404 Not Found</center>')


@app.route('/compare', methods=['GET', 'POST'])
def compare():
    if request.method == 'GET':
        original = request.args.get('original')
        red     = []
        red.append([])
        green   = []
        green.append([])
        blue    = []
        blue.append([])
        new_data    = []
        # new_data.append([])
        sort_data = []
        url_data = []

        cursor.execute("SELECT url FROM image_data WHERE id >= 90")
        data = [item[0] for item in cursor.fetchall()]
        
        img_ori     = Image.open('images/'+str(original)).convert('RGB').histogram()
        
        for url in data:
            img             = Image.open('images/'+url)
            width, height   = img.size
            rgb_im          = img.convert('RGB').histogram()

            # for i in range(0,width):
            #     for j in range(0,height):
            #         pixel_im    = rgb_im.getpixel((i,j))
            #         red_im      = pixel_im[0]

            #         red         += red_im

            # image1  = Image.open('images/'+'Italy.png').histogram()
            # image2  = Image.open('images/'+'India.png').histogram()

            compare = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, img_ori, rgb_im))/len(img_ori))
            # compare2 = math.sqrt(reduce(operator.add, map(lambda a,b: (a-b)**2, image1, image1))/len(image1))

            # print(str(url)+' : '+str(abs(compare)))

            new_data.append([compare, url])

            # histogram   = convert.histogram()
            # # r, g, b       = convert.split()
            # h1          = histogram[0:256]
            # h2          = histogram[256:512]
            # h3          = histogram[512:768]

            # for i in range(0, 256):
            #     red += h1[i]

            # for i in range(0, 256):
            #     green += h2[i]

            # for i in range(0, 256):
            #     blue += h3[i]

            # print(url+' : '+str(len(histogram)))
            # print(url+' : '+str(len(r.histogram()))+str(len(g.histogram()))+str(len(b.histogram())))
            # print(url+' : '+'RGB : '+str(red)+','+str(green)+','+str(blue))

        # print(str(new_data))
        sort_data = sorted(new_data)

        for x in range(0,len(sort_data)):
            url_data.append(sort_data[x][1])

        print(str(url_data))
        
        # sort = sorted(new_data, key=itemgetter(1))

        return render_template('result.html', data=url_data)

    elif request.method =='POST':
        return render_template('result.html')

    else:
        ('<center>404 Not Found</center>')
    
# run app
if __name__ == "__main__":
    app.run()