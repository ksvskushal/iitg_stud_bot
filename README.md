# IITG Student Buddy

An virtual assistant/chat bot that helps students & professors by answering all common queries based on natural language processing and basic database management.


## Working
The bot is built using Google's Dialogflow framework. Dialogflow uses natural language processing to process the user's request and constantly evolves from previous experience as it is based mainly on machine learning. For storing the database of student's schedule, Dialogflow relies on some external API/script. For this we are using a RESTful API(built using flask and deployed on DigitalOcean) at the backend which manages Dialogflow GET/POST to interact with schedule database. The bot is then deployed to facebook messenger and Alexa for human–computer interaction.

### Details

This repo contains the contains webhook part for the Buddy bot. The webhook format is specificed [here](https://developers.google.com/actions/reference/v1/dialogflow-webhook).

### Setting up webhook server

Create a vitual enviroment if you have deal with multiple python projects.

```
sudo apt-get install python-virtualenv
or
sudo easy_install virtualenv
or
sudo pip3 install virtualenv
```

```
mkdir ~/virtualenvironment
virtualenv ~/virtualenvironment/my_new_app
cd ~/virtualenvironment/my_new_app/bin
source activate
```
Install dependencies using

```
sudo pip3 install -r requirements.txt
```

The site has to be hosted on SSL secured site so that Dialogflow can communicate with it. Add the site url in Dialogflow's fulfillment tab.


## Built With

* [Dialogflow](https://dialogflow.com/) - Dialogflow is a Google-owned developer of human–computer interaction technologies based on natural language conversations.
* [Flask](http://flask.pocoo.org/) -  Flask is a microframework for Python based on Werkzeug, Jinja 2 and good intentions.
* [MySQL](https://www.mysql.com/) - MySQL is an open-source relational database management system.


## Authors

* **Kushal KSVS**  - [IITG Student Buddy](https://github.com/ksvskushal/iitg_stud_bot/)
* **[Vivek Raj](https://github.com/codervivek)**
