import requests
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd

# URL base de la web
base_url = "https://caftenerife.org/info-ciudadano/colegiados/"

# Headers para evitar bloqueos
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Lista para almacenar los datos de todos los colegiados
colegiados = []

def scrape_page(url):
    """
    Extrae los datos de la tabla de colegiados de una página y los agrega a la lista 'colegiados'
    """
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error al obtener la página {url}: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    tabla = soup.find("table")
    if not tabla:
        print("No se encontró la tabla en la página.")
        return None

    # Se ignora la cabecera de la tabla
    filas = tabla.find_all("tr")[1:]
    for fila in filas:
        columnas = fila.find_all("td")
        if len(columnas) > 4:
            apellidos = columnas[2].text.strip()
            nombre = columnas[3].text.strip()
            localidad = columnas[4].text.strip()
            estado = columnas[5].text.strip()

            # Obtener enlace al perfil (si existe)
            enlace = columnas[2].find("a")
            perfil_url = enlace["href"] if enlace else None
            if perfil_url and not perfil_url.startswith("http"):
                perfil_url = f"https://caftenerife.org{perfil_url}"

            colegiados.append({
                "nombre": nombre,
                "apellidos": apellidos,
                "localidad": localidad,
                "estado": estado,
                "perfil": perfil_url,
                "email": None,     # Inicializamos el email
                "telefono": None   # Inicializamos el teléfono
            })

def get_total_pages():
    """
    Extrae el número total de páginas a recorrer.
    """
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print("Error al obtener la página principal.")
        return 1  
    soup = BeautifulSoup(response.text, "html.parser")
    paginacion = soup.find("div", class_="tablenav-pages")
    if not paginacion:
        return 1  
    paginas = paginacion.find_all("a", class_="page-numbers")
    max_page = 1
    for pagina in paginas:
        texto = pagina.text.strip()
        if texto.isdigit():
            num = int(texto)
            if num > max_page:
                max_page = num
    return max_page

# --- PROCESO DE SCRAPING ---

# Obtener el número total de páginas
total_pages = get_total_pages()
print(f"Total de páginas: {total_pages}")

# Recorrer todas las páginas y extraer los datos básicos de los colegiados
for page in range(1, total_pages + 1):
    print(f"Scrapeando página {page}...")
    # Se utiliza el parámetro "listpage" 
    scrape_page(f"{base_url}?listpage={page}")

# Recorrer cada perfil y extraer el email y teléfono desde cada perfil
for colegiado in colegiados:
    if colegiado["perfil"]:
        perfil_url = colegiado["perfil"]
        perfil_resp = requests.get(perfil_url, headers=headers)
        if perfil_resp.status_code == 200:
            perfil_soup = BeautifulSoup(perfil_resp.text, "html.parser")
            
            # --- Extracción del EMAIL ---
            # Buscar el primer enlace cuyo href empiece por "mailto:"
            a_tag = perfil_soup.find("a", href=lambda href: href and href.startswith("mailto:"))
            if a_tag:
                email = a_tag.get("href").replace("mailto:", "").strip()
                colegiado["email"] = email
            else:
                colegiado["email"] = "No encontrado"
            
            # --- Extracción del TELÉFONO ---
            # Buscar todas las celdas con clase "label" para encontrar aquella con el texto "Teléfono"
            telefono = "No encontrado"
            for label in perfil_soup.find_all("td", class_="label"):
                if label.get_text(strip=True) == "Teléfono":
                    data_td = label.find_next_sibling("td", class_="data")
                    if data_td:
                        telefono = data_td.get_text(strip=True)
                    break
            colegiado["telefono"] = telefono
        else:
            colegiado["email"] = "Error al cargar perfil"
            colegiado["telefono"] = "Error al cargar perfil"
    print(colegiado)

# --- EXPORTACIÓN DE LOS DATOS ---

# Definir los campos/columnas a exportar
campos = ["nombre", "apellidos", "localidad", "estado", "perfil", "email", "telefono"]

# Exportar a CSV
with open("colegiados.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=campos)
    writer.writeheader()
    writer.writerows(colegiados)
print("Datos exportados a colegiados.csv")

# Exportar a JSON
with open("colegiados.json", "w", encoding="utf-8") as jsonfile:
    json.dump(colegiados, jsonfile, ensure_ascii=False, indent=4)
print("Datos exportados a colegiados.json")

# Exportar a XLSX utilizando pandas
df = pd.DataFrame(colegiados, columns=campos)
df.to_excel("colegiados.xlsx", index=False)
print("Datos exportados a colegiados.xlsx")
