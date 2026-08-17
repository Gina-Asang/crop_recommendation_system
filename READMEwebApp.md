# AI-Powered Crop Recommendation System

This CS254 Introduction to Artificial Intelligence project recommends a crop from soil and environmental conditions. The user enters nitrogen, phosphorus, potassium, temperature, humidity, soil pH and rainfall. A trained machine-learning model then predicts one of 22 crop classes.

## Problem

Choosing a crop that does not match the soil and environmental conditions can lead to poor crop performance and wasted resources. This project explores whether machine learning can use basic soil and weather-related values to support crop-selection decisions.

The system is **decision support**. A recommendation is not a guarantee of crop yield because many real farming factors are not included in the dataset.

## Dataset

The project uses `Dataset/Crop_recommendation_dataset.csv` with 2,200 records and 22 crop classes. The seven input features are:

- Nitrogen (N)
- Phosphorus (P)
- Potassium (K)
- Temperature
- Humidity
- Soil pH
- Rainfall

The dataset used for model training is not presented as a Ghana-specific dataset.

## Models Trained

We trained and compared four classifiers:

- Decision Tree
- K-Nearest Neighbors (KNN)
- Support Vector Machine (SVM)
- Random Forest

All four models use the same stratified **60% training / 20% validation / 20% test** split with `random_state=42`. Validation data is used for simple tuning. The final comparison uses the same untouched test samples for every model.

 |

Random Forest achieved the strongest result in this experiment and is also the deployed model. It is useful for the project because it combines strong performance with feature-importance values that help explain the model at a general level.



## Notebook Order

For a clean run, open a terminal in the project folder, start Jupyter, and run the notebooks in this order:

1. `Dataset_preprocessing.ipynb`
2. `KNN_Model.ipynb`
3. `Decision_Tree_model.ipynb`
4. `SVM_Model.ipynb`
5. `Random_forest_model.ipynb`
6. `Model_comparison.ipynb`

The notebooks use relative paths such as `../Dataset/Crop_recommendation_dataset.csv`, so run them with the notebook working directory set to the `notebooks` folder.

## Installation

Create and activate a virtual environment, then install the project requirements:

```bash
pip install -r requirements.txt
```

## Run the Web Application

The web application uses a Python Flask backend. Flask loads the actual saved Random Forest model and exposes the prediction endpoint used by the interface.

```bash
cd backend
python app.py
```

Open the local address shown by Flask, normally:

```text
http://127.0.0.1:5000
```

The interface collects the seven input values, sends them to `/api/predict`, and follows the project decision-support flow: **Predict → Explain → Evaluate Reliability → Offer Justified Alternatives**.

