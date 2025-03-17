import requests
import chardet
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}
url = 'https://bangumi.tv/subject/840'
response = requests.get(url, headers=headers)
detected_encoding = chardet.detect(response.content)['encoding']
print(detected_encoding)
response.encoding = detected_encoding

content = response.text
print(content)