from typing import Optional
from pydantic import conint
from pyconduit import Category
from pyconduit import block
import datetime
import time

class Time(Category):
    """
    Blocks to manage time and date. 
    """

    @block
    @staticmethod
    def timezone(
        *,
        hours : Optional[conint(ge = -23, le = 23)] = None,
        minutes : Optional[conint(ge = -59, le = 59)] = None
    ) -> datetime.timezone:
        """
        Creates a custom timezone on given parameters. If both hours and minutes not provided,
        it equals to UTC. If None provided, it will be same as 0 (zero).

        Args:
            hours:
                The hour offset from UTC, allowed minimum and maximum value is: -23 and 23. (Default: None)
            minutes:
                The minute offset from UTC, allowed minimum and maximum value is: -59 and 59. (Default: None)

        Returns:
            A timezone object that can be used in other Time blocks.
        """
        return datetime.timezone(None if not (hours and minutes) else datetime.timedelta(hours = hours or 0, minutes = minutes or 0))


    @block
    @staticmethod
    def now() -> datetime.datetime:
        """
        Gets the current time in UTC.

        Returns:
            Created datetime object.
        """
        return datetime.datetime.utcfromtimestamp(time.time())


    @block
    @staticmethod
    def now_timezone(
        *,
        timezone : Optional[datetime.timezone]
    ) -> datetime.datetime:
        """
        Gets the current time with given timezone.

        Args:
            timezone:
                A timezone object.

        Returns:
            Created datetime object.
        """
        return datetime.datetime.fromtimestamp(time.time(), timezone)

    
    @block
    @staticmethod
    def now_seconds() -> int:
        """
        Returns seconds since the epoch.

        Returns:
            A number.
        """
        return time.time()

    
    @block
    @staticmethod
    def create_datetime(
        *,
        year : int,
        month : int,
        day : int,
        hour : Optional[int] = None,
        minute : Optional[int] = None,
        second : Optional[int] = None,
        timezone : Optional[datetime.timezone] = None
    ) -> datetime.datetime:
        """
        Creates a new datetime. `year`, `month` and `day` is required, but others are optional.

        Args:
            year:
                Year of datetime. (1-9999)
            month:
                Month of datetime. (1-12)
            day:
                Day of datetime. (1-31)
            hour:
                Hour of datetime. (0-23) Defaults to None.
            minute:
                Minute of datetime. (0-59) Defaults to None.
            second:
                Second of datetime. (0-59) Defaults to None.
            timezone:
                Timezone for datetime. If not provided, it will be set to UTC. Defaults to None.
        
        Returns:
            Created datetime object.
        """
        return datetime.datetime(year, month, day, hour, minute, second, tzinfo = timezone or datetime.timezone.utc)

    
    @block
    @staticmethod
    def year(*, dt : datetime.datetime) -> int:
        """
        Gets year (1-9999) from a datetime object.

        Args:
            dt:
                A datetime object.

        Returns:
            A number.
        """
        return dt.year


    @block
    @staticmethod
    def month(*, dt : datetime.datetime) -> int:
        """
        Gets month (1-12) from a datetime object.

        Args:
            dt:
                A datetime object.

        Returns:
            A number.
        """
        return dt.month


    @block
    @staticmethod
    def day(*, dt : datetime.datetime) -> int:
        """
        Gets day (1-31) from a datetime object.

        Args:
            dt:
                A datetime object.

        Returns:
            A number.
        """
        return dt.day

    
    @block
    @staticmethod
    def hour(*, dt : datetime.datetime) -> int:
        """
        Gets hour (0-23) from a datetime object.

        Args:
            dt:
                A datetime object.

        Returns:
            A number.
        """
        return dt.hour

    
    @block
    @staticmethod
    def minute(*, dt : datetime.datetime) -> int:
        """
        Gets minute (0-59) from a datetime object.

        Args:
            dt:
                A datetime object.

        Returns:
            A number.
        """
        return dt.minute

    
    @block
    @staticmethod
    def second(*, dt : datetime.datetime) -> int:
        """
        Gets second (0-59) from a datetime object.

        Args:
            dt:
                A datetime object.

        Returns:
            A number.
        """
        return dt.second
