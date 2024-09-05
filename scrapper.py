import base64
import datetime
import requests

# Credentials
USERNAME = ""
PASSWORD = ""

# Base URL
BASE_URL = "https://tc-net.insa-lyon.fr/"

# Target page
TARGET = "/edt/std/AffichageEdtPromo.jsp"

# Group ID
GROUP_ID = "3 TC 4"

# Scrapper class
class Scrapper(requests.Session):
    """
    Creates a new scrapper object that will be used to scrap the TC-Net website.
    """

    def __init__(self, url: str) -> None:
        """
        Initializes a new instance of the Scrapper class.

        Parameters:
        - url (str): The URL to be scrapped.

        Returns:
        - None
        """
        super().__init__()
        self.url = url

    def get(self, path="") -> requests.Response:
        """
        Sends a GET request to the specified path and returns the response.
        Args:
            path (str, optional): The path to append to the base URL. Defaults to "".
        Returns:
            requests.Response: The response object containing the server's response to the request.
        """
        target_url = self.url + path
        response = super().get(target_url)
        return response

    def post(self, path="", data=None) -> requests.Response:
        """
        Sends a POST request to the specified path with the provided data and returns the response.
        Args:
            path (str, optional): The path to append to the base URL. Defaults to "".
            data (dict, optional): The data to send in the request. Defaults to None.
        Returns:
            requests.Response: The response object containing the server's response to the request.
        """
        target_url = self.url + path
        response = super().post(target_url, data=data)
        return response
    
    def put(self, path="", data=None) -> requests.Response:
        """
        Sends a PUT request to the specified path with the provided data and returns the response.
        Args:
            path (str, optional): The path to append to the base URL. Defaults to "".
            data (dict, optional): The data to send in the request. Defaults to None.
        Returns:
            requests.Response: The response object containing the server's response to the request.
        """
        target_url = self.url + path
        response = super().put(target_url, data=data)
        return response
    
    def authenticate(self, username: str, password: str) -> requests.Response:
        """
        Authenticates the user with the provided username and password.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            None
        """
        # Create the payload
        payload = f"{username}:{password}"

        # Encode the payload to base64
        encoded_payload = base64.b64encode(payload.encode("utf-8"))

        print(payload)
        
        # Add authorization header
        self.headers.update({
            "Authorization": f"Basic {encoded_payload.decode('utf-8')}"
        })

    def get_timetable(self, path, date:str, group_id:str) -> requests.Response:
        """
        Retrieves the timetable for a specific date and group.
        Args:
            path (str): The path to send the request to.
            date (str): The date in the format dd/MM/yyyy.
            group_id (str): The ID of the group.
        Returns:
            requests.Response: The response object containing the timetable data.
        """

        # Calculate the hidden_date field, which is 65 days before the date (given in the format dd/MM/yyyy)
        date = datetime.datetime.strptime(date, "%d/%m/%Y")
        hidden_date = date - datetime.timedelta(days=65)

        # Count the week number
        week_number = hidden_date.isocalendar()[1]

        # Get the dates back in the format dd/MM/yyyy and urlencode them
        date = date.strftime("%d/%m/%Y")
        hidden_date = hidden_date.strftime("%d/%m/%Y")
    

        # Forge the payload
        payload = {
            "date_hidden": hidden_date,
            "date": date,
            "USemaine": week_number,
            "choixGroupe": group_id
        }

        # Send the request
        return self.post(path, data=payload)

    
if __name__ == '__main__':
    scrapper = Scrapper(BASE_URL)
    scrapper.authenticate(USERNAME, PASSWORD)
    response = scrapper.get_timetable(TARGET, date="23/06/2025", group_id=GROUP_ID)

    # print raw request and response
    print("========== REQUEST ==========")
    print(response.request.headers)
    print(response.request.body)

    print("========== RESPONSE ==========")
    print(response.headers)
    print("Writing to timetable.html") # To avoid flooding the console with the HTML content
    open("timetable.html", "w").write(response.text)
