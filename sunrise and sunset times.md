# Calculating Sunrise and Sunset Times


```python
import datetime as dt
from zoneinfo import ZoneInfo as tz
# from pytz import timezone
from skyfield import almanac
from skyfield.api import N, W, wgs84, load

import pyperclip as cb
```


```python
# Figure out local midnight.

# set our timezone
zone = tz('US/Central')
zone
```




    zoneinfo.ZoneInfo(key='US/Central')




```python
# grab the current time
now = dt.datetime.now(tz=zone)
now
```




    datetime.datetime(2021, 7, 16, 17, 47, 26, 661109, tzinfo=zoneinfo.ZoneInfo(key='US/Central'))




```python
# set time to midnight
midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
midnight
```




    datetime.datetime(2021, 7, 16, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='US/Central'))




```python
next_midnight = midnight + dt.timedelta(days=1)
next_midnight
```




    datetime.datetime(2021, 7, 17, 0, 0, tzinfo=zoneinfo.ZoneInfo(key='US/Central'))




```python
# now for the skyfield calculations
```


```python
ts = load.timescale()

# one whole day in format for skyfield
t0 = ts.from_datetime(midnight)
t1 = ts.from_datetime(next_midnight)
```


```python
# grab the ephemera, see docs for other ephemera
# ephemera choice affects load time
eph = load('de421.bsp')
```

    [#################################] 100% de421.bsp



```python
# home location (used google maps to get coords)
myhome = wgs84.latlon(30.2950 * N, 97.5559 * W)
```


```python
# use the almanac to load specific ephemera
f = almanac.dark_twilight_day(eph, myhome)
```


```python
# grab the events
times, events = almanac.find_discrete(t0, t1, f)
```


```python
# now print out in human readable form
previous_e = f(t0).item()
for t, e in zip(times, events):
    tstr = str(t.astimezone(zone))[:16]
    if previous_e < e:
        print(tstr, ' ', almanac.TWILIGHTS[e], 'starts')
    else:
        print(tstr, ' ', almanac.TWILIGHTS[previous_e], 'ends')
    previous_e = e
```

    2021-07-16 05:05   Astronomical twilight starts
    2021-07-16 05:40   Nautical twilight starts
    2021-07-16 06:12   Civil twilight starts
    2021-07-16 06:39   Day starts
    2021-07-16 20:32   Day ends
    2021-07-16 20:59   Civil twilight ends
    2021-07-16 21:32   Nautical twilight ends
    2021-07-16 22:06   Astronomical twilight ends



```python
# same as above but for UTC time

zone2 = tz('UTC')

previous_e = f(t0).item()
for t, e in zip(times, events):
    tstr = str(t.astimezone(zone2))[:16]
    if previous_e < e:
        print(tstr, ' ', almanac.TWILIGHTS[e], 'starts')
    else:
        print(tstr, ' ', almanac.TWILIGHTS[previous_e], 'ends')
    previous_e = e
```

    2021-07-16 10:05   Astronomical twilight starts
    2021-07-16 10:40   Nautical twilight starts
    2021-07-16 11:12   Civil twilight starts
    2021-07-16 11:39   Day starts
    2021-07-17 01:32   Day ends
    2021-07-17 01:59   Civil twilight ends
    2021-07-17 02:32   Nautical twilight ends
    2021-07-17 03:06   Astronomical twilight ends


### how to we grab specific times?

We need to figure out how the _skyfield_ `almanac` works.

[https://rhodesmill.org/skyfield/almanac.html]()



```python
# rising and setting times bounded by t0 and t1
# this doesn't account for refraction or vantage point
t, y = almanac.find_discrete(t0, t1,
                             almanac.sunrise_sunset(eph, myhome))
```


```python
print(t.utc_iso())

# 1=rising, 0=setting
print(y)
```

    ['2021-07-16T11:39:29Z', '2021-07-17T01:32:59Z']
    [1 0]


---
The results above are almost exactly what we want except for the formatting. We can use the `utc_strftime()` method to format the time using a formatting string.

The rammb-slider URL time is formatted like this:

```
st=20210214124604
et=20210215005604
```

the string format `'%Y%m%d%H%m%S'` will produce an equivalent time string that can be used with the rammb slider site.



```python
# formatted 2 element list for rise and set times
rise_set = t.utc_strftime('%Y%m%d%H%m%S')
rise_set
```




    ['20210716110729', '20210717010759']




```python
# rise and set times string formatted for rammb slider
rise_time = f'st={rise_set[0]}'
set_time = f'et={rise_set[1]}'
```




    'st=20210716110729'




```python
# url scheme list to generate an animated weather map
url_scheme = ['https://rammb-slider.cira.colostate.edu/?sat=goes-16',
              'z=3',
              'angle=0',
              'im=12',
              'ts=1',
              'st=20210214124604',
              'et=20210215005604',
              'speed=90',
              'motion=loop',
              'maps%5Bborders%5D=white',
              'lat=0',
              'opacity%5B0%5D=1',
              'hidden%5B0%5D=0',
              'pause=0',
              'slider=-1',
              'hide_controls=0',
              'mouse_draw=0',
              'follow_feature=0',
              'follow_hide=0',
              's=rammb-slider',
              'sec=conus',
              'p%5B0%5D=band_02',
              'x=2743.14697265625',
              'y=4909.352783203125']
```


```python
# replacing the start and end times with our custom values
url_scheme[5] = rise_time
url_scheme[6] = set_time

# checking the output on jupyter notebook
url_scheme
```




    ['https://rammb-slider.cira.colostate.edu/?sat=goes-16',
     'z=3',
     'angle=0',
     'im=12',
     'ts=1',
     'st=20210716110729',
     'et=20210717010759',
     'speed=90',
     'motion=loop',
     'maps%5Bborders%5D=white',
     'lat=0',
     'opacity%5B0%5D=1',
     'hidden%5B0%5D=0',
     'pause=0',
     'slider=-1',
     'hide_controls=0',
     'mouse_draw=0',
     'follow_feature=0',
     'follow_hide=0',
     's=rammb-slider',
     'sec=conus',
     'p%5B0%5D=band_02',
     'x=2743.14697265625',
     'y=4909.352783203125']




```python
# generating a url that we can use to create our animation
# pop the main URL stem so we can iterate through the rest
rammb_url = url_scheme.pop(0)

for url in url_scheme:
    rammb_url += '&' + url
    
rammb_url
```




    'https://rammb-slider.cira.colostate.edu/?sat=goes-16&z=3&angle=0&im=12&ts=1&st=20210716110729&et=20210717010759&speed=90&motion=loop&maps%5Bborders%5D=white&lat=0&opacity%5B0%5D=1&hidden%5B0%5D=0&pause=0&slider=-1&hide_controls=0&mouse_draw=0&follow_feature=0&follow_hide=0&s=rammb-slider&sec=conus&p%5B0%5D=band_02&x=2743.14697265625&y=4909.352783203125'




```python
# copy the url to clipboard to test on website
cb.copy(rammb_url)
```

## the code works...but

We still need a way to check to see whether the start and end times actually exist on the server. I believe there is a javascript function for this but don't recall what it's called.
