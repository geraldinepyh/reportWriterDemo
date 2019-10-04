from logs import logDecorator as lD 
import jsonref, pprint
from lib.databaseIO import pgIO
from lib.LaTeXreport import reportWriter as rw

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle

config = jsonref.load(open('../config/config.json'))
logBase = config['logging']['logBase'] + '.modules.module1.module1'
projConfig = jsonref.load(open('../config/modules/module1.json'))

@lD.log(logBase + '.getData')
def getData(logger):
    '''get data and generate some tables and plots. 
    
    Parameters
    ----------
    logger : {logging.Logger}
        The logger used for logging error information
    '''
    dbName = projConfig['inputs']['dbName']
    dbVersion = projConfig['inputs']['dbVersion']
    cohortWindow = [0, 1000]
    daysWindow = [0, 365]

    diabetes = datasets.load_diabetes()
    diabetes_df = pd.DataFrame(diabetes.data, columns=diabetes.feature_names)
    descript = pd.DataFrame(diabetes.data, columns=diabetes.feature_names).describe()
    with open('../data/raw_data/descriptive_table.pkl', 'wb') as f:
        pickle.dump(descript, f)

    diabetes_X = diabetes.data[:, np.newaxis, 2] # using only 1 feature
    diabetes_X_train = diabetes_X[:-20]
    diabetes_X_test = diabetes_X[-20:]
    diabetes_y_train = diabetes.target[:-20]
    diabetes_y_test = diabetes.target[-20:]

    regr = linear_model.LinearRegression()
    regr.fit(diabetes_X_train, diabetes_y_train)
    diabetes_y_pred = regr.predict(diabetes_X_test)

    # Plot outputs
    plt.scatter(diabetes_X_test, diabetes_y_test,  color='black')
    plt.plot(diabetes_X_test, diabetes_y_pred, color='blue', linewidth=3)
    plt.savefig('../data/raw_data/fig1.png')

    plt.clf()
    plt.hist(diabetes_df.age)
    plt.savefig('../data/raw_data/fig2.png')

    print('Coefficients: \n', regr.coef_)
    print("Mean squared error: %.2f"
        % mean_squared_error(diabetes_y_test, diabetes_y_pred))
    print('Variance score: %.2f' % r2_score(diabetes_y_test, diabetes_y_pred))

    results = pd.DataFrame([('Coefficient(s)', regr.coef_),
                        ('Mean Squared Error', mean_squared_error(diabetes_y_test, diabetes_y_pred)),
                        ('Variance Score', r2_score(diabetes_y_test, diabetes_y_pred))
                        ], columns=['Results','Values'])
    results.Results = results.Results.astype('str')
    results.Values  = results.Values.astype('int')
    with open('../data/raw_data/results.pkl', 'wb') as f:
        pickle.dump(results, f)

    # Generate 3 separate dataframes as an example
    df1 = descript.s1
    df2 = descript.s3
    df3 = descript.s5
    df_to_concat = [df1,df2,df3]
    for x, dfx in enumerate(df_to_concat):
        with open(f'../data/raw_data/tbls{x}.pkl', 'wb') as f:
            pickle.dump(dfx, f)

    return [descript, results, [df1,df2,df3]]

@lD.log(logBase + '.runExample')
def runExample(logger, projName='Demo'):

    examples = getData()

    rep = rw.Report(projName) 
    rep.title = "Report Example"
    rep.author = "Insert Author Name here"
    rep.date = '25/09/2019'
    rep.initialize(rep.fpath)

    ### Add figures ###
    # 1. by copying from other filepath 
    rep.saveFigure('Figure1', 
                '../data/raw_data/fig1.png', # some other filepath
                caption='This is a plot of the linear reg output.', 
                option='scale=0.6', override=True)

    # 2. by saving or moving directly to figures folder if it's already created
    rep.saveFigure('Figure2', 
                '../data/raw_data/fig2.png', # some other filepath
                caption='This is a histogram of the patients\' age.',
                option=r'width=0.5\textwidth')

    ### Add tables ###
    # 1. Add directly from pandas dataframe 
    rep.saveTable('Table1', 
                examples[0], 
                caption='Descriptive table of diabetes data.', 
                override=False)

    rep.saveTable('Table2', 
                examples[1], 
                caption='Results of the Logisitic Regression', 
                override=True)

    rep.saveTable('Table3', 
                examples[2], # [df1,df2,df3]
                caption='Merged dataframes example.', 
                override=True)

    # 2. Add tex files directly to tables folder 
    # (No need to run saveTable since it's already in TeX)

    # Add sections
    rep.addSection('Introduction')
    rep.addSection('Data')
    rep.addSection('Linear Regression', level=2)
    rep.addSection('Conclusion')

    rep.makeReport()
    return 


@lD.log(logBase + '.main')
def main(logger, resultsDict):
    '''main function for module1
    
    This function finishes all the tasks for the
    main function. This is a way in which a 
    particular module is going to be executed. 
    
    Parameters
    ----------
    logger : {logging.Logger}
        The logger used for logging error information
    '''

    runExample('Example1')

    return

