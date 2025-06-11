# Ejemplos de uso - removebgcli.py

### 1. Mostrar imágenes creadas hoy (debug)
```bash
today=$(date +%Y-%m-%d)
python3 removebgcli.py --find "-type f -newermt \"$today\"" --find-path /ruta/a/buscar --debug
```

### 2. Mostrar imágenes modificadas en los últimos 15 minutos (debug)
```bash
python3 removebgcli.py --find "-type f -mmin -15" --find-path /ruta/a/buscar --debug
```

### 3. Procesar imágenes creadas hoy y guardar en misma carpeta
```bash
today=$(date +%Y-%m-%d)
python3 removebgcli.py --find "-type f -newermt \"$today\"" --find-path /ruta/a/buscar -o /ruta/a/buscar
```

### 4. Procesar imágenes modificadas en últimos 19 minutos
```bash
python3 removebgcli.py --find "-type f -mmin -19" --find-path /ruta/a/buscar -o /ruta/a/buscar
```
### 5.  

```bash
fecha_inicio="2024-12-01"
fecha_final="2024-01-27"

uv run removebgcli.py \
  --find "-type f -newermt \"$fecha_inicio\" ! -newermt \"$fecha_final\"" \
  --find-path /ruta/a/buscar \
  --debug
```

### Ejemplo específico para Termux y carpeta Telegram:
```bash
python3 removebgcli.py --find "-type f -mmin -15" --find-path /data/data/com.termux/files/home/storage/shared/Pictures/Telegram/ --debug
```

```bash
today=$(date +%Y-%m-%d)
python3 removebgcli.py --find "-type f -newermt \"$today\"" --find-path /data/data/com.termux/files/home/storage/shared/Pictures/Telegram/ --debug
```

```bash
python3 removebgcli.py --find "-type f -mmin -19" --find-path /data/data/com.termux/files/home/storage/shared/Pictures/Telegram/ -o /data/data/com.termux/files/home/storage/shared/Pictures/Telegram/
```
