from driver import Driver
from rider import Rider
from location import manhattan_distance

class Dispatcher:
    """A dispatcher fulfills requests from riders and drivers for a
    ride-sharing service.

    When a rider requests a driver, the dispatcher assigns a driver to the
    rider. If no driver is available, the rider is placed on a waiting
    list for the next available driver. A rider that has not yet been
    picked up by a driver may cancel their request.

    When a driver requests a rider, the dispatcher assigns a rider from
    the waiting list to the driver. If there is no rider on the waiting list
    the dispatcher does nothing. Once a driver requests a rider, the driver
    is registered with the dispatcher, and will be used to fulfill future
    rider requests.
    """

    def __init__(self):
        """Initialize a Dispatcher.

        @type self: Dispatcher
        @rtype: None
        """
        self.rider_waiting_list = []
        self.available_drivers = []

    def __str__(self):
        """Return a string representation.

        @type self: Dispatcher
        @rtype: str
        """
        return "Dispatcher: Available Drivers: {}, Riders waiting: {}".format(len(self.available_drivers),len(self.rider_waiting_list))

    def request_driver(self, rider):
        """Return a driver for the rider, or None if no driver is available.

        Add the rider to the waiting list if there is no available driver.

        @type self: Dispatcher
        @type rider: Rider
        @rtype: Driver | None
        """
        if not self.available_drivers == []:
            closest_driver_integer = manhattan_distance(self.available_drivers[0].location,rider.origin)/self.available_drivers[0].speed
            closest_driver = self.available_drivers[0]
            for driver in self.available_drivers:
                if manhattan_distance(driver.location,rider.origin)/driver.speed < closest_driver_integer:
                    if driver.idle:
                        closest_driver = driver
            return closest_driver
        else:
            self.rider_waiting_list.append(rider)
            return None

    def request_rider(self, driver):
        """Return a rider for the driver, or None if no rider is available.

        If this is a new driver, register the driver for future rider requests.

        @type self: Dispatcher
        @type driver: Driver
        @rtype: Rider | None
        """
        if driver not in self.available_drivers:
            self.available_drivers.append(driver)
            if not self.rider_waiting_list == []:
                driver.idle = False
                return self.rider_waiting_list.pop(0)
            else:
                driver.idle = True
                return None
        else:
            if not self.rider_waiting_list == []:
                driver.idle = False
                return self.rider_waiting_list.pop(0)
            else:
                return None

    def cancel_ride(self, rider):
        """Cancel the ride for rider.

        @type self: Dispatcher
        @type rider: Rider
        @rtype: None
        """
        rider.status = "cancelled"
        self.rider_waiting_list.remove(rider)
