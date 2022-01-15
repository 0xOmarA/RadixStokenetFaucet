from typing import Dict, Optional, Union, List
from faucet_proj import secrets
import dateparser
import validators
import requests
import re

def load_tweet_info(tweet_id: Union[int, str]) -> dict:
    """
    This method is used to load the information for a given tweet through the twitter
    API and the bearer token saved in the secrets.py file.

    # Arguments

    * `tweet_id: Union[int, str]` - An integer of the tweet id

    # Returns

    * `dict` - A dictionary containing the information of this given tweet. 

    # Raises

    * `Exception` - A generic exception is raised if an error is encountered when we query
    the API for the tweet's information.
    """

    # Making the request to the twitter API for the information that we need
    response: requests.Response = requests.get(
        url = f"https://api.twitter.com/2/tweets/{tweet_id}",
        headers = {
            "Authorization": f"Bearer {secrets.twitter_bearer_token}"
        },
        params = {
            "tweet.fields": ",".join(["created_at", "author_id"]),
            "expansions": ",".join(["author_id"]),
            "user.fields": ",".join(["created_at"]),
        }
    )

    response_json: dict = response.json()

    # Checking if there had been an error when retrieving the information for
    # this tweet. If there had been, we throw a generic `Exception`. We need to
    # check for errors using the 'error' key in the json response because the 
    # status code returned from the twitter API is 200 even if the tweet is not
    # found.
    if 'errors' in response_json.keys():
        raise Exception(f"An error has occured while getting the information of the tweet. Error: {response_json}")

    user_object: Dict[str, str] = list(filter(lambda x: x['id'] == response_json['data']['author_id'], response_json['includes']['users']))[0]
    
    return {
        "author_id": int(user_object['id']),
        "username": user_object['username'],
        "name_of_user": user_object['name'],
        "tweet_id": int(response_json['data']['id']),
        "tweet_text": response_json['data']['text'],
        "tweet_created_at": dateparser.parse(response_json['data']['created_at']),
        "user_created_at": dateparser.parse(user_object['created_at']),
    }

def extract_tweet_id(string: str) -> Optional[int]:
    """
    This method is used to search for the tweet id in a given string and return it.

    # Arguments

    * `string: str` - A string to look for the tweet id in.

    # Returns

    * `Optional[int]` - Returns an integer of the tweet id when it is found. If it's not 
    found then None is returned.
    """

    matches: list = list(map(int, re.findall(r'twitter\.com\/.*\/status(?:es)?\/([^\/\?]+)', string)))
    return None if not matches else matches[0]

def extract_stokenet_addresses(string: str) -> List[str]:
    """
    A method which is used to extract all of the stokenet addresses from a given string

    # Arguments

    * `string: str` - The string to look for the testnet addresses in.

    # Returns

    * `List[str]` - A list of strings of the stokenet addresses found in the string
    """

    return re.findall(
        pattern = r'(tdx[0-9]?1[023456789ACDEFGHJKLMNPQRSTUVWXYZacdefghjklmnpqrstuvwxyz]{6,69})',
        string = string
    )

def is_valid_url(string: str) -> bool:
    """
    A simple method which checks if a given string is a valid url or not.

    # Arguments

    * `string: str` - A string of the potential url.

    # Returns

    * `bool` - A boolean of whether the given url is a valid url or not.
    """

    return bool(validators.url(string))