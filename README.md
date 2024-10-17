# Qpanalyzer

### Pre-Requisites

- Make sure you have this DLL named `VC_Redist` installed in your system or else download and install it from below link:
    
  [VC_Redist DLL Download Link](https://aka.ms/vs/16/release/vc_redist.x64.exe)

- Install the requirements from the `requirements.txt` file using the below command:
  ``` commandline
  python -m pip install -r requirements.txt
  ```
- After installing the requirements run the below command as well
  ```commandline
  python -m spacy download en_core_web_md
  ```  


### Model Downloader

First Need to Download Word to Vector Models.

``` python
import gensim.downloader as api

word_vect = api.load('word2vec-google-news-300')
word_vect.save("word2vec-google-news-300.model") #Saves the model
```

> this snippet will download and saves the word vector models. there will be 2 files `.model` and `.npy` files. Both are required.
> **Save both the files under the folder `shared/prediction_models/`**