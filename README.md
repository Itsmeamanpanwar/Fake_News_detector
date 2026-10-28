Fake News Detection System Using spaCy

Overview

The Fake News Detection System is an NLP-based application designed to analyze news text and classify it as potentially real or fake. The project uses spaCy’s text classification capabilities to process textual input and generate predictions.

The application includes separate classification models for COVID-19-related news and Afghanistan-related news. It also incorporates sentiment analysis and user history functionality.

The project demonstrates how Natural Language Processing, machine learning, and web application development can be combined to build a text classification system.

Features

* Fake News Classification: Classifies news text into REAL or FAKE categories using trained spaCy text classification models.
* Multiple News Domains: Includes separate models for COVID-19-related news and Afghanistan-related news.
* Sentiment Analysis: Uses VADER to analyze the sentiment of textual content.
* Interactive Interface: Provides a Streamlit-based user interface.
* User Authentication: Includes login and sign-in functionality through the existing authentication components.
* History Management: Supports storing and retrieving user-related history through the database integration.
* Model Training: Includes Jupyter notebooks for training the classification models.

Technology Stack

Component	Technology
Programming Language	Python
Natural Language Processing	spaCy
Text Classification	spaCy TextCat
Sentiment Analysis	VADER Sentiment
Web Interface	Streamlit
Data Processing	Pandas
Model Training	Jupyter Notebook
Database	MySQL
Database Integration	Existing PHP/MySQL components
Local Database Environment	XAMPP

Project Structure

The repository contains the following major components. Exact filenames and directories may vary depending on the version of the project.

FakeNewsDetectionSpacy-main/
├── model/                    # COVID-19 news classification model
├── modeltaliban/             # Afghanistan-related news classification model
├── Train-COVID.ipynb         # COVID-19 model training notebook
├── Train-Taliban.ipynb       # Afghanistan model training notebook
├── COVID Fake News Data.csv  # COVID-19 news dataset
├── afpfake.csv               # Afghanistan-related news dataset
├── README.md                 # Project documentation
└── ...                       # Application code and supporting files

How It Works

1. Text Input

The application accepts news text for analysis through its user interface.

2. Text Processing

The input is processed using the appropriate text classification pipeline.

3. Model Selection

The application uses the relevant trained model depending on the news category being analyzed:

* model/ for COVID-19-related news.
* modeltaliban/ for Afghanistan-related news.

4. News Classification

The spaCy text classification models predict a label:

* REAL: The model classifies the input as real.
* FAKE: The model classifies the input as fake.

These labels represent model predictions and should not be treated as definitive verification of a news story.

5. Sentiment Analysis

The application uses VADER to analyze the sentiment of the text. Sentiment analysis evaluates the emotional tone of the content; it does not independently establish whether a claim is true or false.

6. User History

The database integration supports user-related functionality and history management through the application’s existing components.

Installation and Setup

Prerequisites

Install or configure the following components:

* Python compatible with the project’s dependencies.
* Git.
* XAMPP, if using the existing PHP/MySQL authentication and history functionality.
* A MySQL database configured for the application.

Compatibility note: This project uses an older spaCy-based model pipeline. Its dependencies may require version adjustments on newer Python versions and Apple Silicon Macs.

1. Clone the Repository

git clone https://github.com/Itsmeamanpanwar/FakeNewsDetectionSpacy.git
cd FakeNewsDetectionSpacy

2. Create a Virtual Environment

python3 -m venv venv

Activate it on macOS or Linux:

source venv/bin/activate

3. Install Dependencies

If the repository contains a requirements.txt file, install its dependencies:

python -m pip install -r requirements.txt

If no requirements file exists, identify the dependencies used by the source code and install compatible versions before running the application.

4. Configure the Database

If you use the existing authentication and history functionality:

1. Install and start XAMPP.
2. Start Apache and MySQL as required by the application.
3. Open phpMyAdmin.
4. Create and configure the database and tables expected by the application.
5. Update the application’s database connection settings.

The original implementation uses a database named mydatabase and references tables named current, customer, and users.

Verify the database schema and configuration against the actual project files before running the application.

5. Run the Application

If the application entry point is app.py, run:

streamlit run app.py

If the main file has a different name, replace app.py with the correct filename.

Model Training

The project includes Jupyter notebooks for training its classification models:

* Train-COVID.ipynb
* Train-Taliban.ipynb

The notebooks use the corresponding datasets to prepare and train the models.

Before retraining, verify that the datasets are available and that the installed spaCy version is compatible with the notebook code.

Applications

Potential applications of this project include:

* Educational demonstrations of NLP-based text classification.
* Exploring machine learning approaches to news classification.
* Comparing text classification models across different news domains.
* Analyzing the sentiment of news content.
* Studying the limitations of automated misinformation detection.

Limitations

* Classification accuracy depends on the quality, size, and representativeness of the training datasets.
* A model may incorrectly classify unfamiliar topics or misleading content.
* Sentiment analysis does not verify factual accuracy.
* A REAL or FAKE prediction is not equivalent to independent fact-checking.
* Older dependencies may require compatibility adjustments on modern systems.
* The models are trained for specific news domains and may not generalize reliably to unrelated topics.

The application should be treated as an educational NLP project rather than a production-grade fact-checking service.

Future Improvements

* Expand the training datasets with diverse and independently verified sources.
* Evaluate precision, recall, F1-score, and confusion matrices.
* Add evidence retrieval and source verification.
* Improve model performance on previously unseen claims.
* Add automated tests and dependency management.
* Modernize the application and database integration.
* Improve the user interface and error handling.

Author

Aman Panwar

GitHub: Itsmeamanpanwar

Disclaimer

This project is intended for educational and research purposes. Its predictions should not be considered conclusive evidence that a news article or claim is true or false. Important claims should be verified using reliable sources and independent fact-checking.
