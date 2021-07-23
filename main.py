#! /Users/peej/.conda/envs/py39/bin/python3

"""Collection of functions to make generating time-lapse sat imagery easier
to create.

Keyword Args:
    sys.argv[1] (int): formatted date 'YYYYMMDD'

"""

import sys
# ---for working with time--- #
import datetime as dt
from zoneinfo import ZoneInfo as tz
# from pytz import timezone
from skyfield import almanac
from skyfield.api import N, W, wgs84, load
# working with html requests #
import requests
import json
# ---exporting to useful form--- #
import pyperclip as cb

# rammb-slider options and typical values
typical_options_dict = {
    'base':              'https://rammb-slider.cira.colostate.edu/?',
    'sat':               'goes-16',
    'z':                 '3',
    'angle':             '0',
    'im':                '12',
    'ts':                '1',
    'st':                '20210214124604',
    'et':                '20210215005604',
    'speed':             '90',
    'motion':            'loop',
    'maps%5Bborders%5D': 'white',
    'lat':               '0',
    'opacity%5B0%5D':    '1',
    'hidden%5B0%5D':     '0',
    'pause':             '0',
    'slider':            '-1',
    'hide_controls':     '0',
    'mouse_draw':        '0',
    'follow_feature':    '0',
    'follow_hide':       '0',
    's':                 'rammb-slider',
    'sec':               'conus',
    'p%5B0%5D':          'band_02',
    'x':                 '2743.14697265625',
    'y':                 '4909.352783203125'
}


def get_sunrise_sunset_times(date='today'):
    """helper function to get sunrise and sunset times for the date specified

    Be aware of the following:

    - This function assumes we are located in the Central Time Zone.
    - This function assumes our location is at my home

    Args:
        date (str): date string as 'YYYYMMDD' or 'today'

    Returns:
        riseAndSet (list): rise and set time as a list

    Notes:
        The rammb-slider URL time is formatted like this:

            st=20210214124604
            et=20210215005604

        the string format `'%Y%m%d%H%m%S'` will produce an equivalent time
        string that can be used with the rammb slider site.
    """
    # Figure out local midnight.

    # set our timezone
    zone = tz('US/Central')

    # get today's date if that's what we want
    if date == 'today':
        now = dt.datetime.now(tz=zone)
    else:
        #todo: could use error correction
        now = dt.datetime.strptime(date, '%Y%m%d')
        now = now.replace(tzinfo=zone)

    # todo: how do I put debugging statements in the code?

    # get midnight to midnight times
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_midnight = midnight + dt.timedelta(days=1)

    # --- skyfield calculations --- #

    ts = load.timescale()

    # one whole day in format for skyfield
    t0 = ts.from_datetime(midnight)
    t1 = ts.from_datetime(next_midnight)

    # grab the ephemera, see docs for other ephemera
    # ephemera choice affects load time
    eph = load('de421.bsp')

    # home location (used google maps to get coords)
    myhome = wgs84.latlon(30.2950 * N, 97.5559 * W)

    # use the almanac to load specific ephemera
    f = almanac.dark_twilight_day(eph, myhome)

    # these are the events that include sunrise/set/twighlight
    times, events = almanac.find_discrete(t0, t1, f)

    # todo: format this in a way that makes more sense
    # now print out in human readable form
    previous_e = f(t0).item()
    for t, e in zip(times, events):
        tstr = str(t.astimezone(zone))[:16]
        if previous_e < e:
            print(tstr, ' ', almanac.TWILIGHTS[e], 'starts')
        else:
            print(tstr, ' ', almanac.TWILIGHTS[previous_e], 'ends')
        previous_e = e

    # rising and setting times bounded by t0 and t1
    # this doesn't account for refraction or vantage point
    t, y = almanac.find_discrete(t0, t1,
                                 almanac.sunrise_sunset(eph, myhome))

    # formatted 2 element list for rise and set times
    rise_set = t.utc_strftime('%Y%m%d%H%m%S')

    # # rise and set times string formatted for rammb slider in UTC time
    # rise_time = f'st={rise_set[0]}'
    # set_time = f'et={rise_set[1]}'

    return rise_set


