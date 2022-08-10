# NYU-final-project (Python)

1. Show basic information for two stocks selected by the user
2. For an input date, the user can check the holding period gain/loss from the two stocks. The system will decide which stock is the winner!
3. A timeseries line chart to compare the stocks' historial performance

## Installation

```sh
cd ~/Desktop/NYU-final-project/
```

Use Anaconda to create and activate a new virtual environment, perhaps called "project-env":

```sh
conda create -n project-env python=3.8
conda activate project-env
```

Then, within an active virtual environment, install package dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

Create an environement file ".env" for API and other vars:

```sh
alphavantage_API_KEY="_____________"  # for this app, I used one of the premium APIs provided by professor

APP_ENV="production"
STOCK_1="GOOGL"
STOCK_2="AAPL"
```
## Usage

Printing the basic information of the stockas:

```sh
python -m app.stock_comparison

# in production mode:
APP_ENV="production" python -m app.stock_info
```




## Web app



## Testing