# Ancillary Stats Data

Ancillary Stats Data (ASD) is the data retrieval and persistence layer of Ancillary Stats. It's currently deployed to AWS Lambda and primarily triggered by the "handlers.main" function.

This project is not intended for commercial use in any form.

## Running Locally

### Installing

Clone the repo

```
git clone https://github.com/arosenberg01/asdata.git
```

Install python packages (recommended to use a virtual environemnt, such as [venv](https://docs.python.org/3/tutorial/venv.html)

```
pip install -r requirements.txt
```

The only remaining requirement to use the service is to supply a SQLAlchemy-compatible database in the form of environment variables, detailed in [settings.py](https://github.com/arosenberg01/asdata/blob/master/settings.py)

### Running

Incoming events are handling through the handler.main, which expects a dictionary as an argument with 'handler_name' and 'args'. 'handler_name' is used to route to the correct sub-handler, and args contains specific function arguments

A sample invocation of updating all game data for a single NBA player can be triggering locally by adding the following to the bottom of [handlers.py](https://github.com/arosenberg01/asdata/blob/master/handlers.py):

```python
if __name__ == "__main__":
    main({
        'handler_name': 'update_player_games',
        'args': {
            'player_ids': ['5601']
    }
}, {})
```

And then run:

```
python handlers.py
```

### Unit tests

These test the main functionality of the NbaPlayerPage and NbaTeamPage classes, as well as utility functions

```
python -m unittest discover tests
```

## Built With

* [SQLAlchemy](http://www.dropwizard.https://www.sqlalchemy.org//1.0.2/docs/)
* [Beautiful Soup](https://https://www.crummy.com/software/BeautifulSoup/.apache.org/)
* [AWS Lambda](https://aws.amazon.com/lambda/)

## Authors

* **Ansel Rosenberg**

## License

This project is licensed under the MIT License - see the [LICENSE.txt](https://github.com/arosenberg01/asdata/blob/master/LICENSE.txt) file for details


