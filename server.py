
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
from flask import Flask, request, render_template, g, redirect, Response, url_for, make_response, session, flash
from datetime import date, datetime
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

@app.route('/logout')
def logout():
  session.pop('loggedin', None)
  session.pop('id', None)
  session.pop('username', None)
  session.pop('usertype', None)
  return redirect(url_for('signIn'))

@app.route('/signIn', methods =['GET', 'POST'])
def signIn():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    args = (username, )
    cursor = g.conn.execute('SELECT * FROM Students WHERE username = %s ', args)
    account = cursor.fetchone()
    if account and (username == account['username'] and password == account['password']):
      session['loggedin'] = True
      session['username'] = account['username']
      session['usertype'] = 'student'
      print(session['username'])
      print('Logged in successfully !')
      return redirect("/")
    else:
      flash('Invalid username/password')
      return render_template("signin_page.html")
  else:
    if session:
      if session['usertype'] == 'student':
        return redirect("/")
      else:
        return redirect("/professor_home")
    else:
      return render_template("signin_page.html")

@app.route('/signUp', methods =['GET', 'POST'])
def signUp():
  msg = 'Registered'
  if request.method == 'POST':
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
      msg = 'Account email or username exists!'
      print(msg)
      flash(msg)
      return render_template("signup_page.html")
    else:
      g.conn.execute("INSERT INTO Students(username, first_name, last_name, gender, email, contact_no, DOB, university, degree, course, country, password) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (username,firstname,lastname,gender,email,phoneNo,dob,university, degree, course, country, password))
      print(msg)
      return redirect("signIn")
  else:
    if session:
      if session['usertype'] == 'student':
        return redirect("/")
      else:
        return redirect("/professor_home")
    else:
      return render_template("signup_page.html")

@app.route('/professor_signIn', methods =['GET', 'POST'])
def professor_signIn():
  print('loggedin')
  print('loggedin')
  if request.method == 'POST':
    print('in post')
    username = request.form['username']
    password = request.form['password']
    cursor = g.conn.execute('SELECT * FROM Professors WHERE username = %s ', (username, ))
    account = cursor.fetchone()
    if account and (username == account['username'] and password == account['password']):
      session['loggedin'] = True
      session['username'] = account['username']
      session['usertype'] = 'professor'
      print(session['username'])
      print('Logged in successfully !')
      return redirect("/professor_home")
    else:
      flash('Invalid username/password')
      return render_template("professor_signin.html")
  else:
    if session:
      if session['usertype'] == 'student':
        return redirect("/")
      else:
        return redirect("/professor_home")
    else:
      return render_template("professor_signin.html")


@app.route('/professor_signUp', methods =['GET', 'POST'])
def professor_signUp():
  msg = 'Registered'
  if request.method == 'POST':
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
    yoe = request.form['yoe']
    qualification = request.form['qualification']
    research = request.form['research']
    cursor = g.conn.execute('SELECT * FROM Professors WHERE username = %s', (username, ))
    account_username = cursor.fetchone()
    cursor.close()
    cursor = g.conn.execute('SELECT * FROM Professors WHERE email = %s', (email, ))
    account_email = cursor.fetchone()
    cursor.close()
    if account_email or account_username:
      msg = 'Account email or username exists!'
      print(msg)
      flash(msg)
      return render_template("professor_signup.html")
    else:
      g.conn.execute("INSERT INTO Professors(username, first_name, last_name, gender, email, contact_no, DOB, years_of_experience, qualification, research_area, password) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (username, firstname, lastname, gender, email, phoneNo, dob, yoe, qualification, research, password))
      print(msg)
      return redirect("professor_signIn")
  else:
    if session:
      if session['usertype'] == 'student':
        return redirect("/")
      else:
        return redirect("/professor_home")
    else:
      return render_template("professor_signup.html")


@app.route('/home', methods=['POST','GET'])
def home():
  cursor = g.conn.execute("select * from professors")
  prof_names = []
  for result in cursor:
    prof_names.append(result)
  cursor.close()
  print(session)
  if request.method == 'GET':
    if session:
      if session['usertype'] == 'student':
        user_name = session['username']
        cursor = g.conn.execute('Select user_id from students where username = (%s)', user_name)
        userid = cursor.fetchone()['user_id']
        print(userid)

        cursor = g.conn.execute("select * from registers r, courses c where r.course_id = c.course_id and r.status = 'Enrolled' and r.user_id = %s order by c.course_rating desc limit 1", (userid, ))
        domain = cursor.fetchone()
        print(domain)
        if domain:
          rec = domain['course_domain'][0]
        else:
          rec = "Computer Science"

        cursor = g.conn.execute("select * from courses where %s=ANY(course_domain) order by course_rating desc limit 3", (rec, ))
        rec_course_names = []
        for result in cursor:
          rec_course_names.append(result)
        cursor.close()
        print(rec_course_names)
        context = dict(professors = prof_names, rec_course_names = rec_course_names)
        return render_template("home.html", **context)
      else:
        return redirect("/professor_home")
    else:
      return redirect("signIn")
  else:
    name = request.form['q']
    difficulty = request.form['difficulty']
    sort = request.form['sort']
    order = request.form['order']
    prof = request.form['prof']

    name = "%{}%".format(name)
    difficulty = "%{}%".format(difficulty)

    args = (name, difficulty)
    query = "select * from courses c,teaches t,professors p where c.course_name ilike %s and c.course_difficulty_level ilike %s and c.course_id = t.course_id and t.user_id = p.user_id "

    if prof:
      query += "and p.user_id = %s"
      args = (name, difficulty, prof)
    if sort:
      query += "order by {} {}".format(sort, order)

    print(query)  
    cursor = g.conn.execute(query, args)
    course_names = []
    for result in cursor:
      course_names.append(result)
    cursor.close()
    context = dict(courses = course_names, professors = prof_names)
    return render_template("home.html", **context)


@app.route('/professor_home', methods=['POST','GET'])
def professor_home():
  if request.method == 'GET':
    if session:
      if session['usertype'] == 'professor':
        prof_user_name = session['username']
        cursor = g.conn.execute("select * from courses c,teaches t,professors p where c.course_id = t.course_id and t.user_id = p.user_id and p.username = %s", (prof_user_name, ))
        courses = []
        for result in cursor:
          courses.append(result)
        cursor.close()
        context = dict(courses = courses)
        print(courses)
        return render_template("professor_home.html", **context)
      else:
        return redirect("/")
    else:
      return redirect("/professor_signIn")


@app.route('/professor/courses')
def professor_courses():
  if session and session['usertype'] == 'professor':
    course_id = request.args.get('course_id')
    #print(course_id)
    
    cursor = g.conn.execute('Select * from courses where course_id = (%s)', course_id)
    course_details = cursor.fetchone()
    #print(course_details)

    cursor = g.conn.execute('Select * from students where user_id in (select user_id from registers where course_id = (%s))', course_id)
    students = []
    for result in cursor:
      students.append(result)
    cursor.close()
    #print(professors)

    cursor = g.conn.execute('Select * from lectures_contains where course_id = (%s)', course_id)
    lectures = []
    for result in cursor:
      lectures.append(result)
    cursor.close()
    #print(lectures)

    cursor = g.conn.execute('Select * from has h, review r where h.course_id = (%s) and r.review_id=h.review_id and r.review_type=h.review_type order by date_of_review desc', course_id)
    reviews = []
    for result in cursor:
      reviews.append(result)
    cursor.close()
    #print(reviews)

    context = dict(course_details = course_details, students = students, lectures = lectures, reviews = reviews)
    return render_template("professor_course.html", **context)
  else:
    return redirect('/')


@app.route('/add_lecture', methods=["POST"])
def add_lecture():

  topic = request.form['topic']
  description = request.form['description']
  course_id = request.args['course_id']

  if topic and description:
    cursor = g.conn.execute("Select max(lecture_id) as max_id from lectures_contains where course_id = %s", (course_id, ))
    max_id = cursor.fetchone()['max_id']

    if max_id:
      print(max_id)
      next_id = int(max_id)+1
    else:
      next_id = 1

    g.conn.execute("Insert into lectures_contains(lecture_id, topic, description, course_id) values(%s, %s, %s, %s)", (next_id, topic, description, course_id))
    return redirect(url_for('professor_courses', course_id=course_id))


@app.route('/add_course', methods=["POST"])
def add_course():

  course_name = request.form['course_name']
  course_fee = request.form['course_fee']
  difficulty = request.form['difficulty']
  course_domain = request.form['course_domain']

  if course_name and course_fee:
    domains = [course_domain]
    g.conn.execute("Insert into courses(course_name, course_rating, course_domain, course_difficulty_level, course_fee) values(%s, 5, %s, %s, %s)", (course_name, domains, difficulty, course_fee))

    cursor = g.conn.execute("SELECT last_value FROM course_id_seq;")
    curr_course_id = cursor.fetchone()['last_value']
    print(curr_course_id)

    user_name = session['username']
    cursor = g.conn.execute('Select user_id from professors where username = (%s)', user_name)
    userid = cursor.fetchone()['user_id']
    print(userid)

    g.conn.execute('INSERT into teaches(user_id, course_id) VALUES ((%s), (%s))', userid, curr_course_id)

    return redirect(url_for('professor_home'))


@app.route('/delete_course', methods=["POST"])
def delete_course():

  course_id = request.args['course_id']
  g.conn.execute('delete from registers where course_id = (%s)', course_id)
  g.conn.execute('delete from teaches where course_id = (%s)', course_id)
  g.conn.execute('delete from has where course_id = (%s)', course_id)
  g.conn.execute('delete from courses where course_id = (%s)', course_id)
  return redirect(url_for('professor_home'))


@app.route('/delete_lecture', methods=["POST"])
def delete_lecture():
  course_id = request.args['course_id']
  lecture_id = request.args['lecture_id']

  g.conn.execute('delete from lectures_contains where lecture_id = (%s) and course_id = (%s)', lecture_id, course_id)
  return redirect(url_for('professor_courses', course_id=course_id))


@app.route('/professors')
def professors():
  if session:
    if session['usertype'] == 'student':
      prof_id = request.args.get('prof_id')
      print(prof_id)
      
      cursor = g.conn.execute('Select * from professors where user_id = (%s)', prof_id)
      prof_details = cursor.fetchone()
      print(prof_details)

      cursor = g.conn.execute('Select * from belongs_to b, organisation o where b.user_id = (%s) and b.org_id = o.org_id', prof_id)
      org_details = cursor.fetchone()
      print(org_details)

      cursor = g.conn.execute('Select * from courses where course_id in (select course_id from teaches where user_id = (%s)) order by course_rating desc limit 10', prof_id)
      courses = []
      for result in cursor:
        courses.append(result)
      cursor.close()
      print(courses)

      cursor = g.conn.execute('Select * from gets g, review r where g.user_id = (%s) and r.review_id=g.review_id and r.review_type=g.review_type order by r.date_of_review desc', prof_id)
      reviews = []
      for result in cursor:
        reviews.append(result)
      cursor.close()
      print(reviews)

      context = dict(prof_details = prof_details, org_details = org_details, courses = courses, reviews = reviews)
      return render_template("professor.html", **context)
    else:
      return redirect('/professor_home')
  else:
    return redirect('/')


@app.route('/courses')
def courses():
  if session:
    if session['usertype'] == 'student':
      course_id = request.args.get('course_id')
      #print(course_id)
      
      cursor = g.conn.execute('Select * from courses where course_id = (%s)', course_id)
      course_details = cursor.fetchone()
      #print(course_details)

      cursor = g.conn.execute('Select * from professors where user_id in (select user_id from teaches where course_id = (%s))', course_id)
      professors = []
      for result in cursor:
        professors.append(result)
      cursor.close()
      #print(professors)

      cursor = g.conn.execute('Select * from lectures_contains where course_id = (%s)', course_id)
      lectures = []
      for result in cursor:
        lectures.append(result)
      cursor.close()
      #print(lectures)

      cursor = g.conn.execute('Select * from has h, review r where h.course_id = (%s) and r.review_id=h.review_id and r.review_type=h.review_type order by date_of_review desc', course_id)
      reviews = []
      for result in cursor:
        reviews.append(result)
      cursor.close()
      #print(reviews)

      user_name = session['username']
      cursor = g.conn.execute('Select user_id from students where username = (%s)', user_name)
      userid = cursor.fetchone()['user_id']
      print(userid)

      cursor = g.conn.execute('Select * from registers where user_id = (%s) and course_id = (%s)', userid, course_id)
      registered_course = cursor.fetchone()
      if registered_course:
        status = registered_course['status']
      else:
        status = "None"
      print(status)

      context = dict(course_details = course_details, professors = professors, lectures = lectures, reviews = reviews, status = status)
      return render_template("course.html", **context)
    else:
      return redirect('professor_home')
  else:
    return redirect('/')


@app.route('/add_review', methods=["POST"])
def add_review():

  feedback = request.form['feedback']
  review_type = request.args['review_type']

  if feedback:
    if review_type == 'Course':
      course_id = request.args['course_id']
      today_date = datetime.today().strftime('%Y-%m-%d')   

      g.conn.execute("Insert into review(review_type, feedback, date_of_review) values('Course', %s, %s)", (feedback, today_date))

      cursor = g.conn.execute("SELECT last_value FROM review_id_seq;")
      review_id = cursor.fetchone()['last_value']

      g.conn.execute("Insert into has(course_id, review_id, review_type) values(%s, %s,'Course')", (course_id, review_id))
      return redirect(url_for('courses', course_id=course_id))
    else:
      prof_id = request.args['prof_id']
      today_date = datetime.today().strftime('%Y-%m-%d')   

      g.conn.execute("Insert into review(review_type, feedback, date_of_review) values('Professor', %s, %s)", (feedback, today_date))

      cursor = g.conn.execute("SELECT last_value FROM review_id_seq;")
      review_id = cursor.fetchone()['last_value']

      g.conn.execute("Insert into gets(user_id, review_id, review_type) values(%s, %s,'Professor')", (prof_id, review_id))
      return redirect(url_for('professors', prof_id=prof_id))
  
  
@app.route('/enroll', methods=["POST"])
def enroll():
  course_id = request.args['course_id']
  user_name = session['username']
  cursor = g.conn.execute('Select user_id from students where username = (%s)', user_name)
  user_id = cursor.fetchone()['user_id']

  cursor = g.conn.execute('Select * from registers where course_id = (%s) and user_id = (%s)', course_id, user_id)
  results = []
  for result in cursor:
    results.append(result)
  cursor.close()

  today_date = datetime.today().strftime('%Y-%m-%d') 

  if results:
    g.conn.execute("update registers set status='Enrolled',reg_date = %s where user_id = %s and course_id = %s", (today_date, user_id, course_id))
  else:
    g.conn.execute("Insert into registers(user_id, course_id, status, reg_date) values(%s, %s, 'Enrolled', %s)", (user_id, course_id, today_date))  
  return redirect(url_for('courses', course_id=course_id))



@app.route('/add_wishlist', methods=["POST"])
def add_wishlist():
  course_id = request.args['course_id']
  user_name = session['username']
  cursor = g.conn.execute('Select user_id from students where username = (%s)', user_name)
  user_id = cursor.fetchone()['user_id']

  cursor = g.conn.execute('Select * from registers where course_id = (%s) and user_id = (%s)', course_id, user_id)
  results = []
  for result in cursor:
    results.append(result)
  cursor.close()

  today_date = datetime.today().strftime('%Y-%m-%d')   

  if results:
    g.conn.execute("update registers set status='Wishlist',reg_date = %s where user_id = %s and course_id = %s", (today_date, user_id, course_id))
  else:
    g.conn.execute("Insert into registers(user_id, course_id, status, reg_date) values(%s, %s, 'Wishlist', %s)", (user_id, course_id, today_date))  
  
  return redirect(url_for('courses', course_id=course_id))


@app.route('/registered_courses', methods=['GET'])
def registered_courses():
  # context = dict(username = session['username'])
  if request.method == 'GET':
    if session:
      if session['usertype'] == 'student':
        username = session['username']
        print(username)
        cursor = g.conn.execute('SELECT user_id FROM Students WHERE username = %s', (username, ))
        account_userid = cursor.fetchone()
        cursor.close()
        print(account_userid[0])

        cursor = g.conn.execute('SELECT r.course_id as id, c.course_name as name, r.status as status, r.reg_date as reg_date FROM Registers r, Courses c WHERE user_id = (%s) and r.course_id = c.course_id', (account_userid[0], ))
        reg_courses = []
        for result in cursor:
          reg_courses.append(result)
        cursor.close()
        print(reg_courses)
        context = dict(courses = reg_courses)
        return render_template("registered_courses.html", **context)
      else:
        return redirect('professor_home')
    else:
      return redirect('/')


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
