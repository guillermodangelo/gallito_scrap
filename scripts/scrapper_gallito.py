from selenium import webdriver
import pandas as pd
import time
from numpy import random
from bs4 import BeautifulSoup


def flatten(t):
    "Flattens a list"
    return [item for sublist in t for item in sublist]

def chrome(path, headless=True):
    "Instantiates a Chrome driver instance"
    opt = webdriver.ChromeOptions()
    if headless:
        opt.add_argument("--headless")
    opt.add_argument('--blink-settings=imagesEnabled=false')
    opt.add_argument('--no-sandbox')
    browser = webdriver.Chrome(path, options=opt)
    browser.implicitly_wait(10)
    browser.set_page_load_timeout(20)

    return browser


def scrapper(url, driver_path='C:/Users/59898/Documents/chromedriver.exe', headless=True):
    "Scrap through a list of Gallitos's URLs"
    data = []
    metraje = []
    url_publicacion=[]

    driver = chrome(driver_path, headless=headless)

    for i in url:
        try:
            driver.get(i)
            time.sleep(random.uniform(2.0, 7.5))
        except Exception as e:
            print('Get method failed, check URL. ', e)

        no_avisos_xpath = '//*[@id="grillaavisos"]'
        grilla = driver.find_elements_by_xpath(no_avisos_xpath)
        texto_no_aviso = 'No se han encontrado avisos para la búsqueda seleccionada.'

        if grilla[0].text == texto_no_aviso:
            driver.quit()
            return
        else:
            pagina = [e.text.splitlines() for e in driver.find_elements_by_css_selector('.contenedor-info')]
            data.append(pagina)
            html = [e.get_attribute("innerHTML") for e in driver.find_elements_by_css_selector('.contenedor-info .mas-info')]

            for i in html:
                soup = BeautifulSoup(i, "html.parser")
                metraje.append(soup.span.text)
                url_publicacion.append(soup.find('a')['href'])

            flat_list = flatten(data)
            result = pd.DataFrame(flat_list, columns=['desc', 'valor'])
            result['metraje'] = metraje
            result['metraje'] = result['metraje'].replace({' m2': ''}, regex=True)
            result['url'] = url_publicacion
            driver.quit()

            return result

       
def scrap_latlng(url, driver_path='C:/Users/59898/Documents/chromedriver.exe', headless=True):
    "Scraps coordinates through a list of URLs of individual real state pages from El Gallito"
    coordenadas = []

    driver = chrome(driver_path, headless=headless)

    for i in url:
        try:   
            driver.get(i)
            elem = driver.find_elements_by_css_selector('#ubicacion')
        except:
            try:
                time.sleep(3)
                driver.get(i)
                elem = driver.find_elements_by_css_selector('#ubicacion')
            except:
                elem = []

        if elem != []:
            element = driver.find_element_by_xpath("/html/body/form/main/div/div[1]/ul/li[4]/a/i")
            element.click()
            ubic_html = [e.get_attribute("innerHTML") for e in driver.find_elements_by_css_selector("#ubicacion")]
            soup = BeautifulSoup(ubic_html[0], "html.parser")
            src = soup.find('iframe')['src']
            latlng = src.split('q=', 1)[1].split('&zoom=', 1)[0]
            if latlng == '/,/':
                coordenadas.append('Nan,Nan')
            else:
                coordenadas.append(latlng)
        else:
            coordenadas.append('Nan,Nan')

    driver.quit()

    return coordenadas


