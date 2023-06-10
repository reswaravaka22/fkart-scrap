from flask import Flask,request,render_template
from flask_cors import CORS,cross_origin
from bs4 import BeautifulSoup as bfs
from urllib.request import urlopen as uGet
import requests
import logging
import pandas as pd
logging.basicConfig(filename="fkartscrap.log" , level=logging.INFO)
flipkartScrapper=Flask(__name__)
app=flipkartScrapper
@app.route('/',methods=["GET"])
def home():
    return render_template('index.html')
    
@app.route('/review',methods=['GET','POST'])
def reviews():
       if request.method=='POST':
        website_name = request.form['website']
        searchString = request.form['product_name'].replace(' ','')
        
        if website_name == 'Flipkart':
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uclient = uGet(flipkart_url)
            flipkartpage = uclient.read()
            flipkart_html_page = bfs(flipkartpage ,"html.parser")
            biglot = flipkart_html_page.findAll("div" , {"class": "_1AtVbE col-12-12"})
            reviews=[]
            csvfilename=searchString+'.csv'
            list_of_lists = []
            for box in biglot:
                try:
                    productlink = "https://www.flipkart.com"+box.div.div.div.a['href']
                    productreq = requests.get(productlink)
                    prod_html = bfs(productreq.text,"html.parser")
                    commentBox = prod_html.find_all("div", {"class" : "_16PBlm"})
                    
                    try:
                        for i in commentBox :
                            list_of_page = []
                            try:
                                rating=(i.div.div.div.div.text)#ratings
                            except Exception as e:
                                rating='No Rating'
                                logging.info(e)
                            try:
                                comment=(i.div.div.find_all("div" ,{"class" : ""})[0].div.text)#comments
                            except:
                                comment='No Comment'
                                logging.info(e)
                            try:
                                customer_name=(i.div.div.find_all("p" , {"class" :"_2sc7ZR _2V5EHH" })[0].text)#customer names
                            except:
                                customer_name='Not Available'
                                logging.info(e)
                            try:
                                list_of_page.append(searchString)
                                list_of_page.append(customer_name)
                                list_of_page.append(rating)
                                list_of_page.append(comment)
                                list_of_lists.append(list_of_page)
                            except :
                                pass
                        
                            try:
                                my_dict={"Product_name":searchString, 
                                    "Customer_name":customer_name,
                                    'Comment':comment,
                                    'Rating':rating}
                                reviews.append(my_dict)
                            except:
                                pass
                    except Exception as e:
                        pass
                    
                except Exception as e:
                    pass
        # Creating the DataFrame
        df = pd.DataFrame(list_of_lists, columns=['Product_name', 'Customer_name', 'Rating','Comment'])
        # Exporting the DataFrame as csv
        df.to_csv(csvfilename, index=False, sep=';')      
        return render_template('result.html',rev=reviews[0:(len(reviews)-1)])
        
if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
