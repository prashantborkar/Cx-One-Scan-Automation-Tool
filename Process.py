import os
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
from datetime import datetime

def find_latest_json_file(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {folder_path}")
    
    # Get file path and modified time for each JSON file
    file_paths = [os.path.join(folder_path, file) for file in json_files]
    file_times = [(file, os.path.getmtime(path)) for file, path in zip(json_files, file_paths)]

    # Sort files by modification time (most recent first)
    sorted_files = sorted(file_times, key=lambda x: x[1], reverse=True)
    
    # Return path of the most recent JSON file
    return os.path.join(folder_path, sorted_files[0][0])

def load_json_report(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def analyze_json_report(report_data):
    results = report_data.get("results")
    
    # Check if results is None or empty
    if results is None or len(results) == 0:
        scan_id = report_data.get("scanID", "Unknown Scan ID")
        severity_count = {"High": 0, "Medium": 0, "Low": 0, "Information": 0}
        vulnerability_summary = {"High": [], "Medium": [], "Low": [], "Information": []}
        return severity_count, vulnerability_summary, f"Risk Level: No Risk with this build, as scan ID is {scan_id}"

    # Initialize severity and vulnerability dictionaries
    severity_count = {"High": 0, "Medium": 0, "Low": 0, "Information": 0}
    vulnerability_summary = {"High": [], "Medium": [], "Low": [], "Information": []}

    scan_id = report_data.get("scanID", "Unknown Scan ID")  # Extract scanID from report_data

    # Analyze each finding
    for result in results:
        severity = result.get("severity", "").capitalize()  # Ensure case uniformity
        if severity not in severity_count:
            severity = "Information"  # Default to Information if severity is not recognized

        severity_count[severity] += 1
        
        description = result.get("description", "")
        vulnerability_details = result.get("vulnerabilityDetails", "")

        if description and vulnerability_details:
            finding_summary = {
                "Description": description,
                "Vulnerability Details": vulnerability_details
            }
            vulnerability_summary[severity].append(finding_summary)
    
    return severity_count, vulnerability_summary, scan_id



def send_summary_email(summary_data, recipients, smtp_server, smtp_port, sender_email, password):
    severity_summary, vulnerability_summary, scan_id = summary_data

    email_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
            }}
            h2 {{
                color: #333;
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
            }}
            .severity {{
                margin-top: 20px;
            }}
            .finding {{
                margin-bottom: 15px;
                padding: 10px;
                background-color: #f9f9f9;
                border-left: 4px solid;
            }}
            .high {{ border-color: #f44336; }}
            .medium {{ border-color: #ff9800; }}
            .low {{ border-color: #4caf50; }}
            .information {{ border-color: #2196f3; }}
            .details {{
                margin-top: 5px;
                color: #666;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <h2>Hello User,</h2>
        <p>Thanks for using Checkmarx Scan. Below are the details of Scan ID: <strong>{scan_id}</strong></p>
        <div class="severity">
            <h3>Results per Severity:</h3>
            <ul>
                <li class="high">High: {severity_summary['High']} finding(s)</li>
                <li class="medium">Medium: {severity_summary['Medium']} finding(s)</li>
                <li class="low">Low: {severity_summary['Low']} finding(s)</li>
                <li class="information">Information: {severity_summary['Information']} finding(s)</li>
            </ul>
        </div>
        <div class="severity">
            <h3>Results per Vulnerability:</h3>
    """

    for severity, findings in vulnerability_summary.items():
        if findings:
            email_content += f"<div class='{severity.lower()} severity'>"
            email_content += f"<h4>{severity} Severity Findings:</h4>"
            for index, finding in enumerate(findings, start=1):
                email_content += f"<div class='finding {severity.lower()}'>"
                email_content += f"<p><strong>{index}. Description:</strong> {finding['Description']}</p>"
                email_content += f"<p class='details'><strong>Vulnerability Details:</strong> {finding['Vulnerability Details']}</p>"
                email_content += "</div>"
            email_content += "</div>"

    email_content += """
        </div>
        <p>These findings are categorized by severity and provide details on the affected files, lines, and potential security implications as described in the SAST scan results.</p>
        <div class="footer">
            <p>Best Regards,</p>
            <p>Checkmarx PS Team</p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = f'Security Scan Summary Report for Scan ID: {scan_id}'
    msg.attach(MIMEText(email_content, 'html'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipients, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    # Read properties from application.properties
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'application.properties'))

    smtp_server = config['EMAIL']['smtp_server']
    smtp_port = int(config['EMAIL']['smtp_port'])
    sender_email = config['EMAIL']['sender_email']
    password = config['EMAIL']['password']

    recipients = config['EMAIL']['recipients'].split(',')  # Split recipients by comma

    try:
        # Find the most recent JSON file in the folder
        folder_path = config['FILES']['checkmarx.output.path']
        json_file_path = find_latest_json_file(folder_path)
        print(f"Found the most recent JSON file: {json_file_path}")

        # Load JSON report from file
        report_data = load_json_report(json_file_path)

        # Analyze JSON report
        summary_data = analyze_json_report(report_data)

        # Send email with summary
        send_summary_email(summary_data, recipients, smtp_server, smtp_port, sender_email, password)

    except Exception as e:
        print(f"Error: {str(e)}")
