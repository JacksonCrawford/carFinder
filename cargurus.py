import requests
import json
import formatUtil
from bs4 import BeautifulSoup
from config import CarConfig
import linker
from pathlib import Path

def scraper(fileName):
    # Creates a config to grab info for the linker
    config = CarConfig()
    # Opens the CSV file for data storage
    # Uses w+ mode; will create the csv file if it doesn't exist
    file = open(fileName, "a")
    for link in linker.cargurus(config.getMake(), config.getModel(), config.getCity(), config.getState()):
        # Creates a GET request to the carGurus link in the config
        site = requests.get(link)
        # Parses the website using lxml
        soup = BeautifulSoup(site.text, "lxml")
        # Grabs the script tags, we're looking for the "featuredListings" object somewhere in the React code
        scripts = soup.find_all("script")
        # Loops through the script tags looking for the featuredListings object
        for script in scripts:
            # Checks if the script tag has any contents
            if len(script.contents) <= 0:
                continue
            # Grabs the text from the script tag
            text = script.contents[0]
            # The script tag we're looking for is about 115,000
            # in size on a small query, so just filter out anything below a certain threshold
            if (len(text) > 50000):
                # Finds the location of the listings object
                startLocation = text.find('"featuredListings"') - 1
                # Finds the locations of the listings object if featuredListings doesn't exist
                if startLocation == -2:
                    startLocation = text.find('"listings"') - 1
                # Checks if it actually exists in this script tag
                if startLocation != -2:
                    # Goes back one index to include the starting {
                    # Finds the end of the listings object using the start of the next line
                    endLocation = text.find("\n        window.__PREFLIGHT__", startLocation) - 1
                    # Takes a substring to grab the entire object
                    listingsText = text[startLocation: endLocation]
                    # Converts from JSON text to a Python Dictionary
                    listings = json.loads(listingsText)["listings"]
                    # Starts putting data into CSV format
                    for listing in listings:
                        # For Debug
                        # print(json.dumps(listing, sort_keys=True, indent=4))
                        # Grabs the year
                        year = listing["carYear"]
                        # Grabs the price
                        try:
                            price = listing["expectedPriceString"].replace(",", "").replace("$", "")
                        except:
                            continue
                        # Grabs the mileage
                        try:   
                            miles = (listing["mileageString"] + " miles").replace(",", "").replace(" miles", "")
                        except:
                            continue
                        # Puts the data into CSV format
                        csvString = (str(year) + "," + price + "," + miles)
                        # Finally writes the CSV data to the file
                        # print(csvString)
                        file.write(csvString + "\n")
    # Closes the csv file
    file.close()
    print("Done Scraping CarGurus!")


if __name__ == '__main__':
    # Creates a file path
    path = Path("output/cargurus.csv")
    # Wipes the CSV file
    formatUtil.fileWipe(path)
    # Starts the scraper
    scraper(path)
