# About
* This fetches continuous data for NIFTY, BANKNIFTY from Zerodha in live market and store in mysql database

# Application startup commands
* start mysql DB server: `docker-compose -f ./startup_scripts/db.yaml -p mysql_db_stock up`
* start price fetch process: `chmod +x ./startup_scripts/price-fetch.sh && ./startup_scripts/price-fetch.sh`
* start api server: `chmod +x ./startup_scripts/api-server.sh && ./startup_scripts/api-server.sh`
* run momentum analysis script: `python manage.py run_momentum_analysis_script`

# DB data storage location
* `/Users/Subhram/my-projects/db-mysql`

# Notes
* Start the application just before 9:15 am as this is the market opening time
* Stop it after 3:30 pm as this is the market closing time.
