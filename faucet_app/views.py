from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from typing import Dict, List
from tldextract import extract
from . import utils as script_utils
import datetime
import json

@csrf_exempt
def xrd_request(request: HttpRequest) -> HttpResponse:
    # Checking for requests and only allowing post requests to the endpoint.
    if request.method != 'POST':
        return JsonResponse(
            data = {
                'error': 'Invalid Request Method',
                'message': 'This endpoint only accepts POST requests.'
            },
            status = 400
        )

    # Ensure that the POST request contains valid JSON in the request body and
    # that the 'tweet_url' key is present.
    try:
        json_data: Dict[str, str] = json.loads(request.body.decode())
    except:
        return JsonResponse(
            data = {
                'error': 'Request body is not JSON serializable',
                'message': 'The data included in the body of the request was not JSON serializable.'
            },
            status = 400
        )

    if 'tweet_url' not in json_data.keys() or 'xrd_amount' not in json_data.keys():
        return JsonResponse(
            data = {
                'error': 'Required keys not found',
                'message': 'It is required that the JSON string in the request body contain the tweet_url and xrd_amount keys.'
            },
            status = 400
        )

    # Getting the url that was sent in the request body
    url: str = json_data['tweet_url']

    # Ensure that the url provided is a valid url and that the domain that
    # the url points to is the twitter domain
    if not script_utils.is_valid_url(url) or extract(url).domain.lower() != 'twitter':
        return JsonResponse(
            data = {
                'error': 'Invalid URL',
                'message': 'An invalid URL was passed in the `tweet_url` parameter of the requests body'
            },
            status = 400
        )

    # Getting the tweet id and then getting the tweet's information
    tweet_id: int = script_utils.extract_tweet_id(url)
    tweet_info: dict = script_utils.load_tweet_info(tweet_id)

    # Getting the addresses included in the body of the tweet. 
    radix_addresses: List[str] = script_utils.extract_stokenet_addresses(tweet_info['tweet_text'])
    
    if not radix_addresses:
        return JsonResponse(
            data = {
                'error': 'No valid addresses',
                'message': 'Your tweet does not include a valid Stokenet wallet address. Are you sure that you included that in your tweet?'
            },
            status = 400
        )
    
    if len(radix_addresses) > 1:
        return JsonResponse(
            data = {
                'error': 'More than 1 address was provided',
                'message': 'Your tweet included more than 1 Stokenet wallet address which is not allowed.'
            },
            status = 400
        )

    wallet_address: str = radix_addresses[0]

    # Ensuring that the twitter account is of enough age.
    min_account_age: datetime.timedelta = datetime.timedelta(days = 30*settings.MINIMUM_ACCOUNT_AGE)
    current_account_age: datetime.timedelta = (timezone.now() - tweet_info['user_created_at'])

    if current_account_age < min_account_age:
        return JsonResponse(
            data = {
                'error': 'Twitter account is too young.',
                'message': f'Your account is too young to perform this action. We require that a twitter account be at least {settings.MINIMUM_ACCOUNT_AGE*30} days old before they can request XRD to their Stokenet address. Your account is currently {current_account_age.total_seconds() / 86400: .2f} days old.'
            },
            status = 400
        )

    # Check if there has been any requests made to this wallet address or from 
    # this twitter account where the cooldown has not expired yet.

    return HttpResponse('hey')

# TODO: Implement CSRF tokens for the xrd_request endpoint.