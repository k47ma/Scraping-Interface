from bs4 import BeautifulSoup
import re


def swap(img1, img2):
    temp = img1['src']
    img1['src'] = img2['src']
    img2['src'] = temp

file = open("C:\Users\kma01\Downloads\images.txt", 'r')
text = file.read()
file.close()

soup = BeautifulSoup(text, "html.parser")

images = soup.find_all('img')

ind = 517922
for image in images:
    if not image.get('alt'):
        image['alt'] = image['src'].split('/')[-1]
    image['src'] = "/common/pages/UserFile.aspx?fileId=" + str(ind)
    ind += 2

soup = re.sub('imagesiteid=".*?" objectid=".*?" ', "", str(soup))

print soup
