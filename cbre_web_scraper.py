# import required libraries
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re
from final_urls import *

""" 
********************************************
Top Level Function
********************************************
"""
def get_toronto_office_building_listings():
    """
    :return: The below section gets URLs for all buildings
    """
    driver.get(cbre_toronto_url)
    print("going to sleep for 25s")
    time.sleep(25)
    print("my 25s wait is over")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    search_results = soup.find_all('a')
    for elem in search_results:
        try:
            if "en-CA/listings/office/details/CA-Plus" in elem["href"]:
                building_urls.append(elem["href"])
        except:
            #Sometimes 'a' tags don't have 'href' inside them
            pass
    print("Buildings URLs : \n")
    print(building_urls)
    return building_urls


""" 
********************************************
Helper Functions
********************************************
"""
def get_unit_address(url):
    """
    :param url:  unit's url
    :return: unit's address
    """
    my_string = url.split('CA-Plus-')[1]
    result = re.search('/(.*)', my_string).group(1).split("?")[0]
    return result


def get_sqft(soup, prefixes, sqft_type):
    """
    ::param soup: bs4 soupStructure obtained for individual units
    :param prefixes: list of prefixes for ignoring
    :param sqft_type: currently only uses "Unit Size", can be extended later
    :return: size in sq.ft. associated with each unit
    """
    sqft_table = soup.find_all("div", {"class": "cbre_table__cell col-xs-6 col-sm-5 col-lg-4"})
    try:
        for x in sqft_table:
            if x.find('h3').text == sqft_type:
                try:
                    sqft_type = x.contents[1].contents[0].contents  # this is a list
                except:
                    sqft_type = x.contents[1].contents
                sqft_type = [x for x in sqft_type if not str(x).startswith(prefixes)]
                result = ''.join(sqft_type)
                return result
    except:
        result = 'N/A'
        return result

def get_rent(soup, prefixes, rent_type):
    """
    :param soup: bs4 soupStructure obtained for individual units
    :param prefixes: list of prefixes for ignoring
    :param rent_type: can be chosen from "Gross Rent", "Net Rent", "Additional Rent"
    :return: rents associated with each unit
    """
    rent_table = soup.find_all("div", {"class": "cbre_table__cell col-xs-6 col-sm-5 col-lg-4"})
    try:
        for x in rent_table:
            if x.find('h3').text == rent_type:
                try:
                    rent = x.contents[1].contents[0].contents # this is a list
                except:
                    rent = x.contents[1].contents
                rent = [x for x in rent if not str(x).startswith(prefixes)]
                result = ''.join(rent)
                return result
    except:
        result = 'N/A'
        return result

def get_unit_number(soup, prefixes):
    """
    :param soup: bs4 soupStructure obtained for individual units
    :param prefixes: list of prefixes for ignoring
    :return: unit number associated with each unit
    """
    main_header = soup.find_all("div", {"class": "header-title"})
    unit_number = main_header[0].contents[0].contents  # this is a list
    try:
        unit_number = unit_number[0].contents[1]
    except:
        unit_number = unit_number
    try:
        result = unit_number.split(',')[0]
    except:
        result = unit_number.split(',')[0][0]
    return result


""" 
****************************************************
Two Major Functions using above Helper Functions
****************************************************
"""
def get_unit_urls(building_urls):
    """
    :param building_urls: dictionary of URL lists for individual buildings
    :return: dictionary of final URLs for individual units in each building
    """
    count = 1
    for building in building_urls:
        building = 'https://www.commerciallistings.cbre.ca' + building
        try:
            driver.get(building)
            title = get_unit_address(building)
            if title not in unit_urls.keys():
                unit_urls[count] = {}
                unit_urls[count][title] = []
                unit_details[count] = {}
        except:
            print(building)

        time.sleep(8)
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            units = soup.find_all('a', {'class':'card_content'})
            for unit in units:
                unit_urls[count][title].append(unit["href"])
            count += 1
        except:
            unit_urls[count][title].append('N/A')
    return  unit_details

