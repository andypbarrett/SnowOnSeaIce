table = pd.pivot_table(df, values='amount', index=df.index, columns='statid')
table = table.resample('MS').sum() # Generate month sums
table = table.where(table > 0) # Set zero to NaN
table.head()

month_table = pd.DataFrame({'Parch': table.mean(axis=1), 'n': table.count(axis=1)})
month_table.resample('Y').sum(min_count=12).dropna()

