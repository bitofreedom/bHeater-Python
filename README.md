# bHeater-Python
Bitcoin heater control dashboard

## heaterService.py
`heaterService.py` is the main application for controlling and monitoring your Bitcoin heater. This script provides a dashboard interface to manage the heater's operations and monitor its performance.

### Setup Instructions

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/bitofreedom/bHeater-Python.git
    cd bHeater-Python
    ```

2. **Install Dependencies:**
    It is recommended to run the `install_dependencies.py` script to install all necessary dependencies.
    ```bash
    python install_dependencies.py
    ```

3. **Configure the Application:**
    Edit the `heaters.json` file to set up your heater's parameters and preferences.

4. **Run the Application:**
    Start the `heaterService.py` application using the following command:
    ```bash
    python heaterService.py
    ```

### Usage

Once the application is running, you can access the dashboard through your web browser at `http://localhost:5000`. The dashboard allows you to:

- Monitor the heater's performance metrics.
- Start and stop the heater.
- Adjust settings and preferences.

Make sure your heater is properly connected and configured before starting the application.

For more detailed information, refer to the documentation within the repository.


# Setup and run Windows Service
Insert details here about allowing a python script to be run as a windows service...
