import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle
import requests
import json

# Woonfunctie = 1
# Winkelfunctie = 2
# Industriefunctie = 3
# anders = 4



dataset = pd.read_csv('D:\ImputedData.csv')
    # Steel = 10
    # Windows included = 1:10
y = dataset.iloc[:, 15].values
X = dataset.iloc[:, 1:9].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

#df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})

filename = 'finalized_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

#pickle.dump(regressor, open('steel.p','wb'))

#model = pickle.load(open('steel.pkl','rb'))