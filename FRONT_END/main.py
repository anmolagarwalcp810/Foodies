# Data from https://data.world/datafiniti/fast-food-restaurants-across-america

from flask import Flask, render_template, session, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, SelectMultipleField
from flask_bootstrap import Bootstrap
# import matplotlib.pyplot as plt
import psycopg2
# psygcopg2 library will be used to send queries to the DB

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'mykey'
con = psycopg2.connect(dbname='group_15', user='group_15', host='10.17.5.99', password='k88sh5PLm33AK', port = '5432')
cur = con.cursor()


class ChooseLocationForm(FlaskForm):
    # We want just one Field, i.e. choose Location
    location = SelectField('Choose your location', choices=[])
    submit = SubmitField('Submit')


class ListRestaurantForm(FlaskForm):
    foodchain = StringField('Name')
    categories = SelectMultipleField('Categories', choices=[], coerce=int)
    website = StringField('Website')
    address = StringField('Address')
    city = SelectField('Choose your location', choices=[])
    postalcode = StringField('Postal Code')
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def chooseLocation():
    query = "SELECT * FROM cities ORDER BY city;"
    cur.execute(query)
    items = cur.fetchall()
    form = ChooseLocationForm()
    form.location.choices = items
    if form.validate_on_submit():
        session['location'] = form.location.data
        return redirect(url_for('ind'))
    return render_template('chooseLocation.html', form=form)


@app.route('/home')
def ind():
    # form = FilterForm()
    # form.location.choices = items
    # if form.validate_on_submit():
    #     session['foodchain'] = form.location.data
    #     session['']
    #     # Query
    #
    #     return render_template()
    # The variable session['location'] contains the location.
    query = "SELECT foodchain, address, postalcode, websites, array_agg(category), city, country FROM restaurants, foodchains, cities, categories\n" \
            "WHERE cities.city_id = " + session['location'] + "\n" \
              "AND foodchains.foodchain_id = restaurants.foodchain_id\n" \
              "AND cities.city_id = restaurants.city_id\n" \
              "AND restaurants.categories = category_id\n" \
              "GROUP BY foodchain, address, postalcode, websites, city, country;"
    cur.execute(query)
    items = cur.fetchall()
    # print(items)
    list_restaurants = []
    for item in items:
        name = item[0]
        address = item[1]
        postalcode = item[2]
        websites = item[3]
        categories = item[4]
        city = item[5]
        country = item[6]
        restaurant = dict()
        restaurant['name'] = name
        restaurant['addr'] = address
        restaurant['postalcode'] = postalcode
        restaurant['link'] = websites
        restaurant['city'] = city
        restaurant['country'] = country
        restaurant['categories'] = categories
        restaurant['websites'] = websites.split(',')
        list_restaurants += [restaurant]
    # print(len(list_restaurants))
    category_query = "SELECT * FROM categories ORDER BY category;"
    cur.execute(category_query)
    items = cur.fetchall()
    category_list = []
    for i in items:
        category = {}
        category['category'] = i[0]
        category['category_id'] = i[1]
        category_list.append(category)

    # get list of foodchains
    foodchain_query = "SELECT * FROM foodchains ORDER BY foodchain;"
    cur.execute(foodchain_query)
    items = cur.fetchall()
    foodchain_list = []
    for i in items:
        FoodChain = {}
        FoodChain['foodchain_id'] = i[0]
        FoodChain['foodchain'] = i[1]
        foodchain_list.append(FoodChain)

    location_query = "SELECT city FROM cities WHERE city_id=" + session['location'] + ";"
    cur.execute(location_query)
    new_location = cur.fetchall()[0][0]

    return render_template('home.html', l=list_restaurants,
    category_list=category_list, foodchain_list=foodchain_list, location=new_location)


