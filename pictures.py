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

ind = 503626
for image in images:
    if not image.get('alt'):
        image['alt'] = image['src'].split('/')[-1]
    image['src'] = "/common/pages/UserFile.aspx?fileId=" + str(ind)
    ind += 2
    if ind == 503381 or ind == 503395 or ind == 503409:
        ind += 2
    if ind == 503395:
        ind += 4
    if ind == 503399 or ind == 503402:
        ind += 1
    if ind == 503413:
        ind += 3

soup = re.sub('imagesiteid=".*?" objectid=".*?" ', "", str(soup))

print soup
