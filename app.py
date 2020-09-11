
from flask import Flask, render_template, request
import logging
import pandas as pd
from joblib import load
from lxml import html
import requests
import datetime


#initialize logging
LOG_FILE_NAME = 'StockAppLog.txt'
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=LOG_FILE_NAME,
                    filemode='w')
#web scraping using lxml
def parse(url):
    
    response = requests.get(url)
    print("Parsing %s" % (url))
    parser = html.fromstring(response.text)
    summary_table = parser.xpath(
        '//div[contains(@data-test,"summary-table")]//tr')
    list1=[]
    list2=[]

    try:

        for table_data in summary_table:
            raw_table_key = table_data.xpath(
                './/td[1]//text()')
            raw_table_value = table_data.xpath(
                './/td[2]//text()')
            table_key = ''.join(raw_table_key).strip()
            table_value = ''.join(raw_table_value).strip()
            list1.append(table_key)
            list2.append(table_value)
        return list2
    except ValueError:
        logging.info("Failed to parse json response")
        return {"error": "Failed to parse json response"}
    except:
        return {"error": "Unhandled Error"}

url_escort = "https://in.finance.yahoo.com/quote/ESCORTS.NS?p=ESCORTS.NS&.tsrc=fin-srch"
url_nifty = "https://in.finance.yahoo.com/quote/%5ENSEI?p=^NSEI&.tsrc=fin-srch"
url_hang = "https://in.finance.yahoo.com/quote/%5EHSI?p=^HSI&.tsrc=fin-srch"
url_kospi = "https://in.finance.yahoo.com/quote/%5EKS11?p=^KS11&.tsrc=fin-srch"
url_euro = "https://in.finance.yahoo.com/quote/%5EN100?p=^N100&.tsrc=fin-srch"
url_nasdaq = "https://in.finance.yahoo.com/quote/%5EIXIC?p=^IXIC&.tsrc=fin-srch"
url_muthoot = "https://in.finance.yahoo.com/quote/MUTHOOTFIN.NS?p=MUTHOOTFIN.NS&.tsrc=fin-srch"
url_sbi = "https://in.finance.yahoo.com/quote/SBIN.NS?p=SBIN.NS&.tsrc=fin-srch"
url_hcl = "https://in.finance.yahoo.com/quote/HCLTECH.NS?p=HCLTECH.NS&.tsrc=fin-srch"
url_icici = "https://in.finance.yahoo.com/quote/ICICIBANK.NS?p=ICICIBANK.NS&.tsrc=fin-srch"
url_nikkei = "https://in.finance.yahoo.com/quote/%5EN225?p=^N225&.tsrc=fin-srch"

dt = datetime.date.today()
logging.info("Fetching Real-time data..")
list1=[]
l1= parse(url_escort)
l2= parse(url_nifty)
l3= parse(url_hang)
l4= parse(url_kospi)
l5= parse(url_euro)
l6= parse(url_nasdaq)
l7= parse(url_muthoot)
l8= parse(url_sbi)
l9= parse(url_hcl)
l10= parse(url_icici)
l11= parse(url_nikkei)

list1.append(dt)
list1.append(float(l1[0].replace(',', '')))
list1.append(float(l2[0].replace(',', '')))
list1.append(float(l3[1].replace(',', '')))
list1.append(float(l4[1].replace(',', '')))
list1.append(float(l5[0].replace(',', '')))
list1.append(float(l6[0].replace(',', '')))
list1.append(float(l7[0].replace(',', '')))
list1.append(float(l8[0].replace(',', '')))
list1.append(float(l9[0].replace(',', '')))
list1.append(float(l10[0].replace(',', '')))
list1.append(float(l11[1].replace(',', '')))

print(list1) 

logging.info("Real-time data Scraping Completed")
data=[tuple(list1)]
#Saving real-time data in csv file

dm = pd.DataFrame(data, columns=['Date', 'Escorts Adj Close', 'NIFTY_India Adj Close', 'HangSeng Open',\
       'KOSPI Open', 'Euronext Adj Close', 'NASDAQ Adj Close',\
       'Muthoot Adj Close', 'SBI Adj Close', 'HCL Adj Close', 'ICICI Adj Close', 'Nikkei Open'])
 
