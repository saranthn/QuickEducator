
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, make_response, session
from datetime import date
import sqlalchemy

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

app.secret_key = 'vk2503'

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://st3523:3325@34.75.94.195/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  # cursor = g.conn.execute("SELECT name FROM test")
  # names = []
  # for result in cursor:
  #   names.append(result['name'])  # can also be accessed using result[0]
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  # context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return redirect("/home")

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')

@app.route('/logout')
def logout():
  session.pop('loggedin', None)
  session.pop('id', None)
  session.pop('username', None)
  return redirect(url_for('signIn'))

@app.route('/signIn', methods =['GET', 'POST'])
def signIn():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    cursor = g.conn.execute('SELECT * FROM Students WHERE username = %s ', (username, ))
    account = cursor.fetchone()
    # print(account)
    if account:
      # resp = make_response(redirect("/"))
      # resp.set_cookie('username', username)
      session['loggedin'] = True
      session['username'] = account['username']
      # session['name'] = account['first_name']
      print(session['username'])
      print('Logged in successfully !')
      return redirect("/")
    else:
      return render_template("signin_page.html")
  return render_template("signin_page.html")

@app.route('/signUp', methods =['GET', 'POST'])
def signUp():
  msg = 'Registered'
  if request.method == 'POST':
    userid = 100
    d1 = date.today().strftime("%m/%d/%Y")
    print("d1 =", d1)
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    username = request.form['username']
    email = request.form['email']
    gender = request.form['gender']
    dob = request.form['dob']
    phoneNo = request.form['phoneNo']
    password = request.form['password']
    university = request.form['university']
    degree = request.form['degree']
    course = request.form['course']
    country = request.form['country']
    cursor = g.conn.execute('SELECT * FROM Students WHERE username = %s', (username, ))
    account_username = cursor.fetchone()
    cursor.close()
    cursor = g.conn.execute('SELECT * FROM Students WHERE email = %s', (email, ))
    account_email = cursor.fetchone()
    cursor.close()
    if account_email or account_username:
      msg = 'Account already exists !'
      print(msg)
    else:
      # g.conn.execute('INSERT INTO Students VALUES('123', 'af12','ak','kk','M','kk@gmail.com','1234',d1,'columbia', 'MS', 'CS', 'USA', )')
      insert_query ="INSERT INTO Students VALUES('{}','{}','{}','{}','{}','{}',{},'{}','{}','{}','{}','{}')".format(userid, username,firstname,lastname,gender,email,phoneNo,dob,university, degree, course, country)
      print(insert_query)
      g.conn.execute(sqlalchemy.text(insert_query))
      print(msg)
    return redirect("signIn")
  else:
    return render_template("signUp_page.html")



@app.route('/home', methods=['POST','GET'])
def home():
  search_query = "select distinct first_name from professors"
  cursor = g.conn.execute(sqlalchemy.text(search_query))
  prof_names = []
  for result in cursor:
    prof_names.append(result['first_name'])  # can also be accessed using result[0]
  cursor.close()
  print(session)
  if request.method == 'GET':
    if session:
      context = dict(professors = prof_names)
      return render_template("home.html", **context)
    else:
      return redirect("signIn")
  else:
    name = request.form['q']
    difficulty = request.form['difficulty']
    sort = request.form['sort']
    order = request.form['order']
    prof = request.form['prof']

    search_query = "select * from courses c,teaches t,professors p where c.course_name ilike '%{}%' and c.course_difficulty_level ilike '%{}%' and c.course_id = t.course_id and t.user_id = p.user_id ".format(name, difficulty)

    if prof:
      search_query += "and p.first_name = '{}'".format(prof)
    print(search_query)
    if sort:
      search_query += "order by {} {}".format(sort, order)

    cursor = g.conn.execute(sqlalchemy.text(search_query))
    course_names = []
    for result in cursor:
      course_names.append(result)  # can also be accessed using result[0]
    cursor.close()
    context = dict(courses = course_names, professors = prof_names)
    return render_template("home.html", **context)


@app.route('/search_professor', methods=['POST'])
def search_professor():
  name = request.form['prof']
  search_query = "select * from professors where first_name ilike '%{}%'".format(name)
  cursor = g.conn.execute(sqlalchemy.text(search_query))
  names = []
  for result in cursor:
    names.append(result['first_name'])
  cursor.close()
  context = dict(professors = names)
  return render_template("home.html", **context)


@app.route('/courses')
def courses():
  course_id = request.args.get('course_id')
  print(course_id)
  
  cursor = g.conn.execute('Select * from courses where course_id = (%s)', course_id)
  course_details = cursor.fetchone()
  print(course_details)

  cursor = g.conn.execute('Select * from lectures_contains where course_id = (%s)', course_id)
  lectures = []
  for result in cursor:
    lectures.append(result)
  cursor.close()
  print(lectures)

  cursor = g.conn.execute('Select * from has h, review r where h.course_id = (%s) and r.review_id=h.review_id and r.review_type=h.review_type order by date_of_review desc', course_id)
  reviews = []
  for result in cursor:
    # a = str(result['date'])
    # result['date'] = a
    reviews.append(result)
  cursor.close()
  print(reviews)

  context = dict(course_details = course_details, lectures = lectures, reviews = reviews)
  return render_template("course.html", **context)

@app.route('/registered_courses', methods =['GET'])
def registered_courses():
  # context = dict(username = session['username'])
  if request.method == 'GET':
    
    return render_template("registered_courses.html")

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
