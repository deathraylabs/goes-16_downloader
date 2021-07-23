# Working with Time and Date


```python
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
```


```python
# our timezone
zone = ZoneInfo("America/Chicago")

print(zone.key)
```

    America/Chicago



```python
# adding time zone info to the current time
dt = datetime.now(tz=zone)
dt
```




    datetime.datetime(2021, 7, 16, 14, 23, 43, 886422, tzinfo=zoneinfo.ZoneInfo(key='America/Chicago'))




```python
# if these conditions are not None, then the object is _aware_
print(dt.tzinfo)
print(dt.tzinfo.utcoffset(aware))

print(dt.tzname())
```

    America/Chicago
    -1 day, 19:00:00
    CDT



```python
# specifying the timezone as UTC makes this object _aware_
aware = datetime.now(timezone.utc)
aware
```




    datetime.datetime(2021, 7, 16, 19, 23, 49, 130226, tzinfo=datetime.timezone.utc)




```python
# if these conditions are not None, then the object is _aware_
print(aware.tzinfo)
print(aware.tzinfo.utcoffset(aware))
```

    UTC
    0:00:00


---

The _datetime_ objects above are what is known as **aware** because they have information regarding the timezone and is handling calculations in the backend as UTC plus an offset.

The _datetime_ object below is **naive** because it doesn't contain timezone information and offset.

---


```python
naive = datetime.now()
naive
```




    datetime.datetime(2021, 7, 16, 14, 13, 44, 528062)




```python
# if these conditions are not None, then the object is _aware_
print(naive.tzinfo)
print(naive.tzinfo.utcoffset(naive))
```

    None



    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    /var/folders/3w/fq697j2j63n7hy8xq7vz9kvm0000gn/T/ipykernel_65434/3205517712.py in <module>
          1 # if these conditions are not None, then the object is _aware_
          2 print(naive.tzinfo)
    ----> 3 print(naive.tzinfo.utcoffset(naive))
    

    AttributeError: 'NoneType' object has no attribute 'utcoffset'



```python
# this method produces an _aware_ version of the now method
datetime.now(timezone.utc)
```




    datetime.datetime(2021, 7, 16, 19, 9, 31, 261344, tzinfo=datetime.timezone.utc)



The datetime object is considered _aware_ if the following two conditions are not null


```python
# returns a string representing the date and time
dt.ctime()
```




    'Fri Jul 16 13:44:59 2021'




```python
# returns a string representing time in the format specified
dt.strftime('year: %Y or %y, month: %m or %h, day: %d, hour: %H, minute: %M')
```




    'year: 2021 or 21, month: 07 or Jul, day: 16, hour: 13, minute: 44'


