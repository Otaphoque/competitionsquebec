from flask import Flask, render_template, request, abort, redirect, url_for, session
from datetime import datetime
import json
import markdown
import markdown2
import re

app = Flask(__name__)

class Event:
    id = 0

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.organizer = kwargs.get("organizer")
        self.organizerLink = kwargs.get("organizerLink")
        self.type = kwargs.get("type")
        self.startDate_string = kwargs.get("startDate")
        self.startDate = datetime.strptime(kwargs.get("startDate"), "%Y-%m-%d")
        self.endDate_string = kwargs.get("endDate")
        self.endDate = datetime.strptime(kwargs.get("endDate"), "%Y-%m-%d")
        self.duration = (self.endDate - self.startDate).days + 1
        self.location = kwargs.get("location")
        self.registrationDeadline_fr = kwargs.get("registrationDeadline_fr")
        self.registrationDeadline_en = kwargs.get("registrationDeadline_en")
        self.language = kwargs.get("language")
        self.price = kwargs.get("price")
        self.links = kwargs.get("links")
        self.displayDate_fr = kwargs.get("displayDate_fr")
        self.displayDate_en = kwargs.get("displayDate_en")
        self.description_fr = self.read_and_convert_description("./static/description/fr/", kwargs.get("description"))
        self.description_en = self.read_and_convert_description("./static/description/en/", kwargs.get("description"))
        self.anotherDateYetAgain = kwargs.get("anotherDateYetAgain")
        self.smallDescription_fr = strip_markdown(self.description_fr)[:140]
        self.smallDescription_en = strip_markdown(self.description_en)[:140]

        Event.id += 1
        self.id = Event.id
    
    def read_and_convert_description(self, path, description):
        with open(f"{path}{description}.md", 'r', encoding='utf-8') as file:
            content = file.read()
            return markdown.markdown(content)

def strip_markdown(text):
    html = markdown2.markdown(text)
    stripped_text = re.sub('<[^<]+?>', '', html)
    return stripped_text

def find_names():
    names = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December",
    ]
    current = datetime.now().month
    return [names[(current - 1 + i) % 12] for i in range(12)]

def trouver_nom():
    names = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet",
        "Août", "Septembre", "Octbore", "Novembre", "Décembre",
    ]
    current = datetime.now().month
    return [names[(current - 1 + i) % 12] for i in range(12)]

def refresh():
    events = []
    Event.id = 0

    with open("./static/events.json", "r") as json_file:
        data = json.load(json_file)

    for event in data:
        haha = Event(**event)
        events.append(haha)

    global user_language
    months = trouver_nom() if user_language else find_names()
    return [events, group_by_month(events), find_names(), months]

def group_by_month(events):
    current_month = datetime.now().month - 1
    monthly_events = [[] for _ in range(12)]

    for event in events:
        event_month = int(event.startDate_string[5:7]) - 1
        index = (event_month - current_month) % 12
        monthly_events[index].append(event)

    return monthly_events

user_language = True

@app.route('/change_language', methods=['POST'])
def change_language():
    global user_language

    if request.method == 'POST':
        user_language = not user_language
        translations = get_translations(user_language)

    referring_page = request.referrer
    return redirect(referring_page or url_for('index'))

translations = {}

def get_translations(language):
    global translations 
    translation_file = f'./static/{"fr" if language else "en"}.json'
    with open(translation_file, 'r', encoding='utf-8') as file:
        translations = json.load(file)
    return translations

@app.route("/")
def index():
    truc = refresh()
    return render_template("/index.html", months=truc[1], months_name=truc[3], translations=get_translations(user_language), language=user_language)

@app.route("/<int:id>/info", methods=("GET",))
def info(id):
    truc = refresh()
    event = truc[0][id - 1]

    if event is None:
        abort(404)

    global translations
    translations['description_fr'] = event.description_fr
    translations['description_en'] = event.description_en

    return render_template("/info.html", event=event, translations=translations, language=user_language)

@app.route("/submit")
def submit():
    return render_template("/submit.html",  translations=translations)

def render_markdown(md_file_path):
    with open(f"{md_file_path}", 'r', encoding='utf-8') as file:
        content = file.read()
        return markdown.markdown(content, extensions=['nl2br'])

@app.route("/about")
def about():
    ressource = ""
    if user_language:
        with open(f"./static/ressources.md", 'r', encoding='utf-8') as file:
            md_content = file.read()
        ressource = markdown.markdown(md_content)
    else:
        with open(f"./static/resources.md", 'r', encoding='utf-8') as file:
            md_content = file.read()
        ressource = markdown.markdown(md_content)
    return render_template("/about.html",  translations=translations, ressource=ressource)

if __name__ == "__main__":
    refresh()
    app.run(debug=True, port=2004, host="0.0.0.0")
