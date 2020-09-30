#%%

import math
import pandas_datareader as web
import numpy as np
import pandas as pd
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

#%%

df = web.DataReader('SPY', data_source='yahoo', start='2000-01-01', end=dt.date.today())
# Show the data
df

#%%

plt.figure(figsize=(30,15))
plt.title('Close Price History between Jan and Mar 2020')
plt.plot(df['Close'], color='steelblue')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.show()

#%%

# Create a new dataframe with only the 'Close Column'
data = df.filter(['Close'])
# Convert the dataframe to a numpy array
dataset = data.values
# Get the number of rows to train the model
training_data_len = math.ceil(len(dataset) * .8)
training_data_len


#%%

scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

#%%

train_data = scaled_data[0:training_data_len , :]
#Split the data into x_train and y_train data sets
x_train = []
y_train = []

for i in range(60, len(train_data)):
  x_train.append(train_data[i-60:i, 0])
  y_train.append(train_data[i, 0])

#%%

x_train, y_train = np.array(x_train), np.array(y_train)

#%%

x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

#%%

model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

#%%

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

#%%

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=1)

#%%

# Create the testing data set
# Create a new array containing scaled values from index 1543 to 2003
test_data = scaled_data[training_data_len - 60: , :]
# Create the data set's x_test and y_test
x_test = []
y_test = dataset[training_data_len:, :]
for i in range(60, len(test_data)):
  x_test.append(test_data[i-60:i, 0])

#%%

x_test = np.array(x_test)

#%%

# Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

#%%

# Get the model's predicted price values
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

#%%

# Evaluate the model by calculating the root mean squared error (RMSE
rmse = np.sqrt(np.mean(((predictions-y_test)**2)))

#%%

# Plot the data
train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions
# Visualize the model
plt.figure(figsize=(50,10))
plt.title('Model for future movement of SPY')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
#plt.plot(train['Close'])
plt.plot(valid[['Close','Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
plt.show()

#%%

# Get the quote
SPY_quote = web.DataReader('SPY', data_source='yahoo', start='1990-01-01', end=dt.date.today())
# Create a new dataframe
new_df = SPY_quote.filter(['Close'])
# Get the last 60 day closing price values and covert the dataframe to an array
last_60_days = new_df[-60:].values
# Scale the data to be values between 0 and 1
last_60_days_scaled = scaler.transform(last_60_days)
# Create an empty list
X_test = []
# Append the past 60 days
X_test.append(last_60_days_scaled)
# Convert the X_test data set to a numpy array
X_test = np.array(X_test)
# Reshape the data
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
# Get the predicted scaled price
pred_price = model.predict(X_test)
# undo the scaling
pred_price = scaler.inverse_transform(pred_price)
print(pred_price)

