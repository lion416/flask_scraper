from flask import Flask, request, render_template, json, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField, validators
from wtforms.validators import InputRequired, Email, Length
from selenium import webdriver
import pyodbc
import time
import json
import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
Bootstrap(app)
   
conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb)};DBQ=F:/project/Webscrapper/db.mdb;')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(),Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(),Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
   # email = StringField('Email', validators=[InputRequired(),Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(),Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8, max=80)])
    fname = StringField('First Name', validators=[InputRequired(),Length(min=3, max=15)])
    lname = StringField('Last Name', validators=[InputRequired(),Length(min=3, max=15)])
    pname = StringField('Project Name', validators=[InputRequired(),Length(min=3, max=15)])

global whichTagList
@app.route('/')
def index():
    return "home page"

loginId = 0;
currentDirectory = "";

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * from Users WHERE Username=? AND Password=?',(form.username.data, form.password.data));
            row = cursor.fetchone()
            if row == None:
                return render_template('loginfailed.html')
            else:
                while row is not None:
                    global loginId
                    loginId = row[0];
                    row = cursor.fetchone()
                return render_template('main.html') 
        except Error as e:
            print(e)
        # finally:
        #     conn.commit();
        #     cursor.close();
        #     conn.close();
        

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        cursor = conn.cursor()
        #save_command = "INSERT INTO Users(Username) VALUES ('+form.username.data+')";
        cursor.execute("INSERT INTO Users(Username,Password,FirstName,LastName,ProjectName) VALUES (?,?,?,?,?)", (form.username.data, form.password.data, form.fname.data, form.lname.data, form.pname.data));
        conn.commit();
        #cursor.close();
        #conn.close();

    
    return render_template('signup.html', form=form)

text = 'd'
@app.route('/main', methods=['GET','POST'])
def main():
    # get the text from the textarea when scrap button is clicked
    text = request.form['text']
    text = text.splitlines()    #this is array of each line
    elementDt = ''
    elementName = list()
    data = list()

    driver = webdriver.Chrome('./chromedriver')
    for eachline in text:
        
        if eachline.split()[0] == "navigate":
            time.sleep(1)
            driver.get(eachline.split()[1])
            driver.save_screenshot('./screenshots/screenshot.png')
        elif eachline.split()[0] == "input":
            time.sleep(1)
                # driver.find_element_by_xpath(eachline.split()[1]).send_keys(eachline.split()[2])
                # driver.save_screenshot('./screenshots/screenshot1.png')
            elementDt = driver.find_elements_by_tag_name("input")
            for element in elementDt:
                elementName.append(element.get_attribute('name'))

            i = 0
            while i < len(elementDt):
                data.append((elementName[i],elementDt[i]))
                #data.append(elementDt[i])
                i+=1

        # elif eachline.split()[0] == "click":
        #     time.sleep(1)
        #     print(eachline.split()[1])
        #     clickBtn = driver.find_elements_by_tag_name("button")
        #     clickA = driver.find_elements_by_tag_name("a")
        #     clickInput = driver.find_elements_by_tag_name("input")

            # driver.find_element_by_xpath(eachline.split()[1]).click()
            # driver.save_screenshot('screenshot2.png')

    #time.sleep(1)
    #driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input').send_keys("car")
    # time.sleep(5)
    #driver.find_element_by_xpath('//*[@id="tsf"]/div[2]/div[1]/div[3]/center/input[1]').click()
    #time.sleep(1)


    return render_template('main.html', data = data)

driver = None;
elementDt = '';
elementName = list();
elementData = list();
textlist = [];



def getElementInfo(elementDt, type):
    elementName = list();
    elementData = list();
    elementValue = list();
    for element in elementDt:
        elementName.append(element.get_attribute('name'))
        # elementData.append("".join(ascii(element)))
        elementData.append(element.get_attribute('outerHTML'))
        elementValue.append(element.get_attribute('innerHTML'))
    print("all input:", elementDt);
    print("converted string", " ".join(ascii(i) for i in(elementDt)));
    print(elementName)
    print(elementData)
    return jsonify(name=elementName, data=elementData, value=elementValue);

@app.route('/scrape', methods=['POST'])
def scrape():
    global loginId
    cursor = conn.cursor()

    text = request.form['text']
    global textlist
    
    textlist = text.splitlines()    #this is array of each line
    print("before:", textlist)
    textlist = list(filter(None, textlist))
    print("after:", textlist)

    
    data = list()
    global driver
    driver = webdriver.Chrome('./chromedriver')
    for i, eachline in enumerate(textlist):
        if eachline.split()[0] == "navigate":
            time.sleep(1)
            driver.get(eachline.split()[1])
            
            global currentDirectory
            currentDirectory = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S");
            os.mkdir('./screenshots/'+str(currentDirectory));
            driver.save_screenshot('./screenshots/'+str(currentDirectory)+'/screenshot0.png')

            cursor.execute("INSERT INTO Images(directory,userid,count) VALUES (?,?,?)", (currentDirectory, loginId, 1));
            conn.commit();
        elif eachline.split()[0] == "input":
            time.sleep(1)
                # driver.find_element_by_xpath(eachline.split()[1]).send_keys(eachline.split()[2])
                # driver.save_screenshot('./screenshots/screenshot1.png')
            elementDt = driver.find_elements_by_tag_name("input")
            print("detected element:", elementDt)
            return getElementInfo(elementDt, "input");
            

        elif eachline.split()[0] == "click":
            time.sleep(1)
            elementDt = driver.find_elements_by_tag_name("a")
            elementDt += driver.find_elements_by_tag_name("button")
            elementDt += driver.find_elements_by_tag_name("input")
            return getElementInfo(elementDt, "click");



