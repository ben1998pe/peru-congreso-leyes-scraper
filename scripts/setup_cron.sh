#!/bin/bash

echo "Configurando automatización con cron..."

# Obtener directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Crear script ejecutable
cat > "$SCRIPT_DIR/run_scraper.sh" << EOF
#!/bin/bash
cd "$PROJECT_DIR"
python scripts/auto_scraper.py
EOF

chmod +x "$SCRIPT_DIR/run_scraper.sh"

# Agregar tarea a crontab (ejecutar diariamente a las 6:00 AM)
(crontab -l 2>/dev/null; echo "0 6 * * * $SCRIPT_DIR/run_scraper.sh") | crontab -

echo "✅ Automatización configurada exitosamente!"
echo "📅 El scraper se ejecutará diariamente a las 6:00 AM"
echo "📁 Script ubicado en: $SCRIPT_DIR/run_scraper.sh"
echo "🔍 Para ver las tareas: crontab -l"
echo "🗑️ Para eliminar: crontab -e (y borrar la línea)"
