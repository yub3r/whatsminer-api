import hashlib
import json
import socket

def send_command(ip, port, command):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    sock.connect(server_address)
    
    try:
        # Enviar el comando como JSON
        message = json.dumps(command) + '\n'
        sock.sendall(message.encode('utf-8'))
        
        # Recibir la respuesta
        response = sock.recv(4096)
        formatted_response = json.dumps(json.loads(response.decode('utf-8')), indent=4)
        print('Respuesta del servidor:', formatted_response)
        return json.loads(response.decode('utf-8'))
    
    except json.JSONDecodeError as e:
        print(f"Error al decodificar la respuesta JSON: {e}")
        return None
    
    finally:
        sock.close()

def get_token(ip, password):
    command = {"cmd": "get_token"}
    response = send_command(ip, 4028, command)
    
    if response and response.get("STATUS") == "S":
        msg = response.get("Msg", {})
        time_salt = msg.get("time")
        salt = msg.get("salt")
        new_salt = msg.get("newsalt")
        
        if time_salt and salt and new_salt:
            key = hashlib.md5((salt + password).encode('utf-8')).hexdigest()
            timesec = time_salt[-4:]  # Últimos 4 caracteres del tiempo
            sign = hashlib.md5((new_salt + key + timesec).encode('utf-8')).hexdigest()
            return key, sign, time_salt
    
    print("Error al obtener el token")
    return None

def get_miner_status(ip, key, sign, time_salt):
    command = {
        "token": f"{time_salt},{sign}",
        "cmd": "summary"  # Comando para obtener el estado del minero
    }
    response = send_command(ip, 4028, command)
    
    if response and response.get("STATUS")[0].get("STATUS") == "S":
        return response.get("SUMMARY", [])[0]
    
    print("Error al obtener el estado del minero")
    return None

def suspend_mining(ip, key, sign, time_salt):
    command = {
        "cmd": "power_off",  # Comando para suspender la minería
        "token": f"{time_salt},{sign}",
        "respbefore": "false"
    }
    response = send_command(ip, 4028, command)
    
    if response and response.get("STATUS") == "S":
        return response.get("Msg", {})
    
    print("Error al suspender la minería")
    return None

def power_on_mining(ip, key, sign, time_salt):
    # Verificar el estado del minero antes de intentar encenderlo
    status = get_miner_status(ip, key, sign, time_salt)
    
    if status:
        # Verificar si el minero ya está encendido (Power Mode "Normal")
        if status.get("Power Mode") == "Normal" and status.get("MHS av") > 0:
            print("El minero ya está encendido y minando.")
            return
        elif status.get("Power Mode") == "Normal" and status.get("MHS av") == 0:
            print("El minero está encendido pero no está minando activamente.")
            return

    # Si no está encendido o está en modo de bajo consumo, proceder con el comando power_on
    command = {
        "token": f"{time_salt},{sign}",
        "cmd": "power_on",  # Comando para encender la minería
    }
    response = send_command(ip, 4028, command)
    
    if response and response.get("STATUS") == "S":
        return response.get("Msg", {})
    
    print("Error al encender la minería")
    return None

def restart_btminer(ip, key, sign, time_salt):
    command = {
        "token": f"{time_salt},{sign}",
        "cmd": "restart_btminer"  # Comando para reiniciar el minero
    }
    response = send_command(ip, 4028, command)
    
    if response and response.get("STATUS") == "S":
        return response.get("Msg", {})
    
    print("Error al reiniciar el minero")
    return None

if __name__ == "__main__":
    ip = input("Ingrese la IP del minero: ")
    password = 'btf.1234'  # Nueva contraseña
    
    try:
        key, sign, time_salt = get_token(ip, password)
        if key and sign and time_salt:
            print(f"Key: {key}, Sign: {sign}, Time Salt: {time_salt}")
            
            # Preguntar al usuario qué acción realizar
            action = input("¿Desea suspender (1), encender (2) la minería, ver el estado (3) o reiniciar el minero (4)? Ingrese 1, 2, 3 o 4: ")

            if action == '1':
                response = suspend_mining(ip, key, sign, time_salt)
                if response:
                    print("Respuesta del comando de suspensión:", response)
            elif action == '2':
                response = power_on_mining(ip, key, sign, time_salt)
                if response:
                    print("Respuesta del comando de encendido:", response)
            elif action == '3':
                status = get_miner_status(ip, key, sign, time_salt)
                if status:
                    print("Estado del minero:")
                    for key, value in status.items():
                        print(f"{key}: {value}")
                else:
                    print("Error al obtener el estado del minero")
            elif action == '4':
                response = restart_btminer(ip, key, sign, time_salt)
                if response:
                    print("Respuesta del comando de reinicio:", response)
            else:
                print("Opción no válida. Por favor, ingrese 1, 2, 3 o 4.")
        else:
            print("No se pudo obtener el token.")
    except TypeError:
        print("Error: No se pudo obtener el token.")