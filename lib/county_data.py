"""
Module to assist with data cleansing.
"""

from collapse_facil_dict import event_facil_addresses
import re

def strip_col_contents(data):
     """
     Pass a datadrame to return all contents in dataframe
     """
     for col in data:
         try:
             data[col] = data[col].map(str.strip)
             success = 'SUCCESS'
             print '{:12}: {} column stripped'.format(success, col)
         except:
             data[col] = data[col]
             unsuccessful = 'UNSUCCESSFUL'
             print '{}: {} column not stripped due to format'.format(unsuccessful, col)

def filter_and_drop_column(data):
    """
    Drop the filter column from a DataFrame.
    """
    data = data[data['filter'] == 1]
    data = data.drop('filter', axis = 1)
    return data

def filter_dataframe(criteria, column, data):
    """
    Pass criteria, column and data to receive a filtered dataframe based on
    specified criteria.
    """
    criteria = criteria.upper()
    column = column.lower()
    
    data['filter'] = data[column].apply(lambda x: 1 if criteria in x else 0)
    
    filtered_data = filter_and_drop_column(data)
    return filtered_data

def max_seating(seating_range):
    """
    Return maximum number of seats given a range of seating.
    """
    if seating_range == '0-30':
        return 30
    elif seating_range == '31-60':
        return 60
    elif seating_range == '61-150':
        return 150
    elif seating_range == '151 + ':
        return 151

def risk_lev(risk_level):
    """
    Return numerical risk level given a string risk level.
    """
    if risk_level == 'HIGH':
        return 3
    elif risk_level == 'MODERATE':
        return 2
    elif risk_level == 'LOW':
        return 1

def rename_facilities(address, facility_name):
    """
    Aggregate multiple facilities within one facility using the
    event facility address dictionary.
    """
    if address in event_facil_addresses:
        return event_facil_addresses[address]
    else:
        return facility_name

def clean_addresses_hash(address):
    """
    Return a pure address if the address contains a number hash
    with a suite number
    """
    new_string = re.sub('( #.*$)', '', address)
    return new_string

def clean_addresses_ste(address):

    return re.sub('( STE .*$)', '', address)