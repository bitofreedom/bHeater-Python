import subprocess
import sys

def install_package(package):
    """Install a package using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Main function to check and install missing dependencies."""
    required_packages = [
        "Flask==2.3.2",
        "paramiko==3.2.0"
    ]

    for package in required_packages:
        try:
            __import__(package.split("==")[0])
        except ImportError:
            print(f"{package} is not installed. Installing...")
            install_package(package)

    print("All dependencies are installed.")

if __name__ == "__main__":
    main()