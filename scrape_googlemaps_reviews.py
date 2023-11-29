from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import time
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
import csv
import requests
import json

def get_gas_stations(api_key, location):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = "YPF OR AXION OR PUMA Gas Station in " + location
    params = {
        "query": query,
        "key": api_key
    }
    response = requests.get(url, params=params)
    return response.json()

def get_concatenated_cities_from_csv(file_name):
    concatenated_cities = []
    with open(file_name, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            concatenated_city = f"{row[0]},{row[1]}"  # Assuming you want to concatenate the first and second columns
            concatenated_cities.append(concatenated_city)
    return concatenated_cities


def get_gas_station_urls(api_key, csv_file_name):
    cities = get_concatenated_cities_from_csv(csv_file_name)  # Replace with your CSV file name
    print(cities)
    urls = []
    for city in cities:
        results = get_gas_stations(api_key, city)
        for result in results['results']:
            if 'Argentina' in result['formatted_address']:
                urls.append(f"https://www.google.com/maps/place/?q=place_id:{result['place_id']}")
    return urls



api_key = "AIzaSyAsLsEphpVv3OgDnf2wLQpAmjI7URDBvFY"
csv_file_name = "C:\\Users\\ivan_\\OneDrive\\Documentos\\PI\\localidades_padron_bocas.csv"  # Replace with your CSV file name
#urls = get_gas_station_urls(api_key, csv_file_name)


urls = []
print(urls)

df = pd.read_csv('./output.csv', index_col=False)
places_id = df['place_id'].unique()

urls = [(f"https://www.google.com/maps/place/?q=place_id:{id}", id) for id in places_id]


header = True

df = pd.DataFrame(columns=['antiguedad', 'puntuacion', 'opinion', 'marca', 'place_id'])
pd.set_option('display.max_colwidth', 1000)

df.to_csv('reviews.csv', mode='w',header=True , index=False)
print('csv header')

for url, id in urls:

    place_id = id

    driver = webdriver.Chrome()

    driver.get(url)

    print('nueva EESS')

    try:
        address = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div:nth-child(9) > div:nth-child(3) > button > div > div.rogA2c > div.Io6YTe.fontBodyMedium.kR99db').text
    except:
        adress = 'No es posible obtener la dirección'
    
    try:
        bandera = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.TIHn2 > div > div.lMbq3e > div:nth-child(1) > h1').text
    except:
        bandera = 'No es posible obtener la marca'

    if 'ypf' in bandera.lower():
        marca = 'YPF'
    elif 'axion' in bandera.lower():
        marca = 'AXION'
    elif 'shell' in bandera.lower():
        continue
    else:
        marca = 'PUMA'


    try:
        # click on all reviews
        element = driver.find_element(By.XPATH,'//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]/div[2]/div[2]')
        print("Element is present")
        try:
            element.click()
            # Review page is loaded
        except:
            # exception and thus quit
            print("Not Loaded")
            driver.quit()
    except:
        # exception and thus quit
        print("Element is not present")
        driver.quit()

    # click on ordenar
    try:
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.m6QErb.Pf6ghf.KoSBEe.ecceSd.tLjsW > div.TrU0dc.kdfrQc > button > span > span')))
        order = driver.find_element(By.CSS_SELECTOR, '#QA0Szd > div > div > div.w6VYqd > div.bJzME.tTVLSc > div > div.e07Vkf.kA9KIf > div > div > div.m6QErb.DxyBCb.kA9KIf.dS8AEf > div.m6QErb.Pf6ghf.KoSBEe.ecceSd.tLjsW > div.TrU0dc.kdfrQc > button > span > span').click()
    except Exception as e:
        order = None
        print(e,'--------------------------------------------------------')

    try:
        actions = ActionChains(driver)

        # mueve el cursor hasta la opcion ordenar por fecha mas reciente
        actions.send_keys(Keys.DOWN, Keys.RETURN).perform()
        sleep(1)
        print('ordenado')
    except:
        print('no ordenado')

    # load the list of already loaded reviews
    try:
        reviews = driver.find_elements(By.CLASS_NAME,'jftiEf')
        sleep(2)
    except:
        continue

    # highlight the last div 
    idx = 0
    formated_date = None
    while True:

        # scroll the window to get more reviews
        for i in range(5):
        #for i in range(idx, len(reviews)):
            try:
                review = reviews[i]
            except IndexError as e:
                continue
            print("\n\n------------------",i,"--------------\n\n")
            try:
                moreButton = review.find_element(By.CLASS_NAME,'w8nwRe')
                moreButton.click()
                sleep(2)
            except:
                pass
            
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.rsqaWe')))
                text_date = review.find_element(By.CSS_SELECTOR, '.rsqaWe').text
                if 'minuto' in text_date:
                    current_date = datetime.now()
                    formated_date = current_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif 'hora' in text_date:
                    current_date = datetime.now()
                    formated_date = current_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '1 día' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(days=1)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '2 días' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(days=1)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '3 días' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(days=2)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '4 días' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(days=3)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '5 días' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(days=4)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '6 días' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(days=5)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif 'una semana' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(weeks=1)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '2 semanas' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(weeks=2)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '3 semanas' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(weeks=3)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                elif '4 semanas' in text_date:
                    current_date = datetime.now()
                    next_date = current_date - timedelta(weeks=4)
                    formated_date = next_date.strftime('%d/%m/%Y')
                    print(formated_date)
                else:
                    print('continue')
                    continue

            except:
                text_date = None

            
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.wiI7pd')))
                text_class = review.find_element(By.CSS_SELECTOR, '.wiI7pd')
                text = text_class.text
            except:
                text = None
            print(text)

                
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.hCCjke.vzX5Ic')))
                img_elements = review.find_elements(By.CSS_SELECTOR, '.hCCjke.vzX5Ic')
                num_img_elements = len(img_elements)
            except:
                num_img_elements = None
            print('puntuacion: ', num_img_elements)
            
            try:
                driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", review, "border: none;")
            except:
                pass

            new_row = pd.DataFrame({
                'antiguedad': [formated_date],
                'puntuacion': [num_img_elements],
                'opinion': [text],
                'marca': [marca],
                'place_id': [place_id]
            })

            df = pd.concat([df, new_row], ignore_index=False)

            driver.execute_script('arguments[0].scrollIntoView(true);', reviews[i])

        

        # get the list of reviews again
        idx = len(reviews) -1
        reviews = driver.find_elements(By.CLASS_NAME,'jftiEf')
        sleep(1)
        print("CHANGEEEEE ",idx,len(reviews))
        break
        # check if the list is loaded
        if len(reviews) == 0:
            break

        print("----------------------------------------------------------------------------")
df.to_csv('reviews.csv', mode='a',header=False , index=False)
print('append csv sin header')