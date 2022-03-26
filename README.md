# Realtime intelligent trading system for Bitcoin
### Project Overview 
This is the final project of MSCA32019, real time intellegent system. In this project, we implemented an intellegent system that trades Bitcoin automatically based on streaming tweets and streaming google search index.

|Team Member|Role|LinkedIn|
|:---:|:-:|:-|
|[**Milan Toolsidas**](https://github.com/mtoolsidas)|collaborator|https://www.linkedin.com/in/kenjilaurens/|
|[**Kenji Laurens**](https://github.com/klaurens)|collaborator|https://www.linkedin.com/in/milantoolsidas/|
|[**Ryan Liao**](https://github.com/Ryan47Liao)|team lead|https://www.linkedin.com/in/bowen-liao/|
  
    Our project has three phases:
    1.collect and prepare the data
    2.Modeling and trading strategy design 
    3.Back-testing and implementing under real-time settings
![image](https://user-images.githubusercontent.com/62736640/160001010-5363183d-0606-4fdc-9699-aa1cb9d72e94.png)
    
## Data ETL
### Data Extraction
    For data extraction,we mainly used: 
    - offical Rest API outlets
    - a combination of selenium and bs4
    - Kaggle.
![image](https://user-images.githubusercontent.com/62736640/160001084-51f5031e-3fad-48de-b9a1-b3a1a5ae2469.png)
![image](https://user-images.githubusercontent.com/62736640/160001108-dc3ab6a9-f4c2-4592-a482-fef2c7a0acb5.png)
![image](https://user-images.githubusercontent.com/62736640/160001125-72422686-7eff-4c6a-a4b5-d7a9bbf32f94.png)
![image](https://user-images.githubusercontent.com/62736640/160001145-96835d95-4557-4b66-947f-8c4a223ab833.png)

### Data Transformation (Cleanning) 
    The bitcoin tweets have very low subjectivity, thus not ideal for sentiment analysis. Our theory was that there were a lot of bot generated tweets, and therefore we need to find ways to remove these tweets.
![image](https://user-images.githubusercontent.com/62736640/160001574-a51f7f87-080f-4684-8e00-55a29cf78bf1.png)

## EDA
### Sentiment Analysis
    Even after cleaning, there is still very little correlation between bitcoin close prices and tweet sentiments.
![image](https://user-images.githubusercontent.com/62736640/160001674-bdcded3d-3532-4771-af2c-a1e735a832c5.png)

### Time Series Analysis
![image](https://user-images.githubusercontent.com/62736640/160001693-de56a57a-a12f-4707-923e-e5e8ae13eb5c.png)

## Modeling
    We used simple ordinary least square as our baseline, and used a variety of nonlinear regression methods. 
![image](https://user-images.githubusercontent.com/62736640/160001743-140cd599-e248-4b00-ac7b-c2a17cc4b898.png)
![image](https://user-images.githubusercontent.com/62736640/160001762-ea8a740b-5839-4b9f-814b-659ca090cbe1.png)
![image](https://user-images.githubusercontent.com/62736640/160001781-de770554-6b32-4d78-8e85-051fc713df21.png)

## Trading Strategy Design
    The trading strategy unit takes the input of historical Bitcoin data, tweet volume data, 
    and outputs an Order as streaming data being received.
![image](https://user-images.githubusercontent.com/62736640/160226779-be7185c6-370a-4787-a03c-822be8d3c091.png)

## Backtesting
    To evaluate our trading strategy, we backtested 6 algorithm across 3 time frames.
    The first 2 algorithm are baselines, 
    the next two smile algorithm are our trading strategy design without implementing our prediction model,
    and finally, the last two are the implementation of our predictive model carried out by 2 different models. 
    
![image](https://user-images.githubusercontent.com/62736640/160226790-7862b363-cc12-4eef-895d-ef7256df6d06.png)
![image](https://user-images.githubusercontent.com/62736640/160226796-05681644-fda7-49c8-a9f6-19f6c984af7b.png)
![image](https://user-images.githubusercontent.com/62736640/160226800-68e29ec0-a9de-496d-9c56-15d602365100.png)
![image](https://user-images.githubusercontent.com/62736640/160226805-4e651cfd-f59e-4aa4-b520-8629d05414a9.png)
![image](https://user-images.githubusercontent.com/62736640/160226809-5819e5f6-cc81-48e9-97e1-ef3a790982d6.png)
![image](https://user-images.githubusercontent.com/62736640/160226812-1c19e521-fb25-4d31-9ee7-b4145fbaacf6.png)

## System design 
    The server would be picking up bitcoin orders in real time, building order book, along with collecting other 
    data such as tweets and google search trends. It will then compile these data and send it to the client, which 
    upon receiving, will feed the streaming data into the trading strategy unit, which outputs an order to be sent 
    to the server. When an order is received, the surver will try to make an match within the order book, if an order
    pair exist, it will then attempt to leverage CoinBase API to place an order.
![image](https://user-images.githubusercontent.com/62736640/160226818-7d175c59-eb8a-4b76-8d65-52c7be2732d7.png)

## Future work
![image](https://user-images.githubusercontent.com/62736640/160001982-de8e27e8-fe52-4e63-a423-1a9fe1b5d2bc.png)

