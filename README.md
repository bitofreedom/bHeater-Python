# bHeater-Python
Bitcoin miner / heater control dashboard

## heaterService.py
`heaterService.py` is the main application for controlling and monitoring your Bitcoin miner and heater. This script provides a dashboard interface to manage the miner's operations and monitor its performance.

### Setup Instructions

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/bHeater-Python.git
    cd bHeater-Python
    ```

2. **Install Dependencies:**
    It is recommended to run the `install_dependencies.py` script to install all necessary dependencies.
    ```bash
    python install_dependencies.py
    ```

3. **Configure the Application:**
    Edit the `config.json` file to set up your miner's parameters and preferences.

4. **Run the Application:**
    Start the `minerService.py` application using the following command:
    ```bash
    python minerService.py
    ```

### Usage

Once the application is running, you can access the dashboard through your web browser at `http://localhost:5000`. The dashboard allows you to:

- Monitor the miner's performance metrics.
- Start and stop the miner.
- Adjust settings and preferences.

Make sure your miner is properly connected and configured before starting the application.

For more detailed information, refer to the documentation within the repository.