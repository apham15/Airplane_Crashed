# -*- coding: utf-8 -*-
"""Unsupervised Learning - Airplane Crash Clustering

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1EcLvcgNmkrYZBPraaOk8EKw9X_KMONN2

#Import libraries and datasets
"""

# Commented out IPython magic to ensure Python compatibility.
#Import libraries 
import scipy.stats as stats
import numpy as np
from numpy import nan, isnan, mean, std, hstack, ravel
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, normalize 
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import AgglomerativeClustering, DBSCAN, KMeans, MiniBatchKMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.manifold import TSNE
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
import umap
import plotly.io as plt_io
import plotly.graph_objects as go

from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import urllib
import requests

from datetime import date, timedelta, datetime

import warnings
warnings.filterwarnings("ignore")
# %matplotlib inline

data = pd.read_csv('https://github.com/apham15/large_csv/raw/main/Airplane_Crashes_and_Fatalities_Since_1908.csv', na_values='nan')

data.head(5)

## Count of instances and features
rows, columns = data.shape
print(data.shape)

data.info()

"""#EDA

## Data Cleaning
"""

#find any null value
data.isnull().sum()

#cleaning up
data['Time'] = data['Time'].replace(np.nan, '00:00') 
data['Time'] = data['Time'].str.replace('c: ', '')
data['Time'] = data['Time'].str.replace('c:', '')
data['Time'] = data['Time'].str.replace('c', '')
data['Time'] = data['Time'].str.replace('12\'20', '12:20')
data['Time'] = data['Time'].str.replace('18.40', '18:40')
data['Time'] = data['Time'].str.replace('0943', '09:43')
data['Time'] = data['Time'].str.replace('22\'08', '22:08')
data['Time'] = data['Time'].str.replace('114:20', '00:00') #is it 11:20 or 14:20 or smth else? 

data.Operator = data.Operator.str.upper() #just to avoid duplicates like 'British Airlines' and 'BRITISH Airlines'

# Transforming Time column to datetime format and splitting into two separate ones
time = pd.to_datetime(data['Time'], format='%H:%M')
data['hour'] = time.dt.hour
data['Year'] = data['Date'].apply(lambda x: int(str(x)[-4:]))

#fill null values
data['Aboard'] = data['Aboard'].fillna(0)
data['Fatalities'] = data['Fatalities'].fillna(0)
data['Ground'] = data['Ground'].fillna(0)

data['Fatalities_percentage'] = data['Fatalities'] / data['Aboard']
data['Time1'] = data['Date'] + ' ' + data['Time'] #joining two rows
def todate(x):
  return datetime.strptime(x, '%m/%d/%Y %H:%M')
data['Time1'] = data['Time1'].apply(todate) #convert to date type

print('Date ranges from ' + str(data.Time1.min()) + ' to ' + str(data.Time1.max()))

#determine the survived groups
data['Survived'] = data['Aboard'] - data['Fatalities'] - data['Ground']
data['Has_Survivors'] = 1 #1 is survive
data.loc[data['Survived'] == 0, 'Has_Survivors'] = 0 #0 is no survive

#recheck data
data.head()

#group the core numerical feature with airline operator
operator_fa = data[['Operator','Fatalities']].groupby('Operator').agg(['sum','count'])

"""## Understand the dataset"""

# Univariate analysis
#statistical information for numerical data
data.describe()

#Correlation among variables
corr = data.corr()
plt.subplots(figsize=(13,10))
plt.title('Correlation between numerical variables')
sns.heatmap(corr, vmax=0.9, cmap="rocket", square=True)

#fatalities based on total accidents
X = operator_fa['Fatalities','count']
Y = operator_fa['Fatalities','sum']
plt.scatter(X, Y,label='Operators')
plt.title('Fatalities Cases based on total Accidents')
plt.ylabel('Fatalities')
plt.xlabel('Accidents');

#Fatailities distribution
y = data['Fatalities']
plt.title('Fatalities distribution')
sns.distplot(y, kde=False, fit=stats.norm)
print("Skewness: %f" % data['Fatalities'].skew())
print("Kurtosis: %f" % data['Fatalities'].kurt())

#Line Plot with Fatalities per Year 
yearly = data[['Year','Fatalities']].groupby('Year').agg(['sum','count'])
plt.style.use('bmh')
plt.figure(figsize=(12,6))
yearly['Fatalities','sum'].plot(title='Fatalities by Year',marker = ".", linewidth=1)
plt.xlabel('Year', fontsize=10)
plt.ylabel('Fatalities', fontsize=10)

#Line plot with Acident by year
Temp = data.groupby(data.Time1.dt.year)[['Date']].count() #Temp is going to be temporary data frame 
Temp = Temp.rename(columns={"Date": "Count"})

