# -*- coding: utf-8 -*-
"""NLPDatasetGenerator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DxY3NCiIJXO6gSc8d7xmx5oo6AtUoBbX
"""

#!cp /usr/lib/chromium-browser/chromedriver /usr/bin

import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver') #the path to chromedriver
from selenium import webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import json
import os
import errno
from multiprocessing import Pool
import wget
import ssl
import time
import urllib
from urllib.request import urlopen
from img2dataset import download
from tqdm import tqdm
import shutil

searched_categories = []

def get_image_caption_pair(args):
    global searched_categories
    page_url = args
    driver = webdriver.Chrome('chromedriver',options=chrome_options)
    driver.get(page_url)
    try:
      info = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "photo__info")))
    except:
      print(f"Couldn't get page with url: {page_url}. will add it to the unsuccessful page loads...")
      return page_url
    title = info.find_element(by=By.TAG_NAME, value="h1").text
    caption = info.find_element(by=By.TAG_NAME, value="p").text
    tags = driver.find_elements(by=By.CLASS_NAME, value="photo__meta")[1].find_elements(by=By.TAG_NAME, value="a")
    for tag in tags:
      if tag.text in searched_categories:
        return None
    image_holder = driver.find_element(by=By.CLASS_NAME, value="photo__centered-frame")
    image_url = image_holder.find_element(by=By.TAG_NAME, value = "img").get_attribute("src")
    main_url = re.search('[^\?]*', image_url).group()
    driver.quit()
    return {"title": title, "image_url": main_url, "caption": caption}

def save_to_json_file(new_data):
  with open(f'{dataset_path}/dataset.json', 'r', encoding='utf-8') as f:
    try: 
        data = json.load(f)
    except ValueError: 
         data = []
  with open(f'{dataset_path}/dataset.json', 'w', encoding='utf-8') as f:
    data = data + new_data
    json.dump(data, f, ensure_ascii=False, indent=4)

def unsuccessful_page_loads(url):
  with open(f"{dataset_path}/unsuccessful_page_loads.txt", "a") as f:
    f.write(url+"\n")

#the raw folder along with dataset.json in it must exist in order for this to work:
def download_images():
  global dataset_path

  if os.path.exists(f"{dataset_path}/images"):
    print(f"the folder {dataset_path}/images exists. removing it...")
    shutil.rmtree(f"{dataset_path}/images")

  try:
    os.mkdir(os.path.join(dataset_path, "images"))
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise

  with open(f'{dataset_path}/dataset.json', 'r', encoding='utf-8') as f:
    try: 
      data = json.load(f)
    except ValueError: 
      data = []
  with open("urls.txt", "w") as f:
    f.write("\n".join([d["image_url"] for d in data]))
  download(
          url_list="urls.txt",
          output_folder= dataset_path+"/images",
          resize_mode="keep_ratio",
          image_size=800,
          resize_only_if_bigger=True,
          retries = 2
        )

def handle_image_caption_pair(data, last_id):
  tmp = []
  for d in data:
    if d == None:
      continue
    elif isinstance(d, str):
      unsuccessful_page_loads(d)
    else:
      tmp.append({"id":last_id, "title": d["title"], "image_url": d["image_url"], "caption": d["caption"]})
      last_id += 1
  return tmp, last_id

def crawl_with_categories():
    global dataset_path
    global searched_categories
    driver = webdriver.Chrome('chromedriver',options=chrome_options)

    categories = ["Nature", "Seasons", "Travel", "City", "Food", "Pets", "Animal", "Product", "Business", "Education", 
                  "People", "Children", "Accessories", "Medical", "Transportation"]
    
    #create a "raw" folder in the folder specified by user
    path = os.path.join(dataset_path, "raw")
    dataset_path = path
    if os.path.exists(f"{dataset_path}/dataset.json"):
        print(f"the file {dataset_path}/dataset.json exists. removing it...")
        os.remove(f"{dataset_path}/dataset.json")
        
    try:
        os.mkdir(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    if os.path.exists(f"{dataset_path}/unsuccessful_page_loads.txt"):
        print(f"the file {dataset_path}/unsuccessful_page_loads.txt exists. removing it...")
        os.remove(f"{dataset_path}/unsuccessful_page_loads.txt")
    
    #creating dataset.json and unsuccessful_page_loads.txt files
    open(f"{dataset_path}/dataset.json",'w+').close()
    open(f"{dataset_path}/unsuccessful_page_loads.txt",'w+').close()

    pages_data = []
    searched_categories = []
    last_id = 0
    page_first = 1
    for category in categories:
      for page in range(page_first,200):
          print(f"Getting data from page {page} : https://burst.shopify.com/{category}?page={page}")
          driver.get(f"https://burst.shopify.com/{category}?page={page}")
          main = driver.find_element(by=By.ID, value="Main")
          grid = main.find_element(by=By.TAG_NAME, value="section").find_element(by=By.CLASS_NAME, value="js-masonry-grid")
          links = [element.get_attribute("href") for element in grid.find_elements(by =By.TAG_NAME, value="a")]
          minibatch_length = 10
          minibatch = int(len(links) / minibatch_length)
          for iter in tqdm(range(minibatch)):
              with Pool() as p:
                  data = p.map(get_image_caption_pair, links[iter*minibatch_length:iter*minibatch_length + minibatch_length])
              data, last_id = handle_image_caption_pair(data, last_id)
              pages_data= pages_data + data
          remainingdata = len(links)-minibatch*minibatch_length
          if remainingdata != 0:
              with Pool() as p:
                  data = p.map(get_image_caption_pair, links[minibatch*minibatch_length:])
              data, last_id = handle_image_caption_pair(data, last_id)
              pages_data= pages_data + data
          save_to_json_file(pages_data)
          pages_data = []
          pagination = main.find_element(by=By.CLASS_NAME, value="pagination")
          if len(pagination.find_elements(by=By.LINK_TEXT, value="Next ›")) == 0:
            break #this category's pages ended
      searched_categories.append(category)
      page_first = 1
    driver.quit()
    print("=============================================")
    print("json file is ready!")
    
    if image_format == "file":
        print("Beginning to save the images in"+ dataset_path + '/images.')
        download_images()

###The path where dataset folder is created on
dataset_path = ".."
#### change this to "file" if you want to download and save the images locally after dataset.json is made. 
# you can also call download_images() for this purpose.
image_format = "url"
crawl_with_categories()
