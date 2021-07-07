"""Simulation Events

This file should contain all of the classes necessary to model the different
kinds of events in the simulation.
"""
from rider import Rider, WAITING, CANCELLED, SATISFIED
from dispatcher import Dispatcher
from driver import Driver
from location import deserialize_location
from monitor import Monitor, RIDER, DRIVER, REQUEST, CANCEL, PICKUP, DROPOFF


class Event:
    """An event.

    Events have an ordering that is based on the event timestamp: Events with
    older timestamps are less than those with newer timestamps.

    This class is abstract; subclasses must implement do().

    You may, if you wish, change the API of this class to add
    extra public methods or attributes. Make sure that anything
    you add makes sense for ALL events, and not just a particular
    event type.

    Document any such changes carefully!

    === Attributes ===
    @type timestamp: int
        A timestamp for this event.
    """

    def __init__(self, timestamp):
        """Initialize an Event with a given timestamp.

        @type self: Event
        @type timestamp: int
            A timestamp for this event.
            Precondition: must be a non-negative integer.
        @rtype: None

        >>> Event(7).timestamp
        7
        """
        self.timestamp = timestamp

    # The following six 'magic methods' are overridden to allow for easy
    # comparison of Event instances. All comparisons simply perform the
    # same comparison on the 'timestamp' attribute of the two events.
    def __eq__(self, other):
        """Return True iff this Event is equal to <other>.

        Two events are equal iff they have the same timestamp.

        @type self: Event
        @type other: Event
        @rtype: bool

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first == second
        False
        >>> second.timestamp = first.timestamp
        >>> first == second
        True
        """
        return self.timestamp == other.timestamp

    def __ne__(self, other):
        """Return True iff this Event is not equal to <other>.

        @type self: Event
        @type other: Event
        @rtype: bool

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first != second
        True
        >>> second.timestamp = first.timestamp
        >>> first != second
        False
        """
        return not self == other

    def __lt__(self, other):
        """Return True iff this Event is less than <other>.

        @type self: Event
        @type other: Event
        @rtype: bool

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first < second
        True
        >>> second < first
        False
        """
        return self.timestamp < other.timestamp

    def __le__(self, other):
        """Return True iff this Event is less than or equal to <other>.

        @type self: Event
        @type other: Event
        @rtype: bool

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first <= first
        True
        >>> first <= second
        True
        >>> second <= first
        False
        """
        return self.timestamp <= other.timestamp

    def __gt__(self, other):
        """Return True iff this Event is greater than <other>.

        @type self: Event
        @type other: Event
        @rtype: bool

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first > second
        False
        >>> second > first
        True
        """
        return not self <= other

    def __ge__(self, other):
        """Return True iff this Event is greater than or equal to <other>.

        @type self: Event
        @type other: Event
        @rtype: bool

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first >= first
        True
        >>> first >= second
        False
        >>> second >= first
        True
        """
        return not self < other

    def __str__(self):
        """Return a string representation of this event.

        @type self: Event
        @rtype: str
        """
        raise NotImplementedError("Implemented in a subclass")

    def do(self, dispatcher, monitor):
        """Do this Event.

        Update the state of the simulation, using the dispatcher, and any
        attributes according to the meaning of the event.

        Notify the monitor of any activities that have occurred during the
        event.

        Return a list of new events spawned by this event (making sure the
        timestamps are correct).

        Note: the "business logic" of what actually happens should not be
        handled in any Event classes.

        @type self: Event
        @type dispatcher: Dispatcher
        @type monitor: Monitor
        @rtype: list[Event]
        """
        raise NotImplementedError("Implemented in a subclass")


class RiderRequest(Event):
    """A rider requests a driver.

    === Attributes ===
    @type rider: Rider
        The rider.
    """

    def __init__(self, timestamp, rider):
        """Initialize a RiderRequest event.

        @type self: RiderRequest
        @type rider: Rider
        @rtype: None
        """
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher, monitor):
        """Assign the rider to a driver or add the rider to a waiting list.
        If the rider is assigned to a driver, the driver starts driving to
        the rider.

        Return a Cancellation event. If the rider is assigned to a driver,
        also return a Pickup event.

        @type self: RiderRequest
        @type dispatcher: Dispatcher
        @type monitor: Monitor
        @rtype: list[Event]
        """
        monitor.notify(self.timestamp, RIDER, REQUEST,self.rider.identifier, self.rider.origin)

        events = []
        driver = dispatcher.request_driver(self.rider)
        if driver is not None:
            travel_time = driver.start_drive(self.rider.origin)
            events.append(Pickup(self.timestamp + travel_time, self.rider, driver))
        events.append(Cancellation(self.timestamp + self.rider.patience, self.rider))
        return events

    def __str__(self):
        """Return a string representation of this event.

        @type self: RiderRequest
        @rtype: str
        """
        return "{} -- {}: Request a driver".format(self.timestamp, self.rider)

