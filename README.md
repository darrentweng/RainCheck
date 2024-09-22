# Travel weather insurance

## Overview

It sucks to travel in bad weather, we learned that in our recent trip to Scandinavia. This calculator calculates the chance of weather related cancellation and unpleasant experience and calculate a fair price for cancellation. Retail hotels, event vendors, and travelers alike, all can benefit from this calculator.

A user (customer, hotel, etc...) can enter a location, date range, and insurance amount per day (hotel/cruise/event daily cost), and this calculator will calculate an insurance premium (price you charge/pay) based on the likelihood of a “bad” weather.

### How we did it

We use Streamlit to do this as provides both front-end and back-end capabilities, which is perfect for quick prototyping. We downloaded a sample 3-city, 18-years historical weather dataset from NOAA (https://www.ncdc.noaa.gov/cdo-web/).

We used mongodb Atlas to store the tabular data, and the Capital One "nessieisreal" API to simulate payments.

Since we only have 18 years of data, to reduce variance, we consider data from n (default:7) days before and after the selected date to calculate probability, which provides a more representative probability in our tests.

#### Smoothing / Statistical Details

In addition to pooling neighboring days, we also have the option to smooth historical weather timeseries data. This is especially beneficial for denoising data without considering an excessively large date range (like the former method), which can lose the significance of the particular date. Instead, we add an additional step of smoothing each yearly series of data. We can see that for ranges that are seasonally consistent, we see lower probabilities of bad weather, but for ranges that are seasonally inconsistent, we see higher probabilities of bad weather, illustrating its effectiveness on top of pooling. For instance, the probability of temperature falling in a 40-75 degree range in Philadelphia for October 21 decreases from 20.57% to 12.98% when a simple moving average is applied to it. However, for out-of-distribution ranges, such as 20-55 degrees, the probability increases from 88.76% to 93.70%.

This also adds more information to the model for a given outlier: if a day is twenty degrees colder than normal, both pooling and smoothing would moderate its effect on the prediction for the correct day, but with smoothing, its effect on the model is not binary based on if it is above or below the threshold as to count into the historicla percentages.

### Future Enhancements

- Add a button to submit the premium through http://api.nessieisreal.com/ to win "Capital One Finance Hack"
- Populate more data, both in terms of the locations, as well as going back more years
- Allow users to enter any location, and we will look up its atitute and longitute, then triangulate and interpolate, to derive the historical weather for any place
- In addition to high/low temperature and precipitation, we can add more weather parameters such as wind speed, snowfall, etc
- Use React to GUI that calls the Python backend
- Open up the online API to be used by places such as hotel websites

### Future Future Enhancements

We can continue developing the model to be able to price weather derivatives, Weather derivatives, which serve as financial instruments designed to mitigate the risks associated with weather variability, which can significantly impact various industries.

"Best Use of Statistics (SIG)"

## How To Run

Instructions should work for docker or podman:

## Development with Podman

```
podman build -t wc .
podman run -p 8501:8501 -p 8888:8888 --name wc -v %cd%:/home/streamlit wc
```

Use the following commands to interact with the containers

```
podman exec -it wc bash  // enter the container
podman exec wc pip install xxx // install package, or run other command
podman start -a wc // start the container with attach mode (if you want to see the stdout)
```


When launching the app, to intialize information for Nessie (Capital One's Hackathon API)