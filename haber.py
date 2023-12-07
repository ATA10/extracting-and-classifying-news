import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

# ChromeDriver'ın bulunduğu dosyanın yolu
chrome_path = 'path/to/chromedriver.exe'

# Headless modda çalışacak tarayıcı seçenekleri
chrome_options = Options()
chrome_options.add_argument('--headless')

# WebDriver'ı başlat
browser = webdriver.Chrome(options=chrome_options)

# İlk sayfanın içeriğini çek ve BeautifulSoup kullanarak parse et
url = requests.get("https://www.ensonhaber.com/mansetler.htm")
soup = BeautifulSoup(url.content, 'html.parser')

# Haberlerin başlık ve içerik linklerini tutmak için CSV dosyasını yazmak için aç 
with open('haberler.csv', 'w', newline='', encoding='utf-8') as file:
    # CSV dosyasına yazmak için writer objesi oluştur
    writer = csv.writer(file)
    
    # CSV dosyasının başlıklarını yaz
    writer.writerow(['Başlık', 'Link'])

    # Sonsuz bir döngü başlat
    while True:
        # 1'den 9'a kadar olan sayılar için bir döngü başlat
        for i in range(1, 10):
            # "manset left" sınıfına sahip div'leri bul
            linkler = soup.find_all("div", {"class": "manset left"})

            # Her bir div içindeki bağlantıları çek
            for link in linkler:
                a_tags = link.find_all("a")

                # Her bir bağlantıdaki başlığı ve linki çek
                for a_tag in a_tags:
                    span_tag = a_tag.find("span")
                    if span_tag:
                        title_text = span_tag.text.strip()
                        link = "https://www.ensonhaber.com" + a_tag["href"]

                        # Başlık ve linki CSV dosyasına yaz
                        writer.writerow([title_text, link])

            # Sayfalama için gerekli elementleri bul
            pagination = soup.find("div", {'class': 'pagination'})
            next_page_link = pagination.find('a', {'class': 'prev'})

            # Bir sonraki sayfa linki varsa, yeni sayfayı çek
            if next_page_link:
                link = "https://www.ensonhaber.com" + next_page_link['href']
                url = requests.get(link)
                soup = BeautifulSoup(url.content, 'html.parser')       
                print(i)  # Hangi sayfada olduğumuzu göstermek için sayfa numarasını yazdır
            else:
                break  # Sayfalama sona erdiğinde döngüyü kır

        # Eğer iç döngü 9'a ulaşırsa, dış döngüyü kır
        if i == 9:
            break

# Haberlerin linklerini öğrenmek için CSV dosyasını oku
df = pd.read_csv('haberler.csv')
#istenilen sutünu ata ve yazdır
hlink = df['Link']
print(hlink)

# haber linklerini açmak ve haber içeriklerini CSV dosyasına yazma işlemi
with open('haberler1.csv', 'w', newline='', encoding='utf-8') as file1:
    writer1 = csv.writer(file1)
    writer1.writerow(['Başlık', 'İçerik', 'Yorumlar'])

    for haber in hlink:
        haberler = requests.get(haber)
        haberler.raise_for_status()  # HTTP hata durumlarını kontrol et
        soup1 = BeautifulSoup(haberler.content, 'html.parser')  #sayfayı html olarak taramak
        haberbaslik = soup1.find("div", {"class": "article-title"})  #haberbaşlığının bulunduğu html etiketini taramak
        if haberbaslik:
            b = haberbaslik.find('h1') #başlık etiketi
            b1 = b.text.strip() #başlık içeriğini texte çevirmek
        else:
            b1 = "" 
        habericerik = soup1.find("div", {"class": "article-body"})
        if habericerik:
            paragraphs = habericerik.find_all('p')
            c1 = ' '.join(paragraph.text.strip() for paragraph in paragraphs)
        else:
            c1 = ""
        e1 =''
        browser.get(haber)
        total_height = browser.execute_script("return document.body.scrollHeight")
        for i in range(total_height // 50):
            browser.execute_script("window.scrollTo(0, arguments[0]);", 50 * i)

        time.sleep(2)
        haberyorum = browser.find_element(By.CSS_SELECTOR, '#yorum > div:nth-child(3) > div > div.comments-list')
        if haberyorum:
            # Find all p elements within the comments list
            paragraphs1 = haberyorum.find_elements(By.TAG_NAME, 'p')    
            # Process each found element
            for paragraph1 in paragraphs1:
                if(paragraph1.text):
                    e1 += '/'+ paragraph1.text
                else:
                    continue
        else:
            print("Comments list not found on the page.")     
        writer1.writerow([b1, c1, e1])
        while True:
            break
browser.quit()
df1 = pd.read_csv('haberler1.csv')
hlink1 = df1['Yorumlar']
# print(hlink1)
#yorumdları tutacağımız dizi
new_lines = []
# yorum sütununu / karakterine göre ayrırıyoruz
for element in hlink1:
    parts = element.split("/")
    new_lines.extend(parts)
# listesindeki öğeleri birleştirerek tek bir dize oluşturur. Her bir yorum arasına yeni bir satır eklemek için "\n" kullanılır.
result = "\n".join(new_lines)

print(result)
