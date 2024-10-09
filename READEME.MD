# About
* This fetches continuous data for NIFTY, BANKNIFTY from Zerodha in live market and store in mysql database

# Application startup commands
* start mysql DB server: `docker-compose -f ./startup_scripts/db.yaml -p mysql_db_stock up`
* start price fetch process: `chmod +x ./startup_scripts/price-fetch.sh && ./startup_scripts/price-fetch.sh`
* start api server: `chmod +x ./startup_scripts/api-server.sh && ./startup_scripts/api-server.sh`
* run momentum analysis script: `python manage.py run_momentum_analysis_script`

# Backtesting
## Momentum v1
* Run momentum v1 backtesting: `chmod +x ./startup_scripts/backtesting/momentum_v1.sh && ./startup_scripts/backtesting/momentum_v1.sh`
* Run optimisation for momentum_v1 by "grip search": `chmod +x ./startup_scripts/backtesting/optimisation_grid_search.sh && ./startup_scripts/backtesting/optimisation_grid_search.sh`
* Run optimisation for momentum_v1 by "bayesian scikit": `chmod +x ./startup_scripts/backtesting/momentum_v1_optimisation_bayesian_scikit.sh && ./startup_scripts/backtesting/momentum_v1_optimisation_bayesian_scikit.sh`

## Momentum 1 min candlesticks
* Run momentum 1 min candlesticks backtesting: `chmod +x ./startup_scripts/backtesting/momentum_1min_candle.sh && ./startup_scripts/backtesting/momentum_1min_candle.sh`
* Run optimisation for momentum_1min_candle by "bayesian scikit": `chmod +x ./startup_scripts/backtesting/momentum_1min_candlestick_optimisation_bayesian_scikit.sh && ./startup_scripts/backtesting/momentum_1min_candlestick_optimisation_bayesian_scikit.sh`
* Run algo on test data for momentum_1min_candle: `chmod +x ./startup_scripts/backtesting/momentum_1min_candle_test_data.sh && ./startup_scripts/backtesting/momentum_1min_candle_test_data.sh`

# DB data storage location
* `/Users/Subhram/my-projects/db-mysql`

# Notes
* Start the application just before 9:15 am as this is the market opening time
* Stop it after 3:30 pm as this is the market closing time.
