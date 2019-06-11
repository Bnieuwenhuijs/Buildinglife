import json
import requests
from google.cloud import vision

def Building_propperties(postalcode, housenumber):
    #BAG API paramers
    url = 'https://bag.basisregistraties.overheid.nl/api/v1/nummeraanduidingen'
    headers = {'X-Api-Key'  : '8d2869b4-2b78-4596-b290-6f2e1e8b4661'}
    adress = {'postcode': postalcode, 'huisnummer': housenumber}
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
    gebruiksdoel_data = requests.get('https://geodata.nationaalgeoregister.nl/bag/wfs?'
                                    'SERVICE=WFS&'
                                    'REQUEST=GetFeature&'
                                    'TYPENAMES=bag:verblijfsobject&'
                                    'PROPERTYNAME=gebruiksdoel&'
                                    'CQL_FILTER=pandidentificatie='
                                    + pand_id +
                                    '&outputFormat=json'
    ).json()
#
    oppervlakte_data = requests.get('https://geodata.nationaalgeoregister.nl/bag/wfs?'
                                    'SERVICE=WFS&'
                                    'REQUEST=GetFeature&'
                                    'TYPENAMES=bag:verblijfsobject&'
                                    'PROPERTYNAME=oppervlakte&'
                                    'CQL_FILTER=pandidentificatie='
                                    + pand_id +
                                    '&outputFormat=json'
    ).json()
#
    #get buildingyear
    pand_bouwjaar = pand_data.get('oorspronkelijkBouwjaar')
#
    #Google API key
    Google_api_key = "AIzaSyDEh5n1Migci53aqLhtOh2Tc_e1FHqMMNU"
#
#
    # Get google streetview image
    Streetview_image = 'https://maps.googleapis.com/maps/api/streetview?' \
                        'size=400x640&' \
                        "location=" + str(object_location[1]) + ',' + str(object_location[0]) +'&' \
                        'fov=40&' \
                        'pitch=0&' \
                        'key=' + str(Google_api_key) + ' '
#
    client = vision.ImageAnnotatorClient()
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
    building_properties = {'building_year'           : pand_bouwjaar,
                           'building_functionality'  : gebruiksdoel_data,
                           'square_meters'           : oppervlakte_data,
                           'windows'                 : window
                          }
#
    return building_properties

k = Building_propperties("3452AN", "103")
print(k)