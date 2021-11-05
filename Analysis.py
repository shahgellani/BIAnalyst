import json
from itertools import chain

import matplotlib.pyplot as plt
import pandas as pd


def analysis():
    """
    The analysis method is responsible for analyse the scraped data from scrapy,
    The main tasks it is performing are :

    ● Make a small graph showing the top 10 highest rated books.
    ● Listing the author who had the most number of books in the popular book list from the last 12 months.
    ● Listing all the genres in order of number of books.
    ● Finally, calculating the average rating of books in each genre.

    :return:
    """
    df = pd.read_json('Data_test.json')
    genre_books = {}
    # Getting dict of authors with number of published books and saving as a dictionary
    author_list_with_most_books = df.groupby('author')['book_name'].size().sort_values(ascending=False).to_dict()
    dict_to_json(file_name='Author list with most books', dict_data=author_list_with_most_books)
    genres_tuple = list(zip(df.rating_value, df.genres))
    total_book_genres_list = set(chain(*df.loc[:, "genres"].values.tolist()))
    for rating, book_genre in genres_tuple:
        for genre in total_book_genres_list:
            if genre in book_genre:
                if genre not in genre_books:
                    genre_books[genre] = 1
                    genre_books[genre + '_rating'] = rating
                else:
                    genre_books[genre] += 1
                    genre_books[genre + '_rating'] += rating
    dict_to_json(dict_data=genre_books, file_name='Total books in each Genre')
    new_genre_dict = {}
    for genre in total_book_genres_list:
        temp_dict = {}
        temp_dict['Genre_name'] = genre
        temp_dict['Total_Books'] = genre_books[genre]
        temp_dict['Avg_rating'] = genre_books.get(genre + '_rating') / genre_books.get(genre)
        new_genre_dict[genre] = temp_dict
    print(new_genre_dict)
    dict_to_json(dict_data=new_genre_dict, file_name='Test result')
    ten_highest_rated_book = df.nlargest(10, 'rating_value')
    rating = ten_highest_rated_book['rating_value'].values.tolist()[::-1]
    books = ten_highest_rated_book['book_name'].values.tolist()[::-1]
    make_graph(x_data=rating, y_data=books)


def make_graph(x_data, y_data):
    """
    For drawing bar graph
    :param x_data:
    :param y_data:
    :return:
    """
    plt.barh(y_data, x_data)
    plt.ylabel('Books')
    plt.xlabel('rating')
    plt.title('Top 10 most rated books')
    plt.show()


def dict_to_json(dict_data, file_name):
    """
    For saving dict into json file
    :param dict_data:
    :param file_name:
    :return:
    """
    output_file = open(file_name + '.json', 'w', encoding='utf-8', )
    json_object = json.dumps(dict_data, indent=4)
    output_file.write(json_object)


def dict_to_df(dictionary):
    """
    Returns the dataframe of dictionary
    :param dictionary:
    :return:
    """
    data_items = dictionary.items()
    data_list = list(data_items)
    data_frame = pd.DataFrame(data_list)
    return data_frame


# Initial point
if __name__ == '__main__':
    analysis()
