import pandas as pd

#read the text file
with open('result.txt') as f:
    data = f.readlines()

#extract the variables
PNL = []
Max_Drawdown = []
slow_ma_period = []
fast_ma_period = []
atr_period = []
takeprofit = []
stoploss = []

for line in data:
    PNL.append(line.split('=')[1].split(' ')[1])
    Max_Drawdown.append(line.split('=')[2].split(' ')[1])
    slow_ma_period.append(line.split('{')[1].split(',')[0].split(':')[1])
    fast_ma_period.append(line.split('{')[1].split(',')[1].split(':')[1])
    atr_period.append(line.split('{')[1].split(',')[2].split(':')[1])
    takeprofit.append(line.split('{')[1].split(',')[3].split(':')[1])
    stoploss.append(line.split('{')[1].split('}')[0].split(',')[4].split(':')[1])


#create a dataframe
df = pd.DataFrame()

#add the variables to the dataframe
df['PNL'] = PNL
df['Max_Drawdown'] = Max_Drawdown
df['slow_ma_period'] = slow_ma_period
df['fast_ma_period'] = fast_ma_period
df['atr_period'] = atr_period
df['takeprofit'] = takeprofit
df['stoploss'] = stoploss

#write the dataframe to a csv file
df.to_csv('result.csv', index=False)