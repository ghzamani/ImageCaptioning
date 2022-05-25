# Image-Captioning Dataset
An image-captioning dataset gathered by crawling https://burst.shopify.com/ and cleaned into several forms. This dataset contains 12602 image with their captions. 
The code for generating and cleaning the dataset each exist in a python file and a jupiter notebook which can run on [Google Colab](http://colab.research.google.com/).

### Dataset format and structure
the raw and processed datasets are each stored in a json file inside their respective folders. These files contain a list of dictionaries. As an example the data with id 1 is stored in a dictionary like this:
```json
{
        "id": 1,
        "title": "Cave Of Wonder And Lights Photo",
        "image_url": "https://burst.shopifycdn.com/photos/cave-of-wonder-and-lights.jpg",
        "caption": "A man stands on a rock pillar in the middle of an underground cave, a large ray of light casts down on him from an opening in the earth above."
    }
```
In case the images are locally saved, they will be stored in two folders: 00000 and 00001. The images' filenames are their ids. The images take up about 3GB of space.

### Requirements:
In case you use the notebook, running the cells will install the required packages. For running the python file install them using this command:

    $ python3 -m pip install -r requirements.txt 

### Usage:
Before running NLPDatasetGenerator, open the code and set the dataset_path to the path you want the raw folder to be created in. You can also change the image_format variable to "file" if you want to download the images locally after dataset.json is made:
```python
###The path where dataset folder is created on
dataset_path = ".."
#### change this to "file" if you want to download and save the images locally after dataset.json is made. 
# you can also call download_images() for this purpose.
image_format = "url"
```
Before running NLPDataCleaning ...
Then run the scripts without any arguments:

    $ python3 src/nlpdatasetgenerator.py
    $ python3 src/nlpdatacleaning.py
