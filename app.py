import http.client
import requests
import \
    strike  # For timbeing, strike is a private library. Has to be downloaded into the local from
# https://github.com/Strike-official/python-sdk
import flask
import requests
from flask import jsonify
from flask import request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# The public API link of the hosted server has to be added here.
# Use ngrok to easily make your api public
baseAPI = "https://6aad-103-211-132-49.in.ngrok.io/"
url = "https://google-maps-search1.p.rapidapi.com/search"
gymdata = {}


@app.route('/', methods=['POST'])
def home():
    ## Create a strike object
    strikeObj = strike.Create("getting_started", baseAPI + "respondBack")

    # First Question: Whats your name?
    print(request.get_json())
    # print(request.get_json())
    quesObj1 = strikeObj.Question("name"). \
        QuestionText(). \
        SetTextToQuestion("Hi! What is your name?")
    quesObj1.Answer("true").TextInput()

    # Second Question: Whats your location?
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
    dir = str(latitude) + "," + str(longitude)
    strikeObj = strike.Create("getting_started", baseAPI + "GymInfo")
    payload = {
        "limit": 30,
        "language": "en",
        "region": "in",
        "queries": ["Gym", "Fitness"],
        "coordinates": dir
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
        gymdata[gym["name"]] = gym
        ansObj.AnswerCard(). \
            SetHeaderToAnswer(1, strike.HALF_WIDTH). \
            AddTextRowToAnswer(strike.H3, gym["name"], "black", False)
        # if "phone_number" in gym:
        #     ansObj.AddTextRowToAnswer(strike.H4, gym["phone_number"], "black", False)
        # if "address" in gym:
        #     ansObj.AddTextRowToAnswer(strike.H3, gym["address"], "black", False)

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
        AddGraphicRowToAnswer(strike.PICTURE_ROW, [gymdata[name]["photos_sample"][0]["large_photo_url"]], [""]). \
        AddTextRowToAnswer(strike.H3, gymdata[name]["full_address"], "black", False)
    if "phone_number" in gymdata[name]:
        ansObj.AddTextRowToAnswer(strike.H4, gymdata[name]["phone_number"], "black", False)

    ansObj.AnswerCard().\
        SetHeaderToAnswer(1, strike.HALF_WIDTH).\
        AddTextRowToAnswer(strike.H4, "click here to go start over ^", "red", False)
    return jsonify(strikeObj.Data())


app.run(host='0.0.0.0', port=5001)
