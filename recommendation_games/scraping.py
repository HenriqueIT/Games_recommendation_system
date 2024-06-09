from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
from datetime import datetime
import pandas as pd

def get_data(driver, base_url, page_number):
    """
    Retrieves data from a webpage.
    
    Parameters:
        driver (WebDriver): The Selenium WebDriver instance.
        base_url (str): The base URL of the webpage.
        page_number (int): The page number to scrape.
    
    Returns:
        tuple: A tuple containing lists of game names, release dates, genres, and scores.
    """

    # Construct the URL for the current page
    url = f"{base_url}{page_number}"
    driver.get(url)

    # Wait for elements to be present and get the value of each element
    game_names = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//h2[@class='line-clamp-2 font-poppins text-base font-bold text-skin-primary md:text-lg']"))
    )
    dates = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'flex items-center space-x-2 text-xs tracking-wider text-skin-secondary/80')]"))
    )
    genres = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "mt-2.flex.items-center.gap-2"))
    )
    scores = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@class, "text-center font-score tracking-wider text-skin-primary shadow-md shadow-black/20")]'))
    )

    # Extract the text from each element and store them in lists
    game_names = [element.text for element in game_names]
    dates = [element.text for element in dates]
    genres = [element.text for element in genres]
    scores = [element.text for element in scores]

    return game_names, dates, genres, scores

def scrape_pages(driver, base_url, start_page, end_page):
    """
    Scrapes data from multiple pages of a website.
    
    Parameters:
        driver (WebDriver): The Selenium WebDriver instance.
        base_url (str): The base URL of the webpage.
        start_page (int): The starting page number.
        end_page (int): The ending page number.
    
    Returns:
        tuple: A tuple containing lists of game names, release dates, genres, and scores.
    """

    game_names = []
    dates = []
    genres = []
    scores = []

    for page_number in range(start_page, end_page + 1):
        print('page_number', page_number)

        # Get data for the current page
        try:
            page_game_names, page_dates, page_genres, page_scores = get_data(driver, base_url, page_number)
            
        except Exception as e:
            print(f"Error on page {page_number}: {e}")
            continue  # Skip this page if an error occurs

        # Extend the lists with data from the current page
        game_names.extend(page_game_names)
        dates.extend(page_dates)
        genres.extend(page_genres)
        scores.extend(page_scores)

    return game_names, dates, genres, scores

def create_dataframe(game_names, dates, genres, scores):
    """
    Creates a pandas DataFrame from scraped data.
    
    Parameters:
        game_names (list): List of game names.
        dates (list): List of release dates.
        genres (list): List of genres.
        scores (list): List of scores.
    
    Returns:
        DataFrame: A DataFrame containing the scraped data.
    """

    # Create data frames for each element
    df_games = pd.DataFrame({'Game': game_names})
    
    # Convert date strings to datetime objects and then to a formatted string
    date_objects = [datetime.strptime(date_str.split('\n')[-1], '%b %d, %Y').strftime('%d/%m/%Y') for date_str in dates]
    df_dates = pd.DataFrame({'Release': date_objects})

    # Split genre strings into separate columns
    genre_lists = [string.split('\n') for string in genres]
    df_genre = pd.DataFrame(genre_lists, columns=['genre1', 'genre2', 'genre3'])

    # Convert score strings to floats
    score_lists = [float(num) for num in scores]
    df_score = pd.DataFrame({'Score': score_lists})

    # Concatenate all data frames horizontally
    df_all = pd.concat([df_games, df_dates, df_genre, df_score], axis=1)
    df_all.insert(0, 'Rank', df_all.index + 1)  # Add a Rank column

    return df_all

def main():
    
    # Define constants for the scraping
    base_url = "https://whatoplay.com/ps4/best/?pageNum="
    start_page = 1
    end_page = 83

    # Specify the path to the Chrome WebDriver
    driver_path = 'PATH_TO_THE_WEBDRIVER'
    driver = webdriver.Chrome(driver_path)

    # Scrape data from the specified range of pages
    game_names, dates, genres, scores = scrape_pages(driver, base_url, start_page, end_page)

    # Create a DataFrame from the scraped data
    df_games = create_dataframe(game_names, dates, genres, scores)

    # Close the browser window
    driver.quit()

    # Save the DataFrame to a CSV file
    df_games.to_csv('games.csv', index=False)

if __name__ == "__main__":
    main()