@app.route('/home/<location>',methods=['GET'])
def filter_page(location):
    foodchain = request.args.get('foodchain')
    categories1 = request.args.getlist('category')
    # print(category)
    for i in range(len(categories1)):
        categories1[i]=int(categories1[i])
    # return render_template('help.html',l=[foodchain,categories1,categories1==['Select Category'],"ARRAY"+str(categories1)])
    # '''
    query = "SELECT DISTINCT foodchain, address, postalcode, websites, array_agg(category), city, country, restaurants.id\n"\
            "FROM restaurants, foodchains, cities, categories \n"\
            "WHERE restaurants.city_id="+location+"\n"
    if foodchain!='-1':
        query+="AND restaurants.foodchain_id="+foodchain+"\n"
    if len(categories1)!=0:
        query+="AND restaurants.categories="+"ANY(ARRAY"+str(categories1)+")\n"
    query+="AND foodchains.foodchain_id = restaurants.foodchain_id\n" \
            "AND cities.city_id = restaurants.city_id\n" \
            "AND restaurants.categories = category_id\n" \
            "GROUP BY foodchain, address, postalcode, websites, city, country, restaurants.id\n" \
            ";"
    cur.execute(query)
    items = cur.fetchall()

    IDs = []

    list_restaurants = []
    for item in items:
        name = item[0]
        address = item[1]
        postalcode = item[2]
        websites = item[3]
        categories = item[4]
        city = item[5]
        country = item[6]
        id = item[7]
        IDs.append(int(id))
        temp_query = "SELECT categories FROM restaurant_categories WHERE id="+str(id)+";"
        cur.execute(temp_query)
        categories = cur.fetchall()[0][0]
        restaurant = dict()
        restaurant['name'] = name
        restaurant['addr'] = address
        restaurant['postalcode'] = postalcode
        restaurant['link'] = websites
        restaurant['city'] = city
        restaurant['country'] = country
        restaurant['categories'] = categories
        restaurant['websites'] = websites.split(',')
        list_restaurants += [restaurant]

    # index used in each of these queries
    location_query = "SELECT city FROM cities WHERE city_id="+location+";"
    cur.execute(location_query)
    new_location = cur.fetchall()[0][0]

    # new_category=[]
    # # restaurant_categories
    # category_query = "SELECT array_agg(DISTINCT a) FROM (SELECT unnest(categories) as a FROM restaurant_categories WHERE\n"\
    # "id=ANY(ARRAY"+str(IDs)+")) as temp;"
    # if len(categories1)!=0:
    #     category_query = "SELECT array_agg(DISTINCT category) FROM categories WHERE category_id=ANY(ARRAY"+str(categories1)+");"
    #
    # cur.execute(category_query)
    # new_category = cur.fetchall()[0][0]
    #
    # foodchain_query = "SELECT array_agg(DISTINCT foodchain) FROM foodchains, restaurants\n"\
    # "WHERE restaurants.foodchain_id=foodchains.foodchain_id AND restaurants.city_id="+location+";"
    # if foodchain!='-1':
    #     foodchain_query = "SELECT foodchain FROM foodchains WHERE foodchain_id="+foodchain+";"
    # cur.execute(foodchain_query)
    # new_foodchain = cur.fetchall()[0][0]

    return render_template('filter_page.html',l=list_restaurants,location=new_location,IDs=(len(IDs)==0))
    # '''

@app.route('/explore')
def explore():
    # The variable session['location'] contains the location.
    # query = "SELECT * FROM restaurants " \
    #         "WHERE location = " + session['location'] + " "+ \
    #         "GROUP BY name"
    # cur.execute(query)
    # items = cur.fetchall()
    list_restaurants = [
        {'name': "Restaurant1", 'addr': "Addr1", 'postalcode': "post1",
         'websites': "link1", 'city': "1", 'country': "country1", 'categories': "category1"},
        {'name': "Restaurant2", 'addr': "Addr2", 'postalcode': "post2",
         'websites': "link2", 'city': "2", 'country': "country2", 'categories': "category1"},
        {'name': "Restaurant3", 'addr': "Addr3", 'postalcode': "post3",
         'websites': "link3", 'city': "City3", 'country': "country3", 'categories': "category3"},
        {'name': "Restaurant4", 'addr': "Addr4", 'postalcode': "post4",
         'websites': "link4", 'city': "City4", 'country': "country4", 'categories': "category4"},
        {'name': "Restaurant5", 'addr': "Addr5", 'postalcode': "post5",
         'websites': "link5", 'city': "City5", 'country': "country5", 'categories': "category5"}
    ]
    return render_template('home.html', l=list_restaurants+list_restaurants)
    # '''

