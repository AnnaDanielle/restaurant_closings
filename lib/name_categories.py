"""
Dictionary to provide facility type based on
words in facility name.
"""

def define_cat(x):
    if 'RALPHS' in x or \
    'GROCERY' in x or \
    'WHOLE FOODS' in x or \
    'WALMART' in x or \
    'GELSONS' in x or \
    'VONS' in x or \
    'CARDENAS' in x or \
    'VALLARTA SUPERMARKET' in x or \
    'HANNAM' in x or \
    'SEAFOOD CITY SUPERMARKET' in x or \
    'PAVILLIONS' in x or \
    '99 RANCH MARKET' in x or \
    'ALBERTSONS' in x or \
    'SMART & FINAL' in x or \
    'H MART' in x or \
    'WALGREENS' in x or \
    'TARGET' in x or \
    'SUPER H' in x:
        return 'grocery'
    elif 'BOB HOPE' in x or \
    'BURBANK' in x or \
    'LAX' in x:
        return 'airport'
    elif 'BRENTWOOD COUNTRY CLUB' in x or \
    'CALIFORNIA CLUB' in x or \
    'JONATHAN CLUB' in x:
        return 'club'
    elif 'CSU DOMINGUEZ' in x or \
    'AZUZA PACIFIC UNIVERSITY' in x or \
    'CAL STATE LA' in x or \
    'CAL STATE NORTHRIDGE' in x or \
    'CERRITOS COLLEGE' in x or \
    'LMU' in x or \
    'PEPPEREDINE' in x or \
    'USC' in x or \
    'UCLA' in x or \
    'SANTA MONICA COLLEGE' in x:
        return 'education'
    elif 'FOUR POINT' in x or \
    'BILTMORE' in x or \
    'SOHO HOUSE' in x or \
    'SHERATON' in x or \
    'MARRIOTT' in x or \
    'NEUEHOUSE' in x or \
    'BEVERLY HILLS HOTEL' in x or \
    'BEL AIR' in x or \
    'ACE' in x or \
    'HOTEL CASA DEL MAR' in x or \
    'FOUR SEASONS' in x or \
    'MARRIOTT' in x or \
    'HYATT' in x or \
    'MONTAGE' in x or \
    'LONDON' in x or \
    'LE MERIDIEN' in x or \
    'BICYCLE HOTEL CASINO' in x or \
    'LOEWS HOTEL' in x or \
    'BEVERLY HILTON' in x or \
    'MARRIOTT' in x or \
    'HYATT REGENCY CENTURY PLAZA' in x or \
    'W HOTEL' in x or \
    'LAAC' in x or \
    'CLIFTONS' in x or \
    'SHERATON' in x or \
    'LINE HOTEL' in x or \
    'HOLIDAY INN' in x or \
    'HILTON' in x or \
    'JW MARRIOTT HOTEL' in x or \
    'HOLLYWOOD PARK CASINO' in x or \
    'EMBASSY SUITES' in x or \
    ' HOTEL ' in x or \
    'ROOSEVELT' in x:
        return 'hotel'
    elif 'WESTFIELD TOPANGA' in x:
        return 'mall'
    elif 'COLISEUM' in x or \
    'RAGING WATER LA' in x or \
    'LA CONVENTION CENTER' in x or \
    'LA ZOO' in x or \
    'MUSIC CENTER' in x or \
    'SHRINE AUDITORIUM' in x or \
    'BELASCO' in x or \
    'CLUB NOKIA' in x or \
    'STUBHUB CENTER' in x or \
    'GREEK THEATER' in x or \
    'MICROSOFT THEATER' in x or \
    'GALEN CENTER' in x or \
    'BANC OF CALIFORNIA STADIUM' in x or \
    'SANTA ANITA PARK' in x or \
    'HOLLYWOOD BOWL' in x or \
    'DODGER STADIUM' in x or \
    'SIX FLAGS MAGIC MOUNTAIN' in x or \
    'MAGNIN AUDITORIUM' in x or \
    'DOLBY' in x or \
    'STAPLES' in x or \
    'FAIRPLEX' in x or \
    'CINEMARK' in x or \
    'ARAMARK' in x or \
    'HOLLYWOOD PALLADIUM' in x or \
    'ARCLIGHT' in x or \
    'PACIFIC PARK' in x or \
    'LA LIVE' in x:
        return 'entertainment'

facility_type = {'airport':       ['BOB HOPE','BURBANK','LAX'],
                 'club':          ['BRENTWOOD COUNTRY CLUB','CALIFORNIA CLUB','JONATHAN CLUB'],
                 'education':     ['CSU DOMINGUEZ','AZUZA PACIFIC UNIVERSITY','CAL STATE LA',
                                   'CAL STATE NORTHRIDGE','CERRITOS COLLEGE','LMU','PEPPEREDINE',
                                   'USC','SANTA MONICA COLLEGE'],
                 'hotel':         ['FOUR POINT','BILTMORE','SOHO HOUSE','SHERATON','MARRIOTT','NEUEHOUSE',
                                   'BEVERLY HILLS HOTEL','BEL AIR','ACE','HOTEL CASA DEL MAR','FOUR SEASONS',
                                   'MARRIOTT','HYATT','MONTAGE','LONDON','LE MERIDIEN','BICYCLE HOTEL CASINO',
                                   'LOEWS HOTEL','BEVERLY HILTON','MARRIOTT','HYATT REGENCY CENTURY PLAZA',
                                   'W HOTEL','LAAC','CLIFTONS','SHERATON','LINE HOTEL','HOLIDAY INN','HILTON',
                                   'JW MARRIOTT HOTEL','HOLLYWOOD PARK CASINO','EMBASSY SUITES', 'ROOSEVELT'],
                 'grocery':       ['RALPHS','GROCERY','WHOLE FOODS','WALMART','GELSONS','VONS','CARDENAS',
                                   'VALLARTA SUPERMARKET','HANNAM','SEAFOOD CITY SUPERMARKET','PAVILLIONS',
                                   '99 RANCH MARKET','ALBERTSONS','SMART & FINAL','H MART','SUPER H','WALGREENS',
                                   'TARGET'],
                 'mall':          ['WESTFIELD TOPANGA'],
                 'entertainment': ['COLISEUM','RAGING WATER LA','LA CONVENTION CENTER','LA ZOO',
                                   'MUSIC CENTER','SHRINE AUDITORIUM','BELASCO','CLUB NOKIA',
                                   'STUBHUB CENTER','GREEK THEATER','MICROSOFT THEATER','GALEN CENTER',
                                   'BANC OF CALIFORNIA STADIUM','SANTA ANITA PARK','HOLLYWOOD BOWL',
                                   'DODGER STADIUM','SIX FLAGS MAGIC MOUNTAIN','MAGNIN AUDITORIUM',
                                   'DOLBY','STAPLES','FAIRPLEX','CINEMARK','ARAMARK','HOLLYWOOD PALLADIUM',
                                   'ARCLIGHT','PACIFIC PARK','LA LIVE']}