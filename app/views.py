"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest
from django.views.generic import ListView, DetailView
from django.db import connection
from django.utils.dateparse import parse_date

from .models import *

import requests;
import re;
import json;
import time;
import logging;

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect



def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    sighting_flowers = Flowers.objects.raw('SELECT * FROM FLOWERS ORDER BY comname ASC;') #flowers in the Flowers table

    #a bit of django "hacking" (aka group-by) needed to get unique names while also providing IDs (required by django raw() method)
    all_people = Sightings.objects.raw('SELECT DISTINCT person, id FROM SIGHTINGS GROUP BY person ORDER BY person ASC;')
    all_locations = Sightings.objects.raw('SELECT DISTINCT location, id FROM SIGHTINGS GROUP BY location ORDER BY location ASC;')
    all_flowers = Sightings.objects.raw('SELECT DISTINCT name, id FROM SIGHTINGS GROUP BY name ORDER BY name ASC;') #flowers in the sightings table
    image_url = None
    sighting_lookup = None
    insertAttempted = False
    returnMessage = None
    all_sightings = None
    updateStatus = "Lookup"

    if request.method == 'POST':

        #QUERY functionality
        if 'flowerdropdown' in request.POST:
            all_sightings = Sightings.objects.raw('SELECT * FROM SIGHTINGS WHERE name = "%s" ORDER BY sighted DESC LIMIT 10;' % (request.POST['flowerdropdown']))
            image_url = search(request.POST['flowerdropdown'], 1)
            
            


        #UPDATE functionality
        if ('sighting_update_flower' in request.POST) or ('sighting_update_person' in request.POST) or ('sighting_update_location' in request.POST) or ('sighting_update_date' in request.POST):
            updateStatus = "Attempted: "


            if (request.POST['sighting_update_flower'] != '') and (request.POST['sighting_update_person'] != '') and (request.POST['sighting_update_location'] != '') and (request.POST['sighting_update_date'] != ''):


                date = parse_date(request.POST['sighting_update_date'])
                
                #The UPDATE portion
                if(request.POST['SubmitButton'] == 'Update'):

                    with connection.cursor() as cursor:
                        cursor.execute('UPDATE SIGHTINGS SET name = %s, person = %s, location = %s, sighted = %s WHERE id = %s;', 
                                       ([request.POST['sighting_update_flower'], request.POST['sighting_update_person'], request.POST['sighting_update_location'], date, request.POST['entryID'] ] ))
                        row = cursor.fetchone()

                    updateStatus = "Successful"

                #The LOOKUP portion
                else:
                    sighting_lookup =  Sightings.objects.raw('SELECT * FROM SIGHTINGS WHERE name = "%s" AND person = "%s" AND location = "%s" AND sighted = "%s"' % 
                                                             ((request.POST['sighting_update_flower'], request.POST['sighting_update_person'], request.POST['sighting_update_location'], date)))
                    if(sighting_lookup): #entry found with this value
                        updateStatus = "Update"
                    else:
                        updateStatus += "Not Found"
            
            #if updating and leave all fields empty, delete that entry from database
            elif ((request.POST['SubmitButton'] == 'Update') and (request.POST['sighting_update_flower'] == '') and (request.POST['sighting_update_person'] == '') and (request.POST['sighting_update_location'] == '') and (request.POST['sighting_update_date'] == '')):
                with connection.cursor() as cursor:
                        cursor.execute('DELETE FROM SIGHTINGS WHERE id = %s;', ([request.POST['entryID']]))
                        row = cursor.fetchone()

                updateStatus = "Successful"
            else:
                updateStatus += "Incomplete"
        else: 
            updateStatus = "Lookup"


        #INSERT functionality
        if ('sighted_flower' in request.POST) or ('sighted_name' in request.POST) or ('sighted_location' in request.POST) or ('sighted_date' in request.POST):
            insertAttempted = True

            #check if all forms are completed
            if (request.POST['sighted_flower'] != '') and (request.POST['sighted_name'] != '') and (request.POST['sighted_location'] != '') and (request.POST['sighted_date'] != ''):

                #check if date is in a correct format
                date = parse_date(request.POST['sighted_date'])


                if(date != None):
                    with connection.cursor() as cursor:
                        cursor.execute('INSERT INTO SIGHTINGS(name, person, location, sighted) VALUES(%s, %s, %s, %s);', [request.POST['sighted_flower'], request.POST['sighted_name'], request.POST['sighted_location'], date] )
                        row = cursor.fetchone()
                    returnMessage = "Sighting successfully recorded into database!"
                else:
                    returnMessage = "Please format the date as YYYY-MM-DD"
            else:
                returnMessage = "Please fill out all fields before submitting your sighting!"

    context = {'all_flowers': all_flowers,
               'all_sightings': all_sightings,
               'all_people': all_people,
               'sighting_flowers': sighting_flowers,
               'all_locations': all_locations,
               'return_message': returnMessage,
               'insert_attempted': insertAttempted,
               'updateStatus': updateStatus,
               'sighting_lookup': sighting_lookup,
               'image_url': image_url,
               'title':'Home Page',
               'year':datetime.now().year}
    return render(request, 'app/index.html', context)
    
    

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Contact me',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'CIS4301 Final Project',
            'year':datetime.now().year,
        }
    )

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'app/signup.html', {'form': form})


# adapted from https://github.com/deepanprabhu/duckduckgo-images-api, used to get the url of the first search result of an image on DuckDuckGo
def search(keywords, max_results=None):
    url = 'https://duckduckgo.com/';
    params = {
    	'q': keywords
    };

    #   First make a request to above URL, and parse out the 'vqd'
    #   This is a special token, which should be used in the subsequent request
    res = requests.post(url, data=params)
    searchObj = re.search(r'vqd=([\d-]+)\&', res.text, re.M|re.I);

    headers = {
        'dnt': '1',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'x-requested-with': 'XMLHttpRequest',
        'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6,ms;q=0.4',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'referer': 'https://duckduckgo.com/',
        'authority': 'duckduckgo.com',
    }

    params = (
    ('l', 'wt-wt'),
    ('o', 'json'),
    ('q', keywords),
    ('vqd', searchObj.group(1)),
    ('f', ',,,'),
    ('p', '2')
    )

    requestUrl = url + "i.js";

    count = 0

    while count <= max_results :
        while True:
            try:
                res = requests.get(requestUrl, headers=headers, params=params);
                data = json.loads(res.text);
                count = len(data["results"])
                break;
            except ValueError as e:
                time.sleep(5);
                continue;
        count = len(data["results"])
        return(data["results"][0]["image"])

