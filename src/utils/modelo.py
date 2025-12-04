import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.select import Select
from bd import conection
import random



def generate_random_mac():
    return "020000%02x%02x%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
    )

# consulta = "SELECT * FROM portales where id = %s"
# valores =(31,)
# resultados = conection.ejecutar_consulta(consulta,valores)
# if resultados:
#     for resultado in resultados:
#         print(resultado)


random_mac = generate_random_mac()
print(f"Generated MAC: {random_mac}")

#portales cautivos - una pagina

#portal sitWifi grupo estrella blanca - una pagina
#https://qa.datawifi.co/easyfi/web/app.php/portal?called=d838fc092e60&mac=

#portal viva centro comercial - una pagina
#https://qa.datawifi.co/easyfi/web/app.php/portal?called=e0cbbc88ca54&mac=

#portal sitWifi open pay final - una pagina
#https://qa.datawifi.co/easyfi/web/app.php/portal?called=1439x8997&mac=


#portales cautivos - VARIOS PANELES

#portal total play - puerta texaco 
#https://qa.datawifi.co/easyfi/web/app.php/portal?called=f89e2875a8aa&mac=

#portal hola bienvenido
#https://qa.datawifi.co/easyfi/web/app.php/portal?called=764x10753&mac=

#portal parque fundidora Nuevo leon (contiene video que hay que reproducir)
#https://qa.datawifi.co/easyfi/web/app.php/portal?called=764x3802&mac=

#portal Walmart (con redes sociales)
#https://qa.datawifi.co/easyfi/web/app.php/portal?called=764x2442&mac=

#portal Zona digital (hay que escoger una opcion para seguir CON O SIN)
#https://app.datawifi.co/newversion/easyfi/web/app.php/portal?called=187c0b116a90&mac=









url = "https://qa.datawifi.co/easyfi/web/app.php/portal?called=e0cbbc88ca54&mac="+random_mac


driver = webdriver.Edge()
driver.get(url)
title = driver.title
driver.implicitly_wait(3)
print("Probando con la url: "+url)
#saber cuandos div con clase panel_portal hay
panels = driver.find_elements(By.CLASS_NAME, 'panel_portal')
for panel in panels:
    #saber en que panel voy por el id
    panel_id = panel.get_attribute('id')
    print(panel_id)
    inputs = panel.find_elements(By.XPATH, ".//input[not(@type='hidden')]")
    for input_element in inputs:
        # Hacer un print del html del elemento
        print(input_element.get_attribute('name'))

        # Si el input es type checkbox seleccionarlo
        if input_element.get_attribute('type') == 'checkbox':
            if not input_element.is_selected():
                driver.execute_script("arguments[0].click();", input_element)
                print("Checkbox ya seleccionado")
        elif input_element.get_attribute('type') == 'tel':
            input_element.send_keys("3118698113")
        elif input_element.get_attribute('type') == 'email':
            input_element.send_keys("testdatawifi@datawifi.co")
        else:
            input_element.send_keys("test data")
        if input_element.get_attribute('title') == 'Zipcode':
            input_element.clear()
            input_element.send_keys("111111")
    driver.implicitly_wait(2)
    select_elements = panel.find_elements(By.TAG_NAME, 'select')
    for select_element in select_elements:
        select = Select(select_element)
        driver.implicitly_wait(1)
        select.select_by_index(1)

    #Buscar los text area y llenarlos
    text_areas = panel.find_elements(By.TAG_NAME, 'textarea')
    for text_area in text_areas:
        text_area.send_keys("test data")

    #buscar los radio buttons y seleccionarlos
    radio_buttons = panel.find_elements(By.XPATH, ".//input[@type='radio']")
    for radio_button in radio_buttons:
        if not radio_button.is_selected():
            driver.execute_script("arguments[0].click();", radio_button)
            print("Radio button seleccionado")

    # Buscar el boton visible con clase continuar dentro del panel
    continuar_button = panel.find_element(By.CLASS_NAME, 'continuar')
    # verificar que el boton esté habilitado y si no lo está, esperar 2 segundos
    while not continuar_button.is_enabled():
        time.sleep(2)
        print("Esperando a que el boton continuar esté habilitado")
    continuar_button.click()
    #esperar a que cargue el siguiente panel
    time.sleep(2)
time.sleep(5)
driver.quit()

#realizar la consulta a la base de datos
consulta = "SELECT * FROM informacion_usuarios where id_cliente = %s and mac= %s"
valores = (None, random_mac)
resultados = conection.ejecutar_consulta(consulta, valores)
if resultados:
    print("Se encontraron resultados en informacion_usuarios para "+random_mac)
else:
    print("No se encontraron resultados en informacion_usuarios para "+random_mac)
#buscar en la tabla de registro_usuarios
consulta = "SELECT * FROM registro_usuarios where id_cliente = %s and mac_usuario= %s"
valores = (None, random_mac)
resultados = conection.ejecutar_consulta(consulta, valores)
if resultados:
    print("Se encontraron resultados en registro_usuarios para "+random_mac)
else:
    print("No se encontraron resultados en registro_usuarios para "+random_mac)



