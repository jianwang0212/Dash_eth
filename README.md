# Dash_eth
This project is trying to fetch real time balance &amp; orderbook of ETH and visualise using dash

## Getting Started

### Running the app locally

First create a virtual environment with conda or venv inside a temp folder, then activate it.

```
virtualenv venv

# Windows
venv\Scripts\activate
# Or Linux
source venv/bin/activate

```

Clone the git repo, then install the requirements with pip

```

git clone https://github.com/jianwang0212/Dash_eth.git
cd Dash_eth
pip install -r requirements.txt

```

Run the app

```

python3 app.py

```

## About the Data_fetcher folder

fetcher_bal_orderbook.py: fetch orderbook and bal data in an exchange => save to
the database.



fetcher_trades.py: fetch historical my trades for an exchange => save to
the database.

merger_td_bal_ods.py: merge all data into a single table in SQL


check_sql.ipynb: check the SQL database for the above three tables in the pandas
dataframe format

other files: make it easy for test single function for the fetcher


## p.s.

* the config file is the API key and secret you need to get your bal & personal trade

The format may look like the following(fake key)

```
indodax = {
    'apiKey': 'BB5W3D5U-SK2PSU13-LYD123412P-DTGTHVOL-ZCU3478KUH',
    'secret': '6028casdw20843c5e1dae31c289d6f45bf742a0dfsdf2c69cd73b7f92cf3901'
}
```

* You may want to use the .ipynb (Jupyter notebook) to see how the fetcher work


## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots
