import json
import requests
from google.cloud import vision
import os
from google.oauth2 import service_account


def get_building_properties(postalcode, housenumber, window_count):
    building_properties = {}
    #BAG API paramers
    url = 'https://bag.basisregistraties.overheid.nl/api/v1/nummeraanduidingen'
    headers = {'X-Api-Key'  : '8d2869b4-2b78-4596-b290-6f2e1e8b4661'}
    adress = {'postcode': postalcode.upper(), 'huisnummer': str(housenumber)}
    #Bag request adress data
    adress_data = requests.get(url, headers=headers, params=adress).json()
    #Get object URL
    object_url = adress_data.get('_embedded').get('nummeraanduidingen')[0].get('_links').get('adresseerbaarObject').get('href')
#
#
    #Get object data
    object_data = requests.get(object_url, headers=headers).json()
    #Get object location - used in google maps api
    object_location = object_data.get('_embedded').get('geometrie').get('coordinates')
    #get pand URL
    pand_url = object_data.get('_links').get('pandrelateringen')[0].get('href')
    pand_data = requests.get(pand_url, headers=headers).json()
    pand_id = pand_data.get('identificatiecode')
#
    #WFS api
#
    gebruiksdoel_Oppervlakte_data = requests.get('https://geodata.nationaalgeoregister.nl/bag/wfs?'
                                    'SERVICE=WFS&'
                                    'REQUEST=GetFeature&'
                                    'TYPENAMES=bag:verblijfsobject&'
                                    'CQL_FILTER=pandidentificatie='
                                    + pand_id +
                                    '&outputFormat=json'
    ).json()
#
    #Create dict with information, does select first building now
    temp = gebruiksdoel_Oppervlakte_data.get('features')[0].get('properties')
    building_properties['square_meters']          = temp.get('oppervlakte')
    building_properties['building_functionality'] = temp.get('gebruiksdoel')
    building_properties['Place_name']             = temp.get('woonplaats')
    #get buildingyear
    building_properties['Building_year']          = pand_data.get('oorspronkelijkBouwjaar')
#
#
    #get 3d buildingdata from delft 3d bag api wfs
    dried_data = requests.get('http://3dbag.bk.tudelft.nl/data/wfs?'
                          'SERVICE=WFS&'
                          'REQUEST=GetFeature&'
                          'TYPENAMES=BAG3D:pand3d&'
                          "CQL_FILTER=identificatie='"
                          + pand_id +
                          "'&outputFormat=json"      
    ).json()
#
    temp1 = dried_data.get('features')[0].get('properties')
    building_properties['ground_0_50']   = temp1.get('ground-0.50')
    building_properties['roof_0_25']     = temp1.get('roof-0.25')
    building_properties['rmse_0_25']     = temp1.get('rmse-0.25')
    building_properties['roof_0_75']     = temp1.get('roof-0.75')
    building_properties['rmse_0_75']     = temp1.get('rmse-0.75')
    building_properties['roof_0_95']     = temp1.get('roof-0.95')
    building_properties['rmse_0_95']     = temp1.get('rmse-0.95')
    building_properties['roof_flat']     = temp1.get('roof_flat')
#
    if window_count == True:
        #Google API key
        Google_api_key = "AIzaSyBl6NXQWRZzq0Of5dehbKhyb2tmpKsYLgU"
        credentials_raw = os.environ.get('Buildinglife_key')
        service_account_info = json.loads(credentials_raw)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info)
        # Get google streetview image
        Streetview_image = 'https://maps.googleapis.com/maps/api/streetview?' \
                            'size=400x640&' \
                            "location=" + str(object_location[1]) + ',' + str(object_location[0]) +'&' \
                            'fov=40&' \
                            'pitch=0&' \
                            'key=' + str(Google_api_key) + ' '
    #
        client = vision.ImageAnnotatorClient(credentials=credentials)
    #
        # Convert streetview
        data = requests.get(Streetview_image)
        content = data.content
        image = vision.types.Image(content=content)
    #
        #define objects
        objects = client.object_localization(
            image=image).localized_object_annotations
    #
        # Count windows
        window = 0
        for object_ in objects:
            if object_.name == 'Window':
                window +=1
    #
        building_properties['windows'] = window
#
    return building_properties