<div align="center">

# Weather Assignment

    A pure Django based api for accessing user account and representing all the events

</div>

## 📖 Prerequisite
- OS used [Ubuntu](https://ubuntu.com/download/desktop)
- Install [Python3](https://www.python.org/)

<h2> Steps for running the assignment :</h2>


```sh
git clone ###
```
```sh
cd calendar_assignment
```
```sh
python -m venv .venv
```
```sh
source .venv/bin/activate
```
```sh
pip install -r requirements.txt
```
```sh
python manage.py migrate
```
```sh
python manage.py runserver
```

<h2> Steps for API access: </h2>

* Go to http://127.0.0.1:8000/rest/v1/calendar/init/ to get to the google credentials page.
* After signin with you google account you will be taken to a httpResponse page to get your events in json format like an api.


<h3> API endpoints </h3>

```
http://127.0.0.1:8000/rest/v1/calendar/init/
http://127.0.0.1:8000/rest/v1/calendar/redirect/
```