from bs4 import BeautifulSoup
import requests
import json
import csv
import math


# ----------------
# Custom Exeptions
# --->>>
class CustomError(Exception):
    pass

# -------------------------------
# Function : get_soup
# Parameters : URL of Website 
# Output : Variable "soup" 
# --->>>
def get_soup( website_url_x):
    
    html_content = ""
    # Getting html_content from "website_url"
    try :
        response = requests.get(website_url_x)
        if response.status_code == 200:
            html_content = response.text
        else :
            raise CustomError(f"Can't get Content From {website_url}")
            
    except Exception as e:
        print(f"Exeption During Getting Content of Website ----> { e }")

    # BeautifulSoup Variables
    soup = BeautifulSoup( html_content , 'html.parser')

    return soup

# -------------------------------
# Function : scrape_magicbricks
# --->>>
def scrape_magicbricks(  ):

    #-----------------------------
    # 1 : Declaration of Variables
    #-----------------------------

    
    array_of_properties = [
        [
            "property_price",     "property_bhk",
            "property_sqft",      "property_city",   "property_locality",
            "property_developer", "is_furnished",    "num_of_lifts", 
            "num_of_carparkings", "floor",           "property_project", 
            "num_of_baths",       "num_of_balconies","bechelors_or_family"
        ]
    ]

    # write_to_csv('./data.csv', array_of_properties)
    # " &page= " 
    website_url = "https://www.magicbricks.com/property-for-rent/residential-real-estate?proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Residentia80l-House,Villa&cityName=Gandhinagar&language=en&page="
    

    # -----------------------------------------
    # 2 : Iterate Over All Pages of "website_url"
    # -----------------------------------------

    num_of_pages = 40

    for page in range(27,num_of_pages):
        print(f"-------------------------->> At Page number {page+1} <<----------------------------------")
        
        website_url_x = website_url + str(page+1)
        soup = get_soup(website_url_x=website_url_x)
        
        
        property_cards = soup.find_all('div', class_= 'mb-srp__list')


        for card in property_cards :

            #-----------------------------------------
            # 3 : Get Link of Detailed Page of Property 
            #-----------------------------------------

            details_inside_script_tag = json.loads( card.find('script').text )
            detailed_page_link = details_inside_script_tag["url"]

            summaryCards = card.find_all('div', class_= "mb-srp__card__summary__list--item")

            bechelors_or_family = ""
            for c in summaryCards:
                if c.get('data-summary') is not None and c['data-summary'] == "tenent-preffered":
                    bechelors_or_family = c.find('div', class_ = "mb-srp__card__summary--value").text # 14 Bechlors or Family

            if detailed_page_link:
                # ---------------------------
                # 4 : Get Details of Property 
                # ---------------------------

                one_property_data_array = get_detailed_data(details_inside_script_tag,  detailed_page_link , bechelors_or_family )
                # array_of_properties.append(one_property_data_array)
                write_to_csv("./output_data/data.csv", one_property_data_array)

# -------------------------------
# Function : get_detailed_data
# Parameters : 
    # detailed_page_link ( Link for Scrapping Content from Detailed Page of a Property ),
    # details_inside_script_tag ( For Extracting Locality and City name ), 
    # bechelors_or_family ( This Variable Just Passes Value of "bechelors_or_family" Because We Earlier Extract This Value )