plt.figure(figsize=(12,6))
plt.style.use('bmh')
plt.plot(Temp.index, 'Count', data=Temp, color='blue', marker = ".", linewidth=1)
plt.xlabel('Year', fontsize=10)
plt.ylabel('Count', fontsize=10)
plt.title('Count of accidents by Year', loc='Center', fontsize=14)
plt.show()

#Bar Graph with No. of Accidents per Month, Day of Week and Hour
gs = gridspec.GridSpec(2, 2)
pl.figure(figsize=(15,10))
plt.style.use('seaborn-muted')
ax = pl.subplot(gs[0, :]) # row 0, col 0
sns.barplot(data.groupby(data.Time1.dt.month)[['Date']].count().index, 'Date', data=data.groupby(data.Time1.dt.month)[['Date']].count(), color='lightskyblue', linewidth=2)
plt.xticks(data.groupby(data.Time1.dt.month)[['Date']].count().index, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
plt.xlabel('Month', fontsize=10)
plt.ylabel('Count', fontsize=10)
plt.title('Count of accidents by Month', loc='Center', fontsize=14)

ax = pl.subplot(gs[1, 0])
sns.barplot(data.groupby(data.Time1.dt.weekday)[['Date']].count().index, 'Date', data=data.groupby(data.Time1.dt.weekday)[['Date']].count(), color='lightskyblue', linewidth=2)
plt.xticks(data.groupby(data.Time1.dt.weekday)[['Date']].count().index, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
plt.xlabel('Day of Week', fontsize=10)
plt.ylabel('Count', fontsize=10)
plt.title('Count of accidents by Day of Week', loc='Center', fontsize=14)

ax = pl.subplot(gs[1, 1])
sns.barplot(data[data.Time1.dt.hour != 0].groupby(data.Time1.dt.hour)[['Date']].count().index, 'Date', data=data[data.Time1.dt.hour != 0].groupby(data.Time1.dt.hour)[['Date']].count(),color ='lightskyblue', linewidth=2)
plt.xlabel('Hour', fontsize=10)
plt.ylabel('Count', fontsize=10)
plt.title('Count of accidents by Hour', loc='Center', fontsize=14)
plt.tight_layout()

matplotlib.rcParams['figure.figsize'] = (12.0, 8.0)
#Lets take a look at the proportion of fatalities per accident for specific operators.
#This bears out some interesting statistics. Thanks for the suggestion on kaggle and stackoverflow
props = operator_fa['Fatalities'].reset_index()
props['Fatalities per Accident'] = props['sum']/props['count']
props.columns = ['Operator','Fatalities','Accidents','Fatalities per Accident']

fig_p,(axp1,axp2) = plt.subplots(2,1,sharex = True)
minacc = 10
fig_p.suptitle('Fatalities per Accident for airlines with > %s Accidents' % minacc)
propstoplot = props[props['Accidents']>minacc]
propstoplot.sort_values('Fatalities per Accident').tail(50).plot(x = 'Operator'
                                                               , y = 'Fatalities per Accident'
                                                               , ax = axp1
                                                               , kind = 'bar'
                                                               , grid = True)
propstoplot.sort_values('Fatalities per Accident').tail(50).plot(x = 'Operator'
                                                               , y = 'Accidents'
                                                               , ax = axp2
                                                               , kind = 'bar'
                                                               , grid = True)

Temp = data.copy()
Temp['isMilitary'] = Temp.Operator.str.contains('MILITARY')
Temp = Temp.groupby('isMilitary')[['isMilitary']].count()
Temp.index = ['Passenger', 'Military']

Temp2 = data.copy()
Temp2['Military'] = Temp2.Operator.str.contains('MILITARY')
Temp2['Passenger'] = Temp2.Military == False
Temp2 = Temp2.loc[:, ['Time1', 'Military', 'Passenger']]
Temp2 = Temp2.groupby(Temp2.Time1.dt.year)[['Military', 'Passenger']].aggregate(np.count_nonzero)

colors = ['yellowgreen', 'lightskyblue']
plt.figure(figsize=(15,6))
plt.subplot(1, 2, 1)
patches, texts = plt.pie(Temp.isMilitary, explode=[0,0.1], colors=colors, labels=Temp.isMilitary, startangle=90)
plt.legend(patches, Temp.index, loc="best", fontsize=10)
plt.axis('equal')
plt.title('Total number of accidents by Type of flight', loc='Center', fontsize=14)

plt.subplot(1, 2, 2)
plt.plot(Temp2.index, 'Military', data=Temp2, color='lightskyblue', marker = ".", linewidth=1)
plt.plot(Temp2.index, 'Passenger', data=Temp2, color='yellowgreen', marker = ".", linewidth=1)
plt.legend(fontsize=10)
plt.xlabel('Year', fontsize=10)
plt.ylabel('Count', fontsize=10)
plt.title('Count of accidents by Year', loc='Center', fontsize=14)
plt.tight_layout()

text = str(data.Summary.tolist())
mask = np.array(Image.open(requests.get('https://i.pinimg.com/originals/65/f5/b4/65f5b4c86574dd2090e9697398ef7a87.jpg', stream=True).raw))

stopwords = set(STOPWORDS)
newStopword = ['aircraft', 'pilot', 'en route', 'airport', 'flight', 'crashed', 'plane crashed', 'plane']
stopwords.update(newStopword)

# Write a function takes in text and mask and generates a wordcloud. 
def generate_wordcloud(mask):
    word_cloud = WordCloud( background_color='black', stopwords=stopwords, mask=mask)
    word_cloud.generate(text)
    plt.figure(figsize=(10,8),facecolor = 'white', edgecolor='blue')
    plt.imshow(word_cloud)
    plt.axis('off')
    plt.tight_layout(pad=0)

#Run the following to generate wordcloud
generate_wordcloud(mask)

text = str(data.Location.tolist())
mask = np.array(Image.open(requests.get('https://i5.walmartimages.com/asr/c90e8d9d-8e28-4430-9930-e038c723b471.1910bb58304eede77fd067448bd91498.jpeg', stream=True).raw))

stopwords = set(STOPWORDS)
newStopword = ['Near']
stopwords.update(newStopword)
#Run the following to generate wordcloud
generate_wordcloud(mask)

#Splitting out the country from the location to see if we can find some interesting statistics about where the most crashes have taken place.
fatalities = operator_fa['Fatalities','sum'].sort_values(ascending=False)
totalfatal = fatalities.sum()
fatalprop = fatalities/totalfatal

s = data['Location'].str[0:].str.split(',', expand=True)
data['Country'] = s[3].fillna(s[2]).fillna(s[1]).str.strip()

#put all the US's states into US columne so it's easier to assign them a country
usNames = ['Virginia','New Jersey','Ohio','Pennsylvania', 'Maryland', 'Indiana', 'Iowa',
          'Illinois','Wyoming', 'Minnisota', 'Wisconsin', 'Nevada', 'NY','California',
          'WY','New York','Oregon', 'Idaho', 'Connecticut','Nebraska', 'Minnesota', 'Kansas',
          'Texas', 'Tennessee', 'West Virginia', 'New Mexico', 'Washington', 'Massachusetts',
          'Utah', 'Ilinois','Florida', 'Michigan', 'Arkansas','Colorado', 'Georgia''Missouri',
          'Montana', 'Mississippi','Alaska','Jersey', 'Cailifornia', 'Oklahoma','North Carolina',
          'Kentucky','Delaware','D.C.','Arazona','Arizona','South Dekota','New Hampshire','Hawaii',
          'Washingon','Massachusett','Washington DC','Tennesee','Deleware','Louisiana',
          'Massachutes', 'Louisana', 'New York (Idlewild)','Oklohoma','North Dakota','Rhode Island',
          'Maine','Alakska','Wisconson','Calilfornia','Virginia','Virginia.','CA','Vermont',
          'HI','AK','IN','GA','Coloado','Airzona','Alabama','Alaksa' 
          ]

#define and clean countries' names
#Decided to try and cleanse the country names.
afNames = ['Afghanstan'] #Afghanistan
anNames = ['off Angola'] #Angola
ausNames = ['Qld. Australia','Queensland  Australia','Tasmania','off Australia'] #Australia
argNames = ['Aregntina'] #Argentina
azNames = ['Azores (Portugal)'] #Azores
baNames = ['Baangladesh'] #Bangladesh
bahNames = ['Great Inagua'] #Bahamas
berNames = ['off Bermuda'] #Bermuda
bolNames = ['Boliva','BO'] #Bolivia
bhNames = ['Bosnia-Herzegovina'] #Bosnia Herzegovina
bulNames = ['Bugaria','Bulgeria'] #Bulgaria
canNames = ['British Columbia', 'British Columbia Canada','Canada2',
            'Saskatchewan','Yukon Territory'] #Canada
camNames = ['Cameroons','French Cameroons'] #Cameroon
caNames = ['Cape Verde Islands'] #Cape Verde
chNames = ['Chili'] #Chile
coNames = ['Comoro Islands', 'Comoros Islands'] #Comoros
djNames = ['Djbouti','Republiof Djibouti'] #Djibouti
domNames = ['Domincan Republic', 'Dominica'] #Dominican Republic
drcNames = ['Belgian Congo','Belgian Congo (Zaire)','Belgium Congo'
           'DR Congo','DemocratiRepubliCogo','DemocratiRepubliCongo',
            'DemocratiRepubliof Congo','DemoctratiRepubliCongo','Zaire',
           'Zaïre'] #Democratic Republic of Congo
faNames = ['French Equitorial Africa'] #French Equatorial Africa
gerNames = ['East Germany','West Germany'] #Germany
grNames = ['Crete'] #Greece
haNames = ['Hati'] #Haiti
hunNames = ['Hunary'] #Hungary
inNames = ['Indian'] #India
indNames = ['Inodnesia','Netherlands Indies'] #Indonesia
jamNames = ['Jamacia'] #Jamaica
malNames = ['Malaya'] #Malaysia
manNames = ['Manmar'] #Myanmar
marNames = ['Mauretania'] #Mauritania
morNames = ['Morrocco','Morroco'] #Morocco
nedNames = ['Amsterdam','The Netherlands'] #Netherlands
niNames = ['Niger'] #Nigeria
philNames = ['Philipines','Philippine Sea', 'Phillipines',
            'off the Philippine island of Elalat'] #Philippines
romNames = ['Romainia'] #Romania
rusNames = ['Russian','Soviet Union','USSR'] #Russia
saNames = ['Saint Lucia Island'] #Saint Lucia
samNames = ['Western Samoa'] #Samoa
siNames = ['Sierre Leone'] #Sierra Leone
soNames = ['South Africa (Namibia)'] #South Africa
surNames = ['Suriname'] #Surinam
uaeNames = ['United Arab Emirates'] #UAE
ukNames = ['England', 'UK','Wales','110 miles West of Ireland'] #United Kingdom
uvNames = ['US Virgin Islands','Virgin Islands'] #U.S. Virgin Islands
wkNames = ['325 miles east of Wake Island']#Wake Island
yuNames = ['Yugosalvia'] #Yugoslavia
zimNames = ['Rhodesia', 'Rhodesia (Zimbabwe)'] #Zimbabwe

clnames = []
for country in data['Country'].values:
  if country in afNames:
      clnames.append('Afghanistan')
  elif country in anNames:
      clnames.append('Angola')
  elif country in ausNames:
      clnames.append('Australia')
  elif country in argNames:
      clnames.append('Argentina')
  elif country in azNames:
      clnames.append('Azores')
  elif country in baNames:
      clnames.append('Bangladesh')
  elif country in bahNames:
      clnames.append('Bahamas')
  elif country in berNames:
      clnames.append('Bermuda')
  elif country in bolNames:
      clnames.append('Bolivia')
  elif country in bhNames:
      clnames.append('Bosnia Herzegovina')
  elif country in bulNames:
      clnames.append('Bulgaria')
  elif country in canNames:
      clnames.append('Canada')
  elif country in camNames:
      clnames.append('Cameroon')
  elif country in caNames:
      clnames.append('Cape Verde')
  elif country in chNames:
      clnames.append('Chile')
  elif country in coNames:
      clnames.append('Comoros')
  elif country in djNames:
      clnames.append('Djibouti')
  elif country in domNames:
      clnames.append('Dominican Republic')
  elif country in drcNames:
      clnames.append('Democratic Republic of Congo')
  elif country in faNames:
      clnames.append('French Equatorial Africa')
  elif country in gerNames:
      clnames.append('Germany')
  elif country in grNames:
      clnames.append('Greece')
  elif country in haNames:
      clnames.append('Haiti')
  elif country in hunNames:
      clnames.append('Hungary')
  elif country in inNames:
      clnames.append('India')
  elif country in jamNames:
      clnames.append('Jamaica')
  elif country in malNames:
      clnames.append('Malaysia')
  elif country in manNames:
      clnames.append('Myanmar')
  elif country in marNames:
      clnames.append('Mauritania')
  elif country in morNames:
      clnames.append('Morocco')
  elif country in nedNames:
      clnames.append('Netherlands')
  elif country in niNames:
      clnames.append('Nigeria')
  elif country in philNames:
      clnames.append('Philippines')
  elif country in romNames:
      clnames.append('Romania')
  elif country in rusNames:
      clnames.append('Russia')
  elif country in saNames:
      clnames.append('Saint Lucia')
  elif country in samNames:
      clnames.append('Samoa')
  elif country in siNames:
      clnames.append('Sierra Leone')
  elif country in soNames:
      clnames.append('South Africa')
  elif country in surNames:
      clnames.append('Surinam')
  elif country in uaeNames:
      clnames.append('UAE')
  elif country in ukNames:
      clnames.append('United Kingdom')
  elif country in usNames:
      clnames.append('United States of America')
  elif country in uvNames:
      clnames.append('U.S. Virgin Islands')
  elif country in wkNames:
      clnames.append('Wake Island')
  elif country in yuNames:
      clnames.append('Yugoslavia')
  elif country in zimNames:
      clnames.append('Zimbabwe')
  else:
      clnames.append(country)

#visuallize the highest fatalities by countries
data['Cleaned Country'] = clnames        
fatalcountries = data[['Fatalities','Cleaned Country']].groupby(['Cleaned Country']).agg('sum')
fatalcountries.reset_index(inplace = True)
fatalcountries['Proportion of Total'] = fatalcountries['Fatalities']/totalfatal

fig_c, (ax1,ax2) = plt.subplots(2,1,sharex = True)
fatalcountries[fatalcountries['Fatalities']>1000].plot(x = 'Cleaned Country'
                                                     , y = 'Fatalities'
                                                     , ax = ax1
                                                     , kind = 'bar'
                                                     , grid = True)
fatalcountries[fatalcountries['Fatalities']>1000].plot(x = 'Cleaned Country'
                                                     , y = 'Proportion of Total'
                                                     , ax = ax2
                                                     , kind = 'bar'
                                                     , grid = True)

data_t = data.groupby('Operator')[['Survived']].sum()
data_t = data_t.rename(columns={"Operator": "Survived"})
data_t = data_t.sort_values(by='Survived', ascending=False)
Prop_by_OpTOP = data_t.head(15)

plt.figure(figsize=(12,6))
sns.barplot(y=Prop_by_OpTOP.index, x="Survived", data=Prop_by_OpTOP, palette="GnBu_d", orient='h')
plt.xlabel('Survived', fontsize=11)
plt.ylabel('Operator', fontsize=11)
plt.title('Total Survived by Operator', loc='Center', fontsize=14)

accidents = operator_fa['Fatalities','count'].sort_values(ascending=False)
interestingOps = accidents.index.values.tolist()[0:5]
optrend = data[['Operator','Year','Fatalities']].groupby(['Operator','Year']).agg(['sum','count'])
ops = optrend['Fatalities'].reset_index()
fig,axtrend = plt.subplots(2,1)
for op in interestingOps:
    ops[ops['Operator']==op].plot(x='Year',y='sum',ax=axtrend[0],grid=True,linewidth=2)
    ops[ops['Operator']==op].plot(x='Year',y='count',ax=axtrend[1],grid=True,linewidth=2)

axtrend[0].set_title('Fatality Trend by Operator')
axtrend[1].set_title('Accident Trend by Operator')
linesF, labelsF = axtrend[0].get_legend_handles_labels()
linesA, labelsA = axtrend[1].get_legend_handles_labels()
axtrend[0].legend(linesF,interestingOps)
axtrend[1].legend(linesA,interestingOps)
plt.tight_layout()

fatalcountries.sort_values(by='Proportion of Total', ascending=False).head(10)

data.groupby(['Type']).agg({'Fatalities_percentage':'count'}).sort_values(by='Fatalities_percentage',ascending=False).head(20).plot.bar()
plt.title('Fatalities Percentage by Aircrafts', loc='Center', fontsize=14)

#route that has high fatalities rate
route= data.groupby('Route').agg({'Fatalities':['sum',lambda x:x.sum() / data['Fatalities'].sum()]})
route.columns=route.columns.map(''.join)
route.reset_index(inplace=True)
route.rename(columns={'Fatalitiessum':'Total Fatalities','Fatalities<lambda_0>':'% of Total Fatalities'}, inplace=True)

route.sort_values(by='Total Fatalities', ascending=False).head(7)

#Location that has most plane crashed
from collections import Counter
loc_list = Counter(data['Location'].dropna()).most_common(10)
locs = []
crashes = []
for loc in loc_list:
    locs.append(loc[0])
    crashes.append(loc[1])
pd.DataFrame({'Crashes in this location' : crashes}, index=locs)

# Creating a fun dataset based on Chinese Zodiac
# Return a bunch of tuples with the Zodiac and its Start/End Dates
def chinese_zodaics():
    start_date = pd.to_datetime("2/2/1908")
    end_date = pd.to_datetime("7/1/2009")
    animals = ['Monkey', 'Rooster', 'Dog', 'Pig', 'Rat', 'Ox', 'Tiger', 'Rabbit', 'Dragon', 'Snake', 'Horse', 'Goat']
    zodiacs = []
    while start_date < end_date:
        for a in animals:    
            year_start = start_date
            year_end = year_start + pd.DateOffset(days=365)
            z = (a, start_date, year_end)
            zodiacs.append(z)
            start_date = year_end
    return zodiacs 

zodiacs = chinese_zodaics()

# Apply the zodiacs to the accident dates
def match_zodiac(date):
    for z in zodiacs: 
        animal, start, end, = z[0], z[1], z[2]
        if start <= date <= end:
            return animal
data_c=data        
data_c.Date = pd.to_datetime(data_c.Date)
data_c['Zodiac'] = data_c.Date.apply(match_zodiac)
data_c['Year'] = pd.DatetimeIndex(data_c['Date']).year
data_c = data_c[['Zodiac', 'Year', 'Fatalities', 'Aboard','Ground']].dropna()
data_c = data_c[data.Fatalities > 1]
data_c

sns.barplot (x='Zodiac', y='Fatalities', data = data_c)
plt.title('Fatalities based on Zodiac', loc='Center', fontsize=14)

# Put key stats into a DataFrame
def zodiac_data(data):
    idx=[ 'Total_Accidents', 'Total_Deaths', 'Mean_Deaths', 'Death_Rate', 'Survival_Rate', 'Deadliest_Accident', 'Total_Survive']
    df = pd.DataFrame()
    for z in data.Zodiac.unique(): 
        zodiac = data[data.Zodiac == z]
        f = zodiac.Fatalities.dropna()
        a = zodiac.Aboard.dropna()
        g = zodiac.Ground.dropna()
        total_accidents = f.count()
        total_deaths = f.sum()
        mean_deaths = f.mean()
        death_rate = total_deaths / a.sum()
        survival_rate = 1 - death_rate
        deadliest = f.max()
        survive = sum(a-f-g)
        df[z] = [total_accidents, total_deaths, mean_deaths, death_rate, survival_rate, deadliest, survive]
    df.index = idx
    df = df.round(2).T
    return df

zodiac_comparison = zodiac_data(data_c)
zodiac_comparison

sns.barplot(x=zodiac_comparison.index, y='Survival_Rate', data=zodiac_comparison)
plt.title('Survival Rate by Zodiac', loc='Center', fontsize=14)

"""# Clustering : Fatalities Clustering

## Data Preparation
"""

data_1 = data.drop(['Date','Time','Location','Summary', 'Fatalities_percentage','hour', 'Year', 'Time1'], axis = 1)
data_1.Country = pd.get_dummies(data_1.Country)
X = data_1.iloc[:,6:12]
X.isnull().any()

cols = ['Aboard', 'Fatalities', 'Ground','Survived','Country']
for col in cols:
	X[col] = X[col].to_numpy()
	X[col] = X[col].astype('int64')

X.info()

"""## Feature Engineering"""

# Standarizing the features
scaler = StandardScaler()
X_stan = scaler.fit_transform(X)

"""## Clustering

### K-Means
"""

# Commented out IPython magic to ensure Python compatibility.
# #Apply KMean with the evaluation based on Silhouette Score
# %%time
# sil_k = np.arange(12,dtype="double")
# for k in np.arange(12):
#   minikm = MiniBatchKMeans(n_clusters=k+2, random_state=0)
#   minikm.fit(X_stan)
#   sil_k[k] = metrics.silhouette_score(X_stan,minikm.labels_,metric='euclidean')
#    
# print(sil_k)
# 
# plt.title("Mini Batch KMeans Silhouette")
# plt.xlabel("Number of Cluster")
# plt.plot(np.arange(2,14,1),sil_k)

"""The best number of cluster is 3, which has the highest Silhouette Coefficient Score (0.661)

### Hierachical Clustering
"""

# Commented out IPython magic to ensure Python compatibility.
# #Apply hierarchical clustering with the evaluation based on Silhouette Score
# %%time
# sil_agg = np.arange(12,dtype="double")
# for k in np.arange(12):
#   agg = AgglomerativeClustering(linkage='complete', 
#                                     affinity='cosine',
#                                     n_clusters=k+2)
#   agg.fit(X_stan)
#   sil_agg[k] = metrics.silhouette_score(X_stan,agg.labels_,metric='euclidean')
#   
# print(sil_agg)
# 
# plt.title("Hierrachy Silhouette")
# plt.xlabel("Number of Cluster")
# plt.plot(np.arange(2,14,1),sil_agg)

"""The best number of cluster is 6, which has the highest Silhouette Coefficient Score (0.6413)

### DBSCAN
"""

# Commented out IPython magic to ensure Python compatibility.
# #Apply dbscan clustering with the evaluation based on Silhouette Score
# %%time
# start   = 0.01
# stop    = 1.5
# step    = 0.01
# my_list = np.arange(start, stop+step, step)
# 
# startb   = 1
# stopb    = 10
# stepb    = .2 # To scale proportionately with epsilon increments
# my_listb = np.arange(startb, stopb+stepb, stepb)
# 
# my_range = range(45)
# 
# one = []
# 
# for i in my_range:
#    dbscan = DBSCAN(eps = 0 + my_list[i] , min_samples = 0 + my_listb[i],metric='euclidean')
#    cluster = dbscan.fit_predict(X_stan)
#    one.append(metrics.silhouette_score(X_stan, cluster))

print(one)
plt.title("DBSCAN Silhouette")
plt.ylabel("Silhouette Score")
plt.xlabel("Number of Eps")
plt.plot(np.arange(0,45,1),one)

"""The best number of Eps is 0.01 and min sample is 1, which has the highest Silhouette Coefficient Score (0.8339)

### Evaluation
"""

random_state = 0
dbscan_eva = DBSCAN(eps = 0.01 , min_samples = 1,metric='euclidean')
cluster_eva = dbscan.fit(X_stan)
labels = cluster_eva.labels_

#print out number of cluster
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
print('Estimated number of clusters: %d' % n_clusters_)

"""> Overal, the best clustering algorithms for clustering the fatilities is DBSCAN with eps = 0.01, min sample is 1, and metric is euclidean, which has 2 clusters

##Visualization with dimensionality reduciton

### PCA's
"""

# We just want the first two principal components
pca = PCA(n_components=2)

# We get the components by 
# calling fit_transform method with our data
X_pca = pca.fit_transform(X)

t = np.arange(5268)
plt.figure(figsize=(10,5))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=t, cmap= cm.rainbow)
plt.xticks([])
plt.yticks([])
plt.axis('off')

"""### t-SNE"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# tsne = TSNE(n_components=2, verbose=1, perplexity=50, n_iter=1000)
# tsne_results = tsne.fit_transform(X_pca)

plt.figure(figsize=(10,5))
plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c=t, cmap= cm.rainbow)
plt.xticks([])
plt.yticks([])
plt.axis('off')

"""### UMAP"""

# Commented out IPython magic to ensure Python compatibility.
# %%time 
# umap_results = umap.UMAP(n_neighbors=3, min_dist=1,
#                       metric='euclidean', target_metric='categorical',
#                       target_n_neighbors=-1, target_weight=0.5,
#      transform_queue_size=4.0, unique=False, verbose=False).fit_transform(X)

plt.figure(figsize=(10,5))
plt.scatter(umap_results[:, 0], umap_results[:, 1], c=t, cmap= cm.rainbow )
plt.xticks([])
plt.yticks([])
plt.axis('off')

"""### Evaluation
> t-SNE's solution is better than those of PCA's, and UMAP's because the different classes are separated more clearly. But it is still not the best one to visualize this dataset

#Clustering: Text Clustering

## Data Preparation
"""

text_data = data['Summary'].dropna()
text_data = pd.DataFrame(text_data)

"""## Feature engineering

* K-Means normally works with numerical feature only, so  I need to convert those world to number. 
* The feature I use is TF-IDF. This statistic uses term frequency and inverse document frequency. The method TfidfVectorizer() implements the TF-IDF algorithm.
"""

documents = list(text_data['Summary'])
vectorizer = TfidfVectorizer(stop_words='english') # Stop words are like "a", "the", or "in" which don't have significant meaning
X = vectorizer.fit_transform(documents)
print(X.shape)

"""## Clustering

### K-Means

Let's test with MiniBatchKmean to get the silhouette score

#### MiniBatchKmean
"""

# Commented out IPython magic to ensure Python compatibility.
# #Apply KMean with the evaluation based on Silhouette Score
# %%time
# sil_k = np.arange(17,dtype="double")
# for k in np.arange(17):
#   minikm = MiniBatchKMeans(n_clusters=k+2, random_state=0)
#   minikm.fit(X)
#   sil_k[k] = metrics.silhouette_score(X,minikm.labels_,metric='euclidean')
#    
# print(sil_k)
# 
# plt.title("Mini Batch KMeans Silhouette")
# plt.xlabel("Number of Cluster")
# plt.plot(np.arange(2,19,1),sil_k)

"""According to this chart, the best silhouette score is 0.0152 when number of clusters are 16
> Let's apply K-means Model

#### KMeans
"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# model = KMeans(n_clusters=16, random_state=0)
# model.fit(X)

# Commented out IPython magic to ensure Python compatibility.
# %%time
# print ('Most Common Terms per Cluster:')
# 
# order_centroids = model.cluster_centers_.argsort()[:,::-1] #sort cluster centers by proximity to centroid
# terms = vectorizer.get_feature_names()
# 
# for i in range(16):
#     print("\n")
#     print('Cluster %d:' % i)
#     for j in order_centroids[i, :17]: #replace 17 with n words per cluster
#         print ('%s' % terms[j]),
#     print

"""### Hierarchical Clustering"""

X1=X.todense()

# Commented out IPython magic to ensure Python compatibility.
# #Apply hierarchical clustering with the evaluation based on Silhouette Score
# %%time
# sil_agg = np.arange(9,dtype="double")
# for k in np.arange(9):
#   agg = AgglomerativeClustering(linkage='complete', 
#                                     affinity='cosine',
#                                     n_clusters=k+2)
#   agg.fit(X1)
#   sil_agg[k] = metrics.silhouette_score(X1,agg.labels_,metric='euclidean')
#   
# print(sil_agg)
# 
# plt.title("Hierrachy Silhouette")
# plt.xlabel("Number of Cluster")
# plt.plot(np.arange(2,11,1),sil_agg)

"""The chart show the best number of cluster for Hierarchy is 2. However, it's not the good clustering method in this case.

###DBSCAN
"""

# Commented out IPython magic to ensure Python compatibility.
# #Apply dbscan clustering with the evaluation based on Silhouette Score
# %%time
# start   = 0.01
# stop    = 1.5
# step    = 0.01
# my_list = np.arange(start, stop+step, step)
# 
# startb   = 1
# stopb    = 10
# stepb    = .2 # To scale proportionately with epsilon increments
# my_listb = np.arange(startb, stopb+stepb, stepb)
# 
# my_range = range(45)
# 
# one = []
# 
# for i in my_range:
#    dbscan = DBSCAN(eps = 0 + my_list[i] , min_samples = 0 + my_listb[i],metric='euclidean')
#    cluster = dbscan.fit_predict(X1)
#    one.append(metrics.silhouette_score(X1, cluster))
#

print(one)
plt.title("DBSCAN Silhouette")
plt.ylabel("Silhouette Score")
plt.xlabel("Number of Eps")
plt.plot(np.arange(0,45,1),one)

"""### Evaluation"""

random_state = 0
dbscan_eva = DBSCAN(eps = 0.01 , min_samples = 1,metric='euclidean')
cluster_eva = dbscan_eva.fit(X1)
labels = cluster_eva.labels_

#print out number of cluster
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
print('Estimated number of clusters: %d' % n_clusters_)

"""The best model which has the highest Silhoette Coefficient Score (0.065) is DBSCAN with eps = 0.01, min_sample = 1, and metric etric='euclidean' with the number of cluster is 4627

## Visualize clustering

### PCA
"""

# We just want the first two principal components
pca = PCA(n_components=2)

# We get the components by 
# calling fit_transform method with our data
pca_components = pca.fit_transform(X.toarray())

# reduce the cluster centers to 2D
reduced_cluster_centers = pca.transform(model.cluster_centers_)

t = np.arange(4878)
plt.figure(figsize=(10,5))
plt.scatter(pca_components[:, 0], pca_components[:, 1], c=t, cmap= cm.rainbow)
plt.scatter(reduced_cluster_centers[:, 0], reduced_cluster_centers[:,1], marker='x', s=150, c='w')
plt.xticks([])
plt.yticks([])
plt.axis('off')

"""### t-SNE"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=300)
# tsne_results = tsne.fit_transform(pca_components)
#

plt.figure(figsize=(10,5))
plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c=t, cmap= cm.rainbow)
plt.xticks([])
plt.yticks([])
plt.axis('off')

"""### UMAP"""

# Commented out IPython magic to ensure Python compatibility.
# %%time 
# umap_results = umap.UMAP(n_neighbors=9, min_dist=1,
#                       metric='euclidean', target_metric='categorical',
#                       target_n_neighbors=-1, target_weight=0.5,
#      transform_queue_size=4.0, unique=False, verbose=False).fit_transform(X.toarray())

plt.figure(figsize=(10,5))
plt.scatter(umap_results[:, 0], umap_results[:, 1], c=t, cmap= cm.rainbow )
plt.xticks([])
plt.yticks([])
plt.axis('off')

"""### Evaluation
> There is no solution better than others. PCA's, t-SNE's, and UMAP's cannot show the different classes which are not separated more clearly.

# Conclusion based on this research
1. Airplane Crashing

* USA has the highest fatility cases in the world
* There are over 85% of airplan crash is from commercial flights
* Don't fly with Aeroflot Operator, there is 68% chance of you dying.
* Don't fly in a Douglas DC-3 aircraft, you are 5 times more chance to die.
* Don't take any flight that flies Tenerife - Las Palmas / Tenerife - Las Palmas route or Tokyo - Osaka.
* Don't fly with any flight of type Douglous DC-3 ,it had highest fatalities percentage.
* Avoid going to Sao Paulo, Brazil ; Moscow, Russia ; Rio de Janeiro, Brazil ; they had highest plane crash location.
* It is so much safer to take flight now-a-days as compared to 1970-80, 1972 was the worst years for airline industry.
* Peole who are born in year of Ox have more chance to die, and people who are born in year of Horse have high chance to survive
* The best clustering algorithms for clustering the fatilities is DBSCAN with eps = 0.01, min sample is 1, and metric is euclidean with the number of cluster is 2

2. Text Clustering
* It's hard to determine which is the best method. Overall, The best model which has the highest Silhoette Coefficient Score (0.065) is DBSCAN with eps = 0.01, min_sample = 1, and metric etric='euclidean', which has 4627 clusters
* Personally, I like K-mean because it returns 16 cluster, which is easy to understand and visuallize. 

3. Outcome
* There is no absolute right answer for clustering. To bring the best results for business solution, I would recomend data scientists consider the best model that fit the business need and apply their business acumen to suggest the best strategy for the whole team.
* My data analysis above is good for travelers around the world to have an insider about traviling with airplane. And it is a good suggestion for operators or aerospace company to look up the disavantages of the past to improve their future businesses.
"""