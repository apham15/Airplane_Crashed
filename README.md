# Airplane_Crashed

At the time this Dataset was created in Kaggle (2016-09-09), the original version was hosted by Open Data by Socrata at the at [![](https://img.shields.io/badge/Data-Orginal__data__set-blue)](https://opendata.socrata.com/Government/Airplane-Crashes-and-Fatalities-Since-1908/q2te-8cvq), but unfortunately that is not available anymore. The dataset contains data of airplane accidents involving civil, commercial and military transport worldwide from 1908-09-17 to 2009-06-08.
![airports-world-network](https://user-images.githubusercontent.com/63126292/100527674-00053d00-319a-11eb-8c97-93025d1dc632.png)

## 1. Business Understanding
I am a traveler, who always use airplane as the main transportation to discover the world. And My favorite desination is Southest Asia, where I can do snokerling, kayaking, and diving. As a result, when I found this dataset, all my curiousities increase. Let's learn what was the airplane crashing from the past, I may know some insightful that would help me to decide for my future trips. Also, as an Asian, Chinese Zodiac is something very interesting. I did some fun stuff with that to learn more about the data.

As a data scientist who loves to learn more about the dataset, I create a few question to ask myself the way I manipulate the data to bring up insightful information for business.

1. What is the fatalities rates? Does it tell us anything?
2. Any other realted variable that may impact on the airplane crashed?
3. How many planes were crashed yearly, monthly, weekly, and hour?
4. What is the interesting trend based on the raw dataset that business/ people would want to know?
5. Any suggestions based on the dataset?
6. Any machine learning algorithm that I can apply?

I found out that to be outstanding, I need to grind the dataset and do something that others never explore. Thanks to Kaggle, I can compare my work with others to find the better solutions.

I am very happy to say thank you and give a credit to [![](https://img.shields.io/badge/Kaggle-Data-blue?logo=Kaggle)](https://www.kaggle.com/saurograndi/airplane-crashes-since-1908)

## 2. What did I do in this project

a. Understand the data
* Applied descriptive analysis and utilized visualization to give some insight
* Created my own grouping to group airplane crashed that related with time (Yearly, Monthly, etc and Chinese zodiac)
* Found out the most mentioned words and the most destinations in the summary section.

b. Machine Learning Algorithms
* Applied Clustering methods to find the common of airplane fatalities
* Applied Clustering to find the most common words in summary section
* Utilized dimensional reduction to visualize those clustering

## 3. Outcome/ results

### 1. Airplane Crashing

* USA has the highest fatility cases in the world

![Screen Shot 2020-11-28 at 5 30 29 PM](https://user-images.githubusercontent.com/63126292/100528183-75274100-319f-11eb-819a-49755eb20a10.png)

`top 10 countries that has the most fatalities cases`
* There are over 85% of airplan crashed which are from commercial flights
![Unknown](https://user-images.githubusercontent.com/63126292/100528169-35605980-319f-11eb-96c2-1eb0e23fac64.png)
* Don't fly with Aeroflot Operator, there is 68% chance of you dying.
![download (7)](https://user-images.githubusercontent.com/63126292/100661072-8ba4d800-3318-11eb-8ff3-a991ba19e87d.png)

* Althout it is a military airplane, Don't fly in a Douglas DC-3 aircraft, you are 5 times more chance to dir and it had highest fatalities percentage.
![download (8)](https://user-images.githubusercontent.com/63126292/100661233-c4dd4800-3318-11eb-9313-b69f8eab1d3c.png)

* Don't take any flight that flies Tenerife - Las Palmas / Tenerife - Las Palmas route or Tokyo - Osaka.
![Screen Shot 2020-11-30 at 2 32 38 PM](https://user-images.githubusercontent.com/63126292/100661381-040b9900-3319-11eb-9808-a040843f7fe9.png)

* Avoid going to Sao Paulo, Brazil ; Moscow, Russia ; Rio de Janeiro, Brazil ; they had highest plane crash location.
![Screen Shot 2020-11-30 at 2 35 28 PM](https://user-images.githubusercontent.com/63126292/100661672-695f8a00-3319-11eb-806d-68a5d4354ac1.png)

* It is so much safer to take flight now-a-days as compared to 1970-80, 1972 was the worst years for airline industry.

![download (6)](https://user-images.githubusercontent.com/63126292/100660930-539d9500-3318-11eb-8aec-2f11c7091964.png)


* Peole who are born in year of Ox have more chance to die, and people who are born in year of Horse have high chance to survive
![download (9)](https://user-images.githubusercontent.com/63126292/100661775-9a3fbf00-3319-11eb-8103-5b35c5bc2d9e.png)
![download (10)](https://user-images.githubusercontent.com/63126292/100661776-9ad85580-3319-11eb-8108-c98376f7e609.png)

### 3. Airplane Fatalities Clustering
* The best clustering algorithms for clustering the fatilities is DBSCAN with eps = 0.01, min sample is 1, and metric is euclidean, which has 2 clusters
![download (11)](https://user-images.githubusercontent.com/63126292/100666375-8480c880-331e-11eb-9d2c-2c8f98bb6353.png)

### 2. Text Clustering
* It's hard to determine which is the best method. Overall, The best model which has the highest Silhoette Coefficient Score (0.065) is DBSCAN with eps = 0.01, min_sample = 1, and metric etric='euclidean', which has 4627 clusters
* Personally, I like K-mean because it returns 16 cluster, which is easy to understand and visuallize. 
![download (12)](https://user-images.githubusercontent.com/63126292/100666428-9b271f80-331e-11eb-95e2-25bdff6ff931.png)
![download (13)](https://user-images.githubusercontent.com/63126292/100666430-9c584c80-331e-11eb-99c1-60147de4b9ad.png)


### 3. Learning from this project
* There is no absolute right answer for clustering. To bring the best results for business solution, I would recomend data scientists consider the best model that fit the business need and apply their business acumen to suggest the best strategy for the whole team.
* My data analysis above is good for travelers around the world to have an insider about traviling with airplane. And it is a good suggestion for operators or aerospace company to look up the disavantages of the past to improve their future businesses.

## 4. My notebook.
Since it is a large jupyternotebook, I store it on google colab.
 [![](https://img.shields.io/badge/Google%20Colab-Airplane__Crashed-yellow)](https://colab.research.google.com/drive/1EcLvcgNmkrYZBPraaOk8EKw9X_KMONN2?usp=sharing)

Also I attach python file above so everyone can learn
 [![](https://img.shields.io/badge/Python-Airplane__Crashed-blue?logo=Python)](https://github.com/apham15/Airplane_Crashed/blob/main/unsupervised_learning_airplane_crash_clustering.py)

And please connect with me on Linkedin. 
 [![](https://img.shields.io/badge/LinkedIn-Anh__(Andrew)__Pham-blue?logo=LinkedIn)](https://www.linkedin.com/in/anhpham96/)

