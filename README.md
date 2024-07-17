# Cx-One-Scan-Automation-Tool
Checkmarx One Server Scan Automation Tool developed for ease the scan process of Client.

# Prerequisites to Run this Tool:

1. Java 1.8: Ensure Java Development Kit (JDK) version 1.8 or higher is installed.

2. Python: Python interpreter installed on the environment.

3. Email SMTP Account: Requires an SMTP server configuration to send email notifications.

4. CheckMarx One Server Account: Access credentials with appropriate group permissions.

5. CheckMarx CLI: Install CheckMarx Command Line Interface (CLI). [Refer to Download ast-cli - https://github.com/Checkmarx/ast-cli/releases]


Note:

- To log in to Checkmarx One Server, you need an API Key. Generate an API key from the Checkmarx platform and use it in the CLI properties file under the key "checkmarx.api.key".

# Procedure to Run the Tool:

- This tool is compatible with multiple environments.

1. Setup:

- Place the entire project folder in your desired environment.
- Ensure the environment meets the aforementioned prerequisites.

2. Configuration:

- Adjust settings in the application.properties file to match your environment configuration.

3. Execution:

- Run the Python script using the following command format:
    python -u "<PATH_TO_CLI-Executor.py>"

    Replace <PATH_TO_CLI-Executor.py> with the actual path where CLI-Executor.py is located.

Example:
    python -u "c:\Users\system\Downloads\CheckMarx-Scan\Project\CLI-Executor.py"

