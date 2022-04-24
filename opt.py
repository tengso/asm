import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

# Read in price data
path = 'data/bbg_return.csv'
df = pd.read_csv(path, parse_dates=True, index_col="Date", delimiter='\t')
df = df['2018']
# Calculate expected returns and sample covariance
df
mu = expected_returns.mean_historical_return(df, returns_data=True)
S = risk_models.sample_cov(df, returns_data=True)

# Optimize for maximal Sharpe ratio
ef = EfficientFrontier(mu, S, weight_bounds=(0.005, 0.10))
raw_weights = ef.max_sharpe()
# raw_weights = ef.min_volatility()

cleaned_weights = ef.clean_weights()
cleaned_weights
ef.portfolio_performance(verbose=True)

ef.save_weights_to_file("weights.csv")  # saves to file
print(cleaned_weights)
ef.portfolio_performance(verbose=True)