@app.route('/thank_you')
def thank_you():
    # we also need to check if the FoodChain added already exists
    query = "SELECT foodchain_id FROM foodchains WHERE foodchain='"+session['foodchain']+"';"
    cur.execute(query)
    query = cur.fetchall()
    # print(query)
    foodchain_id=-1
    if len(query)==0:
        query = "INSERT INTO foodchains (foodchain_id, foodchain) VALUES ((SELECT MAX(foodchain_id) + 1 FROM foodchains), '"+ session['foodchain'] +"');"
        cur.execute(query)
        foodchain_id = "SELECT foodchain_id FROM foodchains WHERE foodchain='"+session['foodchain']+"';"
        cur.execute(foodchain_id)
        foodchain_id = cur.fetchall()[0][0]
    else:
        foodchain_id=query[0][0]
    max_id = "SELECT max(id) FROM restaurants;"
    cur.execute(max_id)
    max_id = int(cur.fetchall()[0][0])+1
    for category in session['categories']:
        query = "INSERT INTO restaurants(id, dateadded, dateupdated, address, categories, city_id, country, keys, " \
            "latitude, longitude,foodchain_id, postalcode, province_id, sourceurls, websites)\n" \
            "VALUES("+str(max_id)+", CURRENT_TIMESTAMP(6), CURRENT_TIMESTAMP(6), '" + session['address']\
                + "'," + str(category) + "," + str(session['city']) + ", 'US', '', 0, 0,"+ str(foodchain_id)+", " \
                + session['postalcode'] + ", 1,'" + session['website'] + "','" + session['website'] + "');"
        print(query)
        cur.execute(query)
    con.commit()
    return render_template('thank_you.html')

@app.route('/list_restaurants', methods=['GET', 'POST'])
def list_restaurants():
    form = ListRestaurantForm()
    query = "SELECT * FROM cities order by city;"
    cur.execute(query)
    cities = cur.fetchall()
    form.city.choices = cities
    query = "SELECT category_id, category FROM categories ORDER BY category;"
    cur.execute(query)
    categories = cur.fetchall()
    form.categories.choices = categories
    if form.validate_on_submit():
        session['foodchain'] = form.foodchain.data
        session['categories'] = form.categories.data
        session['website'] = form.website.data
        session['address'] = form.address.data
        session['city'] = form.city.data
        session['postalcode'] = form.postalcode.data
        # print("Redirecting to the thank you page")
        return redirect(url_for('thank_you'))
    return render_template('list.html', form=form)


# Only used for testing the restaurant template created in restaurant_base.html
# restaurants.html imports the restaurant template
@app.route('/restaurant_card')
def restaurant_card():
    # name,addr,postalcode,link,city,country,category
    name = "Name of the Restaurant"
    addr = "Address of the Restaurant"
    postalcode = 123456
    link = "www.example.com"
    city = "Great City of Restaurant"
    country = "Country of Restaurant"
    category = "Fine Dining"
    return render_template('restaurants.html', name=name,
                           addr=addr, postalcode=postalcode, link=link, city=city,
                           country=country, category=category)

@app.route('/restaurant_details/<name>|<addr>|<postalcode>|<city>|<country>|<categories>')
def restaurant_details(name, addr, postalcode, city, country, categories):
    return render_template('restaurantsDetails.html', name=name,
                           addr=addr, postalcode=postalcode, city=city,
                           country=country, categories=categories)

