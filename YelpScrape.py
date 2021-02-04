#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import pandas as pd
from openpyxl import load_workbook
from selenium import webdriver
import validators
import requests
import re
import time
from airtable import Airtable
import os

requests.packages.urllib3.disable_warnings() 


# In[ ]:


base_key = 'appHujtYhaG4A9Eem'
table_name = 'Industries'
airtable = Airtable(base_key, table_name, api_key='keyz137SlvIHergwt')
industryList = []
industryRecords = airtable.get_all(fields=['Industry'])

for ele in industryRecords:
    try:
        industryList.append(ele["fields"]["Industry"])
    except:
        continue

totalBusinesses = int(input("How many results do you want? "))


# In[ ]:


# Connect with Airtable API for location table
base_key = 'appHujtYhaG4A9Eem'
table_name = 'Locations'
airtable = Airtable(base_key, table_name, api_key='keyz137SlvIHergwt')


locationSearchList = []
locationRecords = airtable.get_all(fields=['Remaining'])

for ele in locationRecords:
    try:
        locationSearchList.append(ele["fields"]["Remaining"])
    except:
        continue

# # Set up new DF
# searchDf = pd.DataFrame(columns = ['Business Name', 'Industry', 'Address', 'Town', 'State', 'Website',
#                                    "Phone Number", "Rating", "Number of Reviews", "Claimed?"])

#Iterate through all desired industries
for location in locationSearchList:

    searchCity = location.split(",")[0].replace(" ", "+")
    searchState = location.split(", ")[1]
    
    for industry in industryList:
        businessStart = 0
        end = False
        
        searchDf = pd.DataFrame(columns = ['Business Name', 'Industry', 'Address', 'Town', 'State',
                                           'Website', "Phone Number", "Rating", "Number of Reviews", "Claimed?"])
        
        while businessStart < totalBusinesses and end == False:  

            #all industry listings
            site = 'https://www.yelp.com/search?find_desc={}&find_loc={}%2C+{}&start={}'.format(industry,
                                                                                                    searchCity,
                                                                                                   searchState,
                                                                                                   businessStart)
            driver = webdriver.Chrome()
            driver.get(site)         
            HTML = driver.execute_script("return document.documentElement.outerHTML")
            driver.quit()
            soupList = BeautifulSoup(HTML)

#             end = False

            try:
                endResults = soup.find_all("p", {"class":"lemon--p__373c0__3Qnnj text__373c0__3rpl1 text-color--normal__373c0__3qpvi text-align--left__373c0__1jZVD"})
                for ele in endResults:
                    if "Try a different location." not in ele.text:
                        end = True

            except:
                end = False



            links = []
            for link in soupList.find_all('a', {"class":"link__09f24__1kwXV link-color--inherit__09f24__3PYlA link-size--inherit__09f24__2Uj95"}):
                if link != None:
                    if link.get('href') != None:
                        links.append(link.get('href'))

            bizLinks = list(set([x for x in links if x[:5] == '/biz/']))
            
#             print(bizLinks)

            #individual business pages
            for link in bizLinks:
                site = 'https://www.yelp.com{}'.format(link)

                driver = webdriver.Chrome()
                driver.get(site)
#                 print("Got site " + site)
                
                
    # Get Business Address
                try:
                    bizAddress = ""
                    bizAddress = driver.find_element_by_xpath("//*[@id='wrap']/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/section[1]/div/div[3]/div/div[1]/p/p").text
#                     print("Address is: ", bizAddress)

                except:

                    try:
                        bizAddress = driver.find_element_by_xpath("//*[@id='wrap']/div[3]/yelp-react-root/div/div[3]/div/div/div[2]/div/div/div[1]/div/div[1]/section[8]/div[2]/div[1]/div/div/div/div[1]/address/p[1]/span").text
#                         print("Address is: ", bizAddress)

                    except:
#                         print("No Listed Address")
                        pass
                    
                    
                HTML = driver.execute_script("return document.documentElement.outerHTML")
                soup = BeautifulSoup(HTML)


    # Business Name
                try:
                    bizName = soup.find("h1", {"class":"lemon--h1__373c0__2ZHSL heading--h1__373c0__dvYgw undefined heading--inline__373c0__10ozy"}).text
#                     print(bizName)
                except:
#                     print("Business Name Error")
                    continue

    # Business Website
                siteList = soup.find_all("a", {"class":"lemon--a__373c0__IEZFH link__373c0__1G70M link-color--blue-dark__373c0__85-Nu link-size--inherit__373c0__1VFlE"})

                for ele in siteList:

                    if ".com" in ele.text or ".net" in ele.text or ".org" in ele.text or ".co" in ele.text or ".us" in ele.text or ".biz"in ele.text:
                        bizSite = "https://www.yelp.com{}".format(ele.get('href'))

                        try:
                            requests.get(bizSite, verify = False, headers={'User-Agent': 'Custom'})
                            bizSite = bizSite[bizSite.find("%3A%2F%2F", 20)+9:]
                            siteEnd = re.search('[^a-zA-Z0-9.\-]', bizSite).start()
                            bizSite = bizSite[:siteEnd]
                            if not bizSite.startswith("www."):
                                bizSite = "www." + bizSite
                            
#                             print(bizSite)
                            break

                        except requests.ConnectionError as exception:
                            bizSite = ""

                    else:
                        bizSite = ""


    # Claimed or Not
#                 claimedList = soup.find_all("a", {"class":"lemon--a__373c0__IEZFH link__373c0__2-XHa link-color--blue-dark__373c0__4vqlF link-size--inherit__373c0__nQcnG"})

#                 for ele in claimedList:
#                     if ele.text == "Claimed" or "Unclaimed":
#                         bizClaim = ele.text.strip()
#                         print(bizClaim)
#                         break
#                     else:
#                         print("Claimed Error")
#                         continue

#                 claimedList = soup.find_all("div", {"class":"lemon--div__373c0__1mboc border-color--default__373c0__3-ifU nowrap__373c0__35McF"})
#                 for ele in claimedList:
#                     if ele.text == "Claimed" or "Unclaimed":
#                         bizClaim = ele.text.strip()
#                         print(bizClaim)
#                         break
#                     else:
#                         print("Claimed Error")
#                         continue
                try:        
                    bizClaim = soup.find("span", {"class":'icon--16-claim-filled-v2 css-1jnn9ss'})
                    bizClaim = "Claimed"
            
                except:
                    
                    try:
                        bizClaim = soup.find("span", {"class":"icon--16-exclamation-v2 css-13zy15n"})
                        bizClaim = "Unclaimed"
                        
                    except:
                        bizClaim = "Claimed Error"
                
#                 print(claim)


    # Business Rating
                try:
                    divs = divs = soup.find_all("div", {"class": lambda x: x and x.startswith('lemon--div__373c0__1mboc i-stars__373c0__1T6rz i-stars--large')})

                    if len(divs)>0:
                        for ele in divs:
                            try:
                                int(ele["aria-label"][0])
                                bizScore = ele["aria-label"]
#                                 print(bizScore)
                                break
                            except:
                                bizScore = ""
                    else:
                        bizScore = ""
                except:
                    bizScore = ""


    # Number of Reviews
                try:
                    bizReview = soup.find("span", {"class":"lemon--span__373c0__3997G text__373c0__2Kxyz text-color--black-regular__373c0__2vGEn text-align--left__373c0__2XGa- text-weight--semibold__373c0__2l0fe text-size--large__373c0__3t60B"}).text
                    try:
                        int(bizReview[0])
#                         print("Number of reviews: ", bizReview)

                    except:
#                         print("Number of Reviews Error")
                        bizReview = ""

                except:
#                     print("Number of Reviews Error")
                    bizReview = ""

    # Phone Number
                try:
                    phoneList = soup.find_all("p", {"class":"lemon--p__373c0__3Qnnj text__373c0__2Kxyz text-color--normal__373c0__3xep9 text-align--left__373c0__2XGa- text-weight--semibold__373c0__2l0fe text-size--large__373c0__3t60B"})
                    for ele in phoneList:
                        if ele.text.startswith("(") and ele.text[1] in "0123456789":
                            bizPhone = ele.text
#                             print("Phone Number is: ", bizPhone)
                            break
                        else:
                            bizPhone = ""
                except:
                    bizPhone = ""


    # Business Address
#                 try:
#                     addressList = soup.find_all("p", {"class":"lemon--p__373c0__3Qnnj text__373c0__2Kxyz text-color--subtle__373c0__3DZpi text-align--left__373c0__2XGa-"})
                
#                     for address in addressList:
#                         print(address.text)
# #                     bizAddressSep = str(addressList.get_text(separator = " "))
# #                     if len(bizAddressSep.split(" ")) <= 3:
# #                         bizAddress = ""
# #                     else:
# #                     bizAddress = bizAddressSep
#                     print("Address is: ", bizAddress)
        
#                 except:
#                     print("Address Error")
#                     bizAddress = ""


    # Business Location

                bizTown = location.split(" ")[0][0:-1]
                bizState = location.split(" ")[1]


    # Create dataframe

                bizDf = pd.DataFrame(data = {'Business Name':[bizName], 'Address':[bizAddress], 'Town':[bizTown],
                                             'State':[bizState], 'Industry':[industry], 'Website':[bizSite],
                                             "Phone Number":[bizPhone], "Rating":[bizScore],
                                             "Number of Reviews":[bizReview], "Claimed?":[bizClaim]})


                searchDf = searchDf.append(bizDf, ignore_index=True)
                print("Added ", bizName)

            businessStart += len(bizLinks)

        # Connect with Airtable API
        base_key = 'appHujtYhaG4A9Eem'
        table_name = 'All Data'
        airtable = Airtable(base_key, table_name, api_key='keyz137SlvIHergwt')


        # Load new data into Airtable
        for index, row in searchDf.iterrows():
            airtable.insert({'Business Name': row[0], "Industry":row[1], "Address":row[2], "Town":row[3], "State":row[4],
                             "Website":row[5], "Phone Number":row[6], "Rating":row[7], "Number of Reviews":row[8],
                             "Claimed?":row[9]})

        print(location + " " + industry + " data added to AirTable.")

        base_key = 'appHujtYhaG4A9Eem'
        table_name = 'Locations'
        airtable = Airtable(base_key, table_name, api_key='keyz137SlvIHergwt')
        
#         print(searchDf)

    driver.quit()


# In[ ]:


# Clean dataframe of duplicates and nulls

base_key = 'appHujtYhaG4A9Eem'
table_name = 'All Data'
airtable = Airtable(base_key, table_name, api_key='keyz137SlvIHergwt')
record_list = airtable.get_all()
rawDf = pd.DataFrame([record['fields'] for record in record_list])

cleanDf = rawDf.drop_duplicates().fillna("")

for index, row in cleanDf.iterrows():
    if re.search('[a-zA-Z]', row["Phone Number"]) != None:
        row["Phone Number"] = ""
    if "claimed" not in row["Claimed?"].lower():
        row["Claimed?"] = ""

# Connect with Airtable API
base_key = 'appXJAHxsGsspDqa9'
table_name = 'All Data'
airtable = Airtable(base_key, table_name, api_key='keyz137SlvIHergwt')


# Load new data into Airtable
for index, row in cleanDf.iterrows():
    airtable.insert({'Business Name': row["Business Name"], "Industry":row["Industry"], "Address":row["Address"],
                     "Town":row["Town"], "State":row["State"], "Website":row["Website"],
                     "Phone Number":row["Phone Number"], "Rating":row["Rating"],
                     "Number of Reviews":row["Number of Reviews"],"Claimed?":row["Claimed?"]})
