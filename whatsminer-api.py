import os
import sys
from whatsminer import WhatsminerAccessToken, WhatsminerAPI
from concurrent.futures import ThreadPoolExecutor
import json

# Cargar la lista de IPs desde el archivo 'asics_list.txt'
def cargar_lista_ips(archivo):
    with open(archivo, 'r') as f:
        ips = f.read().splitlines()  # Cargar cada línea como una IP
    return ips

# Función para enviar el comando a los mineros
def enviar_comando(ip, cmd, admin_password="btf.1234"):
    # Crear el token de acceso con la IP y la contraseña de administrador
    token = WhatsminerAccessToken(ip_address=ip, admin_password=admin_password)
    
    # Enviar el comando sin esperar respuesta
    if cmd == 'summary':
        # Obtener el resumen y mostrarlo
        summary_json = WhatsminerAPI.get_read_only_info(access_token=token, cmd=cmd)
        formatted_summary = json.dumps(summary_json, indent=4)
        print(f"Estado del minero con IP {ip}:")
        print(formatted_summary)
    else:
        # Para power_on o power_off no esperamos la respuesta
        WhatsminerAPI.exec_command(access_token=token, cmd=cmd, additional_params={"respbefore": "true"})
        print(f"Comando '{cmd}' enviado al minero con IP {ip}.")

        # Cerrar conexión inmediatamente después
        sys.stdout.flush()  # Forzar salida de cualquier texto pendiente
        # os._exit(0)  # Forzar salida del programa

# Función principal
def main():
    # Cargar la lista de IPs
    ips = cargar_lista_ips('asics_list.txt')

    # Mostrar opciones de comando
    print("Seleccione una opción:")
    print("1 - Iniciar el minado (power_on)")
    print("2 - Suspender el minado (power_off)")
    print("3 - Obtener el estado (summary)")

    # Obtener la selección del usuario
    while True:
        opcion = input("Ingrese el número de la opción deseada: ").strip()
        if opcion == '1':
            comando = 'power_on'
            break
        elif opcion == '2':
            comando = 'power_off'
            break
        elif opcion == '3':
            comando = 'summary'
            break
        else:
            print("Opción no válida. Por favor, elija 1, 2 o 3.")

    # Enviar el comando a cada IP en paralelo sin esperar respuesta
    with ThreadPoolExecutor() as executor:
        executor.map(lambda ip: enviar_comando(ip, comando), ips)

if __name__ == "__main__":
    main()