@app.route('/data_insights')
def data_insights():
    query = "SELECT COUNT(DISTINCT id) FROM restaurants, cities " \
            "WHERE restaurants.city_id = cities.city_id AND cities.city_id = " \
            + session['location'] + ";"
    cur.execute(query)
    items = cur.fetchall()
    num_restaurants = items[0][0]
    query = "SELECT AVG(num_restaurants) " \
            "FROM (SELECT cities.city_id, COUNT(DISTINCT id) as num_restaurants FROM restaurants, cities " \
            "WHERE restaurants.city_id = cities.city_id " \
            "GROUP BY cities.city_id) as R;"
    cur.execute(query)
    items = cur.fetchall()
    average = round(items[0][0],2)

    query="SELECT rank FROM (SELECT *, row_number() over (order by num_restaurants DESC) AS rank FROM (SELECT " \
          "cities.city_id, COUNT(DISTINCT id) as num_restaurants FROM restaurants, cities WHERE restaurants.city_id = " \
          "cities.city_id GROUP BY cities.city_id ORDER BY num_restaurants DESC) as R) as R2 WHERE city_id = " \
          + session['location'] + ";"
    cur.execute(query)
    items = cur.fetchall()
    rank = items[0][0]
    query = "SELECT cities.city, COUNT(DISTINCT id) as num_restaurants FROM restaurants, cities WHERE " \
            "restaurants.city_id = cities.city_id GROUP BY cities.city_id ORDER BY num_restaurants DESC LIMIT 1;"
    cur.execute(query)
    items = cur.fetchall()
    highest_city = items[0][0]
    highest_number = items[0][1]
    query = "SELECT MAX(dateadded) FROM restaurants, cities WHERE restaurants.city_id = cities.city_id AND " \
            "cities.city_id = " + session['location'] +";"
    cur.execute(query)
    items = cur.fetchall()
    date = items[0][0]

    query="SELECT city FROM cities WHERE city_id =" + session['location'] + ";"
    cur.execute(query)
    items = cur.fetchall()
    city = items[0][0]

    query = "SELECT foodchain, array_length(restaurant_categories.categories, 1) FROM " \
          "restaurant_categories,restaurants,cities, foodchains WHERE cities.city_id = restaurants.city_id AND " \
          "restaurant_categories.id = restaurants.id AND foodchains.foodchain_id = restaurants.foodchain_id AND " \
          "cities.city_id = " + session['location'] + " ORDER BY array_length(restaurant_categories.categories, " \
                                                      "1) DESC LIMIT 1; "
    cur.execute(query)
    items = cur.fetchall()
    largest_restaurant = items[0][0]
    largest_categories = items[0][1]

    national_aggregate_x,national_aggregate_y,current_city_y = data_insights_city(int(session['location']))

    return render_template('data_insights.html', number=num_restaurants, average=average, rank=rank,
    highest_city=highest_city,highest_number=highest_number, date=date, city=city,
    largest_categories=largest_categories, largest_restaurant = largest_restaurant,
    national_aggregate_x=national_aggregate_x,national_aggregate_y=national_aggregate_y,current_city_y=current_city_y)

# @app.route('/data_insights/graph')
def data_insights_city(city):
    # list of foodchains
    d={}
    d['McDonalds'] = [228,368,522,597,847,957,1216,1221,287,369,477]
    d['Subway'] = [732,872,1066,1284,1410,841,1602,1718]
    d['Burger King']=[352,574,754,817,875,1090,1604]
    d['Dominos']=[423,551]
    d['Pizza Hut']=[390,634]
    d['KFC']=[261,415,508,723,796,853,906,1169,1528,1786]
    # city=10
    # city = int(session['location'])    # will be given as input
    print(city)
    city_query = "SELECT count(*) from cities;"
    cur.execute(city_query)
    number_of_cities = int(cur.fetchall()[0][0])
    national_aggregate_x = []
    national_aggregate_y = []
    city_query = "SELECT city FROM cities WHERE city_id="+str(city)+";"
    cur.execute(city_query)
    city_name = cur.fetchall()[0][0]
    current_city_y = []
    for j in d:
        l=d[j]
        national_aggregate_x.append(j)
        national_aggregate_query = "SELECT count(DISTINCT id) FROM restaurants WHERE\n"\
        "foodchain_id=ANY(ARRAY["+str(l)+"]);"
        cur.execute(national_aggregate_query)
        number_of_restaurants = int(cur.fetchall()[0][0])
        national_aggregate_y.append(round(number_of_restaurants/number_of_cities,2))
        current_city_query = "SELECT count(DISTINCT id) FROM restaurants WHERE\n"\
        "city_id="+str(city)+" AND foodchain_id=ANY(ARRAY["+str(l)+"]);"
        cur.execute(current_city_query)
        number_of_restaurants = int(cur.fetchall()[0][0])
        current_city_y.append(number_of_restaurants)

    # x_axis = [i for i in range(len(d.keys()))]
    # w = 0.4
    # fig,ax = plt.subplots()
    # r1 = ax.bar([i-w/2 for i in x_axis],current_city_y,w,label=city_name)
    # r2 = ax.bar([i+w/2 for i in x_axis],national_aggregate_y,w,label='National Avg')
    # ax.set_title('Number of Restaurants in City vs National Avg')
    # ax.set_xticks(x_axis)
    # ax.set_xticklabels(national_aggregate_x)
    # ax.legend()
    # # ax.legend(loc='upper right',bbox_to_anchor=(0.5,0.6))
    # ax.set_ylabel('Number of Restaurants')
    # ax.bar_label(r1)
    # ax.bar_label(r2)
    # plt.savefig("static/graph.png")
    # # plt.show()
    # # return render_template('graph.html')

    return (national_aggregate_x,national_aggregate_y,current_city_y)


if __name__ == "__main__":
    app.run(host="localhost",port=5015,debug=True)
