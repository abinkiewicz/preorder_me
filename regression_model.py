import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np
import matplotlib.pyplot as plt

#Reading file
#Change to with open
socks_data = pd.read_csv('socks_reports.csv') #nazwa pliku do zmiany
socks_data.head()

#Separate features and labels
X, y = socks_data[['columns']].values, socks_data['quantity'].values
print('Features: ', X[:10], '\nLabels:', y[:10], sep='\n')

#Split data 70%-30% into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=0)

print ('Training Set: %d rows\nTest Set: %d rows' % (X_train.shape[0], X_test.shape[0]))

#Fit a linear regression model on the training set
model = LinearRegression().fit(X_train, y_train)
print (model)

#Evaluation
predictions = model.predict(X_test)
np.set_printoptions(suppress=True)
print('Predicted labels: ', np.round(predictions)[:10])
print('Actual labels   : ' ,y_test[:10])

#Plots(?)

#Metrics
mse = mean_squared_error(y_test, predictions)
print("MSE:", mse)

rmse = np.sqrt(mse)
print("RMSE:", rmse)

r2 = r2_score(y_test, predictions)
print("R2:", r2)

