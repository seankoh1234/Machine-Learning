''' 
- Explore the data.
- Find customer pain points
- Find what people love about spotify
'''
#%% Import and install dependencies
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import nltk
from nltk.corpus import stopwords

data = pd.read_csv('C:/Users/user/Documents/coding/spotify reviews/reviews.csv')

#%% Preparation
# Set time of review as dataframe index (row name)
data.Time_submitted = pd.to_datetime(data.Time_submitted)
data.set_index('Time_submitted',inplace=True)
    
#%%
# Aggregate ratings by day, number of ratings by day, and 1 week rolling window average
df1 = pd.DataFrame(data.Rating).resample('D').mean()
df1['Count'] = data.Rating.resample('D').count()
df1['Rolling window average'] = df1.Rating.rolling(window='7D').mean()

x = df1.index
y1 = df1.Count
y2 = df1.Rating
y3 = df1['Rolling window average']

fig = plt.figure()
ax1, ax2 = fig.subplots(2,1,sharex=True)
ax1.plot(x,y2,'C0',x,y3,'C1')
ax1.set_ylabel('Rating')
ax2.plot(x,y1,'C0')
ax2.set_ylabel('Number of reviews')
fig

#%%
ax = data['Rating'].value_counts().sort_index().plot(kind='bar',title='Count of Ratings')

#%%
# We see that there was a sharp spike of negative reviews on a specific few days in March, as well as in mid-April. What seems to be the problem?
lowest = df1.sort_values('Rating').iloc[:10,] # We can pick and choose the dates with the lowest ratings from here
lowestmarapr = lowest.sort_index().loc['2022-3':'2022-4'].index
badreviews = data.loc[(data.index.floor("d").isin(lowestmarapr)) & (data['Rating']<3)]

rawbr = ''.join(badreviews['Review'].array)

# Perform tokenization on these dataframes
def totokens(s):
    sentences = nltk.sent_tokenize(s)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    return sentences
#%%
badreviews = totokens(rawbr)
badreviews = [i.lower() for j in badreviews for i in j]
stop = stopwords.words('english')
stop.remove('in')
badreviews = [i for i in badreviews if i not in stop and i.isalpha()]

#%%
f1 = nltk.FreqDist(badreviews)
f1.plot(20, title='20 Most Common Words (Sans Stopwords)', percents=True)

bi_br = [i for i in list(nltk.bigrams(badreviews))]
f2 = nltk.FreqDist(bi_br)

tri_br = [i for i in list(nltk.trigrams(badreviews))] # Trigrams including stopwords for context
f3 = nltk.FreqDist(tri_br)

def result(n): return [i[0] if type(i[0])==str else ' '.join(i[0]) for i in n]
                         
print(f'Most common words (without stopwords): {result(f1.most_common(20))}\n\
      Bigrams:\n {result(f2.most_common(20))} \n\
      Trigrams:\n {result(f3.most_common(20))}')
      
#%%
# Let's further analyse the contexts using the common words we've found
badreviewtxt = nltk.Text(nltk.word_tokenize(rawbr))
badreviewtxt.collocations()

# We can review the context under which each word appears, and harvest information on the problems from there.
badreviewtxt.concordance('disappears')
badreviewtxt.concordance('update')
# Some things are immediately evident: the last update on these days was a buggy mess.
# By excluding these days from analysis, we should be able to get an idea of the more general areas for improvement.

#%%
# We repeat the process for tokenization and analysis on the rest of the dataset, excluding the days we previously analysed.
dfgood = data.loc[~data.index.floor('d').isin(lowestmarapr)]
rawgr = ''.join(dfgood.Review.array)
goodreviews = totokens(rawgr)
goodreviews = [i.lower() for j in goodreviews for i in j]
goodreviews = [i for i in goodreviews if i not in stop and i.isalpha()]

f4 = nltk.FreqDist(goodreviews)
f4.plot(20, title='20 Most Common Words (Sans Stopwords)', percents=True)

bi_gr = [i for i in list(nltk.bigrams(goodreviews))]
f5 = nltk.FreqDist(bi_gr)

tri_gr = [i for i in list(nltk.trigrams(goodreviews))] # Trigrams including stopwords for context
f6 = nltk.FreqDist(tri_gr)
                         
print(f'Most common words (without stopwords): {result(f4.most_common(20))}\n\
      Bigrams:\n {result(f5.most_common(20))} \n\
      Trigrams:\n {result(f6.most_common(20))}')

#%%
# We definitely see a lot more positivity (trigrams like "best music app" and "best music streaming" appear), but some problems still resurface: reviews complain about not being able to listen or play music, and "please fix" is the 4th most common bigram.
goodreviewstxt = nltk.Text(nltk.word_tokenize(rawgr))
goodreviewstxt.collocations()
# Let's check out the context of some common words:

dfgood[dfgood.Review.str.contains('Joe Rogan')].Rating.mean()
dfgood.Rating.mean()
