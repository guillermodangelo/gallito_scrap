import time
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from tqdm import tqdm

DRIVER_PATH = r"C:\chromedriver.exe"
HEADLESS = True


def flatten(t):
    "Flattens a list"
    return [item for sublist in t for item in sublist]


def chrome(path, headless=HEADLESS):
    "Instantiates a Chrome driver instance"
    opt = webdriver.ChromeOptions()

    args = [
        '--blink-settings=imagesEnabled=false',
        '--no-sandbox',
        '--incognito',
        '--disable-dev-shm-usage'
        '--window-size=1920,1080',
        '--disable-extensions',
        '--dns-prefetch-disable',
        '--disable-gpu',
        '--log-level=3',

    ]

    if headless:
        args.append('--headless=new')

    for arg in args:
        opt.add_argument(arg)

    browser = webdriver.Chrome(service=Service(path), options=opt)
    browser.implicitly_wait(10)
    browser.set_page_load_timeout(35)

    return browser


def scraper(urls, driver_path=DRIVER_PATH, headless=HEADLESS):
    "Scrap through a list of Gallitos's URLs"
    data = []
    metraje = []
    url_publicacion=[]

    driver = chrome(driver_path, headless=headless)

    for url in urls:
        try:
            driver.get(url)
            time.sleep(np.random.uniform(3.0, 11.5))
            print(f'Scrapping {url}...')
        except Exception as e:
            print('Get method failed, check URL. ')
            raise e

        try:
            no_avisos_xpath = '//*[@id="grillaavisos"]'
            grilla = driver.find_element(By.XPATH, no_avisos_xpath)
            texto_no_aviso = 'No se han encontrado avisos para la búsqueda seleccionada.'

            if grilla.text == texto_no_aviso:
                return
            else:
                pagina = [e.text.splitlines() for e in driver.find_elements(By.CSS_SELECTOR, '.contenedor-info')]
                data.append(pagina)
                html = [e.get_attribute("innerHTML") for e in driver.find_elements(By.CSS_SELECTOR,'.contenedor-info .mas-info')]

                for i in html:
                    soup = BeautifulSoup(i, "html.parser")
                    metraje.append(soup.span.text)
                    url_publicacion.append(soup.find('a')['href'])

        except Exception as e:
            print(f'Error scraping {url}: {str(e)}')
            continue

    print('Preparando resultados...')
    flat_list = flatten(data)
    result = pd.DataFrame(flat_list, columns=['desc', 'valor'])
    result['metraje'] = metraje
    result['metraje'] = result['metraje'].replace({' m2': ''}, regex=True)
    result['url'] = url_publicacion
    print('Fin de la preparación de resultados.')
    driver.close()
    driver.quit()

    return result


def scrap_latlng(urls, driver_path=DRIVER_PATH, headless=HEADLESS):
    "Scraps coordinates through a list of URLs of individual real state pages from El Gallito"
    coordenadas = []
    metraje = []

    driver = chrome(driver_path, headless=headless)

    for url in tqdm(urls):
        try:
            time.sleep(2)   
            driver.get(url)

            metros_xpath = '/html/body/form/main/div/div[2]/div[1]/div[6]/p'
            metros_element = driver.find_element(By.XPATH, metros_xpath)
            metros_text = metros_element.text
            print("Extracted text:", metros_text)
            metraje.append(metros_text)

            elem = driver.find_elements(By.CSS_SELECTOR,'#ubicacion')
        except:
            try:
                time.sleep(np.random.uniform(2.0, 8.0))
                driver.get(url)

                metros_xpath = '/html/body/form/main/div/div[2]/div[1]/div[6]/p'
                metros_element = driver.find_element(By.XPATH, metros_xpath)
                metros_text = metros_element.text
                metraje.append(metros_text)

                elem = driver.find_elements(By.CSS_SELECTOR, '#ubicacion')
            except Exception as e:
                print(f'Failed at URL: {url}.', e)
                elem = []
                metraje.append('sin datos')

        if elem != []:
            try:
                element = driver.find_element('xpath', "/html/body/form/main/div/div[1]/ul/li[4]/a/i")
                element.click()
                ubic_html = [e.get_attribute("innerHTML") for e in driver.find_elements(By.CSS_SELECTOR,"#ubicacion")]
                soup = BeautifulSoup(ubic_html[0], "html.parser")
                src = soup.find('iframe')['src']
                latlng = src.split('q=', 1)[1].split('&zoom=', 1)[0]
            except Exception as e:
                print(e)
                latlng = '/,/'
    
            if latlng == '/,/':
                coordenadas.append('Nan,Nan')
            else:
                coordenadas.append(latlng)
        else:
            coordenadas.append('Nan,Nan')

    driver.close()
    driver.quit()

    return coordenadas, metraje
