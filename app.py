import http.client
import requests
import datetime
import \
    strike  # For time being, strike is a private library. Has to be downloaded into the local from
# https://github.com/Strike-official/python-sdk
import flask
import requests
from flask import jsonify
from flask import request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# The public API link of the hosted server has to be added here.
# Use ngrok to easily make your api public
baseAPI = "https://234b-103-211-132-49.in.ngrok.io/"
url = ""
gym_data = {}
week_day = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}


@app.route('/', methods=['POST'])
def home():
    # Create a strike object
    strikeObj = strike.Create("getting_started", baseAPI + "respondBack")

    # First Question: What's your name?
    print(request.get_json())
    # print(request.get_json())
    quesObj1 = strikeObj.Question("name"). \
        QuestionText(). \
        SetTextToQuestion("Hi! What is your name?")
    quesObj1.Answer("true").TextInput()

    # Second Question: What's your location?
    quesObj2 = strikeObj.Question("location"). \
        QuestionText(). \
        SetTextToQuestion("Hi! What is your current location?")
    quesObj2.Answer("true").LocationInput("Your Location")

    return jsonify(strikeObj.Data())


@app.route('/respondBack', methods=['POST'])
def respondBack():
    data = request.get_json()
    name = data["user_session_variables"]["name"]
    location_lat = data["user_session_variables"]["location"]["latitude"]
    location_long = data["user_session_variables"]["location"]["longitude"]
    latitude = location_lat
    longitude = location_long
    direction = str(latitude) + "," + str(longitude)
    strikeObj = strike.Create("getting_started", baseAPI + "GymInfo")
    payload = {
        "limit": 30,
        "language": "en",
        "region": "in",
        "queries": ["Gym"],
        "coordinates": direction
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Host": "google-maps-search1.p.rapidapi.com",
        "X-RapidAPI-Key": "70c2ab0b3amsh8aa4e736881836cp1d253ajsnef71490f71f6"
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    response = response.json()

    question_card = strikeObj.Question("gym_name"). \
        QuestionCard().SetHeaderToQuestion(1, strike.FULL_WIDTH). \
        AddTextRowToQuestion(strike.H1, "Hello " + name + "\nBelow are the Gyms near you", "Black", True)
    ansObj = question_card.Answer(True).AnswerCardArray(strike.VERTICAL_ORIENTATION)

    for gym in response["response"]["places"]:
        gym_data[gym["name"]] = gym
        ansObj.AnswerCard(). \
            SetHeaderToAnswer(1, strike.HALF_WIDTH). \
            AddTextRowToAnswer(strike.H3, gym["name"], "black", False)
    return jsonify(strikeObj.Data())


@app.route('/GymInfo', methods=['POST'])
def gyms():
    # Create a strike object
    strikeObj = strike.Create("getting_started", baseAPI)
    data = request.get_json()
    name = data["user_session_variables"]["gym_name"][0]
    question_card = strikeObj.Question("gym_name"). \
        QuestionCard().SetHeaderToQuestion(1, strike.FULL_WIDTH). \
        AddTextRowToQuestion(strike.H1, "This " + name + "'s details are given below", "Black", True)
    ansObj = question_card.Answer(True).AnswerCardArray(strike.VERTICAL_ORIENTATION)

    ansObj.AnswerCard(). \
        SetHeaderToAnswer(1, strike.HALF_WIDTH). \
        AddGraphicRowToAnswer(strike.PICTURE_ROW, [gym_data[name]["photos_sample"][0]["large_photo_url"]], [""]). \
        AddTextRowToAnswer(strike.H3, gym_data[name]["full_address"], "Purple", False)
    if "phone_number" in gym_data[name]:
        ansObj.AddTextRowToAnswer(strike.H4, gym_data[name]["phone_number"], "black", False)
    ansObj.AddTextRowToAnswer(strike.H3, "Rating:", "blue", False)
    ansObj.AddTextRowToAnswer(strike.H4, gym_data[name]["rating"], "green", False)
    ansObj.AddTextRowToAnswer(strike.H3, "Click the below link to check the review", "blue", False)
    ansObj.AddTextRowToAnswer(strike.H4, gym_data[name]["reviews_link"], "green", False)
    ansObj.AddTextRowToAnswer(strike.H3, "Website:", "blue", False)
    if "website" in gym_data[name]:
        ansObj.AddTextRowToAnswer(strike.H4, gym_data[name]["website"], "green", False)
    else:
        ansObj.AddTextRowToAnswer(strike.H3, "No Website for this Gym I am afraid", "Red", False)
    ansObj.AddTextRowToAnswer(strike.H3, "Click on the below link to check the location on map", "blue", False)
    ansObj.AddTextRowToAnswer(strike.H4, gym_data[name]["place_link"], "green", False)

    today_day = datetime.datetime.today().weekday()
    day = week_day[today_day]
    status = gym_data[name]["opening_hours"][day][0]
    ansObj.AddTextRowToAnswer(strike.H4, "Opening Hours for today:", "blue", False)
    if status == "Closed":
        ansObj.AddTextRowToAnswer(strike.H4, status, "red", False)
    else:
        ansObj.AddTextRowToAnswer(strike.H4, status, "blue", False)

    ansObj.AnswerCard(). \
        SetHeaderToAnswer(1, strike.HALF_WIDTH). \
        AddTextRowToAnswer(strike.H4, "click here to go start over ^", "red", False)
    return jsonify(strikeObj.Data())


app.run(host='0.0.0.0', port=5001)