def get_individual_unit_details(final_unit_urls, base_unit_details_dict):
    """
    :param final_unit_urls: dictionary of final URLs for individual units in each building
    :param base_unit_details_dict: empty dictionary with basic key:value structure
    :return: a filled-in dictionary with basic required details
             about all required units in all office buildings in toronto
    """
    count = 1
    unit_count = 1
    for each_unit in final_unit_urls:
        unit_count = 1
        for key,values in final_unit_urls[each_unit].items():
            base_unit_details_dict[count] = {}
            if key not in base_unit_details_dict[count]:
                base_unit_details_dict[count][key] = {}
            for value in values:
                try:
                    value = 'https://www.commerciallistings.cbre.ca' + value
                    driver.get(value)
                except:
                    print(value)
                time.sleep(5)
                try:
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    prefixes = ('react', ' react', ' /react')
                    base_unit_details_dict[count][key][unit_count] = {}
                    base_unit_details_dict[count][key][unit_count]['Unit Number'] = get_unit_number(soup, prefixes)
                    base_unit_details_dict[count][key][unit_count]['Unit Size'] = get_sqft(soup, prefixes, "Unit Size")
                    base_unit_details_dict[count][key][unit_count]['Gross Rent'] = get_rent(soup, prefixes, "Gross Rent")
                    base_unit_details_dict[count][key][unit_count]['Additional Rent'] = get_rent(soup, prefixes, "Additional Rent")
                    base_unit_details_dict[count][key][unit_count]['Net Rent'] = get_rent(soup, prefixes, "Net Rent")
                except:
                    base_unit_details_dict[count][key][unit_count] = {}
                    base_unit_details_dict[count][key][unit_count]['Unit Number'] = 'N/A'
                    base_unit_details_dict[count][key][unit_count]['Unit Size'] = 'N/A'
                    base_unit_details_dict[count][key][unit_count]['Gross Rent'] = 'N/A'
                    base_unit_details_dict[count][key][unit_count]['Additional Rent'] = 'N/A'
                    base_unit_details_dict[count][key][unit_count]['Net Rent'] = 'N/A'
                unit_count += 1
        count +=1
    # print(base_unit_details_dict)
    return base_unit_details_dict


if __name__=="__main__":

    # specify the url
    cbre_toronto_url = "https://www.commerciallistings.cbre.ca/en-CA/listings/office/results?Common.HomeSite=ca-comm&CurrencyCode=CAD&Interval=Monthly&RadiusType=Kilometers&Site=ca-comm&Unit=sqft&aspects=isLetting&isParent=true&lat=43.653226&location=Toronto%2C+ON%2C+Canada&lon=-79.38318429999998&placeId=ChIJpTvG15DL1IkRd8S0KlBVNTI&polygons=%5B%5B%2243.8554579%2C-79.11689710000002%22%2C%2243.5810245%2C-79.11689710000002%22%2C%2243.5810245%2C-79.63921900000003%22%2C%2243.8554579%2C-79.63921900000003%22%5D%5D&radius=0&searchMode=bounding&sort=asc%28_distance%29&usageType=Office"
    building_urls = []
    unit_addresses = []
    unit_urls = {}
    unit_details = {}
    driver = webdriver.Chrome('./chromedriver')

    # Get URL for every Office building in Toronto
    building_urls = get_toronto_office_building_listings()

    # Get URL for every unit inside every building
    base_unit_details_dict = get_unit_urls(building_urls)

    # Access individual unit URL and access unit's base details
    final_dict = get_individual_unit_details(final_unit_urls, base_unit_details_dict)
    driver.close()

    addresses =[]
    df = pd.DataFrame()
    for key, minor_values in final_dict.items():
        for k, v in minor_values.items():
            addresses.append(k)
            if df.empty:
                df = pd.DataFrame(v).T
                df['Address'] = k
            else:
                temp_df = pd.DataFrame(v).T
                temp_df['Address'] = k
                df = pd.concat([df, temp_df], sort=True)

    #Final Address cleanup
    df['Address'] = df['Address'].replace('-', ' ', regex=True)
    df['Address'] = df['Address'].str.title()
    # Arrange columns in final csv
    final_df = df[['Address', 'Unit Number', 'Unit Size', 'Gross Rent', 'Net Rent', 'Additional Rent']]
    final_df.to_csv('cbre_data_table_Deepika.csv')
