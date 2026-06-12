# removebgcli.py

Herramienta CLI para eliminar el fondo de imágenes usando rembg.

## Instalación

### Prerrequisitos
- Python 3.12 o superior
- UV (gestor de paquetes Python) instalado

### Configuración del entorno

1. **Crear el entorno virtual e instalar dependencias:**
```bash
# UV creará automáticamente el venv y sincronizará las dependencias
uv sync
```

2. **O si necesitas añadir las dependencias manualmente:**
```bash
# Inicializar el proyecto (si no existe pyproject.toml)
uv init

# Añadir las dependencias necesarias
uv add rembg pillow onnxruntime "numpy<2.0"
```

3. **Verificar la instalación:**
```bash
uv run removebgcli.py --help
```

### Dependencias del proyecto
- `rembg>=2.0.67` - Librería principal para eliminar fondos
- `pillow>=11.3.0` - Procesamiento de imágenes
- `onnxruntime>=1.23.0` - Runtime para modelos ONNX
- `numpy<2.0` - Cálculos numéricos (versión <2.0 para compatibilidad)

## Ejemplos de uso

### 1. Mostrar imágenes creadas hoy (debug)
```bash
today=$(date +%Y-%m-%d)
uv run removebgcli.py --find "-type f -newermt \"$today\"" --find-path /ruta/a/buscar --debug
```

### 2. Mostrar imágenes modificadas en los últimos 15 minutos (debug)
```bash
uv run removebgcli.py --find "-type f -mmin -15" --find-path /ruta/a/buscar --debug
```

### 3. Procesar imágenes creadas hoy y guardar en misma carpeta
```bash
today=$(date +%Y-%m-%d)
uv run removebgcli.py --find "-type f -newermt \"$today\"" --find-path /ruta/a/buscar -o /ruta/a/buscar
```

### 4. Procesar imágenes modificadas en últimos 19 minutos
```bash
uv run removebgcli.py --find "-type f -mmin -19" --find-path /ruta/a/buscar -o /ruta/a/buscar
```

### 5. Buscar imágenes en un rango de fechas
```bash
fecha_inicio="2024-12-01"
fecha_final="2024-01-27"

uv run removebgcli.py \
  --find "-type f -newermt \"$fecha_inicio\" ! -newermt \"$fecha_final\"" \
  --find-path /ruta/a/buscar \
  --debug
```

### Ejemplos específicos para Termux (carpeta Telegram)

**Buscar imágenes de los últimos 15 minutos:**
```bash
uv run removebgcli.py --find "-type f -mmin -15" --find-path /data/data/com.termux/files/home/storage/shared/Pictures/Telegram/ --debug
```

**Buscar imágenes creadas hoy:**
```bash
today=$(date +%Y-%m-%d)
uv run removebgcli.py --find "-type f -newermt \"$today\"" --find-path /data/data/com.termux/files/home/storage/shared/Pictures/Telegram/ --debug
```

**Procesar imágenes de los últimos 19 minutos:**
```bash
uv run removebgcli.py --find "-type f -mmin -19" --find-path /data/data/com.termux/files/home/storage/shared/Pictures/Telegram/ -o /data/data/com.termux/files/home/storage/shared/Pictures/Telegram/
```

## Modelos disponibles

El script soporta los siguientes modelos de rembg (usar con `-m` o `--model`):
- `u2net` (por defecto)
- `u2netp`
- `u2net_human_seg`
- `u2net_cloth_seg`
- `silueta`
- `isnet-general-use`
- `isnet-anime` (por defecto en el script)
- `sam`

**Ejemplo con modelo específico:**
```bash
uv run removebgcli.py --find "-type f -mmin -15" --find-path /ruta/a/buscar -o /ruta/salida -m u2net_human_seg
```

## Notas

- El modo `--debug` solo muestra los archivos encontrados sin procesarlos
- El flag `--delete` permite eliminar archivos (con confirmación)
- Las imágenes procesadas se guardan en formato PNG
- El script usa find de Unix, por lo que soporta todas sus opciones de búsqueda
- En la primera ejecución, rembg descargará el modelo seleccionado (puede tardar unos minutos)
