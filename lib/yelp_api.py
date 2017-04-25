"""
Module to perform post and get functions on Yelp API.
"""

from sklearn.externals import joblib
from db_creds import fusion_creds
from urllib import urlencode, quote
from time import sleep
import pandas as pd
import requests
import random
import json

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

def append_process_tracker(process, process_list):
    """
    Create a dictionary, tracking how much of our data requests
    is requested accurately from Yelp. 
    """
    if process in process_list:
        return 'Warning: this process has already been performed'
    else:
        process_list.append(process)

def create_not_null_phone_df(data, process_list):
    """
    Return a DataFrame with restaurants who have a non-null
    phone number.
    """

    total_search_list_length = len(data['phone'])

    process = ['The total Yelp search is {} restaurants'.format(total_search_list_length)]
    append_process_tracker(process, process_list)
    
    return data[data['phone'] != '+1nan']

def create_searches(data, search_type, process_list, optional_data=False):
    """
    Provide a list of terms for our Yelp API search.
    """
    if search_type.lower() == 'phone':
        phone_df = create_not_null_phone_df(data, process_list)
        terms = phone_df['facility'].values
        location = (phone_df['address'].values + ' ' + phone_df['city'].values + ' ' 
                    + phone_df['zip_cd'].values)
        phone_num = phone_df['phone'].values
        phone_search_list = zip(terms, location, phone_num)

        phone_search_list_length = len(phone_search_list)
        phone_search_list_pct = round((phone_search_list_length * 100. / len(data['phone'])), 2)

        process = ['{} restaurants provided a phone number ({}%)'.format(phone_search_list_length, 
                                                                         phone_search_list_pct)]
        append_process_tracker(process, process_list)

        return process_list, phone_search_list

    elif search_type.lower() == 'term_loc':
        terms = data['facility'].values
        locations = (data['address'].values + ' ' + data['city'].values + ' ' 
                    + data['zip_cd'].values)
        term_matches = optional_data['search_name']
        address_matches = optional_data['search_address']
        
        succussful_phone_searches = set(zip(term_matches, address_matches))
        term_loc_searches = set(zip(terms, locations)) - set(zip(term_matches, address_matches))

        number_of_remaining_searches = len(term_loc_searches)
        number_of_remaining_searches_pct = round(number_of_remaining_searches * 100. / 
                                                 int(process_list[0][0].split(' ')[5]),2)

        process = ['{} remaining restaurants to search with term/location({}%)'.format(number_of_remaining_searches,
                                                                                       number_of_remaining_searches_pct)]

        append_process_tracker(process, process_list) 
        
        return term_loc_searches

    else:  
        print 'Provide a proper input for a search_type (phone or term_loc)' 

def yelp_api_calls(search_list, search_type):
    """
    Provide a dictionary of Yelp API searches, as well as a list of 
    failed searches.
    """
    bearer_token = obtain_bearer_token()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}
    search_dict = {}
    unsearchable_list = []

    if search_type.lower() == 'phone':
        url = 'https://api.yelp.com/v3/businesses/search/phone'

        for i in search_list:
            url_params = {'phone': i[2]}
            for u_ in url_params:
                try:
                    search_dict[i[0],i[1]] = dict(requests.request('GET', url, 
                                                                   headers=headers, 
                                                                   params=url_params).json())['businesses']
                except:
                    unsearchable_list.append(i)

        return search_dict, unsearchable_list

    elif search_type.lower() == 'term_loc':
        url = 'https://api.yelp.com/v3/businesses/search'

        for i in search_list:
            url_params = {'location': i[1],
                          'term': i[0],
                          'limit': 30,
                          'locale': 'en_US'}
            try:
                search_dict[i] = dict(requests.request('GET', url, 
                                                       headers=headers, 
                                                       params=url_params).json())['businesses']
            except:
                unsearchable_list.append(url_params)

        return search_dict, unsearchable_list
    
    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'    

def find_failed_searches(search_dict, search_type, process_list, save_as_name):
    """
    Remove empty Yelp results from our search dictionary, and 
    return the search list of those results.
    """
    yelp_search_fail_list = []
    revised_search_dict = {}
    for key, value in search_dict.items():
        if value == []:
            yelp_search_fail_list.append(key)
        else:
            revised_search_dict[key] = value

    number_of_successful_searches = len(revised_search_dict.keys())
    number_of_successful_searches_pct = round(number_of_successful_searches * 100. / 
                                              int(process_list[0][0].split(' ')[5]),2)

    if search_type.lower() == 'phone':
        process = ['{} restaurant phone searches yielded a response from yelp ({}%)'.format(number_of_successful_searches, 
                                                                                            number_of_successful_searches_pct)]
        append_process_tracker(process, process_list)    
        joblib.dump(revised_search_dict, 'data/phone_search_dict_{}.pkl'.format(save_as_name))

    elif search_type.lower() == 'term_loc':
        process = ['{} restaurant term/location searches yielded a response from yelp ({}%)'.format(number_of_successful_searches, 
                                                                                                    number_of_successful_searches_pct)]
        append_process_tracker(process, process_list)    
        joblib.dump(revised_search_dict, 'data/term_loc_search_dict_{}.pkl'.format(save_as_name))
    
    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'

    return yelp_search_fail_list

