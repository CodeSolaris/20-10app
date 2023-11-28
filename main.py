import os
import smtplib
import ssl
import requests
import selectorlib
from dotenv import load_dotenv
from datetime import datetime

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Macintosh; "
                  "Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}
EXTRACT_YAML_PATH = "extract.yaml"
DATA_FILE_PATH = "data.txt"

load_dotenv()


def get_url_from_env(option):
    match option:
        case "TOURS_URL":
            return os.getenv("TOURS_URL")
        case "AVERAGE_TEMPERATURE_URL":
            return os.getenv("AVERAGE_TEMPERATURE_URL")


def get_email_credentials():
    username = os.getenv("MY_EMAIL")
    password = os.getenv("PASSWORD")
    return username, password


def create_email_server(username, password):
    host = "smtp.gmail.com"
    port = 465
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(host, port, context=context)
    server.login(username, password)
    return server


def scrape(url):
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract_tours(source):
    extractor = selectorlib.Extractor.from_yaml_file(EXTRACT_YAML_PATH)
    value = extractor.extract(source)["tours"]
    return value


def extract_temperatures(source):
    extractor = selectorlib.Extractor.from_yaml_file(EXTRACT_YAML_PATH)
    value = extractor.extract(source)["home"]
    return value


def store(extracted_data, file_path):
    """
    Store the extracted data in a file.

    Args:
        extracted_data (str): The data to be stored.
        file_path (str): The path of the file to store the data.

    Raises:
        Exception: If an error occurs while writing to the file.

    Returns:
        None
    """
    try:
        with open(file_path, 'w') as file:
            file.write(extracted_data)
    except Exception as e:
        print(f"Error occurred while writing to file: {e}")


def read(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, "w") as file:
            pass
    with open(file_path, "r") as file:
        return file.read()


def send_email(server, receiver, message):
    server.sendmail(receiver, receiver, message)
    print("Email has been sent")


def get_tour_info(url):
    url = get_url_from_env(url)
    username, password = get_email_credentials()
    server = create_email_server(username, password)

    scraped = scrape(url)
    extracted = extract_tours(scraped)
    content = read(DATA_FILE_PATH)

    if extracted not in content:
        store(extracted, DATA_FILE_PATH)
        send_email(server, username, "new event was found!")


def get_average_temperature():
    url = get_url_from_env("AVERAGE_TEMPERATURE_URL")
    scraped = scrape(url)
    extracted = extract_temperatures(scraped)
    return extracted


def main():
    get_tour_info("TOURS_URL")


if __name__ == "__main__":
    temps = get_average_temperature()
    print(temps)
