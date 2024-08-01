import requests

url = "https://img2txt.p.rapidapi.com/img2txt"

querystring = {"encode":"true","text":"mono"}

payload = "-----011000010111000001101001--\r\n\r\n"
headers = {
	"x-rapidapi-key": "919c7ea1efmshd90b30b3ec115d8p1a3950jsnff93f38123f0",
	"x-rapidapi-host": "img2txt.p.rapidapi.com",
	"Content-Type": "multipart/form-data; boundary=---011000010111000001101001"
}

response = requests.post(url, data=payload, headers=headers, params=querystring)

print(response.json())