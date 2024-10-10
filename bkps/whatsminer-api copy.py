from whatsminer import WhatsminerAccessToken, WhatsminerAPI
import json

# token = WhatsminerAccessToken(ip_address="10.45.98.155")
# summary_json = WhatsminerAPI.get_read_only_info(access_token=token, cmd="summary")

# Formatear el JSON
# formatted_summary = json.dumps(summary_json)

# print(formatted_summary)

while True:
    ip_address = input("Ingrese la dirección IP del minero: ")
    admin_password = "btf.1234"  # Contraseña de administrador fija

    # Crear el token de acceso con la IP y la contraseña de administrador
    token = WhatsminerAccessToken(ip_address=ip_address, admin_password=admin_password)

    # Ejecutar el comando "power_off" sin esperar respuesta
    try:
        WhatsminerAPI.exec_command(access_token=token, cmd="power_on", additional_params={"respbefore": "true"})
        print(f"Se ha enviado el comando 'power_on' al minero con IP {ip_address}.")
    except Exception as e:
        print(f"Error al enviar el comando: {e}")

    # Obtener y mostrar el resumen (opcional)
    try:
        summary_json = WhatsminerAPI.get_read_only_info(access_token=token, cmd="summary")
        formatted_summary = json.dumps(summary_json, indent=4)
        print("Resumen del minero:")
        print(formatted_summary)
    except Exception as e:
        print(f"Error al obtener el resumen del minero: {e}")

    # Preguntar al usuario si desea ingresar otra dirección IP
    another_ip = input("¿Desea ingresar otra dirección IP? (s/n): ")
    if another_ip.lower() != 's':
        break

