import google_auth_oauthlib.flow
import googleapiclient.discovery
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.views.generic import View,TemplateView
import google.oauth2.credentials
import os
import json

SECRETS_FILE = "secrets.json"

# scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

REDIRECT_URI = "http://127.0.0.1:8000/rest/v1/calendar/redirect"
API_SERVICE_NAME = "calendar"
API_VERSION = "v3"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


# class HomePage(TemplateView):
#     template_name = "home.html"

class GoogleCalendarInitView(View):
    
    def get(self, request):
        # Create flow instance to manage the OAuth 2.0 Authorization
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            SECRETS_FILE, scopes=SCOPES
        )

        flow.redirect_uri = REDIRECT_URI

        authorized_url, state = flow.authorization_url(access_type="offline")

        # Store the state so the callback can verify the auth server response.
        request.session["state"] = state
        # with below code the django will automatically takes user to the authorization url
        return redirect(authorized_url)
        # return JsonResponse({"authorization_url": authorized_url})


class GoogleCalendarRedirectView(View):
    """
    A generic view for redirecting the token_access
    """
    def get(self, request):
        """
        A get request to get the user credentials straight from the
        browser.

        Returns:
            _type_: _description_
        """
        # Represent the state when creating the flow in the callback
        state = request.session["state"]
        # print("session state:  "+state)
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            SECRETS_FILE, scopes=SCOPES, state=state
        )
        flow.redirect_uri = REDIRECT_URI

        # fetching the OAuth 2.0 token.
        authorization_response = request.get_full_path()
        flow.fetch_token(authorization_response=authorization_response)

        # Saving credentials back to session in case access token was refreshed.
        credentials = flow.credentials
        request.session["credentials"] = credentials_dictionary(credentials)

        # Checking credentials are in session
        if "credentials" not in request.session:
            return redirect("v1/calendar/init")

        # Loading credentials from the session.
        credentials = google.oauth2.credentials.Credentials(
            **request.session["credentials"]
        )

        services = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials
        )

        # Returns the calendars on the user's calendar list
        calendar_list = services.calendarList().list().execute()

        # Getting user ID which is his/her email address
        calendar_id = calendar_list["items"][0]["id"]

        # Using userID to get all the events.
        events = services.events().list(calendarId=calendar_id).execute()
        if events["items"]:
            # if you don't require the clean form data and need full data from api you can
            # use no_clean_list method.
            data = create_list(events)
            return HttpResponse(
                # used json to beautify the json data
                json.dumps(data, indent=4), content_type="application/json"
            )
        return JsonResponse({"error": "There are no events in calendar"})


def create_list(events):
    """
    Create a cleaned list of all events
    and their important information like :
    summary,id,htmlLink,creator_email etc.

    Args:
        events (dictionary)

    Returns:
        dictionary
    """
    events_lists = []
    # using for loop to go to each event and fetch
    # data and keeping it in the dictionary variable data.
    for events_list in events["items"]:
        summary = events_list["summary"]
        id = events_list["id"]
        htmlLink = events_list["htmlLink"]
        creator_email = events_list["creator"]["email"]
        organizer_email = events_list["organizer"]["email"]
        start_time = str(events_list["start"]["dateTime"] + " - " + events_list["start"]["timeZone"])
        end_time = str(events_list["end"]["dateTime"] + " - " + events_list["end"]["timeZone"])
        eventType = events_list["eventType"]
        data = {
            "summary": summary,
            "id": id,
            "htmlLink": htmlLink,
            "creator_email": creator_email,
            "organizer_email": organizer_email,
            "startTime/timeZone": start_time,
            "endTime/timeZone": end_time,
            "eventType": eventType,
        }
        events_lists.append(data)
    return events_lists

# this function is created if you do not require any kind of clean data and need straight
# forward api get requested json response
def no_clean_list(events):
    """
    Return the api get requested json response
    without cleaning.
    Args:
        events : a dictionary variable

    Returns:
        list
    """
    events_lists = []
    for events_list in events["items"]:
        events_lists.append(events_list)
    return events_lists

def credentials_dictionary(credentials):
    """
    Fetch all the important details from
    credentials dictionary variable.

    Args:
        credentials : (dictionary)

    Returns:
        dictionary
    """
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }
