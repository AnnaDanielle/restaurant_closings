"""
Module to perform post and get functions on Yelp API.
"""

from sklearn.externals import joblib
from db_creds import fusion_creds, v_2_creds
from urllib import urlencode
import requests
import random

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
    process_tracker[key_name] = (num_value, prcnt_value)

def return_proccess_tracker():
    return process_tracker

def create_phone_not_null_df(data):
    appnd_prcss_trckr('0_Total DataFrame', len(data['phone']), '100%')
    return data[data['phone'] != '+1nan']

def create_phone_searches(data):
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

def yelp_api_calls_phone(searches):
    bearer_token = obtain_bearer_token()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
    url = 'https://api.yelp.com/v3/businesses/search/phone'
    
    for i in searches[:10]:
        url_params = {'phone': i[2]}
        for u_ in url_params:
            try:
                phn_srch_dict[i[0],i[1]] = dict(requests.request('GET', url, 
                                                                 headers=headers, 
                                                                 params=url_params).json())['businesses']
            except:
                unsrchbl_phn.append(i)

    return phn_srch_dict, unsrchbl_phn

def find_failed_searches(search_num, phn_srch_dict):
    for key, value in phn_srch_dict.items():
        if value == []:
            yp_phn_srch_fail.append(key)
            phn_srch_dict.pop(key, value)
    
    num_succ_srch = process_tracker['1_Restaurants with Phone Provided'][0] - len(yp_phn_srch_fail)
    tot_df_num = process_tracker['0_Total DataFrame'][0]
    
    joblib.dump(phn_srch_dict, 'data/phn_srch_dict_{}.pkl'.format(search_num))
    appnd_prcss_trckr('2_Restaurants with Successful Searches', 
                      num_succ_srch, 
                      '{}%'.format(round(num_succ_srch*100./tot_df_num),2))

    return yp_phn_srch_fail

def load_phn_srch_dict(search_num):
    return joblib.load('data/phn_srch_dict_{}.pkl'.format(search_num))

def format_phn_srch_dict(srch_dict):
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

def format_term_loc_srch_dict(srch_dict):
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

def pick_correct_match(phn_frmt_dict):
    for key, attribute in phn_frmt_dict.items():
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

def return_accuracy_phn_srch(data):
    num_matches = sum(data['match'])
    tot_df_num = process_tracker['0_Total DataFrame'][0]
    rem_srch = tot_df_num - num_matches
    appnd_prcss_trckr('3_Successful Matches from Phone Searches', 
                      num_matches, 
                      '{}%'.format(round(num_matches*100./tot_df_num),2))
    
    return process_tracker

def create_remaining_searches(original_data, phone_srch_data):
    facil_val = original_data['facility'].values
    add_val = original_data['address'].values
    name_srch_val = phone_srch_data[phone_srch_data['match'] == 1.0]['search_name']
    add_srch_val = phone_srch_data[phone_srch_data['match'] == 1.0]['search_address']
    
    new_search = set(zip(facil_val, add_val)) - set(zip(name_srch_val, add_srch_val))
    
    tot_df_num = process_tracker['0_Total DataFrame'][0]
    appnd_prcss_trckr('4_Remaining Restaurants to Search with Term/Location', 
                      len(new_search), 
                      '{}%'.format(round(len(new_search)*100./tot_df_num),2))
    
    return new_search

def yelp_api_calls_term_loc(searches):
    bearer_token = obtain_bearer_token()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
    url = 'https://api.yelp.com/v3/businesses/search'
    searches = random.sample(searches, 10)

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




