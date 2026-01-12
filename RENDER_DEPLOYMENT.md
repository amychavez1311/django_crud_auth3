# Guía de Despliegue en Render con Azure Storage

## 📋 Requisitos Previos

1. ✅ Cuenta de Render (https://render.com)
2. ✅ Cuenta de Azure con Storage Account creado
3. ✅ Repositorio en GitHub con el proyecto

---

## 🔧 Paso 1: Configurar Azure Storage

### 1.1 Crear Storage Account en Azure

1. Ve al Portal de Azure (https://portal.azure.com)
2. Busca "Storage accounts" y crea uno nuevo
3. Configuración recomendada:
   - **Performance**: Standard
   - **Redundancy**: LRS (Locally Redundant Storage)
   - **Access tier**: Hot

### 1.2 Crear Container para Certificados

1. Dentro de tu Storage Account, ve a "Containers"
2. Crea un nuevo container llamado `certificados`
3. **Public access level**: Private (recomendado)

### 1.3 Obtener Connection String

1. Ve a tu Storage Account
2. En el menú izquierdo, selecciona "Access keys"
3. Copia el **Connection string** de la Key 1 o Key 2
4. Debe verse así:
   ```
   DefaultEndpointsProtocol=https;AccountName=tuaccount;AccountKey=tukey==;EndpointSuffix=core.windows.net
   ```

---

## 🚀 Paso 2: Configurar Render

### 2.1 Crear Web Service en Render

1. Inicia sesión en Render (https://dashboard.render.com)
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Selecciona el repositorio del proyecto

### 2.2 Configuración del Web Service

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
gunicorn djangocrud.wsgi:application
```

**Environment:**
- **Python 3**

---

## 🔐 Paso 3: Variables de Entorno en Render

Ve a la sección **"Environment"** en tu Web Service de Render y agrega estas variables:

### Variables Requeridas:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `SECRET_KEY` | `tu-secret-key-segura-aqui` | Django SECRET_KEY (genera una nueva) |
| `PYTHON_VERSION` | `3.11.0` | Versión de Python |
| `AZURE_STORAGE_CONNECTION_STRING` | `DefaultEndpointsProtocol=https;AccountName=...` | Tu connection string de Azure |
| `AZURE_STORAGE_CONTAINER_NAME` | `certificados` | Nombre del container en Azure |

### Variables Opcionales:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `DEBUG` | `False` | Siempre False en producción |
| `ALLOWED_HOSTS` | `tu-app.onrender.com` | Se configura automático |

---

## 📝 Paso 4: Verificar Archivos del Proyecto

### 4.1 Archivo `build.sh` (Debe existir en raíz)

```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
```

### 4.2 Archivo `requirements.txt` (Ya configurado)

Verifica que incluya:
```
Django==4.2
gunicorn==21.2.0
whitenoise==6.5.0
azure-storage-blob==12.19.0
reportlab==4.0.7
PyPDF2==3.0.1
Pillow==9.5.0
psycopg2-binary==2.9.6
dj-database-url==2.0.0
```

### 4.3 Archivo `djangocrud/settings.py` (Ya configurado)

Verifica que tenga:
```python
# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_STORAGE_CONTAINER_NAME = os.environ.get('AZURE_STORAGE_CONTAINER_NAME', 'certificados')

# Debug basado en entorno
DEBUG = 'RENDER' not in os.environ

# Static files con WhiteNoise
if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## 🎯 Paso 5: Desplegar

1. **Hacer Push al repositorio:**
   ```bash
   git add .
   git commit -m "Configuración para Render con Azure"
   git push origin main
   ```

2. **En Render:**
   - Render automáticamente detectará el push
   - Iniciará el build
   - Ejecutará `build.sh`
   - Desplegará la aplicación

3. **Monitorear el Build:**
   - Ve a la pestaña "Logs" en Render
   - Verifica que no haya errores
   - El build debería completarse en 2-5 minutos

---

## ✅ Paso 6: Crear Superusuario

Una vez desplegado, necesitas crear un superusuario:

1. Ve a tu Web Service en Render
2. Click en **"Shell"** (terminal)
3. Ejecuta:
   ```bash
   python manage.py createsuperuser
   ```
4. Sigue las instrucciones para crear el admin

---

## 🧪 Paso 7: Verificar Funcionamiento

### 7.1 Verificar la Aplicación

1. Abre tu URL de Render: `https://tu-app.onrender.com`
2. Registra un usuario de prueba
3. Crea una hoja de vida
4. Sube certificados (PDFs)
5. Descarga el CV en PDF

### 7.2 Verificar Azure Storage

1. Ve a Azure Portal
2. Abre tu Storage Account
3. Ve a "Containers" → "certificados"
4. Deberías ver los PDFs subidos con rutas como:
   ```
   reconocimientos/user_1/certificado_20260112.pdf
   cursos/user_1/certificado_python_20260112.pdf
   ```

---

## 🔍 Troubleshooting (Solución de Problemas)

### 🖼️ Problema: Las imágenes de perfil no aparecen en el PDF generado

**Causa:** En Azure Storage, los archivos no tienen una ruta local (`.path`). Solo tienen una URL (`.url`).

**Solución (Ya Implementada):**
- El `CVPDFGenerator` ahora descarga las imágenes temporalmente desde Azure
- Usa `urllib.request.urlretrieve()` para descargar desde la URL de Azure
- Crea archivos temporales con `tempfile`
- Los archivos temporales se eliminan automáticamente después de generar el PDF

**Cómo funciona:**
```python
# En _add_header()
cert_url = imagen.url  # Obtener URL de Azure
urllib.request.urlretrieve(cert_url, temp_path)  # Descargar a archivo temporal
# Usar temp_path en ReportLab para insertar en PDF
os.remove(temp_path)  # Limpiar temporal
```

### 📄 Problema: Los certificados (PDFs) no se incrustan en el CV

**Causa:** Similar al anterior - no se puede acceder a `.path` en Azure Storage.

**Solución (Ya Implementada):**
- El método `_incrustar_certificados()` ahora:
  1. Detecta si es una URL (Azure) o ruta local
  2. Si es URL, descarga el PDF temporalmente
  3. Usa PyPDF2 para mergear el PDF
  4. Limpia el archivo temporal

**Verificar en Logs de Render:**
```
Certificado incrustado: Curso: Python Avanzado
```

### Problema: Error al subir certificados

**Solución:**
- Verifica que `AZURE_STORAGE_CONNECTION_STRING` esté correctamente configurada
- Revisa los logs en Render: "Logs" tab
- Verifica que el container `certificados` exista en Azure

### Problema: Archivos estáticos no se cargan

**Solución:**
- Verifica que `build.sh` ejecute `collectstatic`
- Asegúrate que WhiteNoise esté en `INSTALLED_APPS` (middleware)
- Revisa los logs del build

### Problema: Base de datos vacía después de deploy

**Solución:**
- Render usa PostgreSQL por defecto
- Los datos de SQLite local NO se transfieren
- Necesitas crear un nuevo superusuario (Paso 6)
- Los datos serán persistentes entre deploys

### Problema: SECRET_KEY inválida

**Solución:**
Genera una nueva SECRET_KEY segura:
```python
import secrets
print(secrets.token_urlsafe(50))
```
Copia el resultado y úsalo en la variable de entorno en Render

---

## 📊 Monitoreo y Mantenimiento

### Ver Logs en Tiempo Real
```bash
# En el Shell de Render
tail -f /var/log/render-build.log
```

### Reiniciar el Servicio
- Ve a tu Web Service
- Click en "Manual Deploy" → "Clear build cache & deploy"

### Base de Datos PostgreSQL
- Render provee PostgreSQL automáticamente
- La URL se configura en `DATABASE_URL` automáticamente
- Las migraciones se ejecutan en cada deploy

---

## 🔒 Seguridad en Producción

### ✅ Configuraciones Importantes:

1. **DEBUG = False** en producción
2. **SECRET_KEY** única y segura (no usar la de desarrollo)
3. **ALLOWED_HOSTS** configurado correctamente
4. **Azure Storage** con acceso privado (no público)
5. **HTTPS** habilitado (Render lo hace automático)

### ❌ NO HACER:

- ❌ NO commitear `.env` con credenciales
- ❌ NO usar `DEBUG = True` en producción
- ❌ NO usar la misma SECRET_KEY que en desarrollo
- ❌ NO subir archivos sensibles al repositorio

---

## 📚 Recursos Adicionales

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Azure Storage Python SDK**: https://docs.microsoft.com/azure/storage/blobs/storage-quickstart-blobs-python
- **WhiteNoise**: http://whitenoise.evans.io/

---

## 🎉 ¡Listo!

Tu aplicación Django está desplegada en Render con Azure Storage funcionando. Los certificados se almacenan en Azure y la aplicación corre en Render.

**URL de tu app:** `https://tu-app.onrender.com`

### Próximos Pasos:

1. Configurar dominio personalizado (opcional)
2. Configurar emails con SendGrid o similar
3. Añadir monitoreo con Sentry
4. Configurar backups automáticos de PostgreSQL
