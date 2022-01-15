from django.utils import timezone
from django.db import models
import datetime

class FaucetRequest(models.Model):
    """ A class which defines a request which has been made to the faucet. """

    requested_at = models.DateTimeField(verbose_name = 'Requested At', default=timezone.now)
    wallet_address = models.CharField(verbose_name = 'Wallet Address', max_length = 128)
    xrd_amount_requested = models.FloatField(verbose_name = 'XRD Amount Requested')
    cooldown_period_in_hours = models.FloatField(verbose_name = 'Cooldown Period in Hours')
    tweet_id = models.IntegerField(verbose_name = 'Tweet ID')
    tweet_link = models.TextField(verbose_name = 'Tweet Link')
    twitter_author_id = models.IntegerField(verbose_name = 'ID of Twitter Author')

    def cooldown_until(self) -> datetime.datetime:
        """ This method is used to calculate when the cooldown is supposed to end for this request """
        return self.requested_at + datetime.timedelta(hours = self.cooldown_period_in_hours)

    def is_cooldown_over(self) -> bool:
        """ A method which tells us if the cooldown is over for this faucet request or not """
        return timezone.now() >= self.cooldown_until()

    def seconds_until_cooldown_ends(self) -> float:
        """ A method that returns the amount of time in seconds for the cooldown to end """
        return (self.cooldown_until() - timezone.now()).total_seconds()

    def seconds_since_request(self) -> float:
        """ A method which returns the remaining cooldown time in seconds """
        return (timezone.now() - self.requested_at).total_seconds()