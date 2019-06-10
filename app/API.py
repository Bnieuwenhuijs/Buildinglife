def Building_propperties(postalcode, housenumber):
    import json
    import requests
    from google.cloud import vision



    #BAG API

    url = 'https://bag.basisregistraties.overheid.nl/api/v1/nummeraanduidingen'
    headers = {'X-Api-Key'  : '8d2869b4-2b78-4596-b290-6f2e1e8b4661'}
    adress = {'postcode': '3452AM', 'huisnummer': 29}

    adress_data = requests.get(url, headers=headers, params=adress).json()
    object_url = adress_data.get('_embedded').get('nummeraanduidingen')[0].get('_links').get('adresseerbaarObject').get('href')



    object_data = requests.get(object_url, headers=headers).json()
    oppervlakte = object_data.get('oppervlakte')
    #Get object location - used in google maps api
    object_location = object_data.get('_embedded').get('geometrie').get('coordinates')
    pand_url = object_data.get('_links').get('pandrelateringen')[0].get('href')

    pand_data = requests.get(pand_url, headers=headers).json()
    pand_id = pand_data.get('identificatiecode')

    #WFS api

    gebruiksdoel_data = requests.get('https://geodata.nationaalgeoregister.nl/bag/wfs?'
                                    'SERVICE=WFS&'
                                    'REQUEST=GetFeature&'
                                    'TYPENAMES=bag:verblijfsobject&'
                                    'PROPERTYNAME=gebruiksdoel&'
                                    'CQL_FILTER=pandidentificatie='
                                    + pand_id +
                                    '&outputFormat=json'
    ).json()

    oppervlakte_data = requests.get('https://geodata.nationaalgeoregister.nl/bag/wfs?'
                                    'SERVICE=WFS&'
                                    'REQUEST=GetFeature&'
                                    'TYPENAMES=bag:verblijfsobject&'
                                    'PROPERTYNAME=oppervlakte&'
                                    'CQL_FILTER=pandidentificatie='
                                    + pand_id +
                                    '&outputFormat=json'
    ).json()

    pand_bouwjaar = pand_data.get('oorspronkelijkBouwjaar')

    #Google API
    Google_api_key = "AIzaSyDEh5n1Migci53aqLhtOh2Tc_e1FHqMMNU"


    # Define parameters for street view api
    Streetview_image = 'https://maps.googleapis.com/maps/api/streetview?' \
                        'size=400x640&' \
                        "location=" + str(object_location[1]) + ',' + str(object_location[0]) +'&' \
                        'fov=40&' \
                        'pitch=0&' \
                        'key=' + str(Google_api_key) + ' '


    client = vision.ImageAnnotatorClient()

    data = requests.get(Streetview_image)
    content = data.content
    image = vision.types.Image(content=content)

    objects = client.object_localization(
        image=image).localized_object_annotations


    window = 0
    for object_ in objects:
        if object_.name == 'Window':
            window +=1

    return gebruiksdoel_data + oppervlakte_data + pand_bouwjaar + window