def get_available_times_for_date(date,
                                 section="conus",
                                 product="geocolor"):
    """Given a properly formatted date, this function will request a json
    file containing the timestamps of available sat photos

    Args:
        date (str): date formatted string as YYYYMMDD
        hour (str): the hour of requested photo 'HH'
        minute (str): the minute we would like 'mm' (but might not be present)
                          defaults to first available
        section (str): map section we are requesting
                       - "full_disk": full view of earth
                       - "conus"    : view of continental US

    Returns:
        available_times (dict): dict containing timestamps of available photos
            keys (str): 'HH' formatted hour
            values (str): list of 'YYYYMMDDHHmmss' equally spaced timestamps
    """
    # this url will fetch the data we're after
    request_url = f'https://rammb-slider.cira.colostate.edu/data/json/goes-16' \
                  f'/{section}/{product}/{date}_by_hour.json'

    # get the raw bytestring json response with date-time data
    response = requests.get(request_url)

    # convert the bytestring response to a dict we can use
    date_times_json = json.loads(response.content)

    # the top level has only one item, it contains date-times
    available_times = date_times_json['timestamps_int']
    print(f'{len(available_times.keys())} hours with recorded photos')

    return available_times


def get_closest_photo_timestamp(available_times, desired_time):
    """Find the timestamp closest to our desired time

    Args:
        available_times (dict): key: hour str, value: list of times
        desired_time (str): formatted date/time 'YYYYMMDDhhmmss'

    Returns:
        timestamp (str): photo shot at closest available time
    """

    desired_hour = desired_time[-6:-4]

    # timestamps for photos available during the desired hour
    available_photos = available_times[desired_hour]

    desired_minute = int(desired_time[-4:-2])
    timestamp = available_photos[0]
    for time in available_photos:
        available_minute = int(str(time)[-4:-2])
        current_minute = int(str(timestamp)[-4:-2])
        if abs(desired_minute - available_minute) < abs(desired_minute -
                                                        current_minute):
            timestamp = time

        # debugging
        print(f'desired minute:   {desired_minute}\n'
              f'available minute: {available_minute}\n'
              f'current minute:   {current_minute}\n')

    print(f'I think {timestamp} is the closest time.\n---')

    return timestamp


def generate_url(url_dict):
    """Helper function to assemble the URL request string

    Args:
        url_dict (dict): key/value pairs that make up the URL request string

    Returns:
        url_request (str): formatted string to get sat image timelapse
    """

    # start the url string with the base address
    rammb_url = url_dict.pop('base')

    # assemble the formatted url
    for key, value in url_dict.items():
        rammb_url += f'{key}={value}&'

    # remove the extraneous final ampersand added in the last step
    rammb_url = rammb_url[:-1]

    print(f'The generated URL string is:\n\n{rammb_url}')

    return rammb_url


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # check to see if user passed date in command line
    try:
        # user input date to use for time-lapse
        desired_date = str(sys.argv[1])
    except IndexError:
        # default to today if user doesn't input a date
        desired_date = 'today'

    # get the sunrise and sunset times for the date
    riseandset = get_sunrise_sunset_times(date=desired_date)
    print(riseandset)

    # we need the sunrise data to generate our URL
    sunrise = riseandset[0]
    sunrise_date = sunrise[:-6]
    # print(f'the sunrise date is {sunrise_date}')

    # these are the times that sat photos are available
    times_available = get_available_times_for_date(sunrise_date)
    start_time = str(get_closest_photo_timestamp(times_available, sunrise))

    sunset = riseandset[1]
    sunset_date = sunset[:-6]

    times_available = get_available_times_for_date(sunset_date)
    end_time = str(get_closest_photo_timestamp(times_available, sunset))

    # we need to change the typical options dict to match our generated times
    typical_options_dict['st'] = start_time
    typical_options_dict['et'] = end_time

    # generated url
    url = generate_url(url_dict=typical_options_dict)
    # copies the generated url to clipboard for pasting into browser
    cb.copy(url)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
