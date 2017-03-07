"""
Module to perform post and get functions on Yelp API.
"""

from sklearn.externals import joblib
from db_creds import fusion_creds
from urllib import urlencode
from time import sleep
import requests
import random
import json

# dictionary for phone and term/loc searches


# lists and dictionaries for phone searches
process_tracker = {}
phn_srch_dict = {}
phn_frmt_dict = {}
unknwn_phn = {}
unsrchbl_phn = []
yp_phn_srch_fail = []

# lists and dictionaries for term/location searches
tl_srch_dict = {}
tl_frmt_dict = {}
unknwn_tl = {}
unsrchbl_tl = []
yp_tl_srch_fail = []

# lists and dictionaries for business id searches
ratings = {}

def obtain_bearer_token():
    """
    Provide the bearer token through an API post request.
    """
    url = 'https://api.yelp.com/oauth2/token'
    data = urlencode({'client_id': fusion_creds['app_id'],
                      'client_secret': fusion_creds['app_secret'],
                      'grant_type': 'client_credentials'})
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, data, headers)

    bearer_token = response.json()['access_token'].encode('ascii')

    if response.status_code == 200:
        return bearer_token

def appnd_prcss_trckr(key_name, num_value, prcnt_value):
    """
    Create a dictionary, tracking how much of our data requests
    is requested accurately from Yelp. 
    """
    process_tracker[key_name] = (num_value, prcnt_value)

def return_proccess_tracker():
    """
    Show all processes at any point in our Yelp searches.
    """
    return process_tracker

def create_phone_not_null_df(data):
    """
    Return a DataFrame with restaurants who have a non-null
    phone number.
    """
    appnd_prcss_trckr('0_Total DataFrame', len(data['phone']), '100%')
    return data[data['phone'] != '+1nan']

def create_searches(data, search_type, optional_data=False):
    """
    Provide a list of terms for our Yelp API search.
    """
    if search_type.lower() == 'phone':
        non_nan_df = create_phone_not_null_df(data)
        trms = non_nan_df['facility'].values
        lctn = (non_nan_df['address'].values + ', ' + non_nan_df['city'].values + ' ' 
                 + non_nan_df['zip_cd'].values) + ' CA'
        phn = non_nan_df['phone'].values
        search_list = zip(trms, lctn, phn)
        appnd_prcss_trckr('1_Restaurants with Phone Provided', 
                          len(search_list), 
                          '{}%'.format(round(len(search_list)*100./len(data['phone'])),2))
        return search_list

    elif search_type.lower() == 'term_loc':
        facil_val = data['facility'].values
        add_val = data['address'].values
        name_srch_val = optional_data[optional_data['match'] == 1.0]['search_name']
        add_srch_val = optional_data[optional_data['match'] == 1.0]['search_address']
        
        succ_srch = set(zip(name_srch_val, add_srch_val))
        new_search = set(zip(facil_val, add_val)) - set(zip(name_srch_val, add_srch_val))
        tot_df_num = process_tracker['0_Total DataFrame'][0]

        appnd_prcss_trckr('3_Successful Matches from Phone Searches', 
                          len(succ_srch), 
                          '{}%'.format(round(len(succ_srch)*100./tot_df_num),2))
        appnd_prcss_trckr('4_Remaining Restaurants to Search with Term/Location',
                          len(new_search),
                          '{}%'.format(round(len(new_search)*100./tot_df_num),2))   
        
        return new_search

    else:  
        print 'Provide a proper input for a search_type (phone or term_loc)' 

