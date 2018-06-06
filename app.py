# create by : eepis-fire 
# !/usr/bin/python3

# how to run flask without restart :
# a) export FLASK_APP=app.py
# b) export FLASK_DEBUG=1
# c) python3 -m flask run

# tuorial link :
# https://www.tutorialspoint.com/flask/flask_templates.htm
# https://stackoverflow.com/questions/12867140/python-mysqldb-get-the-result-of-fetchall-in-a-list?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
# http://www.guguncube.com/1656/python-image-similarity-comparison-using-several-techniques

from flask import Flask, render_template, request
# from skimage.measure import structural_similarity as ssim
from PIL import Image, ImageChops
from functools import reduce
from operator import itemgetter
import pymysql
import math, operator
import numpy as np
from collections import defaultdict
# import cv2

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


@app.route('/compare-histogram', methods=['GET', 'POST'])
def compare_histogram():
    if request.method == 'GET':
        original    = request.args.get('original')
        new_data    = []
        sort_data   = []
        url_data    = []
        red1=0
        red2=0
        green1=0
        green2=0
        blue1=0
        blue2=0

        cursor.execute("SELECT url FROM image_data WHERE id >= 90")
        data = [item[0] for item in cursor.fetchall()]
        
        img_ori     = Image.open('images/'+str(original))
        image1      = get_resize(img_ori)
        img1        = image1.convert('RGB').histogram()

        # red1         = img1[0:255]
        # green1       = img1[256:511]
        # blue1        = img1[512:768]
        # print(str(img1[0:255]))

        print("JUMLAH HISTOGRAM : "+str(len(img1)))
        
        for url in data:
            img         = Image.open('images/'+url)
            image2      = get_resize(img)
            img2        = image2.convert('RGB').histogram()

            # compare1    = math.sqrt(reduce(operator.add, list(map(lambda a,b: (a-b)**2, img1[0:255], img2[0:255]))))

            # dinamis bin
            sum_bin = 64
            bins    = {}
            result  = 0 
            var_a   = 0
            tmp     = 768 / sum_bin
            var_b   = tmp - 1
            for x in range(0,sum_bin):
                # print(str(var_a)+"-"+str(var_b))
                print("VARIABEL BIN : "+str(var_a)+" dan "+str(var_b))
                bins[x]    = math.sqrt(reduce(operator.add, list(map(lambda a,b: (a-b)**2, img1[int(var_a):int(var_b)], img2[int(var_a):int(var_b)]))))
                var_a += tmp
                var_b = (var_a+tmp) - 1

            for y in range(0,sum_bin):
                result += bins[y]

            # print(str(compare))
            new_data.append([result, url])

        sort_data = sorted(new_data)

        # print(str(sort_data))

        for x in range(0,10):
            url_data.append(sort_data[x][1])

        return render_template('result-compare.html', data=url_data)

    elif request.method =='POST':
        return render_template('result.html')

    else:
        ('<center>404 Not Found</center>')


@app.route('/compare-greyscale', methods=['GET', 'POST'])
def image_similarity_greyscale_hash_code():
    # source: http://blog.safariflow.com/2013/11/26/image-hashing-with-python/
    if request.method == 'GET':
        original    = request.args.get('original')
        new_data    = []
        sort_data   = []
        url_data    = []

        cursor.execute("SELECT url FROM image_data WHERE id >= 90")
        data = [item[0] for item in cursor.fetchall()]
        
        img_ori = Image.open('images/'+str(original))
        image1  = get_thumbnail(img_ori, greyscale=True)
        # img1        = image1.histogram()
        
        for url in data:
            img     = Image.open('images/'+url)
            image2  = get_thumbnail(img, greyscale=True)
            # img2        = image2.histogram()

            code1 = image_pixel_hash_code(image1)
            code2 = image_pixel_hash_code(image2)
            # use hamming distance to compare hashes
            compare = hamming_distance(code1,code2)

            # compare = math.sqrt(reduce(operator.add, list(map(lambda a,b: (a-b)**2, img1, img2)))/len(img1))

            new_data.append([compare, url])

        sort_data = sorted(new_data)

        print(str(sort_data))

        for x in range(0,len(sort_data)):
            url_data.append(sort_data[x][1])

        # print(str(url_data))

        return render_template('result.html', data=url_data)

    elif request.method =='POST':
        return render_template('result.html')

    else:
        ('<center>404 Not Found</center>')


def image_pixel_hash_code(image):
    pixels = list(image.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join(map(lambda pixel: '1' if pixel < avg else '0', pixels))  # '00010100...'
    hexadecimal = int(bits, 2).__format__('016x').upper()
    return hexadecimal
 

def hamming_distance(s1, s2):
    len1, len2= len(s1),len(s2)
    if len1!=len2: 
        "hamming distance works only for string of the same length, so i'll chop the longest sequence"
        if len1>len2:
            s1=s1[:-(len1-len2)]
        else:
            s2=s2[:-(len2-len1)]
    assert len(s1) == len(s2)
    return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])


def get_resize(image, size=(256,256), stretch_to_fit=False, greyscale=False):
    " get a smaller version of the image - makes comparison much faster/easier"
    if not stretch_to_fit:
        image.thumbnail(size, Image.ANTIALIAS)
    else:
        image = image.resize(size); # for faster computation
    if greyscale:
        image = image.convert("L")  # Convert it to grayscale.
    return image
 
    
# run app
if __name__ == "__main__":
    app.run()