class DriverRequest(Event):
    """A driver requests a rider.

    === Attributes ===
    @type driver: Driver
        The driver.
    """

    def __init__(self, timestamp, driver):
        """Initialize a DriverRequest event.

        @type self: DriverRequest
        @type driver: Driver
        @rtype: None
        """
        super().__init__(timestamp)
        self.driver = driver

    def do(self, dispatcher, monitor):
        """Register the driver if this is the first request, and
        assign a rider to the driver if one is available.

        If a rider is available, return a Pickup event.

        @type self: DriverRequest
        @type dispatcher: Dispatcher
        @type monitor: Monitor
        @rtype: list[Event]
        """
        monitor.notify(self.timestamp,DRIVER,REQUEST,self.driver.identifier,self.driver.location)

        events = []
        rider = dispatcher.request_rider(self.driver)
        if rider is not None:
            self.driver.idle = False
            travel_time = self.driver.start_drive(rider.origin)
            events.append(Pickup(self.timestamp + travel_time,rider,self.driver))
        else:
            self.driver.idle = True
        return events

    def __str__(self):
        """Return a string representation of this event.

        @type self: DriverRequest
        @rtype: str
        """
        return "{} -- {}: Request a rider".format(self.timestamp, self.driver)


class Cancellation(Event):
    """
    A Riders cancels their request

     === Attributes ===
    @type rider: Rider
    """

    def __init__(self,timestamp,rider):
        """
        Initialize a ride cancel request

        :param: self: Cancellation
        :param rider: Rider
        :return: None
        """
        super().__init__(timestamp)
        self.rider = rider


    def do(self, dispatcher, monitor):
        """
        If a riders patience has run out, cancels the request. Although, if a rider is already satisfied, does nothing and also
        notifies the monitor of the event

        :param dispatcher: Dispatcher
        :param monitor: Monitor
        :param self: Cancellation
        :return: Empty list
        """
        if self.timestamp > self.rider.patience:
            if self.rider.status != SATISFIED:
                self.rider.status = CANCELLED
                monitor.notify(self.timestamp,RIDER,CANCEL,self.rider.identifier,self.rider.origin)
        return []

    def __str__(self):
        """
        A string representation of this event
        @type self: Cancellation
        @rtype str
        """
        return "{} -- {}: Cancel request".format(self.timestamp, self.rider)


class Pickup(Event):
    """
    Initializes a pickup event

    === Attributes ===
    @type rider: Rider
    A rider
    @type driver: Driver
    A driver
    """

    def __init__ (self,timestamp,rider,driver):
        """
        Initializes a pickup event

        :self: Pickup
        :return: None
        """
        super().__init__(timestamp)
        self.driver = driver
        self.rider = rider

    def do(self, dispatcher, monitor):
        """
        Notifies the monitor of the event, if a riders patience has not run out, schedules a pickup event at the time of the arrival
        and the driver begins driving to the riders location

        :param dispatcher: Dispatcher
        :param self: Pickup
        :param monitor: Monitor
        :return: list[Events]
        """
        events = []
        self.driver.location = self.rider.origin
        if self.rider.status == WAITING:
            if self.timestamp < self.rider.patience:
                self.driver.idle = False
                monitor.notify(self.timestamp,DRIVER,PICKUP,self.driver.identifier,self.driver.location)
                arrival_time = self.driver.start_ride(self.rider)
                events.append(Dropoff(self.timestamp+arrival_time,self.rider,self.driver))
                self.rider.status = SATISFIED

        elif self.rider.status == CANCELLED:
            self.driver.idle = True
            events.append(DriverRequest(self.timestamp,self.driver))

        return events

    def __str__(self):
        """
        A string representation of Pickup

        @type self: Pickup
        @rtype: str
        """
        return "{} -- {}: Pickup {}".format(self.timestamp,self.driver,self.rider)


class Dropoff(Event):
    """
    Initializes a dropoff event

    === Attributes ===
    @type rider: Rider
    A rider
    @type driver: Driver:
    A driver
    """


    def __init__(self,timestamp,rider,driver):
        """
        Initilizes a dropoff event

        :self: Dropoff
        :return: None
        """
        super().__init__(timestamp)
        self.rider = rider
        self.driver = driver


    def do(self, dispatcher, monitor):
        """
        Notifies the monitor of the event. Sets the riders status to satisfied and the driver begins a request
        for a new rider immediately.

        :param dispatcher: Dispatcher
        :param monitor: Monitor
        :param self: Dropoff
        :return: list[Events]
        """
        monitor.notify(self.timestamp,RIDER,DROPOFF,self.driver.identifier,self.driver.location)
        events = []
        self.driver.location = self.rider.destination
        self.rider.status = SATISFIED
        self.driver.idle = True
        events.append(DriverRequest(self.timestamp,self.driver))
        return events

    def __str__(self):
        """
        A string representation of Dropoff
        @type self: Dropoff
        :rtype: str
        """
        return "{} -- {}: Dropoff {}".format(self.timestamp,self.driver,self.rider)


def create_event_list(filename):
    """Return a list of Events based on raw list of events in <filename>.

    Precondition: the file stored at <filename> is in the format specified
    by the assignment handout.

    @param filename: str
        The name of a file that contains the list of events.
    @rtype: list[Event]
    """
    events = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            tokens = line.split()
            timestamp = int(tokens[0])
            event_type = tokens[1]
            identifier = tokens[2]
            location = deserialize_location(tokens[3])

            if event_type == "DriverRequest":
                speed = int(tokens[4])
                event = DriverRequest(timestamp,Driver(identifier,location,speed))
            elif event_type == "RiderRequest":
                destination = deserialize_location(tokens[4])
                patience = int(tokens[5])
                event = RiderRequest(timestamp,Rider(identifier,location,destination,WAITING,patience))

            events.append(event)

    return events
