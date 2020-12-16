from selenium import webdriver
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Pool, cpu_count
import urllib.request
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


if __name__ == "__main__":
    url = 'https://oficinajudicialvirtual.pjud.cl/home/index.php#'

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")

    ubicacion = '/Users/giuseppe/Documents/proyectos/scrapping/documents'

    options = webdriver.ChromeOptions()

    prefs = {"download.default_directory": ubicacion,
             "plugins.always_open_pdf_externally": True}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(executable_path=DRIVER_BIN, options=options)

    driver.get(url)
    windows_before = driver.current_window_handle


    # Inicio del flujo
    btnAllServices = driver.find_element_by_xpath(
        "/html/body/div[4]/div/section[1]/div/div[1]/div[1]/div[1]/div/button")
    btnAllServices.click()
    driver.implicitly_wait(5)
    unique_key = driver.find_element_by_xpath(
        "/html/body/div[4]/div/section[1]/div/div[1]/div[1]/div[1]/div/div/a[1]")
    print(unique_key)
    print("Element is visible? " + str(unique_key.is_displayed()))
    unique_key.click()
    driver.implicitly_wait(5)

    # Pagina para iniciar sesion en el pjud
    uname = driver.find_element_by_id('uname')
    pword = driver.find_element_by_id('pword')
    sesionFile = open("sesion.txt", "r")
    rut = sesionFile.readline()
    password = sesionFile.readline()
    sesionFile.close()
    uname.send_keys(rut)
    pword.send_keys(password)
    btnSubmit = driver.find_element_by_xpath(
        '/html/body/main/section/div/div[1]/div/form/div[3]/div/button')
    btnSubmit.click()

    # PAGINA DEL PJUDICIAL
    wait = WebDriverWait(driver, 10)
    wait.until(EC.title_is("Oficina Judicial Virtual"))

    myCauses = driver.find_element_by_xpath('/html/body/div[1]/nav/ul/li[1]/a')
    myCauses.click()

    familiaTab = driver.find_element_by_id('familiaTab')
    familiaTab.click()
    driver.implicitly_wait(10)

    openModal = driver.find_element_by_xpath(
        '/html/body/div[1]/div/div[2]/div[2]/div/div/section/div/div/div[2]/div[7]/div/div/div[2]/div/div/table/tbody/tr[2]/td[1]/a')
    openModal.click()

    waitModal = WebDriverWait(driver, 20)
    waitModal.until(EC.visibility_of_element_located(
        (By.ID, "modalDetalleMisCauFamilia")))
    print('Se termino la espera del modal')
    modal = driver.find_element_by_id('modalDetalleMisCauFamilia')

    # existen los input
    # dtatxtDoc => action="misCausas/familia/documentos/docMovimientosFamilia.php"
    # dtaCert => action="misCausas/familia/documentos/docCertificadoEscrito.php"
    # dtaDocRes => misCausas/familia/documentos/docDiligenciaRespuestaFamilia.php

    js = "document.getElementsByName('dtatxtDoc').forEach(e => e.setAttribute('type', ''))"
    driver.execute_script(js)
    js2 = "document.getElementsByName('dtaCert').forEach(e => e.setAttribute('type', ''))"
    driver.execute_script(js2)

    # crear un archivo
    open("data.txt", "w")

    file = open("data.txt", "a")
    download_list = []
    # Obtener los documentos
    allDocs = driver.find_elements_by_css_selector(
        "form[action='misCausas/familia/documentos/docMovimientosFamilia.php'][target='txtdoc']>input")
    pathDoc = 'https://oficinajudicialvirtual.pjud.cl/misCausas/familia/documentos/docMovimientosFamilia.php?dtatxtDoc='
    for doc in allDocs:
        # print(pathDoc + doc.get_attribute('value'))
        download_list.append(pathDoc + doc.get_attribute('value'))
        # file.write("ARCHIVO: " + doc.get_attribute('value') + "\n")

    patchCert = 'https://oficinajudicialvirtual.pjud.cl/misCausas/familia/documentos/docCertificadoEscrito.php?dtaCert='
    certFamilia = driver.find_elements_by_css_selector(
        "form[action='misCausas/familia/documentos/docCertificadoEscrito.php'][target='cert']>input")
    for cert in certFamilia:
        download_list.append(patchCert + cert.get_attribute('value'))
    file.close()

    print('documents', download_list)
    # Abrir nueno tab y posicionarse en el
    jsOpenNewTab = "window.open()"
    driver.execute_script(jsOpenNewTab)
    WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
    windows_after = driver.window_handles
    new_window = [x for x in windows_after if x != windows_before][0]
    driver.switch_to.window(new_window)

    # Descargar los archivos
    for doc in download_list:
        driver.get(doc)

    print('TERMINO')

