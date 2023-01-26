#these are the libraries used for these sns.twitter scrape methods using a customizes streamlit website
import streamlit as st
import base64
from PIL import Image
import snscrape.modules.twitter as sntwitter
import numpy as np
import datetime
import json
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from wordcloud import STOPWORDS
import pandas as pd
from pymongo import MongoClient
from streamlit_option_menu import option_menu

#connecting MongoDB-Database and creating a collection
conn = MongoClient("mongodb+srv://danavasanth:Krishnaveni@cluster0.0azflq3.mongodb.net/?retryWrites=true&w=majority")
db = conn["snscrape"]
coll = db["twitter-data"]
img = Image.open("media/twitter.png")
st.set_page_config(page_title="Twitter scraping",page_icon = img,layout="wide")

#This is used to make the streamlit web-page customized
def get_img_as_base64(file):
    with open(file,"rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()
img = get_img_as_base64("image/twitter-splash.jpg")
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image :url("data:image/png;base64,{img}");
background-size : cover;
}}
[data-testid="stHeader"]{{
background:rgba(0,0,0,0);
}}
</style>

"""
st.markdown(page_bg_img, unsafe_allow_html=True)
st.header("TWITTER SCRAPPING USING SNSCRAPE")

#It enables user to scrape the data from twitter using "snscrape"
def ScrapingTheBird(word,From,To,maxTweets):
  tweets_list = []
  for i,tweet in enumerate(sntwitter.TwitterSearchScraper(f'{word} since:{From} until:{To}').get_items()):
      if i>maxTweets-1:
          break
      tweets_list.append([tweet.date,tweet.id,tweet.user.username,tweet.url,tweet.rawContent,tweet.replyCount,tweet.likeCount,tweet.retweetCount,tweet.lang,tweet.source ])
  tweets_df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet Id','User Name','URL','Content','ReplyCount','LikeCount','Retweet-Count','Language','Source'])
  tweets_df.to_json("user-tweets.json")
  tweets_df.to_csv("user-tweets.csv")
  return tweets_df

#It is to visualize the most frequent word used by peoples along with the search word in wordcloud form
def word_cloud():
    stopwords = set(STOPWORDS)
    data = pd.read_csv("user-tweets.csv")
    mask = np.array(Image.open("media/tweetie.png"))
    text = " ".join(review for review in data.Content)
    wordcloud = WordCloud(background_color = "white",max_words=500,mask=mask).generate(text)
    plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    plt.savefig("media/word-cloud.png",format="png")
    return plt.show()

#It is to upload the search document in Mongodb database
def Bird_In_Database(n_word):
    with open("user-tweets.json","r") as file:
        data = json.load(file)
    dt = datetime.datetime.today()
    db.twitter_data.insert_many([{
            "Key-Word":n_word,
            "datetime":dt,
            "Data":data
            }])

#creating a navigation menu used to select the user to what to visible and perform
#with st.sidebar:
choice = option_menu(
    menu_title = None,
    options = ["About","Search","Visualize","Home","Data-Base","Download","Contact"],
    icons =["archive","search","camera2","house","boxes","download","at"],
    default_index=3,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "white","size":"cover"},
        "icon": {"color": "cyan", "font-size": "20px"},
        "nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#29BDE9 "},
        "nav-link-selected": {"background-color": "black"},}
    )
#It remains default web-page
if choice=="Home":
    col1, col2,col3 = st.columns(3)
    col1.image(Image.open("media/tweet.png"),width = 500)
    col2.header("“There are NO magic wands, NO hidden tracks, NO secret handshakes that can bring you immediate success..! But with Time, Energy and Determination you can get there...!”")
    col3.image(Image.open("media/smiles.png"),width = 500)

#It enables user to search the key-word , from date , to date and no of datas
if choice=="Search":
    word = st.text_input("Enter Word to Search")
    if word:
        From = st.date_input("From Date")
        if From:
            To = st.date_input("To Date")
            if To:
                maxTweets = st.number_input("Number of Tweets",1,1000)
                if maxTweets:
                    check = st.button("Caught the Bird")
                    if check:
                        st.dataframe(ScrapingTheBird(word,From,To,maxTweets).iloc[0:10])
                        col1, col2 = st.columns(2)
                        col1.image(Image.open("media/smiles.png"))
                        col2.image(Image.open("media/thumbsup.png"))
                        st.snow()

#It enables user to visualize the data in wordcloud form with similar tag's
if choice=="Visualize":
    col1,col2,col3= st.columns(3)
    col1 = (st.button("Click to here to Release :bird:"))
    col2.image(Image.open("media/cage bird.png"),width = 250)
    if (col1):
        st.balloons()
        word_cloud()
        col3.image(Image.open("media/word-cloud.png"))

#It enables user to download the search data in JSON or CSV file
if choice=="Download":
    col1,col2,= st.columns(2)
    col1.image(Image.open("media/bell.png"),width = 300)
    col2.header("*You can Download the previous search data ( or ) You can search for new-data")
    choice1 = ["--SELECT-OPTIONS--", "Pre-Search-data", "New-Search"]
    menu=st.selectbox("SELECT", choice1)
    if menu=="Pre-Search-data":
        with open("user-tweets.csv") as CSV:
            if st.download_button("DOWNLOAD THE BIRD IN --> .csv ",CSV,file_name="My-Blue-Bird.csv"):
                st.image("media/baby-right.png",width = 250)
                st.success("My-Blue-Bird.csv..! has been downloaded")
        with open("user-tweets.json") as JSON:
            if st.download_button("DOWNLOAD THE BIRD IN --> .json",JSON,file_name="My-Blue-Bird.json"):
                st.image("media/baby-left.png",width = 250)
                st.success("My-Blue-Bird.json..! has been downloaded")

    if menu=="New-Search":
        word = st.text_input("Enter Word to Search")
        if word:
            From = st.date_input("From Date")
            if From:
                To = st.date_input("To Date")
                if To:
                    maxTweets = st.number_input("Number of Tweets", 1, 1000)
                    if maxTweets:
                        check = st.button("Caught the Bird")
                        if check:
                            st.dataframe(ScrapingTheBird(word, From, To, maxTweets).iloc[0:10])
                            with open("user-tweets.csv") as CSV:
                                st.download_button("DOWNLOAD THE BIRD IN --> .csv ", CSV,file_name="My-Blue-Bird.csv")
                            with open("user-tweets.json") as JSON:
                                st.download_button("DOWNLOAD THE BIRD IN --> .json", JSON,file_name="My-Blue-Bird.json")

#It is to upload the search data into mongodb database
if choice=="Data-Base":
    col1,col2,col3 = st.columns(3)
    col1.image(Image.open("media/data-base.png"),width = 250)
    col3.image(Image.open("media/Mongodb.png"))
    col2.header("You can ADD your Previous Search DATA into MongoDB data base to work with Cloud-Network")

    list = ['',"store in data-base","view as data-frame"]
    CHOICE = st.selectbox("SELECT",list)
    if CHOICE=="store in data-base":
        n_word = st.text_input("Enter the KEY-WORD")
        Bird_In_Database(n_word)
        if st.button("upload"):
            st.success("Your DATA-BASE has been UPDATED SUCCESSFULLY :smiley:")
            col1,col2,col3=st.columns(3)
            col1.image(Image.open("media/jerry-cheese.png"))
            col2.header("THANKS FOR THE CHEESE..!")
            col3.image(Image.open("media/tom.png"))
    if CHOICE=="view as data-frame":
        if st.button("view :goggles:"):
            df = pd.read_csv("user-tweets.csv")
            st.dataframe(df)
            st.balloons()

#It is to know what is sns-crape
if choice=="About":
    col1,col2,col3,col4,col5,col6,col7,col8 = st.columns(8)
    col1.image(Image.open("media/facebook.png"))
    col2.image(Image.open("media/whatsapp.png"))
    col3.image(Image.open("media/vibe.png"),width = 300)
    col4.image(Image.open("media/instagram.png"))
    col5.image(Image.open("media/twitter.png"))
    col6.image(Image.open("media/youtube.png"),width=250)
    col7.image(Image.open("media/telegram.png"))
    col8.image(Image.open("media/mail.png"))
    st.subheader("Twitter is a social media platform that allows users to post and interact with short messages called tweets." 
                "Tweets can include text, images, and videos, and have a 280-character limit. " 
                "Users can follow other users, view and respond to tweets, and use hashtags to categorize and find tweets on specific topics. "  
                "Twitter is widely used for news, communication, and entertainment purposes. " 
                "It was created in 2006 and has become one of the most popular social media platforms in the world.")
    if st.button("How To Caught The Bird"):
        col1,col2 = st.columns(2)
        col1.subheader("snscrape is a command-line tool for scraping data from social media websites."
                           " It can be used to scrape data from websites such as Twitter, Instagram, and Facebook."
                           " The data that can be scraped includes information such as user profiles, posts, and comments. snscrape can be used to scrape data for research, data analysis, or other purposes."
                           " It was created using Python and can be run on Windows, macOS, and Linux. Some of the key features of snscrape include the ability to scrape data for specific users, hashtags, and keywords, and the ability to save the scraped data in various formats such as CSV, JSON, and SQLite.")
        col2.image(Image.open("media/sns.png"),width = 600)
        st.success("OK..It's time to caught the BIRD :gun: ")
        st.balloons()

#It is to tell about myself and my social-pages
if choice=="Contact":
    name = "DHANA VASANTH"
    mail = (f'{"Mail Me At :"}  {"danavasanth@gmail.com"}')
    description = "An aspiring DATA-SCIENTIST with un-discribable idea's"
    social_media = {
        "TWITTER":"https://twitter.com/im_vazanth",
        "GIT-HUB":"https://github.com/dhanavasanth",
        "linkedIN":"www.linkedin.com/in/dhana-vasanth-7462a5256",
        "INSTAGRAM":"https://www.instagram.com/dana_vasanth_/",

    }
    col1,col2,col3= st.columns(3)
    col1.image(Image.open("media/space.png"),width = 500)
    col2.image(Image.open("media/my.png"),width = 400)
    with col3:
        st.title(name)
        st.write("---")
        st.write(description)
        st.write(mail)
    st.write("#")
    cols = st.columns(len(social_media))
    for index,(platform,link) in enumerate(social_media.items()):
        cols[index].write(f"[{platform}]({link})")





































