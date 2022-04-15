from fastapi import FastAPI, Response
from pydantic import BaseModel
from urllib.parse import quote
import requests
import os

app = FastAPI()
BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json?"
API_KEY = os.environ.get('GMAPS_API')


class AddressPayload(BaseModel):
    """
    A base model that is used by an endpoint,
    to send a payload
    """
    address: str
    output_format: str


@app.post("/getAddressDetails/")
def details(address_payload: AddressPayload):
    address = address_payload.address
    output_format = address_payload.output_format

    address = quote(address)  # encode the url format

    """
      check if the output_format is valid
      and then make a request
    """
    if output_format.upper() == 'JSON' or output_format.upper() == 'XML':
        # make a request to the api
        response = requests.post(f"{BASE_URL}address={address}&key={API_KEY}")

        if response.status_code != 200:
            return {"message": "Invalid Request"}
        else:
            output_response = response.json()
            response_status = output_response["status"]

            """
                Only parse the api for longitude and
                lattitude if there is a result
            """

            if response_status == "OK":
                """
                    Parsing the json response from the api to
                    get lattitude, longitude and address
                """
                parse_output = output_response["results"][0]
                lat = parse_output["geometry"]["location"]["lat"]
                lng = parse_output["geometry"]["location"]["lng"]
                address_output = parse_output["formatted_address"]

                """
                    check the output format
                    and render accordingly
                """

                if output_format.upper() == 'JSON':
                    return {
                        "coordinates": {
                            "lat": lat,
                            "lng": lng
                        },
                        "address": address_output
                    }
                else:
                    data = f"""<?xml version="1.0" encoding="UTF-8"?>
                                <root>
                                <address>{address_output}</address>
                                <coordinates>
                                    <lat>{lat}</lat>
                                    <lng>{lng}</lng>
                                </coordinates>
                                </root>
                            """
                    return Response(content=data, media_type="application/xml")
            else:
                return "Zero Results Found"
    else:
        return "Enter a valid output format - json or xml"
