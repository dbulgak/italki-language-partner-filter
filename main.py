import requests
import configparser
import time
import logging
import argparse

def get_partner(config):
    found = 0
    page = 1

    while True:
        # /api/partner?speak=&learn=&gender=&country=AF&city=&page=1&hl=en-us&i_token=1599892361gAAAAABfNN6J6NhPopyFFVUaPw1cQYI_kBWOyZFQ-pHcp-PyJzkE_f0vjEhCHts5rbwVRyX3OuLRmZQZgls1hROi7dkkDfFbr5OvXDaQfehS-b7EZWG2zESH8PirGyt0OCLcvnsOuvHVVCKuB1S8HIoqu2zqK02QhSt5TsyMr85Doir4An6YrFk%3D&i_device=10
        params={"learn": "russian", "i_device": "10", "i_token": config['TOKEN'], "page": page}
        logging.info(f"making requests with params {params}")
        r = requests.get(config['PARTNER_API'], params=params)

        # logging.info(r.text)

        for item in r.json()['data']:
            learning = []
            speaking = []

            for lang in item['language_obj_s']:
                if lang['is_learning']:
                    learning.append([lang['language'], lang['level']])
                else:
                    speaking.append([lang['language'], lang['level']])

            if len(speaking) > 2:
                # logging.info(f"{item['nickname']} speaks too many languages")
                continue

            if len(learning) > 2:
                # logging.info(f"{item['nickname']} learns too many languages")
                continue

            match = filter_spearking_lang(speaking)

            if match == False:
                # logging.info(f"{item['nickname']} is not a native english speaker")
                continue


            match = filter_learning_lang(learning)

            if match == False:
                logging.info(f"{item['nickname']} does not learn russian")
                continue

            logging.info(f"MATCH: {item['nickname']} -> {item['learning_language']} -> https://www.italki.com/user/{item['id']}")
            logging.info(f"learning: f{learning}, speaking: f{speaking}")
            found = found + 1

        if found >= int(config['LIMIT']):
            break

        page = page + 1

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
    parser.add_argument('-c', '--config', help="config file", default=".config")

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

    config = configparser.ConfigParser()
    config.read(args.config)
    default_section = config['default']

    get_partner(default_section)


if __name__ == "__main__":
    main()
