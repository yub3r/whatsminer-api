import requests
import hashlib
import urllib3

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_token(ip, admin_password):
    response = requests.post(
        f'https://{ip}/api',
        json={"cmd": "get_token"},
        verify=False
    )
    
    if response.status_code != 200:
        raise Exception("Error al obtener los datos del dispositivo.")
    
    data = response.json()
    time = data['time']
    salt = data['salt']
    newsalt = data['newsalt']
    
    key = hashlib.md5((salt + admin_password).encode()).hexdigest()
    time_suffix = time[-4:]
    sign = hashlib.md5((newsalt + key + time_suffix).encode()).hexdigest()
    
    return sign

def power_off(ip, token, respbefore):
    response = requests.post(
        f'https://{ip}/api',
        json={
            "token": token,
            "cmd": "power_off",
            "respbefore": "true" if respbefore else "false"
        },
        verify=False
    )
    
    if response.status_code == 200:
        print("Hashboard apagado correctamente.")
    else:
        print("Error al apagar el hashboard:", response.text)

def power_on(ip, token):
    response = requests.post(
        f'https://{ip}/api',
        json={
            "token": token,
            "cmd": "power_on"
        },
        verify=False
    )
    
    if response.status_code == 200:
        print("Hashboard encendido correctamente.")
    else:
        print("Error al encender el hashboard:", response.text)

# Example usage
ip = "10.45.98.155"
admin_password = "btf.1234"

try:
    token = get_token(ip, admin_password)
    power_off(ip, token, respbefore=True)  # Set to False if you want to close first
    power_on(ip, token)
except Exception as e:
    print("Error:", e)