# AI Safety Resource Allocation Optimization Algorithm

This repository contains the code and data for optimizing resource allocation across AI governance and policy advocacy projects. The goal is to distribute a fixed budget to maximize the impact of AI safety efforts while accounting for factors such as impact potential, uncertainty, scalability, and neglectedness.

## Table of Contents
1. [Introduction](#introduction)
2. [Problem Statement](#problem-statement)
3. [Methodology](#methodology)
4. [Data](#data)
5. [Model Details](#model-details)
6. [Results](#results)
7. [Usage](#usage)
8. [Future Work](#future-work)
9. [License](#license)

---

## Introduction

As AI technologies rapidly advance, effectively allocating resources to AI safety research and advocacy is critical. This project aims to create an optimization model that allocates funding to AI governance and policy advocacy projects. By considering impact potential, uncertainty, scalability, and other criteria, this model seeks to ensure that limited resources are used as effectively as possible to mitigate risks posed by advanced AI systems.

## Problem Statement

The challenge is to optimize the allocation of a fixed budget across AI safety projects to:
- Maximize the overall impact
- Minimize uncertainty in project outcomes
- Ensure scalability and feasibility
- Consider neglectedness of important research areas

This linear programming model was developed to address these issues by optimizing the budget allocation using real-world data scraped from Manifund’s AI Governance funding portal.

## Methodology

### 1. **Data Collection**
The dataset consists of 20 AI safety projects scraped from Manifund’s AI Governance funding portal. Each project includes details such as:
- Project title
- Funding raised
- Funding goal
- Project summary

### 2. **Evaluation Criteria**
The following criteria were used to evaluate and rank projects:
- **Impact Potential (1-10)**: Higher impact is assigned to projects with larger goals and those aiming to address critical AI safety issues.
- **Uncertainty (1-10)**: This score indicates the level of risk based on how much funding the project has already raised relative to its goal.
- **Scalability (1-10)**: Higher scalability is assigned to projects with larger goals that can potentially scale up with additional funding.
- **Timeframe Priority (1-10)**: Projects with shorter-term goals may be given higher priority based on the model’s timeframe setting.
- **Geographic Scope (1-10)**: Global projects receive the highest score, while local or unclear projects receive lower scores.
- **Neglectedness (1-10)**: Projects with smaller goals are given higher neglectedness scores, indicating that these areas may have received less attention and are more impactful to address.
- **Tractability (1-10)**: This measures how feasible a project is to complete, with smaller, more achievable projects scoring higher.

### 3. **Model Constraints**
Several constraints are applied:
- **Budget Constraint**: Ensures that the total funding allocated does not exceed the fixed budget.
- **Risk Tolerance**: Adjusts the uncertainty scores based on the model's tolerance for risk, allowing more risky projects to be selected when appropriate.
- **Data Integrity Flags**: Flags projects with vague or incomplete information, reducing their funding priority.

### 4. **Monte Carlo Simulation**
A Monte Carlo simulation was used to estimate opportunity cost, evaluating the potential loss from not funding alternative high-impact projects.

## Data

The dataset used in this model is stored in `aisf_projects.csv`, which includes:
- Project title
- Summary
- Funding raised and goal
- Impact and uncertainty scores (generated using an LLM and project metadata)

## Usage

### Prerequisites
- Python 3.x
- PuLP library
- Pandas library

Install the necessary packages with:
```bash
pip install pulp pandas
```
# Running the Model

To run the linear programming model:
1. Create and export [openai API key](https://platform.openai.com/docs/quickstart/create-and-export-an-api-key)
2. Run `python3 scrape_html.py` script.
3. Ensure the dataset `aisf_projects.csv` is in the working directory.

```bash
python allocation_model.py
```

## Future Work
- Remove duplicate slugs
- Create a script to turn the output into a csv file
