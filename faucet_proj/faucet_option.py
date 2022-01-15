from typing import Union


class FaucetOption():
    """ A simple implementation for an option to choose from when requesting Radix tokens """

    def __init__(
        self,
        xrd_amount: Union[int, float],
        cooldown_in_hours: Union[int, float]
    ) -> None:
        """
        Instantiates a new option for the faucet with the xrd_amount and the cooldown period
        
        # Arguments

        * `xrd_amount: Union[int, float]` - A float or an integer of the XRD amount to be sent
        in this option.
        * `cooldown_in_hours: Union[int, float]` - A float or an integer of the cooldown period
        (in hours) asociated with this option.
        """

        self.__xrd_amount: Union[int, float] = xrd_amount
        self.__cooldown_in_hours: Union[int, float] = cooldown_in_hours

    @property
    def xrd_amount(self) -> float:
        """ A getter method for the xrd_amount. """
        return float(self.__xrd_amount)

    @property
    def cooldown_in_hours(self) -> float:
        """ A getter method for the cooldown_in_hours. """
        return float(self.__cooldown_in_hours)

    def __str__(self) -> str:
        """ A string representation of this Option object """
        # return f"{self.xrd_amount} XRD ({self.cooldown_in_hours:.2f} hours cooldown)"
        return f"{int(self.xrd_amount)} XRD ({int(self.cooldown_in_hours)} hours cooldown)"