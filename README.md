GUIA PASO A PASO PARA PONER EN FUNCIONAMIENTO EL PROYECTO SCOUTER_LOL

Esta guia resume todo el proceso realizado para ejecutar correctamente el proyecto.

==================================================

PASO 1: Instalar herramientas básicas

```bash
sudo apt update

sudo apt install git python3-pip python3-venv python3-full
```

==================================================

PASO 2: Instalar Miniconda

Descargar Miniconda para Linux x86_64.

Ir a Descargas:

```bash
cd ~/Downloads
```

Instalar:

```bash
bash Miniconda3-latest-Linux-x86_64.sh
```

Aceptar:
- ENTER
- yes

Cargar Conda:

```bash
source ~/.bashrc
```

==================================================

PASO 3: Crear entorno virtual compatible con TensorFlow

Crear entorno Conda con Python 3.11:

```bash
conda create -n ia python=3.11
```

Activar entorno:

```bash
conda activate ia
```

Verificar que aparezca:

```text
(ia)
```

==================================================

PASO 4: Ir a la carpeta del proyecto

Ejemplo:

```bash
cd ~/Desktop/sf_django_deep_learning/scouter_lol
```

Verificar que exista `manage.py`:

```bash
ls
```

==================================================

PASO 5: Instalar Django

```bash
pip install Django==4.1
```

Verificar versión:

```bash
python -m django --version
```

==================================================

PASO 6: Instalar dependencias del proyecto

Instalar librerías necesarias:

```bash
pip install numpy pandas matplotlib seaborn scikit-learn pillow opencv-python torch opencv-python-headless Pillow django-cors-headers
```

==================================================

PASO 7: Entrenar modelos

```bash
python backend/cv_scouter/scripts/train_pipeline.py
python backend/lol_scouter/scripts/train_pipeline.py
```

==================================================

PASO 8: Aplicar migraciones

```bash
python manage.py migrate
```

==================================================

PASO 9: Ejecutar el servidor

```bash
python manage.py runserver
```

Si todo funciona aparecerá:

```text
Starting development server at http://127.0.0.1:8000/
```

==================================================

PASO 10: Abrir el proyecto en el navegador

Entrar a:

```text
http://127.0.0.1:8000/
```

==================================================

PASO 11: Detener el servidor

En terminal:

```text
CTRL + C
```

==================================================

PASO 12: Activar nuevamente el entorno en futuras sesiones

Cada vez que abras Ubuntu:

```bash
conda activate ia
```

Luego:

```bash
cd ~/Desktop/sf_django_deep_learning/scouter_lol
```

y finalmente:

```bash
python manage.py runserver
```
==================================================
==================================================

EJECUCIÓN DEL NLP

```bash
# 1. Entrenar (solo la primera vez)
python backend/lol_scouter/scripts/train_pipeline.py

# 2. Generar scouting (editar equipos en el script)
python backend/lol_scouter/backend/scripts/run_scouting.py
```


EJECUCIÓN DE LA VISIÓN POR COMPUTADORA

```bash
# Entrenar (solo la primera vez)
python backend/cv_scouter/scripts/train_pipeline.py
```

EJECUCIÓN DEL FRONTEND

```bash
cd frontend
npm install # Solamente la primera vez
npm run dev```
