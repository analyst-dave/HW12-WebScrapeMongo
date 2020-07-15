from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars
import flask

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# Or set inline
# mongo = PyMongo(app, uri="mongodb://localhost:27017/craigslist_app")


@app.route("/")
def index():
#    listings = db.posts.find()
#
#for listing in listings:
#    print(listing)
#
#print(db.posts.count())
    print("------------- inside app.index() -------------\n")
    listings = mongo.db.listings.find_one()
    # run scraper() to init db if run 1st time
    if ( not listings ) :
        return scraper()
    print(listings)
    return render_template("index.html", listings=listings)


@app.route("/scrape")
def scraper():
    print("------------- inside app.scraper() -------------\n")
    listings = mongo.db.listings
    listings_data = scrape_mars.scrape()
    #print(listings_data)
    listings.update({}, listings_data, upsert=True)
    return redirect("/", code=302)

@app.route("/html_table")
def html_table():
    print("------------- inside app.html_table() -------------\n")
    return render_template("table.html")

if __name__ == "__main__":
    app.run(debug=True)
