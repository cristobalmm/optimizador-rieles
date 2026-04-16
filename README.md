Guía para compartir tu Optimizador de Rieles

Para que otra persona use este programa desde cualquier lugar del mundo sin instalar Python, sigue estos pasos:

Paso 1: Estructura de Archivos (CRÍTICO)

Para que Streamlit Cloud funcione, tu repositorio en GitHub debe tener esta estructura. El archivo de requerimientos no puede estar dentro de carpetas.

📦 optimizador-rieles (Nombre de tu repositorio)
 ┣ 📂 app
 ┃ ┗ 📜 optimizador.py
 ┗ 📜 requirements.txt  <-- DEBE ESTAR AQUÍ (EN LA RAÍZ)


Paso 2: Verificación de Git y GitHub

Como futuro Ingeniero de TI, verifica estos tres puntos directamente en la web de GitHub:

Ortografía Exacta: El archivo debe llamarse requirements.txt (en minúsculas y terminado en s). Un error común es poner requirement.txt (singular) o requirements.txt.txt (si tienes extensiones ocultas en Windows).

Ubicación en la Raíz: Entra a tu repo en GitHub. ¿Ves el archivo apenas entras? Si tienes que entrar a la carpeta app para verlo, está mal ubicado.

Rama Correcta: Asegúrate de que los cambios estén en la rama main (o la que hayas seleccionado en el despliegue de Streamlit).

Paso 3: Depuración en Streamlit Cloud (Logs)

Si el error persiste, abre tu aplicación en Streamlit Cloud y:

Haz clic en "Manage app" (esquina inferior derecha).

Se abrirá una consola lateral. Busca el icono de la "hoja de papel" o "terminal" para ver los Logs.

Busca una línea que diga: Installing dependencies from requirements.txt....

Si no aparece esa línea, Streamlit no encontró el archivo.

Si aparece pero dice Error, es porque hay un error de escritura dentro del archivo.

🛠️ Solución de Emergencia (Limpiar Caché)

A veces, Streamlit Cloud guarda una imagen del contenedor antiguo. Para forzar una instalación limpia:

En el panel de Streamlit Cloud, borra la app (Delete).

Crea una nueva (New app).

Selecciona el repositorio nuevamente. Esto obliga al servidor a leer el requirements.txt desde cero.

Contenido del archivo requirements.txt

streamlit
pandas
openpyxl
pulp
