# Real Estate Dashboard

This project is a real estate dashboard application built using Streamlit. It allows users to fetch and analyze real estate data ON THE MARKET RIGHT NOW from various cities, providing insights into rental and investment opportunities.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/real-estate-dashboard.git
    cd real-estate-dashboard
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the Streamlit application:
    ```sh
    streamlit run app/application.py
    ```

2. Open your web browser and navigate to `http://localhost:8501` to access the dashboard.

3. Enter your credentials in the sidebar to authenticate and fetch new ads.

## Features

- **City Selection**: Choose a city to analyze real estate data.
- **Rent and Investment Analysis**: View rental and investment opportunities with various visualizations.
- **Data Fetching**: Fetch new ads from the API and update the local database.
- **Outlier Cleaning**: Clean outliers from the database to ensure data quality.
- **Historical Data**: Analyze historical trends in rental prices and market tension.


## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Notes

Integrate INSEE data on population: [INSEE Statistics](https://www.insee.fr/fr/statistiques/2011101?geo=COM-38053#chiffre-cle-1)
=> Use the INSEE commune code