@app.route('/receiver', methods=['GET','POST'])
def receiver():
    # selectedName = request.form['name']
    # selectedValue = request.form['value']
    # selectedData = request.form['data']
    index = request.form['num']
    selectedindex = request.form['index']

    global textlist
    global driver
    global loginId
    global currentDirectory

    # print("selectedName:", selectedName);
    print("textlist:", textlist);
    print("index:", index);

    
    actionflag = 0;
    for i, eachline in enumerate(textlist):
        print("loop index:", i)
        print("target index", index)
        if i == int(index):
            print("progress index", index);
            
            if eachline.split()[0] == "input":
                elementDt = driver.find_elements_by_tag_name("input");
                targetEle = elementDt[int(selectedindex)];
                print("here input:", eachline.split()[1])
                time.sleep(1);
                targetEle.send_keys(eachline.split()[1]);
                actionflag = 1;
                time.sleep(1);
            elif eachline.split()[0] == "click":
                elementDt = driver.find_elements_by_tag_name("a")
                elementDt += driver.find_elements_by_tag_name("button")
                elementDt += driver.find_elements_by_tag_name("input")
                targetEle = elementDt[int(selectedindex)];
                targetEle.click()

    time.sleep(1);
    cursor = conn.cursor()
    cursor.execute('UPDATE Images SET count=? WHERE directory=? AND userid=?', (int(index)+1, currentDirectory, loginId));
    conn.commit();
    driver.save_screenshot('./screenshots/'+str(currentDirectory)+'/screenshot'+str(index)+'.png')
    if int(index)+1 == len(textlist):
        return "done"

    for i, eachline in enumerate(textlist):
        if i == int(index)+1:
            if eachline.split()[0] == "input":
                time.sleep(1)
                elementDt = driver.find_elements_by_tag_name("input")
                return getElementInfo(elementDt, "input")
            elif eachline.split()[0] == "click":
                elementDt = driver.find_elements_by_tag_name("a")
                elementDt += driver.find_elements_by_tag_name("button")
                elementDt += driver.find_elements_by_tag_name("input")
                return getElementInfo(elementDt, "click")
    return "notdone"
    
@app.route('/userinfo', methods=['GET','POST'])
def userinfo(): 
    username = "";
    totalcnt = 0;
    directorycnt = 0;   
    try:
        global loginId
        cursor = conn.cursor()
        cursor.execute('SELECT * from Users WHERE id=?', (loginId));
        row = cursor.fetchone()
        if row == None:
            return "failed"
        else:
            while row is not None:
                username = row[1];
                
                cursor1 = conn.cursor()
                cursor1.execute('SELECT * from Images WHERE userid=?',(str(loginId)));
                imagerow = cursor1.fetchone()
                if imagerow == None:
                    directorycnt = 0;
                    totalcnt = 0;
                else:
                    directorycnt = 0;
                    totalcnt = 0;
                    while imagerow is not None:
                        totalcnt += int(imagerow[3]);
                        directorycnt += 1;
                        imagerow = cursor1.fetchone()
                row = cursor.fetchone()
            return jsonify(data=[username, directorycnt, totalcnt]);
    except Error as e:
        print(e)


    # elementDt = ''
    # elementName = list()
    # textPart = list()
    # text = request.form['textVal']
    # text = text.splitlines()    #this is array of each line

    # driver = webdriver.Chrome('./chromedriver')
    # for i, eachline in enumerate(text):  #should load previous chrome windows
    #     if eachline.split()[0] == "navigate":
    #         driver.get(eachline.split()[1])
    #         time.sleep(1)

    #     elif i == int(request.form['ii']):# when it is to send data to main
    #         elementDt = driver.find_elements_by_tag_name(eachline.split()[0])
    #         for element in elementDt:
    #             elementName.append(element.get_attribute('name'))
    #         return jsonify(data=elementName)

    #     elif eachline.split()[0] == "input":
    #         whichTagList.append(eachline.split()[whichTagList[i]])
    #         driver.find_element_by_tag_name(eachline.split()[request.form["which"]]).send_keys(eachline.split()[1])
    #         time.sleep(1)

    #     elif eachline.split()[0] == "click":
    #         driver.find_element_by_tag_name().click()

    #     elif eachline.split()[0] == "check":
    #         driver.find_element_by_tag_name().click()



    # for x in range(int(request.form['num'])+1):
    #     print(x)
    # print(textPart)
    # driver.get("https://google.com")
    # driver.find_elements_by_tag_name("input")[2].send_keys("car")

    # #get data for table and show
    # time.sleep(1)
    # clickBtn = driver.find_elements_by_tag_name("button")
    # clickA = driver.find_elements_by_tag_name("a")
    # clickInput = driver.find_elements_by_tag_name("input")
    # for element in clickBtn:
    #     clickElement.append(element.get_attribute('name'))
    # for element in clickA:
    #     clickElement.append(element.get_attribute('name'))
    # for element in clickInput:
    #     clickElement.append(element.get_attribute('name'))
    # print("clickElement=")
    # print(clickElement)

    # for item in data:
    #     # loop over every row
    #     result += str(item['make']) + '\n'

    #return jsonify(list_of_data="element")

if __name__ == '__main__':
    app.run(debug=True)