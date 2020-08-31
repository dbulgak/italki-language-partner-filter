import requests
import configparser
import time
from datetime import datetime
# from pytz import timezone
import logging
import argparse
import webbrowser
import re

PARTNER_API="https://api.italki.com/api/partner"
USER_API="https://api.italki.com/api/user/"

def get_partner(args):
    limit = int(args.limit)

    logging.info(f"ready to search, limiting to {limit}")

    found = 0
    page = 1

    while True:
        # /api/partner?speak=&learn=&gender=&country=AF&city=&page=1&hl=en-us&i_token=1599892361gAAAAABfNN6J6NhPopyFFVUaPw1cQYI_kBWOyZFQ-pHcp-PyJzkE_f0vjEhCHts5rbwVRyX3OuLRmZQZgls1hROi7dkkDfFbr5OvXDaQfehS-b7EZWG2zESH8PirGyt0OCLcvnsOuvHVVCKuB1S8HIoqu2zqK02QhSt5TsyMr85Doir4An6YrFk%3D&i_device=10
        params={"learn": "russian", "i_device": "10", "page": page}
        logging.debug(f"making requests with params {params}")
        r = requests.get(PARTNER_API, params=params)

        logging.debug(r.text)

        for item in r.json()['data']:
            learning = []
            speaking = []

            # lang can be either learning or be learned
            # learning languages are added into list of all languages on a profile page

            for lang in item['language_obj_s']:
                if lang['is_learning']:
                    learning.append([lang['language'], lang['level']])
                else:
                    speaking.append([lang['language'], lang['level']])

            if len(speaking) > 2:
                logging.debug(f"{item['nickname']} speaks too many languages")
                continue

            if len(learning) > 2:
                logging.debug(f"{item['nickname']} learns too many languages")
                continue

            match = filter_spearking_lang(speaking)

            if match == False:
                logging.debug(f"{item['nickname']} is not a native english speaker")
                continue

            match = filter_learning_lang(learning)

            if match == False:
                logging.debug(f"{item['nickname']} does not learn russian")
                continue

            user_profile = "https://www.italki.com/user/" + str(item['id'])
            user_country = item['living_country_id']

            logging.info(f"MATCH: {item['nickname']} -> {item['learning_language']} -> {user_profile}")
            logging.info(f"learning: f{learning}, speaking: f{speaking}")
            logging.debug(item)

            # get extra user information

            user_api_requests = USER_API + str(item['id'])
            params={"i_device": "10"}
            logging.debug(f"making user info {user_api_requests} request with params {params}")
            r = requests.get(user_api_requests, params=params)
            data = r.json()['data']
            logging.debug(data)
            user_timezone_utc = data['user_timezone_utc']

            # find users that are closer to my own time zone
            match = filter_timezone(user_timezone_utc)

            if match == False:
                logging.info(f"{item['nickname']} does not match required timezone")
                continue

            if args.web == True:
                webbrowser.open(user_profile)
            
            found = found + 1

        if found >= limit:
            break

        page = page + 1


# filter users with +/-3 hours from my timezone(so it should be convinient for us to talk)
def filter_timezone(user_timezone_utc):
    match = False

    ts = time.time()
    my_utc_offset = (datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts)).total_seconds()/60/60
    re_match = re.search("UTC([+-]\d+):\d+", user_timezone_utc)

    if re_match:
        user_utc_offset = int(re_match[1])
    else:
        logging.info("no UTC timezone found, skipping")

    logging.info(f"my_utc_offset = {my_utc_offset}, user_utc_offset = {user_utc_offset}")
    six_pm_msk_to_user_time = (user_utc_offset - 3 + 18) % 24
    logging.info(f"18:00MSK -> {six_pm_msk_to_user_time:02}:00MSK")

    return abs(my_utc_offset - user_utc_offset) <= 3


def filter_spearking_lang(speaking):
    match = False

    for lang in speaking:
        if lang[0] == "english" and lang[1] > 5:
            match = True
    
    return match

      
def filter_learning_lang(learning):
    match = False

    for lang in learning:
            if lang[0] == "russian":
                match = True

    return match

def setup_args_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose output")
    parser.add_argument('-w', '--web', help="open in browser", action='store_true', default=False)
    parser.add_argument('-l', '--limit', help="number of people to find", default=10)
    # parser.add_argument('-t', '--time', help="convinient time to talk, inclusive", nargs=2, default="18 21")

    return parser

def setup_logging(args):
    level = logging.INFO

    if args.verbose:
        level = logging.DEBUG

    logging.basicConfig(level=level)

def main():
    parser = setup_args_parser()
    args = parser.parse_args()

    setup_logging(args)

    get_partner(args)


if __name__ == "__main__":
    main()
