# Crypto Universe
![Demo](demo/crypto-universe.gif)

## Getting Started

To get a local copy of this project up and running, follow these simple steps.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/starling114/crypto-universe.git
   ```

2. Navigate to the project directory:

   ```bash
   cd crypto-universe
   ```

3. Install Node.js dependencies:

   ```bash
   npm install
   ```

4. Set up the Python environment:

    Navigate to the `scripts` directory:

    ```bash
    cd scripts
    ```

    Create a virtual environment:

    ```bash
    python -m venv myenv
    ```

    Activate the virtual environment:

    ```bash
    source myenv/bin/activate
    ```

    Activate the virtual environment (Windows):

    ```bash
    myenv\Scripts\activate
    ```

    Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

Once you have installed all dependencies and set up the Python environment, you can start the application with the following command from the root directory:

```bash
npm start
```

The server will start on [http://localhost:3000](http://localhost:3000). You can open this URL in your web browser to view the application.

### Configuration Files

There are two main configuration files used in the project:

- **configs.json**: This file holds information about networks, their tokens, RPCs, native tokens, etc.

- **private_configs.json**: This file holds information about networks and their RPCs that are your private RPCs.

Make sure to update these files with the correct information to ensure the application functions correctly.

### Python Scripts configuration and execution

For the Python scripts, there are two configuration files:

- **Configs**: Located under `scripts/modules/NAME_OF_MODULE/configs.json`, these files store configurations needed for the scripts. UI also shows options (in selects, etc.) based on these files.
- **Instructions**: Located under `scripts/modules/NAME_OF_MODULE/instructions.json`, these files store instructions needed to run each script.
- **Secrets**: Located under `scripts/modules/NAME_OF_MODULE/secrets.json`, these files store sensitive information needed for the scripts, such as API keys and private keys.

## VPS Authentication Configuration

To enable basic authentication for the application, follow these steps:

1. Copy `.env.example` file as `.env` in the root directory of the project.

2. Edit the following environment variables in the `.env` file:

  ```plaintext
  BASIC_AUTH=true
  BASIC_AUTH_USERNAME=YOUR_USERNAME
  BASIC_AUTH_PASSWORD=YOUR_PASSWORD
  ```

3. Start the server or restart if it is already running.

With these steps, basic authentication will be enabled for your application, requiring you to enter the specified username and password to access it.