def yelp_api_calls(searches, search_type):
    """
    Provide a dictionary of Yelp API searches, as well as a list of 
    failed searches.
    """
    bearer_token = obtain_bearer_token()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    if search_type.lower() == 'phone':
        url = 'https://api.yelp.com/v3/businesses/search/phone'
    
        for i in searches:
            url_params = {'phone': i[2]}
            for u_ in url_params:
                try:
                    phn_srch_dict[i[0],i[1]] = dict(requests.request('GET', url, 
                                                                     headers=headers, 
                                                                     params=url_params).json())['businesses']
                except:
                    unsrchbl_phn.append(i)

        return phn_srch_dict, unsrchbl_phn

    elif search_type.lower() == 'term_loc':
        url = 'https://api.yelp.com/v3/businesses/search'

        for i in searches:
            url_params = {'location': i[1],
                          'term': i[0],
                          'limit': 30,
                          'locale': 'en_US'}
            try:
                tl_srch_dict[i] = dict(requests.request('GET', url, 
                                                        headers=headers, 
                                                        params=url_params).json())['businesses']
            except:
                unsrchbl_tl.append(url_params)

        return tl_srch_dict, unsrchbl_tl
    
    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'    

def find_failed_searches(search_num, srch_dict, search_type):
    """
    Remove empty Yelp results from our search dictionary, and 
    return the search list of those results.
    """
    if search_type.lower() == 'phone':
        for key, value in srch_dict.items():
            if value == []:
                yp_phn_srch_fail.append(key)
                srch_dict.pop(key, value)
    
        num_succ_srch = len(phn_srch_dict.keys())
        tot_df_num = process_tracker['0_Total DataFrame'][0]
    
        joblib.dump(srch_dict, 'data/phn_srch_dict_{}.pkl'.format(search_num))
        appnd_prcss_trckr('2_Restaurants with Successful Phone Searches', 
                          num_succ_srch, 
                          '{}%'.format(round(num_succ_srch*100./tot_df_num),2))

        return yp_phn_srch_fail

    elif search_type.lower() == 'term_loc':
        for key, value in srch_dict.items():
            if value == []:
                yp_tl_srch_fail.append(key)
                srch_dict.pop(key, value)
    
        num_succ_srch = len(tl_srch_dict.keys())
        tot_df_num = process_tracker['0_Total DataFrame'][0]
    
        joblib.dump(srch_dict, 'data/tl_srch_dict_{}.pkl'.format(search_num))
        appnd_prcss_trckr('5_Restaurants with Successful Term/Location Searches', 
                          num_succ_srch, 
                          '{}%'.format(round(num_succ_srch*100./tot_df_num),2))

        return yp_tl_srch_fail

    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'

def load_srch_dict(search_num, search_type):
    """
    Load a pickled search dictionary.
    """
    if search_type.lower() == 'phone':
        return joblib.load('data/phn_srch_dict_{}.pkl'.format(search_num))
    elif search_type.lower() == 'term_loc':
        return joblib.load('data/tl_srch_dict_{}.pkl'.format(search_num))
    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'

def format_srch_dict(srch_dict, search_type):
    """
    Return dictionaryh with parsed Yelp API results to only provide 
    necessary parameters.
    """
    if search_type.lower() == 'phone': 
        for rest, value in srch_dict.items():
            search_name = rest[0]
            search_address = rest[1].split(',')[0]
            for i, x in enumerate(value):
                max_items = i + 1
            for i in range(max_items):
                values = value[i]
                bus_id = values['id']
                name = values['name']
                try:
                    price = values['price']
                except:
                    price = None
                try:    
                    cat_1 = values['categories'][0]['alias']
                except:
                    cat_1 = None
                try:
                    cat_2 = values['categories'][1]['alias']
                except:
                    cat_2 = cat_1
                closed = values['is_closed']
                address = values['location']['address1']
                city = values['location']['city']
                zip_code = values['location']['zip_code']
                latitude = values['coordinates']['latitude']
                longitude = values['coordinates']['longitude']
                indiv_rest_list = [search_name, search_address, bus_id, name, 
                                   price, cat_1, cat_2, closed, address, city, 
                                   zip_code, latitude, longitude]
                phn_frmt_dict[bus_id] = indiv_rest_list
        return phn_frmt_dict

    elif search_type.lower() == 'term_loc':
        for rest, value in srch_dict.items():
            search_name = rest[0]
            search_address = rest[1].split(',')[0]
            for i, x in enumerate(value):
                max_items = i + 1
            for i in range(max_items):
                values = value[i]
                bus_id = values['id']
                name = values['name']
                try:
                    price = values['price']
                except:
                    price = None
                try:    
                    cat_1 = values['categories'][0]['alias']
                except:
                    cat_1 = None
                try:
                    cat_2 = values['categories'][1]['alias']
                except:
                    cat_2 = cat_1
                closed = values['is_closed']
                address = values['location']['address1']
                city = values['location']['city']
                zip_code = values['location']['zip_code']
                latitude = values['coordinates']['latitude']
                longitude = values['coordinates']['longitude']
                indiv_rest_list = [search_name, search_address, bus_id, name, 
                                   price, cat_1, cat_2, closed, address, city, 
                                   zip_code, latitude, longitude]
                tl_frmt_dict[bus_id] = indiv_rest_list
        return tl_frmt_dict
    
    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'

