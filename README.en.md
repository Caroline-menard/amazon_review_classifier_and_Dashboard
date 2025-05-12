<p align="right">
  <img src="https://github.com/Caroline-menard/-Caroline-menard/blob/main/logo_blanc.png?raw=true" alt="Logo Caroline Ménard" width="120">
</p>

# Amazon Review Classifier & Dashboard

This project is an automatic customer review classification application combined with an interactive dashboard built using Streamlit. It enables the detection and visualization of the main types of issues reported by customers in Amazon reviews.

## Data Source

The data comes from a public dataset provided by Amazon as part of the **Amazon Customer Reviews Dataset** program.
The dataset contains several million reviews left by Amazon customers (only reviews from the "Beauty" category were used here).

👉 👉 In this project, a set of **4,600 reviews** was manually labeled to train a multi-label (and multi-output) classification model.
This model was then used to automatically predict issue categories for over **150,000 additional reviews**.

## General Project Architecture
This project is built around an automated classification pipeline for product reviews, combined with a cloud-hosted interactive visualization interface.

<p align="center">
  <img src="https://github.com/Caroline-menard/-Caroline-menard/blob/main/Capture%20d%E2%80%99e%CC%81cran%202025-05-11%20a%CC%80%2017.59.15.png?raw=true" alt="Architecture" width="380">
</p>

### Data

Originally, the full dataset (Amazon customer reviews) was hosted in a Supabase database, allowing dynamic batch predictions and insertion of the results.
To ensure better service stability and avoid interruptions due to free-tier quotas, the data used in the Streamlit dashboard is now loaded locally from a .parquet file provided in the repository.

### Dashboard

The user interface is an interactive dashboard hosted on Streamlit Cloud.
It allows users to visualize the distribution of reported issue types, filter the data, explore raw customer comments, and export selected subsets.

Curious to try it out? It’s available here 👉 [Launch the dashboard](https://caroline-menard-amazon-reviews-dashboard.streamlit.app/)

### Prediction Pipeline

The entire process relies on several Python scripts, executed sequentially to automate label prediction on customer reviews:

  > - predict_batch.py: selects a batch of unlabeled reviews from the database, runs the prediction pipeline, and generates the results.<br>
  > -  etl_insert.py: inserts these results into the Supabase database.<br>
  > -   main.py: orchestrates a full prediction session by calling predict_batch.py followed by etl_insert.py.<br>
  > -   batch_loop.py: continuously runs main.py until there are no more reviews to process. Once the database is fully annotated, the loop stops automatically.<br>
  > -  utils.py: contains all the model components: preprocessing and feature extraction functions, vectorization (TF-IDF + SVD), classifier (XGBClassifier), and post-prediction corrections.<br>

## Focus on the Prediction Pipeline
### the Core of the Pipeline

The core of the model relies on a relatively complex Scikit-learn pipeline, illustrated below:
<p align="center">
  <img src="https://github.com/Caroline-menard/-Caroline-menard/blob/main/pipeline.png?raw=true" alt="Architecture" width="1000">
</p>

##### This pipeline is framed by two custom classes:

  >  **Preprocessor(BaseEstimator, TransformerMixin):** <br>
    This preprocessor operates before the main pipeline. It concatenates the title and text of each review into a single analysis field, selects relevant columns, and converts certain variables into the appropriate format (boolean, categorical, etc.).

  >  **LabelCorrection(BaseEstimator, TransformerMixin):** <br>
    This post-prediction step applies simple logical rules to correct inconsistent outputs:<br>
  > -If the rating is ≥ 4, the label is corrected to “no issue” (only the retour_client label is preserved if activated).<br>
  > -If no label is detected, the label “other issue” is assigned to avoid empty predictions.

##### Internal Structure of the Pipeline

The pipeline is composed of two main groups of features:

  > - The first group is derived from text data (title + review), vectorized using a TfidfVectorizer and reduced to 20 dimensions via TruncatedSVD (dimensionality reduction).<br>

  > - The second group consists of handcrafted features created using **FunctionTransformer**.<br>
        These include keyword detectors or regular expression matches related to specific issue categories: customer returns, perceived quality, side effects, etc.
        These features are then standardized using a **StandardScaler**.

The final output is passed to a MultiOutputClassifier, which wraps an **XGBClassifier** to handle multilabel classification.