def load_search_dict(save_as_name, search_type):
    """
    Load a pickled search dictionary.
    """
    if search_type.lower() == 'phone':
        return joblib.load('data/phone_search_dict_{}.pkl'.format(save_as_name))
    elif search_type.lower() == 'term_loc':
        return joblib.load('data/term_loc_search_dict_{}.pkl'.format(save_as_name))
    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'

def format_search_dict(search_dict):
    """
    Return dictionaryh with parsed Yelp API results to only provide 
    necessary parameters.
    """
    format_lst = []
    for rest, value in search_dict.items():
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
            rating = values['rating']
            review_count = values['review_count']
            closed = values['is_closed']
            address = values['location']['address1']
            city = values['location']['city']
            zip_code = values['location']['zip_code']
            latitude = values['coordinates']['latitude']
            longitude = values['coordinates']['longitude']
            indiv_rest_list = [search_name, search_address, bus_id, name, 
                               price, cat_1, cat_2, rating, review_count, 
                               closed, address, city, zip_code, latitude, 
                               longitude]
            format_lst.append(indiv_rest_list)
    return format_lst

def pick_correct_matches(formatted_list, search_type, process_list):
    """
    Determine proper matches from Yelp searches by specifying
    a new 'match' value in the search dictionary. Return any failed
    determinations.
    """
    unknown = []
    running_count = 0

    for i in formatted_list:
        search_name = i[0].lower().split(' ')
        search_address = i[1].split()[0]
        yelp_name = i[3].lower()
        try:
            yelp_address = i[10].split()[0]
        except:
            yelp_address = i[10]
        address_prob = 0
        name_prob = 0
        try:
            if yelp_address == search_address:
                address_prob = 1
                for word in search_name:
                    word = word[:-1]
                    if word in yelp_name:
                        name_prob += 1.0 / len(search_name)
            total_prob = address_prob + name_prob
            i.append(total_prob)
        except:
            unknown.append(i)

    return formatted_list, unknown

def create_dataframe_of_matches(formatted_list, search_type, process_list):
    """nothing"""

    bus_ids = [i[2] for i in formatted_list]

    df = pd.DataFrame(formatted_list, index=bus_ids,
                      columns = ['search_name', 'search_address', 'bus_id', 'name', 
                                 'price', 'cat_1', 'cat_2', 'rating', 'review_count', 
                                 'closed','address', 'city', 'zip_code', 'latitude', 
                                 'longitude', 'match'])

    best_match = df[df['match'] > 1.0].groupby(['search_name', 'search_address'], 
                                                as_index=False)['match'].max()

    best_match_df = pd.merge(best_match, df)

    number_of_search_matches = len(best_match)
    number_of_search_matches_pct = round(number_of_search_matches * 100. / 
                                         int(process_list[0][0].split(' ')[5]),2)

    if search_type.lower() == 'phone':
        process = ['{} successful matches from phone searches ({}%)'.format(number_of_search_matches,
                                                                            number_of_search_matches_pct)]
        append_process_tracker(process, process_list)
    
    elif search_type.lower() == 'term_loc':
        total_num_of_successful_searches = int(process_list[2][0].split(' ')[0]) + number_of_search_matches
        total_num_of_successful_searches_pct = round(total_num_of_successful_searches * 100. / 
                                                     int(process_list[0][0].split(' ')[5]),2)
        process_1 = ['{} successful matches from term/location searches ({}%)'.format(number_of_search_matches, 
                                                                                      number_of_search_matches_pct)]
        process_2 = ['{} successful matches from all searches ({}%)'.format(total_num_of_successful_searches, 
                                                                            total_num_of_successful_searches_pct)]
        append_process_tracker(process_1, process_list)
        append_process_tracker(process_2, process_list)
        
    else:
        print 'Provide a proper input for a search_type (phone or term_loc)'

    return best_match_df

def yelp_api_bus_id_calls(list_of_business_ids):

    bearer_token = obtain_bearer_token()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    for bus in list_of_business_ids:
        failures = []
        successes = []
        new_str = quote(bus.encode('utf8'))
        url_new = 'https://www.yelp.com/biz/{}?sort_by=date_asc'.format(new_str)
        url_old = 'https://www.yelp.com/biz/{}?sort_by=date_desc'.format(new_str)
        try:
            rqst_new = requests.request('GET', url_new, headers=headers)
            sleep(5)
            rqst_old = requests.request('GET', url_old, headers=headers)
            successes.append(rqst_new.content)
            successes.append(rqst_old.content)
        except:
            sleep(30)
            try:
                rqst_new = requests.request('GET', url_new, headers=headers)
                sleep(3)
                rqst_old = requests.request('GET', url_old, headers=headers)
                successes.append(rqst_new.content)
                successes.append(rqst_old.content)
            except:
                failures.append(new_str)
    return failures, successes

def yelp_api_calls_business_id(list_of_business_ids):

    ratings = {}
    bearer_token = obtain_bearer_token()
    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    for bus in list_of_business_ids:
        values = []
        new_str = quote(bus.encode('utf8'))
        url = 'https://www.yelp.com/biz/{}?sort_by=date_asc'.format(new_str)
        try:
            rqst = requests.request('GET', url, headers=headers)
        except:
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
        
        url_recent = 'https://www.yelp.com/biz/{}?sort_by=date_desc'.format(new_str)
        try:
            rqst = requests.request('GET', url_recent, headers=headers)
        except:
            sleep(30)
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
