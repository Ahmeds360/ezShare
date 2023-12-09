import base64
from io import BytesIO
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import socket
import webbrowser
import qrcode
import os
import colorama
from colorama import Fore, Back, Style
colorama.init()

DEBUG = True


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def gererateBase64QRCode(text: str):
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white',)
    buffered = BytesIO()
    img.save(buffered)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def printQRCode(text: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=3)
    qr.add_data(text)
    qr.print_ascii()

    

print(Fore.CYAN + "")
print(Fore.YELLOW + "" + Style.RESET_ALL)
print(Fore.BLUE + "            _____ _                    ")
print(Fore.BLUE + "           / ____| |                   ")
print(Fore.BLUE + "   ___ ___| (___ | |__   __ _ _ __ ___ ")
print(Fore.BLUE + "  / _ \_  /\___ \| '_ \ / _` | '__/ _ \ ")
print(Fore.BLUE + " |  __// / ____) | | | | (_| | | |  __/")
print(Fore.BLUE + "  \___/___|_____/|_| |_|\__,_|_|  \___|")
print(Fore.BLUE + "")
print(Fore.BLUE + "")

print(Fore.BLUE + f"Files available at http://{get_local_ip()}:1337/files")
print(Fore.BLUE + "")
printQRCode(f"http://{get_local_ip()}:1337/files")
print(Fore.RED + "" + Style.RESET_ALL)


app = FastAPI()
templates = Jinja2Templates(directory="templates")


def getFiles():
    files = []
    for file in os.listdir():
        if os.path.isfile(file):
            files.append({"name": file, "size": f"{os.path.getsize(file) / 1000000} MB", "url": f'http://{get_local_ip()}:1337/download/{file}'})

    return files


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):


    return templates.TemplateResponse("index.html", {"request": request, "filesUrl": f'http://{get_local_ip()}:1337/files', "qr": f'data:image/png;base64,{gererateBase64QRCode(f"http://{get_local_ip()}:1337/files")}'})


@app.get("/files", response_class=HTMLResponse)
async def files(request: Request):
    return templates.TemplateResponse("files.html", {"request": request, "files": getFiles()})


@app.get("/download/{file}", response_class=FileResponse)
async def download(file: str):
    return FileResponse(file)


if __name__ == "__main__":
    
    if not DEBUG:
        webbrowser.open_new_tab(f'http://{get_local_ip()}:1337')
    uvicorn.run(app, host="0.0.0.0", port=1337)
