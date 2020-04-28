#import dependencies
from bs4 import BeautifulSoup as bs
from splinter import Browser
import os
import pandas as pd
import datetime as dt
from selenium import webdriver


# Choose the executable path to driver 
executable_path = {"executable_path":"C:\\Users\\lex83\\Downloads\\chromedriver_win32\\chromedriver"}
browser = Browser("chrome", **executable_path, headless=True) 

#Define scrape function to retrive data from all sources.
def scrape():

    mars_facts_data = {}
    news_all = mars_news()
    mars_facts_data["mars_news"] = news_all[0]
    mars_facts_data["mars_paragraph"] = news_all[1]
    mars_facts_data["mars_image"] = mars_image()
    #mars_facts_data["mars_weather"] = marsWeather()
    mars_facts_data["mars_facts"] = mars_facts()
    mars_facts_data["mars_hemisphere"] = mars_hemispheres()

    return mars_facts_data

# Mars Facts 
def mars_news():
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html_nasa = browser.html
    soup_nasa = bs(html_nasa,"html.parser")
    #Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text
    news_title = soup_nasa.find("div",class_="content_title").text
    news_p = soup_nasa.find("div", class_="article_teaser_body").text
    news_all = [news_title,news_p]
    return news_all


#JPL Mars Space Images - Featured Image
def mars_image():
    url_image = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url_image)

    from urllib.parse import urlsplit
    base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(url_image))
    xpath = "//*[@id=\"page\"]/section[3]/div/ul/li[1]/a/div/div[2]/img"

    #Use splinter to click on the mars featured image
    results = browser.find_by_xpath(xpath)
    img = results[0]
    img.click()
    
    #get image url using BeautifulSoup
    html_image = browser.html
    soup = bs(html_image, "html.parser")
    img_url = soup.find("img", class_="fancybox-image")["src"]
    full_img_url = base_url + img_url
    return full_img_url
    

#Mars Weather (code did not run in notebook just used for reference)
#def mars_weather():
    #url = 'https://twitter.com/marswxreport?lang=en'
    #browser.visit(url)
    #html = browser.html
    #weather_soup = bs(html, 'html.parser')
    #mars_weather_tweet = weather_soup.find('div', attrs={"class": "tweet", "data-name": "Mars Weather"})
    #mars_weather = mars_weather_tweet.find('p', 'tweet-text').get_text()
    #return mars_weather


#Mars Facts
def mars_facts():
    url_facts = "https://space-facts.com/mars/"
    table = pd.read_html(url_facts)
    table[0]

    #Create dataframe using table as reference
    df_mars_facts = table[0]
    df_mars_facts.columns = ["Parameter", "Values"]
    clean_table = df_mars_facts.set_index(["Parameter"])

    #Format dataframe for html. Eliminate /n (clean entries)
    mars_html_table = clean_table.to_html()
    mars_html_table = mars_html_table.replace("\n", "")
    m_facts = mars_html_table.to_html(index = True, header =True)
    return m_facts


#Mars Hemisperes
def mars_hemispheres():
    mars_hemisphere_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    hemi_dicts = []

    #loop thru list. Use find_by_css to access image on click. Print in dictionary

    for i in range(1,9,2):
        hemi_dict = {}
    
        browser.visit(mars_hemisphere_url)
        hemispheres_html = browser.html
        hemispheres_soup = bs(hemispheres_html, 'html.parser')
        hemi_name_links = hemispheres_soup.find_all('a', class_='product-item')
        hemi_name = hemi_name_links[i].text.strip('Enhanced')
    
        detail_links = browser.find_by_css('a.product-item')
        detail_links[i].click()
        browser.find_link_by_text('Sample').first.click()
        browser.windows.current = browser.windows[-1]
        hemi_img_html = browser.html
        browser.windows.current = browser.windows[0]
        browser.windows[-1].close()
    
        hemi_img_soup = bs(hemi_img_html, 'html.parser')
        hemi_img_path = hemi_img_soup.find('img')['src']

        hemi_dict['title'] = hemi_name.strip()
    
        hemi_dict['img_url'] = hemi_img_path

        hemi_dicts.append(hemi_dict)

        return hemi_dicts