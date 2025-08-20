# ML & Data Science Template

## Overview
Comprehensive template for machine learning and data science projects with Claude Code integration.

## Features
- ✅ **ML Pipeline Ready**: End-to-end model development
- ✅ **Data Processing**: Advanced ETL and feature engineering
- ✅ **Model Deployment**: Production-ready MLOps
- ✅ **Experiment Tracking**: Comprehensive model versioning
- ✅ **Performance Monitoring**: Real-time model performance

## Tech Stack

### Core ML
- **Python**: Primary language with scientific stack
- **PyTorch**: Deep learning framework
- **Scikit-learn**: Traditional ML algorithms
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

### Data Processing
- **Apache Spark**: Large-scale data processing
- **Dask**: Parallel computing for Python
- **Polars**: Fast DataFrame library
- **Apache Airflow**: Workflow orchestration

### MLOps
- **MLflow**: Experiment tracking and model registry
- **DVC**: Data and model versioning
- **Kubeflow**: Kubernetes-native ML workflows
- **Docker**: Containerized deployments

## Quick Start
```bash
# Initialize ML project
./scripts/ml-setup.sh --type=classification --data=structured

# Setup environment
conda env create -f environment.yml
conda activate ml-project

# Start Jupyter Lab
jupyter lab

# Run training pipeline
python scripts/train_model.py

# Deploy model
python scripts/deploy_model.py
```

## Project Structure
```
├── data/                     # Raw and processed data
│   ├── raw/                 # Original datasets
│   ├── processed/           # Cleaned datasets
│   └── external/            # Third-party data
├── notebooks/               # Jupyter notebooks
│   ├── exploratory/        # EDA notebooks
│   ├── modeling/           # Model development
│   └── evaluation/         # Model assessment
├── src/                     # Source code
│   ├── data/               # Data processing
│   ├── models/             # Model definitions
│   ├── features/           # Feature engineering
│   └── visualization/      # Plotting utilities
├── models/                  # Trained model artifacts
├── reports/                 # Analysis reports
├── .claude/                 # Claude Code configuration
└── scripts/                 # Automation scripts
```

## Specialized Commands
- `/ml:explore` - Generate comprehensive EDA
- `/ml:preprocess` - Create data preprocessing pipeline
- `/ml:model` - Develop and train ML models
- `/ml:evaluate` - Generate model evaluation reports
- `/ml:deploy` - Setup model deployment infrastructure

## ML Agents
- **Data Analyst**: Automated EDA and insights
- **Feature Engineer**: Advanced feature creation
- **Model Architect**: ML model design and optimization
- **MLOps Engineer**: Deployment and monitoring
- **Performance Monitor**: Real-time model tracking