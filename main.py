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
from jinja2 import Environment, BaseLoader

indexhtml = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ezShare</title>
</head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@500&display=swap" rel="stylesheet">
<body style="height: 100vh; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; background-color: #ebdbbc; justify-content: center; font-family: 'Inter', sans-serif;">
    <h1>ezShare</h1>
    <p>Your files are avaliable at <a href= {{ filesUrl }}> {{ filesUrl }} </a> </p>
    <img src={{qr}} >
    <p>Thank you for using ezShare!</p>
</body>
</html>
"""


fileshtml = """
<!DOCTYPE html>
<html lang="en">
<head>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@500&display=swap" rel="stylesheet">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Files View</title>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        .file-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background-color: #ebdbbc;
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
        }

        .file-details {
            display: flex;
            flex-direction: column;
        }

        .file-name {
            margin-bottom: 5px;
            font-weight: bold;
        }

        .file-size {
            font-size: 0.8em;
            color: #555;
        }
        .download-button {
            background-color: #1a1a1a;
            color: #fff;
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
        }
    </style>
</head>
<body>
    {% for file in files %}
    <div class="file-bar">
        

        <div class="file-details">
            <span class="file-name">{{file['name']}}</span>
            <span class="file-name">{{file['size']}}</span>


        </div>
        <a href="{{file['url']}}" class="download-button">Download</a>
    </div>
    
    {% endfor %}
</body>
</html>
"""



DEBUG = False


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
#templates = Jinja2Templates(directory="templates")


def getFiles():
    files = []
    for file in os.listdir():
        if os.path.isfile(file):
            files.append({"name": file, "size": f"{os.path.getsize(file) / 1000000} MB", "url": f'http://{get_local_ip()}:1337/download/{file}'})

    return files


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    template = Environment(loader=BaseLoader()).from_string(indexhtml)
    data = template.render({"request": request, "filesUrl": f'http://{get_local_ip()}:1337/files', "qr": f'data:image/png;base64,{gererateBase64QRCode(f"http://{get_local_ip()}:1337/files")}'})


    #return templates.TemplateResponse("index.html", {"request": request, "filesUrl": f'http://{get_local_ip()}:1337/files', "qr": f'data:image/png;base64,{gererateBase64QRCode(f"http://{get_local_ip()}:1337/files")}'})
    return HTMLResponse(content=data, status_code=200)


@app.get("/files", response_class=HTMLResponse)
async def files(request: Request):
    template = Environment(loader=BaseLoader()).from_string(fileshtml)
    data = template.render({"request": request, "files": getFiles()})
    
    #return templates.TemplateResponse("files.html", {"request": request, "files": getFiles()})
    return HTMLResponse(content=data, status_code=200)


@app.get("/download/{file}", response_class=FileResponse)
async def download(file: str):
    return FileResponse(file)


if __name__ == "__main__":
    
    if not DEBUG:
        webbrowser.open_new_tab(f'http://{get_local_ip()}:1337')
    uvicorn.run(app, host="0.0.0.0", port=1337)
