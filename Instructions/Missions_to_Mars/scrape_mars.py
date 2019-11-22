from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()

    #Visit url for news data
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    time.sleep(1)

    #convert parse html with Beautiful Soup, scrape first title and paragraph
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    news_title = soup.find('div',class_='content_title').text
    news_p = soup.find('div',class_='article_teaser_body').text

    #Visit url for Mars image
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    time.sleep(1)

    #create soup instance and scrape image url
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    article = soup.find('article',class_='carousel_item')
    img_url1 = 'https://www.jpl.nasa.gov'
    img_url2 = article['style'].split("'")[1]

    featured_image_url = img_url1 + img_url2

    #Visit url for Mars Weather Twitter
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)
    time.sleep(1)

    #create soup instance and scrape latest weather
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    mars_weather = soup.find('p',class_='TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text.split('pic.twitter.com')[0]

    #Visit url for Mars Facts
    url = 'https://space-facts.com/mars/'
    browser.visit(url)
    time.sleep(1)

    #parse url to retrieve Mars table and set column headers
    tables = pd.read_html(url)
    df = tables[0]
    df= df.set_index(0)
    del df.index.name
    df.columns=['Value']
    df
    
    #Use Pandas to convert the data to a HTML table string
    html_table = df.to_html()

    #Visit USGS Astrogeology site here to obtain high resolution images for each of Mar's hemispheres
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    time.sleep(1)

    #create soup instance to scrape images
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')

    #empty list to store image dictionaries and find image links
    hemisphere_image_urls = []

    image_links = soup.find_all('div',class_='description')

    for link in image_links:
        image_url = {}
        #Find name of Hemisphere link, use to go to click on link
        hemisphere = link.find('h3').text
        image_url['title'] = hemisphere
        browser.click_link_by_partial_text(hemisphere)
        time.sleep(1)
        #reset soup instance, fetch image link on new site
        html = browser.html
        child_soup = BeautifulSoup(html, 'html.parser')
        img = child_soup.find('img',class_='wide-image')['src']
        img = 'https://astrogeology.usgs.gov' + img
        image_url['img_url'] = img 
        hemisphere_image_urls.append(image_url)
        #go back to original page and repeat process for other links
        browser.back()
        time.sleep(1)
    
    #store information into dictionary
    scraping_info = {}
    scraping_info['news_title'] = news_title
    scraping_info['news_p'] = news_p
    scraping_info['featured_image_url'] = featured_image_url
    scraping_info['mars_weather'] = mars_weather
    scraping_info['html_table'] = html_table
    scraping_info['hemisphere_image_urls'] = hemisphere_image_urls

    browser.quit()

    return scraping_info