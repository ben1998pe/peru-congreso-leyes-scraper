from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# =========================
# CONFIGURACIÓN DEL NAVEGADOR
# =========================
options = Options()
options.add_argument("--start-maximized")
service = Service("chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# =========================
# ABRIR PÁGINA
# =========================
url = "https://wb2server.congreso.gob.pe/spley-portal/#/expediente/search"
driver.get(url)
time.sleep(5)

# =========================
# MOSTRAR FILTROS AVANZADOS
# =========================
try:
    btn_filtros = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[.//i[contains(@class, "pi-filter")]]')
    ))
    btn_filtros.click()
    print("✅ Botón 'Ver Filtros Avanzados' clickeado correctamente.")
    time.sleep(2)
except Exception as e:
    print("❌ Error al hacer clic en 'Ver Filtros Avanzados':", e)

# =========================
# INGRESAR FECHAS
# =========================
hoy = datetime.now().strftime("%d/%m/%Y")
try:
    input_desde = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//input[@placeholder="Seleccionar desde"]')
    ))
    input_desde.clear()
    input_desde.send_keys(hoy)

    input_hasta = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//input[@placeholder="Seleccionar hasta"]')
    ))
    input_hasta.clear()
    input_hasta.send_keys(hoy)

    print(f"✅ Fechas ingresadas: {hoy} - {hoy}")
    time.sleep(2)
except Exception as e:
    print("❌ Error al ingresar fechas:", e)

# =========================
# CLIC EN BOTÓN "BUSCAR"
# =========================
try:
    btn_buscar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//button[.//i[contains(@class, "pi-filter")] and .//span[contains(text(), "Buscar")]]')
    ))
    btn_buscar.click()
    print("✅ Botón 'Buscar' clickeado correctamente.")
    time.sleep(5)
except Exception as e:
    print("❌ Error al hacer clic en 'Buscar':", e)

# =========================
# SCRAPING DE RESULTADOS
# =========================
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
filas = soup.select("tbody.p-datatable-tbody > tr")

resultados = []
for fila in filas:
    try:
        columnas = fila.find_all("td")
        proyecto = columnas[0].text.strip()
        fecha = columnas[1].text.strip()
        titulo = columnas[2].find("span", class_="ellipsis").text.strip()
        estado = columnas[3].text.strip()
        proponente = columnas[4].text.strip()
        autores = columnas[5].find_all("li")
        lista_autores = [a.text.strip() for a in autores]
        autores_str = ", ".join(lista_autores)

        resultados.append({
            "proyecto": proyecto,
            "fecha": fecha,
            "titulo": titulo,
            "estado": estado,
            "proponente": proponente,
            "autores": autores_str
        })
    except Exception as e:
        print("❌ Error procesando fila:", e)

# =========================
# GUARDAR CSV
# =========================
df = pd.DataFrame(resultados)

os.makedirs("data", exist_ok=True)
# Guardar CSV con la fecha del día
fecha_archivo = datetime.now().strftime("%Y-%m-%d")
nombre_archivo = f"data/proyectos_ley_{fecha_archivo}.csv"
df.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")
print(f"✅ Datos guardados en {nombre_archivo}")
print(df.head())

# =========================
# CERRAR NAVEGADOR
# =========================
driver.quit()
print("👋 Navegador cerrado correctamente.")
