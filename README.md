# web-scraping

# Scraping de Administradores de findas Colegiados de Tenerife

Este proyecto realiza un web scraping sobre la página web de la CAF Tenerife para obtener información sobre los colegiados registrados. La información extraída incluye el nombre, apellidos, localidad, estado, enlace al perfil, correo electrónico y teléfono de cada colegiado.

## Requisitos

Asegúrate de tener los siguientes paquetes instalados:

- `requests`: para realizar las peticiones HTTP a la web.
- `beautifulsoup4`: para parsear y extraer los datos del HTML.
- `pandas`: para exportar los datos a un archivo Excel.
- `openpyxl`: requerido por `pandas` para exportar a Excel.
- `csv`: para exportar los datos a un archivo CSV.
- `json`: para exportar los datos a un archivo JSON.

Puedes instalar las dependencias necesarias con el siguiente comando:

```bash
pip install requests beautifulsoup4 pandas openpyxl
