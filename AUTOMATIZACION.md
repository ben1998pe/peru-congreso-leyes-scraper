# 🤖 Guía de Automatización del Scraper

Esta guía te muestra cómo automatizar el scraper para que se ejecute diariamente y suba los cambios automáticamente.

## 🚀 Opciones de Automatización Gratuitas

### 1. **GitHub Actions (Recomendado) ⭐**

**Ventajas:**
- ✅ Completamente gratuito
- ✅ No requiere mantener tu computadora encendida
- ✅ Ejecuta en la nube de GitHub
- ✅ Historial de ejecuciones
- ✅ Notificaciones por email

**Configuración:**
1. El archivo `.github/workflows/daily-scraper.yml` ya está configurado
2. Simplemente haz push de los cambios
3. GitHub ejecutará el scraper diariamente a las 6:00 AM UTC

**Para activar:**
```bash
git add .github/workflows/daily-scraper.yml
git commit -m "feat: Agregar automatización con GitHub Actions"
git push
```

### 2. **Automatización Local (Windows)**

**Ventajas:**
- ✅ Control total sobre la ejecución
- ✅ Puedes personalizar horarios
- ✅ Acceso directo a los datos

**Configuración:**
```bash
# Instalar dependencias de automatización
pip install schedule

# Ejecutar el script de configuración
scripts/configurar_automatizacion.bat
```

**Para ejecutar manualmente:**
```bash
python scripts/auto_scraper.py
```

### 3. **Automatización Local (Linux/Mac)**

**Ventajas:**
- ✅ Muy confiable
- ✅ Usa el sistema cron nativo
- ✅ Bajo consumo de recursos

**Configuración:**
```bash
# Dar permisos de ejecución
chmod +x scripts/setup_cron.sh

# Ejecutar configuración
./scripts/setup_cron.sh
```

## 📊 **Comparación de Opciones**

| Característica | GitHub Actions | Windows Task Scheduler | Linux Cron |
|----------------|----------------|------------------------|------------|
| **Costo** | Gratis | Gratis | Gratis |
| **Computadora encendida** | No | Sí | Sí |
| **Configuración** | Fácil | Media | Media |
| **Confiabilidad** | Alta | Media | Alta |
| **Notificaciones** | Sí | No | No |
| **Historial** | Sí | No | No |

## 🔧 **Configuración Detallada**

### GitHub Actions

El workflow está configurado para:
- **Horario:** Todos los días a las 6:00 AM UTC (1:00 AM hora de Perú)
- **Datos:** Últimos 7 días de proyectos
- **Commit automático:** Si hay datos nuevos
- **Notificaciones:** Resumen en la pestaña Actions

### Script Local

El script `auto_scraper.py` incluye:
- **Scraping automático** de últimos 7 días
- **Limpieza de datos** automática
- **Commit y push** automático
- **Logging detallado** de todas las operaciones
- **Manejo de errores** robusto

## 📈 **Monitoreo y Logs**

### GitHub Actions
- Ve a la pestaña "Actions" en tu repositorio
- Cada ejecución muestra logs detallados
- Recibe notificaciones por email si falla

### Script Local
- Los logs se guardan en `logs/scraper_YYYYMMDD.log`
- El script muestra progreso en tiempo real
- Errores se registran automáticamente

## 🛠️ **Personalización**

### Cambiar Horario de Ejecución

**GitHub Actions:**
```yaml
# En .github/workflows/daily-scraper.yml
- cron: '0 6 * * *'  # Cambiar por tu horario deseado
```

**Script Local:**
```python
# En scripts/auto_scraper.py
schedule.every().day.at("06:00").do(tarea_diaria)  # Cambiar hora
```

### Cambiar Rango de Fechas

```python
# En scripts/auto_scraper.py
fecha_desde = fecha_hasta - timedelta(days=7)  # Cambiar número de días
```

### Agregar Notificaciones

```python
# Agregar al final de tarea_diaria()
import smtplib
from email.mime.text import MIMEText

def enviar_notificacion(mensaje):
    # Configurar email aquí
    pass
```

## 🚨 **Solución de Problemas**

### GitHub Actions Falla
1. Verifica que el repositorio tenga permisos de escritura
2. Revisa los logs en la pestaña Actions
3. Asegúrate de que el archivo `.github/workflows/daily-scraper.yml` esté en la rama main

### Script Local No Ejecuta
1. Verifica que Python esté en el PATH
2. Instala las dependencias: `pip install -r requirements.txt`
3. Revisa los logs en `logs/`

### ChromeDriver Issues
1. El script usa `webdriver-manager` que descarga automáticamente la versión correcta
2. Si falla, actualiza Chrome a la última versión

## 📋 **Checklist de Configuración**

- [ ] Repositorio configurado con GitHub Actions
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Script de automatización probado manualmente
- [ ] Configuración de horario verificada
- [ ] Logs funcionando correctamente
- [ ] Commit automático funcionando

## 🎯 **Recomendación Final**

**Para la mayoría de usuarios:** Usa **GitHub Actions** porque:
- No requiere mantener tu computadora encendida
- Es completamente gratuito
- Tiene mejor monitoreo y logs
- Es más confiable

**Para usuarios avanzados:** Usa **automatización local** si necesitas:
- Control total sobre la ejecución
- Personalizaciones muy específicas
- Acceso directo a los datos antes del commit

---

¿Necesitas ayuda con alguna configuración específica? ¡No dudes en preguntar! 🚀
