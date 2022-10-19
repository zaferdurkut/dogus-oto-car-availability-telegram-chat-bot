from datetime import datetime
from typing import List
import requests

from config import (
    SEND_MESSAGE_API_URL,
    CAR_CONTROL_TOKEN,
    CAR_CONTROL_GROUP_CHAT_ID,
    DOGUS_OTO_GET_CARS_API_URL,
    DOGUS_OTO_GOLF_KEY,
    DOGUS_OTO_BASE_URL,
    CAR_CONTROL_CHAT_ID,
    DOGUS_OTO_OCTAVIA_KEY,
)


def populate_message(items: List[dict], is_not_found_message: bool):
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
            result_str
            + f"{item['model']}, *{item['price']}* fiyat ile, \n\t {locations}, \n\t url: {item['url']}\n"
        )
    search_time = " Arama Zamanı: " + datetime.now().strftime("%Y/%m/%d-%H:%M")
    if len(result_str) > 0:
        return "*Sıfır Araba Arama Sonucu* \t " + search_time + "\n\n" + result_str
    else:
        if is_not_found_message:
            return "*Araç Bulunamadı* \t " + search_time


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
        print(response.json()["ok"])
    except Exception as e:
        print(e)


def get_cars_from_dogus_oto_api(model_key: str) -> List[dict]:
    response = requests.post(
        DOGUS_OTO_GET_CARS_API_URL.format(CAR_MODEL_KEY=model_key),
        json={},
        verify=False,
    )
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


def main(car_key: str, is_not_found_message=False):
    cars = get_cars_from_dogus_oto_api(model_key=car_key)
    message = populate_message(cars, is_not_found_message)
    if message is not None:
        send_to_telegram(message, chat_id=CAR_CONTROL_CHAT_ID)


main(car_key=DOGUS_OTO_OCTAVIA_KEY, is_not_found_message=False)
