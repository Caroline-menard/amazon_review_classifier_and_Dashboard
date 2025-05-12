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

