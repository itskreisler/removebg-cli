import shlex
import argparse
import glob
import os
import subprocess
from rembg import remove, new_session
from PIL import Image
from onnxruntime import SessionOptions

modelos = [
    'u2net', 'u2netp', 'u2net_human_seg', 'u2net_cloth_seg',
    'silueta', 'isnet-general-use', 'isnet-anime', 'sam'
]

def remove_bg(input_path, output_path, session):
    with Image.open(input_path) as input_image:
        output_image = remove(input_image, session=session)
        output_image.save(output_path, format='PNG')

def expand_input_patterns(patterns):
    files = []
    for pattern in patterns:
        matched = glob.glob(pattern, recursive=True)
        files.extend(matched)
    return files

def find_files_with_command(find_path, find_args):
    command = ["find", find_path] + shlex.split(find_args)
    print(f"[INFO] Ejecutando: {' '.join(command)}")
    try:
        files = subprocess.check_output(command).decode().splitlines()
        return files
    except subprocess.CalledProcessError as e:
        print("[ERROR] Falló el comando 'find':", e)
        return []

def main():
    parser = argparse.ArgumentParser(description="Elimina el fondo de imágenes.")

    parser.add_argument("-i", "--input", nargs="+", help="Archivos o patrones (e.g., '*.jpg')")
    parser.add_argument("--find", help="Argumentos para usar con 'find'")
    parser.add_argument("--find-path", default=".", help="Ruta raíz para buscar con 'find'")
    parser.add_argument("-o", "--output", required=False, help="Archivo o directorio de salida")
    parser.add_argument("-m", "--model", default="isnet-anime", help="Modelo a utilizar (por defecto: isnet-anime)")
    parser.add_argument("--debug", action="store_true", help="Imprime los archivos y no procesa nada")
    parser.add_argument("--delete", action="store_true", help="Eliminar los archivos encontrados en vez de procesarlos")

    args = parser.parse_args()

    if args.model not in modelos:
        print(f"[ERROR] Modelo no soportado. Modelos disponibles: {modelos}")
        exit(1)

    input_files = []
    if args.find:
        input_files = find_files_with_command(args.find_path, args.find)
    elif args.input:
        input_files = expand_input_patterns(args.input)
    else:
        print("[ERROR] Debes proporcionar -i o --find para buscar imágenes.")
        exit(1)

    if not input_files:
        print("[WARN] No se encontraron archivos que coincidan.")
        exit(0)

    if args.delete:
        print(f"[INFO] Se encontraron {len(input_files)} archivo(s) para eliminar.")
        for f in input_files:
            print(" -", f)
        confirm = input("[CONFIRMAR] ¿Deseas borrar estos archivos? (s/n): ")
        if confirm.lower() == "s":
            for f in input_files:
                try:
                    os.remove(f)
                    print(f"[BORRADO] {f}")
                except Exception as e:
                    print(f"[ERROR] No se pudo borrar {f}: {e}")
            print("[INFO] Archivos eliminados.")
        else:
            print("[INFO] Operación cancelada por el usuario.")
        return

    print(f"[INFO] Se encontraron {len(input_files)} archivo(s).")

    if args.debug:
        print("[DEBUG] Archivos encontrados:")
        for f in input_files:
            print(" -", f)
        print("[DEBUG] Modo depuración activado. Saliendo sin procesar imágenes.")
        return

    if not args.output:
        print("[ERROR] Debes especificar la salida con -o.")
        exit(1)

    options = SessionOptions()
    options.intra_op_num_threads = 1
    session = new_session(model_name=args.model, session_options=options)

    if len(input_files) == 1:
        input_file = input_files[0]
        output_path = args.output
        if os.path.isdir(output_path):
            filename = os.path.splitext(os.path.basename(input_file))[0] + '.png'
            output_path = os.path.join(output_path, filename)
        else:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            remove_bg(input_file, output_path, session)
            print(f"[OK] Procesado: {input_file} -> {output_path}")
        except Exception as e:
            print(f"[ERROR] Falló con {input_file}: {e}")
    else:
        output_dir = args.output
        os.makedirs(output_dir, exist_ok=True)
        for input_file in input_files:
            filename = os.path.splitext(os.path.basename(input_file))[0] + '.png'
            output_file = os.path.join(output_dir, filename)
            try:
                remove_bg(input_file, output_file, session)
                print(f"[OK] Procesado: {input_file} -> {output_file}")
            except Exception as e:
                print(f"[ERROR] Falló con {input_file}: {e}")

if __name__ == "__main__":
    main()
