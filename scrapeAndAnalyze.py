import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests
import csv
import re


def getAmazonPrice(productUrl):
    """Return HMTL from the page"""
    # using headers to pretending to be a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # getting the HTML of the page
    page = requests.get(productUrl, headers=headers)

    # parsing the HTML
    soup = BeautifulSoup(page.content, "html.parser")
    # returning the html from the page
    return soup


def remove_dollar_sign(price):
    """Return the truncated price without the $ sign"""
    return re.sub(r'\$', '', price)


def get_books_details(soup):
    """Return book details and takes html string"""
    details = []

    # finding all the divs
    divs = soup.find_all("div", {"class": "a-section a-spacing-base"})

    for div in divs:
        # getting title of the book
        try:
            title = div.find(
                "span", {"class": "a-size-base-plus a-color-base a-text-normal"}).text
            # getting the price of the book
            initialPrice = div.find("span", {"class": "a-offscreen"}).text
            # removing the dollar sign
            price = remove_dollar_sign(initialPrice)
            # getting the rating of the book inside the div "a-row a-size-small"
            ratingDiv = div.find("div", {"class": "a-row a-size-small"})
            # getting the rating of the book
            rating = ratingDiv.find("span", {"class": "a-size-base"}).text

            # appending the details to the list in from of a dictionary
            details.append({
                "title": title,
                "price": price,
                "rating": rating
            })
        except:
            pass
    return details


def get_next_page(soup):
    """return the next page's link"""
    # the next page button
    next_page = soup.find(
        "a", {"class": "s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"})["href"]
    # nextpagelink path
    next_page = "https://www.amazon.com" + next_page
    return next_page


class Book:

    # runs on initialization and takes the keyworkd option

    def __init__(self, keyword):
        self.keyword = keyword
        self.url = "https://www.amazon.com/s?k=" + keyword
        self.csv_name = f'{self.keyword}_books'
        self.Books = []

    def getDetails(self):
        """Get book search details and create a CSV file of the data"""
        # getting the first html then loop through the pages
        soup = getAmazonPrice(self.url)
        # books = []
        # getting the details of the books and appending to the list
        self.Books += get_books_details(soup)
        # getting the first 5 next pages only into a list.
        pageLinks = []
        try:
            while True:
                # getting the next page
                next_page = get_next_page(soup)
                # getting the details of the books and appending to the list
                self.Books += get_books_details(soup)
                # appending the next page to the list
                pageLinks.append(next_page)
                # getting the html of the next page
                soup = getAmazonPrice(next_page)
                # stopping at lastpage or on page 5
                if "s-pagination-disabled " in str(soup) or len(pageLinks) == 2:
                    break
        except:
            pass

        # Calculating the minmaxes with lamda functions
        highest_rated_book = max(self.Books, key=lambda x: x["rating"])
        lowest_rated_book = min(self.Books, key=lambda x: x["rating"])
        highest_priced_book = max(self.Books, key=lambda x: x["price"])
        lowest_priced_book = min(self.Books, key=lambda x: x["price"])

        print("------------------------------------------------------------------------------------------------------------")

        print(f"Total {self.keyword} books found: {len(self.Books)}")
        print(
            f"Highest rated {self.keyword} book: {highest_rated_book['title']}")
        print(
            f"Lowest rated {self.keyword} book: {lowest_rated_book['title']}")
        print(
            f"Highest priced {self.keyword} book: {highest_priced_book['title']}")
        print(
            f"Lowest priced {self.keyword} book: {lowest_priced_book['title']}")

        print("------------------------------------------------------------------------------------------------------------")

        # writing the details to a csv file.
        with open(self.csv_name + ".csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Price", "Rating"])
            for book in self.Books:
                writer.writerow([book["title"], book["price"], book["rating"]])
        print(f"CSV file created: {self.csv_name}.csv")
        self.analyzedata()

    def analyzedata(self):
        print("Analyzing data...")
        """Analyze the data from the saved csv file and generate a plot"""
        # getting books data from csv.
        # booksDf = pd.read_csv(f'{self.csv_name}.csv')

        booksDf = pd.DataFrame(self.Books)

        print(
            f"*********************************{self.keyword} sample data*****************************")
        print(booksDf.head(20))

        newDf = booksDf.dropna()

        # migrare rating from object to float and coerce errors
        newDf['rating'] = pd.to_numeric(newDf['rating'], errors='coerce')
        # # drop all rows with NaN rating values
        newDf = newDf.dropna(subset=['rating'])
        # # drop all rows with rating more than 5
        newDf = newDf[newDf['rating'] <= 5]

        # make new_df csv
        newDf.to_csv(f'{self.keyword}_new.csv')

        newDf = pd.read_csv(f'{self.keyword}_new.csv')

        print(
            f"////////////////////// {self.keyword} Data Description//////////////////////////")

        print(newDf.describe())

        # generate bar graph for min maxes, mean

        min_price = newDf['price'].min()
        max_price = newDf['price'].max()
        mean_price = newDf['price'].mean()
        min_rating = newDf['rating'].min()
        max_rating = newDf['rating'].max()
        mean_rating = newDf['rating'].mean()

        price_names = np.array(
            [f'{self.keyword} MinPrice', f'{self.keyword} MaxPrice', f'{self.keyword} MeanPrice'])
        price_values = np.array([min_price, max_price, mean_price])
        rating_names = np.array(
            [f'{self.keyword} MinRating', f'{self.keyword} MaxRating', f'{self.keyword} MeanRating'])
        rating_values = np.array([min_rating, max_rating, mean_rating])

        colors = ['yellow', 'blue', 'orange']
        # scale the plot size
        plt.figure(figsize=(10, 6))
        plt.subplot(1, 2, 1)
        plt.bar(price_names, price_values, color=colors)
        plt.title(f'{self.keyword} Price')
        plt.savefig(f'{self.keyword}_price.png')
        plt.show()

        plt.figure(figsize=(10, 6))
        plt.subplot(1, 2, 2)
        plt.bar(rating_names, rating_values, color=colors)
        plt.title(f'{self.keyword} Rating')
        plt.savefig(f'{self.keyword}_rating.png')
        plt.show()

        # scatter plot for price and rating
        plt.figure(figsize=(10, 6))
        # add title, x and y labels
        plt.title('Price vs Rating', fontsize=20)
        plt.xlabel('Price ($)', fontsize=15)
        plt.ylabel('Rating', fontsize=15)
        # add the scatter plot
        plt.scatter(booksDf['Price'], booksDf['Rating'],
                    s=100, color='slateblue', alpha=0.5)

        plt.show()


def main():
    keyword_options = [{"1": "python"}, {"2": "javascript"}, {"3": "java"}, {
        "4": "php"}, {"5": "Golang"},  {"6": "data structures and algorithms"}, {"7": "css"}]
    print("Choose a keyword to search for books")
    for option in keyword_options:
        for key, value in option.items():
            print(f"{key} - {value}")
    try:
        keyword = input("Enter an option number: ")
        # checking if keyword is valid
        if keyword not in [str(i) for i in range(1, 8)]:
            print("Invalid option")
            return

        # getting the keyword from the options
        for option in keyword_options:
            for key, value in option.items():
                if keyword == key:
                    keyword = value

        print(f"Searching for books related to {keyword}")
        # initializing the class
        book = Book(keyword)
        # gettung book deatils
        book.getDetails()
        # analyzing data
        # book.analyzedata()
    except:
        pass


main()
