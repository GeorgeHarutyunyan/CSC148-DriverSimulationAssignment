"""
The rider module contains the Rider class. It also contains
constants that represent the status of the rider.

=== Constants ===
@type WAITING: str
    A constant used for the waiting rider status.
@type CANCELLED: str
    A constant used for the cancelled rider status.
@type SATISFIED: str
    A constant used for the satisfied rider status
"""

WAITING = "waiting"
CANCELLED = "cancelled"
SATISFIED = "satisfied"


class Rider:
    """
    Initialize a new rider
    """
    def __init__(self,identifier,origin,destination,status,patience):
        '''
        :param identifier: A riders identifier
        :param origin: Location
        :param destination: Location
        :param patience: Integer, the riders patience
        :return: None
        '''
        self.status = status
        self.identifier = identifier
        self.origin = origin
        self.destination = destination
        self.patience = patience


    def __str__(self):
        """
        A string representation of Rider
        :param: self: Rider
        :rtype: str
        """
        return self.identifier