def pick_correct_matches(frmt_dict, search_type):
    """
    Determine proper matches from Yelp searches by specifying
    a new 'match' value in the search dictionary. Return any failed
    determinations.
    """
    if search_type.lower() == 'phone':
        for key, attribute in frmt_dict.items():
            search_address = attribute[1].split()[0]
            yelp_address = attribute[8]
            try:
                split_address = yelp_address.split()[0]
                if split_address == search_address:
                    attribute.append(1)
                else:
                    attribute.append(0)
            except:
                unknwn_phn[key] = attribute

        return unknwn_phn

    elif search_type.lower() == 'term_loc':
        running_list = [] 
        for key, attribute in frmt_dict.items():
            search_address = attribute[1].split()[0]
            yelp_address = attribute[8]
            try:
                split_address = yelp_address.split()[0]
                if split_address == search_address:
                    attribute.append(1)
                    running_list.append((attribute[0], attribute[1]))
                else:
                    attribute.append(0)
            except:
                unknwn_tl[key] = attribute

        tot_df_num = process_tracker['0_Total DataFrame'][0]

        appnd_prcss_trckr('6_Successful Matches from Term/Loc Searches', 
                          len(set(running_list)), 
                          '{}%'.format(round(len(set(running_list))*100./tot_df_num),2))
        
        all_succ_srchs = (process_tracker['6_Successful Matches from Term/Loc Searches'][0] +
                           process_tracker['3_Successful Matches from Phone Searches'][0])

        appnd_prcss_trckr('7_Successful Matches all Searches', 
                          all_succ_srchs, 
                          '{}%'.format(round(all_succ_srchs*100./tot_df_num),2))
        
        return unknwn_tl        
    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'

def yelp_api_calls_business_id(list_of_business_ids):

    bearer_token = obtain_bearer_token()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    for bus in list_of_business_ids:
        values = []
        url = 'https://www.yelp.com/biz/{}?sort_by=date_asc'.format(bus)
        sleep(30)
        rqst = requests.request('GET', url, headers=headers)
        beg_reviews = rqst.content.split('<script type="application/ld+json">')[1].split(', "servesCuisine":')[0] + '}'
        try:
            json_reviews = json.loads(beg_reviews)    
        except:
            beg_reviews = rqst.content.split('<script type="application/ld+json">')[1].split(', "priceRange":')[0] + '}'
            json_reviews = json.loads(beg_reviews)
        rating_cnt = json_reviews['aggregateRating']['reviewCount']
        rating_val = json_reviews['aggregateRating']['ratingValue']
        values.append(rating_cnt)
        values.append(rating_val)
        for review in json_reviews['review']:
            values.append((review['author'], review['datePublished'], review['reviewRating']['ratingValue']))
            url_recent = 'https://www.yelp.com/biz/{}?sort_by=date_desc'.format(bus)
        
        rqst = requests.request('GET', url_recent, headers=headers)
        beg_reviews = rqst.content.split('<script type="application/ld+json">')[1].split(', "servesCuisine":')[0] + '}'
        try:
            json_reviews = json.loads(beg_reviews)    
        except:
            beg_reviews = rqst.content.split('<script type="application/ld+json">')[1].split(', "priceRange":')[0] + '}'
            json_reviews = json.loads(beg_reviews)
        for review in json_reviews['review']:
            values.append((review['author'], review['datePublished'], review['reviewRating']['ratingValue']))
        ratings[bus] = values

    return ratings