# Output : Array
# --->>>
def get_detailed_data(details_inside_script_tag , detailed_page_link , bechelors_or_family):    
    
    # declaration of variables
    property_name  = "" 
    property_price  = "" 
    property_bhk  = "" 
    property_sqft  = "" 
    property_city  = "" 
    property_locality  = "" 
    property_devloper  = "" #
    isFurnished = "" 
    num_of_lifts  = "" #
    num_of_carparkings  = "" 
    floor  = "" 
    property_project = "" 
    num_of_baths  = "" 
    num_of_balconies = "" 

    # --------------------------------->>

    detailed_page_soup = get_soup(detailed_page_link)
    summary_items = detailed_page_soup.find_all('li', class_="mb-ldp__dtls__body__summary--item")

    if summary_items:
        for item in summary_items:
            itemText = item.text
            value = itemText[0]
            key = itemText[1:].strip()

            if key == "Baths": # 13(Number of Bathrooms)
                num_of_baths = value
            if key == "Balcony": # 14(Number of Balconies)
                num_of_balconies = value
    else:
        num_of_baths = "-"
        num_of_balconies  = "-"

    # ------------------------------>>


    if details_inside_script_tag.get("address") is not None:
        if details_inside_script_tag["address"].get("addressRegion") is not None:
            property_city = details_inside_script_tag["address"]["addressRegion"] # 2(City)
        else:
            property_city = "-"
    else:
        property_city = "-"

    if details_inside_script_tag.get("address") is not None:
        if details_inside_script_tag["address"].get("addressLocality") is not None:
            property_locality = details_inside_script_tag["address"]["addressLocality"] # 2(Locality)
            print(property_locality)
        else:
            property_locality = "-"
            print(property_locality)
    else:
        property_locality = "-"
        print(property_locality)


    if details_inside_script_tag.get("numberOfRooms") is not None:
        property_bhk = details_inside_script_tag["numberOfRooms"] # 3 (PropertyBHK)
    else:
         property_bhk = "-"

    # if details_inside_script_tag["name"]:
    #     property_name = details_inside_script_tag["name"] # 4(Property Name)
    # else:
    #      property_name = "-"

    # ------------------------------->>
    if detailed_page_soup.find('div', class_="mb-ldp__dtls__price") is not None:
        property_price = detailed_page_soup.find('div', class_="mb-ldp__dtls__price").text
        try:
            if  property_price.split("₹")[1]:
                property_price = property_price.split("₹")[1]# 5(Property-Price)
            else:
                property_price = "-"
        except Exception as e:
            print("error at price")

    if detailed_page_soup.find('span', class_= 'mb-ldp__dtls__title--text1--text pad-r-4') is not None:
        property_sqft = detailed_page_soup.find('span', class_= 'mb-ldp__dtls__title--text1--text pad-r-4').text # 6(Property-Sqft)
    else:
         property_sqft = "-"

    # -------------------------------->>

    labelli = detailed_page_soup.find_all('li', class_="mb-ldp__dtls__body__list--item")
    if labelli is not None:
        for li in labelli:
            label = li.find('div', class_="mb-ldp__dtls__body__list--label").text
            if label == "Developer":
                property_devloper = li.find('a', class_="mb-ldp__dtls__body__list--link").text # 7(Property-Devloper)
            if label == "Project":
                property_project = li.find('a', class_="mb-ldp__dtls__body__list--link").text # 8(Property-Project)
            if label == "Furnished Status":
                isFurnished = li.find('div', class_="mb-ldp__dtls__body__list--value").text # 9(IsFurnished)
            if label == "Car parking":
                num_of_carparkings = li.find('div', class_="mb-ldp__dtls__body__list--value").text # 10(CarParking)
            if label == "Lifts":
                num_of_lifts = li.find('div', class_="mb-ldp__dtls__body__list--value").text # 11(Lifts)
            if label == "Floor":
                floor = li.find('div', class_="mb-ldp__dtls__body__list--value").text # 12(Floor)

    # -------------------------------->>

    # ------------------------------
    # 5 Data Formatting and cleaning 
    # ------------------------------

    # Cleaning of ( property_price ) --> Done
    if property_price.find("Lac") != -1:
        property_price =  math.floor( float ( property_price.split(" Lac")[0]) * 100000 )
    elif property_price.find(",") != -1:
        property_price = math.floor( float( str(property_price.split(",")[0]) + str(property_price.split(",")[1] )) )

    # Cleaning of ( property_bhk ) --> Done
    if property_bhk.isnumeric():
        property_bhk = int( property_bhk.strip() )
    else:
        property_bhk = "-"

    # Cleaning of ( property_sqft )
    try:
        if property_sqft.find("Sq-ft") != -1:
            property_sqft = property_sqft.split(" Sq-ft")[0].split(" ")[-1]
        elif property_sqft.find("Sq-m") != -1:
            property_sqft = property_sqft.split(" Sq-m")[0].split(" ")[-1]
            property_sqft = math.floor(float(property_sqft) * 10.7639104)
        elif property_sqft.find("Sq-yrd") != -1:
            property_sqft = property_sqft.split(" Sq-yrd")[0].split(" ")[-1]
            property_sqft = math.floor(int(property_sqft) * 9)
        else:
            property_sqft = "-"  
    except Exception as e:
        property_sqft = "-"  

    # Cleaning of ( property_city ) --> Done
    if property_city == "":
        property_city = "-"
    else:
        property_city = property_city.strip()

    # Cleaning of ( property_locality ) --> Done
    if property_locality == "": 
        property_locality = "-"
    else:
        property_locality = property_locality.strip()

    # Cleaning of ( property_devloper) --> Done
    if property_devloper == "":
        property_devloper = "-"
    else:
        property_devloper = property_devloper.strip()

    # Cleaning of ( isFurnished ) --> Done
    if isFurnished == "":
        isFurnished = "-"
    else:
        isFurnished = isFurnished.strip()

    # Cleaning of ( num_of_lifts ) --> Done
    if num_of_lifts == "":
        num_of_lifts = "-"
    elif num_of_lifts.isnumeric():
        num_of_lifts = int(num_of_lifts)

    # Cleaning of ( num_of_carparkings ) --> Done

    temp = num_of_carparkings
    if num_of_carparkings == "":
            num_of_carparkings = "-"
    else:
        num_of_carparkings = 0
        for i in temp:
            if i.isnumeric():
                num_of_carparkings += int(i)


    # Cleaning of ( floor ) --> Done
    if floor == "":
        floor = "-"
    else:
        floormain = floor.split(" (Out of ")[0]
        if floormain == "Ground":
            floormain = 0
        if floormain == "Upper Basement":
            floormain = -1
        if floormain == "Lower Basement":
            floormain = -2
        else: 
            try:
                floormain = int(floormain)
                flooroutof = floor.split(" (Out of ")[1].split(" ")[0]
                flooroutof = int(flooroutof)

                floor = str(floormain) + "-" + str(flooroutof)
            except Exception as e :
                floor = "-"
        

    # Cleaning of ( property_project ) --> Done
    if property_project == "":
        property_project = "-"
    else:
        property_project = property_project.strip()

    # Cleaning of ( num_of_baths ) --> Done
    if num_of_baths == "":
        num_of_baths = "-"
    elif num_of_baths.isnumeric():
        num_of_baths = int(num_of_baths)

    # Cleaning of ( num_of_balconies ) --> Done
    if num_of_balconies == "":
        num_of_balconies = "-"
    elif num_of_balconies.isnumeric():
        num_of_balconies = int(num_of_balconies)

    # Cleaning of ( bechelors_or_family ) --> Done
    bechelors_or_family = bechelors_or_family.strip()


    # -------------------------------->>

    data = [
        property_price,   property_bhk, 
        property_sqft,     property_city,    property_locality, 
        property_devloper ,isFurnished,      num_of_lifts,
        num_of_carparkings,floor,            property_project, 
        num_of_baths,      num_of_balconies, bechelors_or_family
    ]

    print(data)
    return data

    # -------------------------------->>

# -------------------------------
# Function : write_to_csv
# Output : None
# --->>>
def write_to_csv( file_path, dataArray ):
    with open ( file_path, 'a' , newline="") as file:
        writer = csv.writer(file)
        writer.writerow(dataArray)

# ----------------
# Function Calling
# --->>>
scrape_magicbricks()
