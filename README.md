## Directory Structure

```
web_deployment/
│
├── fastapi_elastic_beanstalk/ - FastAPI deployment on AWS Elastic Beanstalk.
│   ├── application.py - Main application file for FastAPI.
│   └── source_python/ - Python scripts and modules for the app's functionality.
│       ├── MCMC.py - Script related to Markov Chain Monte Carlo.
│       ├── RSF.py - Related to rate state functions or models.
│       ├── RateStateModel.py - Python implementation of rate state models.
│       ├── __init__.py - Initializes the Python package.
│       ├── __pycache__/ - Compiled Python files for faster loading.
│       ├── dl_inference.py - Scripts for deep learning inference.
│       ├── lstm/ - Contains LSTM related models and utilities.
│       │   ├── lstm_encoder_decoder.py
│       │   └── utils.py
│       └── utils/ - Utility scripts for operations like JSON and MySQL interactions.
│           ├── json_save_load.py
│           └── mysql_save_load.py
│
├── flask_elastic_beanstalk/ - Flask deployment on AWS Elastic Beanstalk.
│   ├── .ebextensions/ - Configuration for AWS Elastic Beanstalk.
│   │   └── nginx.config - Configuration for NGINX.
│   ├── application.py - Main application file for Flask.
│   ├── elasticbean_tester.py - Script for testing Elastic Beanstalk deployment.
│   ├── flask_api_tester.py - Script for testing the Flask API.
│   ├── requirements.txt - Python dependencies for the Flask project.
│   ├── source_python/ - Similar to the FastAPI directory, for Flask.
│   │   ├── MCMC.py
│   │   ├── RSF.py
│   │   ├── RateStateModel.py
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── dl_inference.py
│   │   ├── lstm/
│   │   └── utils/
│   └── start_flask.py - Script to start the Flask application.
│
└── README.md - The repository's readme file with an overview and instructions.
```

## Running FastAPI
1. Navigate to fastapi folder
2. Run the main script: `uvicorn application:app --reload`

## Running Flask
1. Navigate to flask folder
2. Set environment variables and run the flask application: `python3 start_flask.py`
3. On a separate terminal, test the API endpoints: `python3 flask_api_tester.py`. 