def format_barrio(df, column):
    "Formatea strings de Barrio Gallito a Barrio INE"
    barrios_dict = {
        'Aguada' : 'Aguada',
        'Aires Puros' : 'Aires Puros',
        'Atahualpa' : 'Atahualpa',
        'B. De Carrasco' : 'Bañados de Carrasco',
        'Barrio Sur' : 'Barrio Sur',
        'Belvedere' : 'Belvedere',
        'Brazo Oriental' : 'Brazo Oriental',
        'Buceo' : 'Buceo',
        'Capurro' : 'Capurro, Bella Vista',
        'Carrasco' : 'Carrasco',
        'Carrasco Norte' : 'Carrasco Norte',
        'Casabo' : 'Casabó, Pajas Blancas',
        'Casavalle' : 'Casavalle',
        'Centro' : 'Centro',
        'Cerrito' : 'Cerrito',
        'Cerro' : 'Cerro',
        'Ciudad Vieja' : 'Ciudad Vieja',
        'Cno. Maldonado' : 'Colón Centro y Noroeste',
        'Colon' : 'Colón Sureste, Abayubá',
        'Cordon' : 'Cordón',
        'Golf' : 'Flor de Maroñas',
        'Ituzaingo' : 'Ituzaingó',
        'J. Hipodromo' : 'Jardines del Hipódromo',
        'Jacinto Vera' : 'Jacinto Vera',
        'La Blanqueada' : 'La Blanqueada',
        'La Comercial' : 'La Comercial',
        'La Figurita' : 'La Figurita',
        'La Teja' : 'La Teja',
        'Larrañaga' : 'Larrañaga',
        'Las Acacias' : 'Las Acacias',
        'Lezica' : 'Lezica, Melilla',
        'Malvin' : 'Malvín',
        'Malvin Norte' : 'Malvín Norte',
        'Manga' : 'Manga',
        'Maroñas' : 'Maroñas, Parque Guaraní',
        'Maroñas Curva' : 'Maroñas, Parque Guaraní',
        'Melilla' : 'Lezica, Melilla',
        'Nuevo Paris' : 'Mercado Modelo, Bolívar',
        'Pajas Blancas' : 'Nuevo París',
        'Palermo' : 'Palermo',
        'Parque Batlle' : 'Parque Batlle, Villa Dolores',
        'Parque Rodo' : 'Parque Rodó',
        'Paso De La Arena' : 'Paso de la Arena',
        'Peñarol' : 'Peñarol, Lavalleja',
        'Perez Castellanos' : 'Castro, P. Castellanos',
        'Piedras Blancas' : 'Piedras Blancas',
        'Pocitos' : 'Pocitos',
        'Pocitos Nuevo' : 'Pocitos',
        'Prado' : 'Prado, Nueva Savona',
        'Prado Norte' : 'Prado, Nueva Savona',
        'Puerto Buceo' : 'Buceo',
        'Punta Carretas' : 'Punta Carretas',
        'Punta Gorda' : 'Punta Gorda',
        'Punta Rieles' : 'Punta Rieles, Bella Italia',
        'Reducto' : 'Reducto',
        'Sayago' : 'Sayago',
        'Tres Cruces' : 'Tres Cruces',
        'Union' : 'Unión',
        'Villa Dolores' : 'Parque Batlle, Villa Dolores',
        'Villa Española' : 'Villa Española',
        'Villa Muñoz' : 'Villa Muñoz, Retiro'
        }

    return df[column].map(barrios_dict)


def encode_barrio(df, column):
    "Codifica barrio INE"
    barrios_dict = {
    'Ciudad Vieja':1,
    'Centro':2,
    'Barrio Sur':3,
    'Cordón':4,
    'Palermo':5,
    'Parque Rodó':6,
    'Punta Carretas':7,
    'Pocitos':8,
    'Buceo':9,
    'Parque Batlle, Villa Dolores':10,
    'Malvín':11,
    'Malvín Norte':12,
    'Punta Gorda':13,
    'Carrasco':14,
    'Carrasco Norte':15,
    'Bañados de Carrasco':16,
    'Maroñas, Parque Guaraní':17,
    'Flor de Maroñas':18,
    'Las Canteras':19,
    'Punta Rieles, Bella Italia':20,
    'Jardines del Hipódromo':21,
    'Ituzaingó':22,
    'Unión':23,
    'Villa Española':24,
    'Mercado Modelo, Bolívar':25,
    'Castro, P. Castellanos':26,
    'Cerrito':27,
    'Las Acacias':28,
    'Aires Puros':29,
    'Casavalle':30,
    'Piedras Blancas':31,
    'Manga, Toledo Chico':32,
    'Paso de las Duranas':33,
    'Peñarol, Lavalleja':34,
    'Cerro':35,
    'Casabó, Pajas Blancas':36,
    'La Paloma, Tomkinson':37,
    'La Teja':38,
    'Prado, Nueva Savona':39,
    'Capurro, Bella Vista':40,
    'Aguada':41,
    'Reducto':42,
    'Atahualpa':43,
    'Jacinto Vera':44,
    'La Figurita':45,
    'Larrañaga':46,
    'La Blanqueada':47,
    'Villa Muñoz, Retiro':48,
    'La Comercial':49,
    'Tres Cruces':50,
    'Brazo Oriental':51,
    'Sayago':52,
    'Conciliación':53,
    'Belvedere':54,
    'Nuevo París':55,
    'Tres Ombúes, Victoria':56,
    'Paso de la Arena':57,
    'Colón Sureste, Abayubá':58,
    'Colón Centro y Noroeste':59,
    'Lezica, Melilla':60,
    'Villa García, Manga Rural':61,
    'Manga':62
        }

    return df[column].map(barrios_dict)