dm.to_csv('RealTime_data.csv', mode = 'a', header = False,index=False)       
        

df = pd.read_csv('RealTime_data.csv')
df=df.tail(1)

#loading models
escorts_model = load('escorts_SVR.joblib')
muthoot_model = load('muthoot_SVR.joblib')
sbi_model = load('sbi_SVR.joblib')
hcl_model = load('hcl_rf.joblib')
icici_model = load('icici_lr.joblib')

# REST API service
app = Flask(__name__)


@app.route('/',methods=['POST', 'GET'])
def home():   
    logging.info("Opening Home page ")
    return render_template('home.html')


@app.route('/predict',methods=['POST', 'GET'])
def stock_predict():
    
    global df
    global dt
    json_object={}
    stock_status = ""
    if request.method == 'POST':
        try:
            t=request.form['tick']
            if t=='MTH':
                
                df1 = df[['Date', 'NIFTY_India Adj Close', 'Muthoot Adj Close', \
                          'Euronext Adj Close', 'NASDAQ Adj Close']]     
                data_df1=df1[df1.columns[1:]]
                logging.info(data_df1.columns)
                prediction1 = muthoot_model.predict(data_df1)
                price1=round(prediction1[0],3)
                logging.info("Prediction Completed.. ")
                logging.info(price1)
                stock_status = 'The Open Price of Muthoot Finance on '+str(dt)+' : ₹ ' + str(price1)
                json_object = {"Muthoot Price" : stock_status}
                
            elif t=='SBI':
                
                df2 = df[['Date','NIFTY_India Adj Close', 'SBI Adj Close',\
                          'HangSeng Open', 'Euronext Adj Close']]
                data_df2=df2[df2.columns[1:]]
                logging.info(data_df2.columns)
                prediction2 = sbi_model.predict(data_df2)
                price2=round(prediction2[0],3)
                logging.info("Prediction Completed.. ")
                logging.info(price2)
                stock_status = 'The Open Price of State Bank of India on '+str(dt)+' : ₹ ' + str(price2)
                json_object = {"SBI Price" : stock_status}
                
            elif t=='ESC':
                
                df3 = df[['Date','NIFTY_India Adj Close', 'Escorts Adj Close',\
                         'HangSeng Open','KOSPI Open']]
                data_df3=df3[df3.columns[1:]]
                logging.info(data_df3.columns)
                prediction3 = escorts_model.predict(data_df3)
                price3=round(prediction3[0],3)
                logging.info("Prediction Completed.. ")
                logging.info(price3)
                stock_status = 'The Open Price of Escorts Ltd on '+str(dt)+' : ₹ ' + str(price3)
                json_object = {"Escorts Price" : stock_status}
                
            elif t=='HCL':
                
                df4 = df[['Date', 'NIFTY_India Adj Close', 'HCL Adj Close','HangSeng Open',\
                          'Euronext Adj Close']]
                data_df4=df4[df4.columns[1:]]
                logging.info(data_df4.columns)
                prediction4 = hcl_model.predict(data_df4)
                price4=round(prediction4[0],3)
                logging.info("Prediction Completed.. ")
                logging.info(price4)
                stock_status = 'The Open Price of HCL Tech on '+str(dt)+' : ₹ ' + str(price4)
                json_object = {"HCL Price" : stock_status}
             
            elif t=='ICI':
                
                df5 = df[['Date', 'NIFTY_India Adj Close', 'ICICI Adj Close',\
                          'Euronext Adj Close','Nikkei Open']]
                data_df5=df5[df5.columns[1:]]
                logging.info(data_df5.columns)
                prediction5 = icici_model.predict(data_df5)
                price5=round(prediction5[0],3)
                logging.info("Prediction Completed.. ")
                logging.info(price5)
                stock_status = 'The Open Price of ICICI Bank on '+str(dt)+' : ₹ ' + str(price5)   
                json_object = {"ICICI Price" : stock_status}
                
            
            else:
                stock_status = 'Wrong Ticker'
                
                
        except:
            stock_status = 'Error!'
            logging.exception(stock_status)            
        
         
    return render_template('predict.html',stock_status = json_object)
  
    
if __name__ == '__main__':
    app.run()


     