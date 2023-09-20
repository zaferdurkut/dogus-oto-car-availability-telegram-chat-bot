import logging
from datetime import datetime
from time import sleep
from typing import List

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from config import (
    SEND_MESSAGE_API_URL,
    CAR_CONTROL_TOKEN,
    CAR_CONTROL_GROUP_CHAT_ID,
    DOGUS_OTO_GET_CARS_API_URL,
    DOGUS_OTO_BASE_URL,
    DOGUS_OTO_CAR_KEYS,
)
from logging_config import setup_logger


urllib3.disable_warnings(InsecureRequestWarning)

logger = setup_logger(__name__, level=logging.INFO)


def populate_message(model_key: str, items: List[dict], is_not_found_message: bool):
    result_str = ""
    for item in items:

        locations = [
            "".join(
                [
                    location["dealer_name"],
                    " - ",
                    "*** Rezerve Edilebilir ***"
                    if location["is_option"] is True
                    else " Opsiyonlu",
                ]
            )
            for location in item["locations"]
        ]
        result_str = (
            result_str + f"*Model*: {item['model']}\n"
            f"*Fiyat*: {item['price']}\n"
            f"*URL*:   {item['url']}\n"
            f"*Konum*: {', '.join(locations)}\n"
            f"----------\n"
        )

    search_time = "Arama Zamanı: " + datetime.now().strftime("%Y/%m/%d-%H:%M")
    if len(result_str) > 0:
        return (
            "\n\n"
            f"*#----------------------------------------#*\n"
            + f"*Sıfır Araba Arama Sonucu ({model_key})* \t "
            + search_time
            + "\n\n"
            + result_str
        )
    else:
        if is_not_found_message:
            return f"{model_key.upper()} - *Araç Bulunamadı* \t " + search_time


def send_to_telegram(message, chat_id):

    try:
        response = requests.post(
            SEND_MESSAGE_API_URL.format(API_TOKEN=CAR_CONTROL_TOKEN),
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
            },
        )
        logger.info(response.json()["ok"])
    except Exception as e:
        logger.error(e)


def get_cars_from_dogus_oto_api(model_key: str) -> List[dict]:
    request_url = DOGUS_OTO_GET_CARS_API_URL.format(CAR_MODEL_KEY=model_key)
    response = requests.post(
        request_url,
        json={},
        verify=False,
    )
    logger.info(request_url + " | Status Code:  " + str(response.status_code))
    if response.status_code == 200:
        result = []
        for item in response.json()["data"]:
            result.append(
                {
                    "model": item["submodelname"],
                    "price": item["price"],
                    "url": DOGUS_OTO_BASE_URL.format(PATH=item["permalink"]),
                    "locations": [
                        {
                            "dealer_name": dealer["dealername"],
                            "is_option": dealer["isoptiontocustomer"],
                            "is_showroom": dealer["isshowroombadge"],
                        }
                        for dealer in item["vehiclereservedealer"]
                    ],
                }
            )

        return result
    return []


def search_car_availability(model_key: str, is_not_found_message=False):
    cars = get_cars_from_dogus_oto_api(model_key=model_key)
    message = populate_message(
        model_key=model_key, items=cars, is_not_found_message=is_not_found_message
    )
    if message is not None:
        send_to_telegram(message, chat_id=CAR_CONTROL_GROUP_CHAT_ID)


if __name__ == "__main__":
    logger.info("Starting to search cars")
    while True:
        for model_key in DOGUS_OTO_CAR_KEYS:
            logger.info(f"Searching for {model_key}")
            search_car_availability(model_key=model_key, is_not_found_message=False)
            sleep(5)
        logger.info("Finished searching cars")
        sleep(60 * 60)
