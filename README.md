# SI 364 - Winter 2018 - Final Project

## Cameron Chandra - Fantasy Baseball App

In this project:
* Users are able to add their favorite baseball players to the system, select the players they would like to have on their team, see the stats for each player on their team, and view the latest tweets about players.
* The application saves: the entered players (along with their information, stats, and tweets), the entered teams, and the user profiles.
* Users can login through a registration form or through their Google accounts.
* Users who have not logged in cannot create their own teams, while logged in users can only see the teams they created. 

## Requirements
### Installations:

* `flask` library and all `flask`-related modules we have used in SI364
* The modules 'tweepy' and 'ohmysportsfeedspy' must be pip installed before use.

### Other
* When installing the ohmysportsfeedspy module, a folder called mysportsfeeds-python will also be downloaded.
* Because I was not able to get the Github Student Pack in time, I have committed my Twitter and MySportsFeed API to this repository.
* I have included a migrations folder to prove that I successfully used database migrations.
* In order to sign in using the OAuth protocol, you must have a Google account

## What to do to run this application

* `cd` to the directory in which the app files live
* run, in Python `python SI364final.py runserver`
* On the homepage, new users are directed to register. This directs users to a registration form.
* Previous users can login with their email address and password, or use Google OAuth.
* After login, add players for each position as you so choose. Users do not have to add a player at every position, this step simply adds players to the system.
* Disclaimer: Users have to be careful during this step. You must spell each player's name exactly correctly and the API does not work with non word characters, like periods. In other words, you cannot add players whose names contain J.R.
* By submitting players in the form, users are directed to the create team page. This form allows users to pick a team name, and choose from every player in the system to populate their roster.
* Using the navigation, users can now see their rosters (Rosters), see their team's stats (Team Stats), or see tweets about any inputted player (Player News). 
* Examples of data to enter: Anthony Rizzo, Javier Baez, Addison Russell, Kris Bryant, Buster Posey, Bryce Harper, Dexter Fowler, Ichiro Suzuki

## Routes in this application

* `/index` -> `index.html`
* `/register` -> `register.html`
* `/create_team` -> `team.html` (login restricted)
* `/show_teams` -> `roster.html` (login restricted)
* `/delete/<team>` -> redirects to 'show_teams'
* `/team/<id_num>` -> `single_team.html`
* `/update/<name>` -> `update_name.html` 
* `/show_stats` -> 'stat_roster.html'
* `/show_news -> `player_news.html`

### **Documentation README Requirements**

- [x] **Create a `README.md` file for your app that includes the full list of requirements from this page. The ones you have completed should be bolded or checked off.**

- [x] **The `README.md` file should use markdown formatting and be clear / easy to read.**

- [x] **The `README.md` file should include a 1-paragraph (brief OK) description of what your application does**

- [x] **The `README.md` file should include a detailed explanation of how a user can user the running application (e.g. log in and see what, be able to save what, enter what, search for what... Give us examples of data to enter if it's not obviously stated in the app UI!)**

- [x] **The `README.md` file should include a list of every module that must be installed with `pip` if it's something you installed that we didn't use in a class session. If there are none, you should note that there are no additional modules to install.**

- [x] **The `README.md` file should include a list of all of the routes that exist in the app and the names of the templates each one should render OR, if a route does not render a template, what it returns (e.g. `/form` -> `form.html`, like [the list we provided in the instructions for HW2](https://www.dropbox.com/s/3a83ykoz79tqn8r/Screenshot%202018-02-15%2013.27.52.png?dl=0) and like you had to on the midterm, or `/delete -> deletes a song and redirects to index page`, etc).**

### Code Requirements

- [x] **Ensure that your `SI364final.py` file has all the setup (`app.config` values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on `http://localhost:5000` (and the other routes you set up).**

- [x] **A user should be able to load `http://localhost:5000` and see the first page they ought to see on the application.**

- [x] **Include navigation in `base.html` with links (using `a href` tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, [like this](https://www.dropbox.com/s/hjcls4cfdkqwy84/Screenshot%202018-02-15%2013.26.32.png?dl=0) )**

- [x] **Ensure that all templates in the application inherit (using template inheritance, with `extends`) from `base.html` and include at least one additional `block`.**

- [x] **Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).**

- [x] **Must have data associated with a user and at least 2 routes besides `logout` that can only be seen by logged-in users.**

- [x] **At least 3 model classes *besides* the `User` class.**

- [x] **At least one one:many relationship that works properly built between 2 models.**

- [x] **At least one many:many relationship that works properly built between 2 models.**

- [x] **Successfully save data to each table.**

- [x] **Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).**

- [x] **At least one query of data using an `.all()` method and send the results of that query to a template.**

- [x] **At least one query of data using a `.filter_by(...` and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).**

- [x] **At least one helper function that is *not* a `get_or_create` function should be defined and invoked in the application.**

- [x] **At least two `get_or_create` functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).**

- [x] **At least one error handler for a 404 error and a corresponding template.**

- [x] **At least one error handler for any other error (pick one -- 500? 403?) and a corresponding template.**

- [x] **Include at least 4 template `.html` files in addition to the error handling template files.**

- [x] **At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.**

- [x] **At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that *does* accord with other involved sites' Terms of Service, etc).**

 - [x] **Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source *to the database* (in some way).**

- [x] At least one WTForm that sends data with a `GET` request to a *new* page. I am not 100% sure that I did this correctly so I won't bold it.

- [x] **At least one WTForm that sends data with a `POST` request to the *same* page. (NOT counting the login or registration forms provided for you in class.)**

- [x] **At least one WTForm that sends data with a `POST` request to a *new* page. (NOT counting the login or registration forms provided for you in class.)**

- [x] **At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.**

- [x] **Include at least one way to *update* items saved in the database in the application (like in HW5).**

- [x] **Include at least one way to *delete* items saved in the database in the application (also like in HW5).**

- [x] **Include at least one use of `redirect`.**

- [x] **Include at least two uses of `url_for`.**

- [x] **Have at least 5 view functions that are not included with the code we have provided.**

## Additional Requirements for additional points -- an app with extra functionality!

- [] (100 points) Include a use of an AJAX request in your application that accesses and displays useful (for use of your application) data.
- [x]  **(100 points) Create, run, and commit at least one migration.**
- [ ] (100 points) Include file upload in your application and save/use the results of the file. (We did not explicitly learn this in class, but there is information available about it both online and in the Grinberg book.)
- [ ]  (100 points) Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)
- [x]  **(100 points) Implement user sign-in with OAuth (from any other service), and include that you need a *specific-service* account in the README, in the same section as the list of modules that must be installed.**
