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

    # Steel = 8
    # Windows not included = 1:7
    # Windows included = 1:8

dataset = pd.read_csv('D:\Data for Model\completed.csv')
X = dataset.iloc[:, 1:8].values

# --- STEEL ----
y = dataset.iloc[:, 8].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

#df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})

filename = 'steel_window_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

# --- Copper ----
y = dataset.iloc[:, 9].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

filename = 'copper_window_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

# --- Timber ---
y = dataset.iloc[:, 10].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

filename = 'timber_window_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

# --- Concrete ----
y = dataset.iloc[:, 11].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

filename = 'concrete_window_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

# --- Glass ---

y = dataset.iloc[:, 12].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

filename = 'glass_window_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

# --- Polystyrene

y = dataset.iloc[:, 13].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

filename = 'polystyrene_window_model.sav'
pickle.dump(regressor, open(filename, 'wb'))

