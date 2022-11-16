# Team Name: KANDY
# Date: November 6, 2022
# Project: Analyzing Information on Car Collision in Canada
# Competition: HACKED(beta) 2022 at the University of Alberta
# Author: Taekwan Yoon
# Team Members: Taekwan Yoon, Min Joh, Jamie Lee, Yongbin Kim, Dohyun Kim

# Description of file: 
#   This file scrapes the website: "https://www.navbug.com/alberta_traffic.htm".
#   The website provides data on news reports on car collisions or severe road 
#   conditions. Although the number of news reports may not accurately reflect
#   the actual number of car collisions, this website provided one of the most
#   thoroughly tracked and systematic information. The file outputs the number
#   of car collisions in specific years in specific areas/counties of Alberta,
#   Canada.

# Side note:
#   In the same folder, the output text file was generated in Nov 6, 2022.
#   In the terminal, type the following to newly generate the output text file:
#               $ python3 web_scraper.py <output_file_name>
#
# Warning: The compiling time may vary depending on the computer performance.

# BeautifulSoup for web scraping (no JavaScript used) 
import requests
from bs4 import BeautifulSoup
import re

def num_cities(url):
    """
    This function returns the list of cities under the "Traffic by City" tab.
    """
    # website content
    result = requests.get(url)

    # parse through website content
    soup = BeautifulSoup(result.text, "lxml")

    # find the length of the list of cities
    # scrape the list of cities from website
    possible_cities = soup.find_all("ul",{"class":"sidebar-list"})
    list_cities = []  # initialize the list of cities

    # split a single string of cities
    for city in possible_cities:
        list_cities.append(city.text.split("\n"))

    # there are multiple lists with the same tag --> scrape the desired one
    list_cities = list_cities[0]

    # trim the list
    while '' in list_cities:
        list_cities.remove('')

    return list_cities


def format_list(list_cities):
    """
    This function modifies the format of the city list so that it can be incorprated in hyperlink.
    It returns a list of the modified formats.
    """
    
    hyper_city_list = []
    
    # modify the format to match the hyperlinks
    for city in list_cities:
        city = city.replace(" ", "_").lower()
        if "_traffic" in city:
            city = city.replace("_traffic","_1_archived_reports")
        hyper_city_list.append(city)

    return hyper_city_list

def get_archived_link(link_of_desired_city):
    """
    This function gets the link of the 2022 incident archives of the specified city. 
    """
    full_link = "https://www.navbug.com/alberta/{}.htm".format(link_of_desired_city)
    return full_link

def get_archived_titles(full_link):
    """
    This function returns the titles of the archived posts.
    """

    result = requests.get(full_link)
    soup = BeautifulSoup(result.text, "lxml")
    
    # all posts have "Incident Archives" string
    post_titles = soup.find_all(string = re.compile("Incident Archives"))
    archived_post_list = []
    for title in post_titles:
        archived_post_list.append(title.text)
    return archived_post_list

def trim_archives(archived_post_list):
    """
    This function removes posts that are not of concern (prior to 2021).

    Prior to 2021, a lot of data are missing or have been erased.
    """
    
    list2021 = []
    list2022 = []

    for post in archived_post_list:
        if "2021" in post: 
            list2021.append(post)
        elif "2022" in post:
            list2022.append(post)
        else:
            continue
    return list2021, list2022

def get_archive_link(archive_list, year, city):
    """
    This function returns the list of links to archived reports.

    It takes the post titles, year of concern (2021 or 2022),
    and city of interest as its argument.
    """

    months = [
            "January", "February", "March", "April", "May", "June", "July", 
            "August", "September", "October", "November", "December"
            ]

    month_list = []
    # hyperlinks use integers, instead of strings to specify months
    for title in archive_list:
        if months[0] in title:
            month_list.append("01")
        elif months[1] in title:
            month_list.append("02")
        elif months[2] in title:
            month_list.append("03")
        elif months[3] in title:
            month_list.append("04")
        elif months[4] in title:
            month_list.append("05")
        elif months[5] in title:
            month_list.append("06")
        elif months[6] in title:
            month_list.append("07")
        elif months[7] in title:
            month_list.append("08")
        elif months[8] in title:
            month_list.append("09")
        elif months[9] in title:
            month_list.append("10")
        elif months[10] in title:
            month_list.append("11")
        elif months[11] in title:
            month_list.append("12")

    # hyperlinks use year + months
    date_list = []
    for i in range(len(month_list)):
        date_list.append(str(year) + month_list[i])
    
    # full hyperlinks
    link_list = []
    for date in date_list:
        link_list.append("https://www.navbug.com/alberta/{}/archives/{}.htm".format(city,date))
    return link_list

def num_posts(link_list):
    """
    This function returns the number of news reports in a year.
    """

    num_posts = 0
    
    for link in link_list:
        result = requests.get(link)
        soup = BeautifulSoup(result.text, "lxml")
        post_titles = soup.find_all("span",{"class":"listarticle_title"})
        post_list = []
        for post in post_titles:
            post_list.append(post.text)
        num_posts += len(post_list) 

    return num_posts

def list_options(list_cities):
    """
    This function shows the list of city options that you can input in
    "get_archived_link" function. The list has specific formats. 
    """

    list_of_cities = []
    for city in list_cities:
        # all lowercase, whitespace --> underscore, erase "_traffic"
        list_of_cities.append(city.lower().replace(" ","_").replace("_traffic",""))
    
    return list_of_cities

def scrape_main(city,index):
    """
    This function applies many of scraping tasks performed by other functions
    in this module.
    """
    
    # main page to get list of city names
    list_cities = num_cities("https://www.navbug.com/alberta/calgary_traffic.htm")
    
    # modify and format city names to use for webscraping (must match hyperlinks)
    formatted_list = format_list(list_cities)
    
    # each city has multiple links corresponding to months & years
    # so make a list of hyperlinks corresponding to these months & years
    archive_list = get_archived_link(formatted_list[index])

    # in each link of specific month & year, get the number of news reports 
    archived_titles = get_archived_titles(archive_list)

    # remove news reports before 2021 because many of them were removed and empty
    list2021, list2022 = trim_archives(archived_titles)

    # scrape data for specified city in 2021
    list_of_archived_link2021 = get_archive_link(list2021, 2021, city)

    # scrape data for specified city in 2022
    list_of_archived_link2022 = get_archive_link(list2022, 2022, city)

    # number of news reports in 2021 in specified city
    num2021 = num_posts(list_of_archived_link2021)

    # number of news reports in 2022 in specified city
    num2022 = num_posts(list_of_archived_link2022)

    print(city)
    print('2021:', num2021)
    print('2022:', num2022)

def main():
    
    # get the list of all cities
    list_cities = num_cities("https://www.navbug.com/alberta/calgary_traffic.htm")
    
    # format the city for displaying output
    formatted_list = format_list(list_cities)

    # show city options in output
    option_list = list_options(list_cities)
    print(option_list)
    
    # loop through each city to get number of news reports in each year
    for i in range(len(option_list)):
        city = option_list[i]
        scrape_main(city, i)

if __name__ == "__main__":
    main()

