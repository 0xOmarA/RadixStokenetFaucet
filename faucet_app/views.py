from django.http import HttpResponse, HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings
from typing import Dict, List
from tldextract import extract
from faucet_proj.faucet_option import FaucetOption
from faucet_app.models import FaucetRequest
from . import utils as script_utils
from faucet_proj import secrets
import radixlib as radix
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
                'message': 'It is required that the JSON string in the request body contain the `tweet_url` and `xrd_amount` keys.'
            },
            status = 400
        )

    # Getting the url that was sent in the request body and the amount of XRD
    # that was requested
    url: str = json_data['tweet_url']
    xrd_requested: float = float(json_data['xrd_amount'])

    # Getting the correct `FaucetOption` associated with the requested amount.
    matches: List[FaucetOption] = list(filter(lambda x: float(x.xrd_amount) == xrd_requested ,settings.FAUCET_OPTIONS))
    if not matches:
        return JsonResponse(
            data = {
                'error': 'Invalid XRD amount requested',
                'message': 'You have requested an amount of XRD which the system can not support.'
            },
            status = 400
        )
    
    faucet_option: FaucetOption = matches[0]

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
    try:
        tweet_info: dict = script_utils.load_tweet_info(tweet_id)
    except:
        return JsonResponse(
            data = {
                'error': 'Invalid Tweet',
                'message': 'You have provided a link to a tweet which seems to not be available. Is it possible that your account is private or that the tweet was deleted?'
            },
            status = 400
        )

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
                'message': f'Your account is too young to perform this action. We require that a twitter account be at least {settings.MINIMUM_ACCOUNT_AGE*30} days old before they can request XRD to their Stokenet address. Your account is currently {current_account_age.total_seconds() / 86400:.2f} days old.'
            },
            status = 400
        )

    # Check if there has been any requests made to this wallet address or from 
    # this twitter account where the cooldown has not expired yet.
    try:
        last_request_by_twitter_user: FaucetRequest = list(FaucetRequest.objects.all().filter(twitter_author_id = tweet_info['author_id']))
        if last_request_by_twitter_user and not last_request_by_twitter_user[-1].is_cooldown_over():
            return JsonResponse(
                data = {
                    'error': 'Twitter account is in cooldown',
                    'message': f'Your twitter account was recently used by the faucet to send XRD. You can make another request in: {last_request_by_twitter_user[-1].seconds_until_cooldown_ends() / 60:.2f} minutes.'
                },
                status = 400
            )
    except ObjectDoesNotExist:
        pass

    try:
        last_request_for_wallet_address: FaucetRequest = list(FaucetRequest.objects.all().filter(wallet_address = wallet_address))
        if last_request_for_wallet_address and not last_request_for_wallet_address[-1].is_cooldown_over():
            return JsonResponse(
                data = {
                    'error': 'Wallet address is in cooldown',
                    'message': f'The faucet has recently sent your wallet address XRD. You can make another request in: {last_request_for_wallet_address[-1].seconds_until_cooldown_ends() / 60:.2f} minutes.'
                },
                status = 400
            )
    except ObjectDoesNotExist:
        pass

    # Checking if this twitter author or wallet has been blacklisted from using the wallet service.
    if tweet_info['author_id'] in secrets.BLACKLISTED_TWITTER_AUTHORS or wallet_address in secrets.BLACKLISTED_WALLETS:
        return JsonResponse(
                data = {
                    'error': 'Blacklisted from service',
                    'message': f'You have been blacklisted from using this service due to the a number of violations. Please contact 0xOmarA on twitter to know more.'
                },
                status = 400
            )

    # If we get to this point here, it means that we can indeed send XRD to this wallet
    # address.
    try:
        wallet: radix.Wallet = settings.WALLET
        tx_id: str = wallet.build_sign_and_send_transaction(
            actions = (
                wallet.action_builder
                    .token_transfer(
                        from_account_address = wallet.address,
                        to_account_address = wallet_address,
                        transfer_amount = radix.derive.atto_from_xrd(faucet_option.xrd_amount),
                        token_rri = radix.constants.XRD_RRI['stokenet'],
                    )
            ),
            message_string = f"Here is {faucet_option.xrd_amount:.2f} XRD for your tweet: {tweet_id}",
            encrypt_for_address = wallet_address
        )
        
        FaucetRequest.objects.create(
            requested_at = timezone.now(),
            wallet_address = wallet_address,
            xrd_amount_requested = faucet_option.xrd_amount,
            cooldown_period_in_hours = faucet_option.cooldown_in_hours,
            tweet_id = tweet_id,
            tweet_link = url,
            twitter_author_id = tweet_info['author_id']
        )

        return JsonResponse({
            'success': True,
            'tx_id': tx_id,
            'message': f"The requested XRD have been sent in transaction: {tx_id}"
        })
    
    except Exception as e:
        return JsonResponse(
            data = {
                'error': 'Unexpected Error',
                'message': f'An unexpected error has occured. Error: {e}'
            },
            status = 500
        )

def wallet_balance(request: HttpRequest) -> HttpResponse:
    # Checking for requests and only allowing GET requests to the endpoint.
    if request.method != 'GET':
        return JsonResponse(
            data = {
                'error': 'Invalid Request Method',
                'message': 'This endpoint only accepts GET requests.'
            },
            status = 400
        )

    wallet: Radix.Wallet = settings.WALLET
    return JsonResponse({
            'success': True,
            'message': Radix.utils.atto_to_xrd(wallet.get_balance_of_token(Radix.NetworkSpecificConstants.XRD[Radix.Network.STOKENET]))
        })

def faucet_homepage(request: HttpRequest) -> HttpResponse:
    return render(
        request = request,
        template_name = 'home.html',
        context = {
            'faucet_options': settings.FAUCET_OPTIONS
        }
    )