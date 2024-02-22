import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup


def check_product_on_stylus(product_name):
    try:
        search_url = f"https://stylus.ua/search?q={product_name.replace(' ', '+')}"
        response = requests.get(search_url)

        if response.status_code != 200:
            return 'error', "Failed to fetch the search results page from Stylus."

        soup = BeautifulSoup(response.text, 'html.parser')
        product_listing = soup.find('div', class_='product-listing-right')

        if product_listing:
            return 'error', f"The product name '{product_name}' is ambiguous."

        product = soup.find('div', class_='product-page-block')
        if not product:
            return 'error', f"The product '{product_name}' is not present on Stylus."

        model = product.find('h1', class_='page-name').text
        availability = product.find('div', class_='availability-block mobile').find('div').text
        result = f"The product '{model}' is currently "

        if availability == 'Нет в наличии':
            status = 'out of stock'
            result += 'out of stock on Stylus.'
        elif availability == 'Доступен предзаказ':
            status = 'available on preorder'
            result += 'available on preorder on Stylus.'
        else:
            status = 'available'
            result += 'available on Stylus.'

        return status, result

    except Exception as e:
        return 'error', f"An error occurred: {e}"


def check_products(products):
    statuses, times = [], []

    for product in products:
        status, message = check_product_on_stylus(product)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        statuses.append(status if status != 'error' else '')
        times.append(current_time)
        print(f'{current_time} {message}')

    return statuses, times


if __name__ == '__main__':
    products_df = pd.read_excel('products.xlsx')
    products_df['status'], products_df['time'] = check_products(products_df['model'])
    products_df.to_excel('products_availability.xlsx', index=False)
