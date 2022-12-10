import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
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

    def getDetails(self):
        """Get book search details and create a CSV file of the data"""
        # getting the first html then loop through the pages
        soup = getAmazonPrice(self.url)
        books = []
        # getting the details of the books
        books = get_books_details(soup)
        # getting the first 5 next pages only into a list.
        pageLinks = []
        try:
            while True:
                # getting the next page
                next_page = get_next_page(soup)
                # getting the details of the books and appending to the list
                books += get_books_details(soup)
                # appending the next page to the list
                pageLinks.append(next_page)
                # getting the html of the next page
                soup = getAmazonPrice(next_page)
                # stopping at lastpage or on page 5
                if "s-pagination-disabled " in str(soup) or len(pageLinks) == 4:
                    break
        except:
            pass

        # Calculating the minmaxes with lamda functions
        highest_rated_book = max(books, key=lambda x: x["rating"])
        lowest_rated_book = min(books, key=lambda x: x["rating"])
        highest_priced_book = max(books, key=lambda x: x["price"])
        lowest_priced_book = min(books, key=lambda x: x["price"])

        print(f"Total books found: {len(books)}")
        print(f"Highest rated book: {highest_rated_book['title']}")
        print(f"Lowest rated book: {lowest_rated_book['title']}")
        print(f"Highest priced book: {highest_priced_book['title']}")
        print(f"Lowest priced book: {lowest_priced_book['title']}")

        # writing the details to a csv file.
        with open(self.csv_name + ".csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Price", "Rating"])
            for book in books:
                writer.writerow([book["title"], book["price"], book["rating"]])

    def analyzedata(self):
        """Analyze the data from the saved csv file and generate a plot"""
        # getting books data from csv.
        booksDf = pd.read_csv(f'{self.csv_name}.csv')
        print("*********************************sample data*****************************")
        print(booksDf.head())
        # getting type of rating
        booksDf['Price'].dtype
        # migrating Rating from object to float
        booksDf['Rating'] = pd.to_numeric(booksDf['Rating'], errors='coerce')
        # getting all rows with null rating
        booksDf[booksDf['Rating'].isnull()]
        # dropping all rows with null rating
        booksDf = booksDf.dropna()
        # dropping all rows with ratings which are more than 5
        booksDf = booksDf[booksDf['Rating'] <= 5]

        print("//////////////////////Data Description//////////////////////////")

        print(booksDf.describe())

        plt.figure(figsize=(10, 6))
        # add title, x and y labels
        plt.title('Price vs Rating', fontsize=20)
        plt.xlabel('Price ($)', fontsize=15)
        plt.ylabel('Rating', fontsize=15)
        # add the scatter plot
        plt.scatter(booksDf['Price'], booksDf['Rating'],
                    s=100, color='slateblue', alpha=0.5)

        # save the plot as a png image
        plt.savefig(f'{self.csv_name}_plot.png')


def main():
    keyword_options = [{"1": "python"}, {"2": "javascript"}, {"3": "java"}, {
        "4": "php"}, {"5": "perl"},  {"6": "data structures and algorithms"}, {"7": "css"}]
    print("Choose a keyword to search for books")
    for option in keyword_options:
        for key, value in option.items():
            print(f"{key} - {value}")
    try:
        keyword = input("Enter an option number: ")
        try:
            if eval(keyword) != (len(keyword_options)):
                return
        except:
            pass
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
        book.analyzedata()
    except:
        pass


main()
