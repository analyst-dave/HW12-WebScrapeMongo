from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pymongo
import time
import pandas as pd

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    
    # Initialize PyMongo to work with MongoDBs
    #conn = 'mongodb://localhost:27017'
    #client = pymongo.MongoClient(conn)
    # Define database and collection
    #db = client.mars
    #posts = db.posts
    print("------------- scrape_mars.init_browser() -------------\n")
    executable_path = {'executable_path': 'chromedriver.exe'}
    #browser = Browser('chrome', **executable_path, headless=False)
    #executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():

    listings = {}
    print("------------- scrape_mars.scrape() -------------\n")
    # URL of page to be scraped
    nasa_url = "https://mars.nasa.gov/news"
    jpl_url  = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    twit_url = "https://twitter.com/marswxreport?lang=en"
    fact_url = "https://space-facts.com/mars/"
    usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    
    print( scrape_usgs(scrape_fact(scrape_twit(scrape_jpl(scrape_nasa(listings,nasa_url), jpl_url), twit_url), fact_url), usgs_url) )

    return listings

def scrape_nasa(listings, url):

    browser = init_browser()
    print("------------- scrape_mars.scrape_nasa() -------------\n")
    ########
    # begin logic for: nasa_url = "https://mars.nasa.gov/news"
    #
    try:
        browser.visit(url)
        time.sleep(2)
        soup = BeautifulSoup(browser.html, 'html.parser')
        txtdiv = soup.find('div', class_="list_text")
        date = txtdiv.find('div', class_="list_date").text
        desc = txtdiv.find('div', class_="article_teaser_body").text
        titlediv = txtdiv.find('div', class_="content_title")
        title = titlediv.text
        href = titlediv.find('a')
        #title = txtdiv.find('div', class_="content_title").text
        
        imgdiv = soup.find('div', class_="list_image")
        img = imgdiv.find('img')

        # Print results only if title and desc are available
        if ( title and desc):
            print('-------------')
            print('scraping: ' + url)
            print(date)
            print(title)
            print(desc)
            # Dictionary to be inserted as a MongoDB document
            listings['news_title'] = title
            listings["news_p"] = desc
            listings["news_thumb"] = "https://mars.nasa.gov" + img['src']
            listings["news_link"] = "https://mars.nasa.gov" + href['href']
            listings["date"] = date

        browser.quit()
    except AttributeError as e:
        print(e)
    #
    # end logic for: nasa_url = "https://mars.nasa.gov/news"
    ########

    return listings

def scrape_jpl(listings, url):

    browser = init_browser()
    print("------------- scrape_mars.scrape_jpl() -------------\n")
    ########
    # begin logic for: jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    #
    try:
        browser.visit(url)
        time.sleep(1)
        browser.click_link_by_partial_text('FULL IMAGE')
        time.sleep(1)
        browser.click_link_by_partial_text('more info')
        time.sleep(2)
        soup1 = BeautifulSoup(browser.html, 'html.parser')
        main_img = soup1.find('img', class_="main_image")
        href = main_img['src']
        title = main_img['title']
        print('-----------')
        print('scraping: ' + url)
        print(title)
        print('https://www.jpl.nasa.gov' + href)
        listings['featured_image_url'] = 'https://www.jpl.nasa.gov'+href
        browser.quit()
    except Exception as e:
        print("#### Error: " + e)
    #
    # end logic for: jpl_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    ########

    return listings

def scrape_twit(listings, url):

    browser = init_browser()
    print("------------- scrape_mars.scrape_twit() -------------\n")
    ########
    # begin logic for: twit_url = "https://twitter.com/marswxreport?lang=en"
    #
    browser.visit(url)
    time.sleep(4)
    soup2 = BeautifulSoup(browser.html, 'html.parser')
    firstTime = True
    print('-----------------')
    print('scraping: ' + url)
    for article in soup2.find_all('article'):
        try:
            print('-----------------')
            inSightStr = article.text
            splitstr = inSightStr.split('InSight')[1]
            postinfo = inSightStr.split('InSight')[0]
            print(postinfo)
            print(splitstr)
            if ( firstTime ) :
                listings['mars_weather'] = splitstr
                listings['postinfo'] = postinfo
                firstTime = False
        except:
            print("Nothing to scrape for this twit")
    browser.quit()
    #
    # end logic for: twit_url = "https://twitter.com/marswxreport?lang=en"
    ########

    return listings

def scrape_fact(listings, url):

    print("------------- scrape_mars.scrape_fact() -------------\n")
    ########
    # begin logic for: facts_url = "https://space-facts.com/mars/"
    #
    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['description', 'values']
    df.set_index('description', inplace=True)
    
    html_table = df.to_html(classes='table table-striped table-hover')
    html_table.replace('\n', '')
    # we can safely use html_table now with the {{mars_facts | safe}} solution
    listings['mars_facts'] = html_table
    
    # this is the work around before the annoucement of {{marc_fact_html | safe}} solution in class
    # which onload inject html in Mars Facts <div> by loading the "/html_table" route
    # which tells Flask to use the html file(from df.to_html('/template/table.html')) stored under "templates" folder 
    df.to_html('templates/table.html', classes='table table-striped table-hover')
    #
    # end logic for: facts_url = "https://space-facts.com/mars/"
    ########

    return listings
    
def scrape_usgs(listings, url):

    browser = init_browser()
    print("------------- scrape_mars.scrape_usgs() -------------\n")
    ########
    # begin logic for: usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    hemisphere_image_urls = []
    browser.visit(url)
    time.sleep(2)
    soup3 = BeautifulSoup(browser.html, 'html.parser')
    for item in soup3.find_all('div', class_='item'):
        print('-----------------')
        try:
            img = item.find('img', class_="thumb")
            href = img['src']
            alink = item.find('h3')
            txt = alink.text
            print('-----------')
            print(txt)
            print('https://www.jpl.nasa.gov' + href)
            browser.click_link_by_partial_text(txt)
            time.sleep(2)
            soup3 = BeautifulSoup(browser.html, 'html.parser')
            div = soup3.find('div', class_="downloads")
            full = div.find('a')
            print(full['href'])
            #hemisphere_image_urls.append({'title': txt, 'img_url': full['href']})
            hemisphere_image_urls.append(full['href'])
            browser.back()
        except:
            print("Scraping Complete")
    # in case their website is down... which happened on 7/14/20
    if ( not hemisphere_image_urls ) : 
        print("### usgs_url unresponsive again!!! ###")
        hemisphere_image_urls.append("http://placehold.it/400x400")
        hemisphere_image_urls.append("http://via.placeholder.com/400")
        hemisphere_image_urls.append("http://placehold.it/400x400")
        hemisphere_image_urls.append("http://via.placeholder.com/400")

    listings['hemisphere_image_urls'] = hemisphere_image_urls
    browser.quit()
    #
    # end logic for: usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars""
    ########

    return listings