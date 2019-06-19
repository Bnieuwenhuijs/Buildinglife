import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
import requests
import json

dataset = pd.read_csv('ImputedData.csv', sep=';')
y = dataset.iloc[:, 10].values
X = dataset.iloc[:, 0:3].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

#df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})

filename = 'finalized_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

#pickle.dump(regressor, open('steel.p','wb'))

#model = pickle.load(open('steel.pkl','rb'))