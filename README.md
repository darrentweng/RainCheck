# Travel weather insurance

## Overview
It sucks to travel in bad weather, just like our recent trip to Norway and Iceland. This calculator calculates the chance of weather related cancellation and unpleasant experience and calculate a fair price for cancellation. Retail hotels, event vandors, and travelers alike, all can benefit from this calculator. 

A user (customer, hotel, etc...) can enter a location, date range, and insurance amount per day (hotel/cruise/event daily cost), and this calculator will calculate an insurance premium (price you charge/pay) based on the likelihood of a “bad” weather.

### How we do it

We use streamlit to do this as it's both front-end and back-end, which is perfect for quick prototyping. We downloaded a sample 3-city, 18-years historical weatehr data from NOAA (https://www.ncdc.noaa.gov/cdo-web/).

Since we only have 18 years of data, to smooth it, we include data from n (default:7) days before and after the selected date, to calculate probability. This smoothing trick works well in our test.

### Future Enhancements

- Add a button to submit the premium through http://api.nessieisreal.com/ to win "Capital One Finance Hack"
- Populate more data, both in terms of the locations, as well as going back more years
- Allow users to enter any location, and we will look up its atitute and longitute, then triangulate and interpolate, to derive the historical weather for any place
- In addition to high/low temperature and precipitation, we can add more weather parameters such as wind speed, snowfall, etc
- Use React to GUI that calls the Python backend
- Open up the online API to be used by places such as hotel websites

### Future Future Enhancements

We can continue developing the model to be able to price weather derivatives, Weather derivatives, which serve as financial instruments designed to mitigate the risks associated with weather variability, which can significantly impact various industries.


"Best Use of Statistics (SIG)", 


## How To Run

Should work for docker or podman 

## Development with Podman
Run the following commands to build the dev docker image and run the container that use local files throughout development process:
```
podman build -t wc .
podman run -p 8501:8501 -p 8888:8888 --name wc -v %cd%:/home/streamlit wc
```
Use the following command to interactive with the containers
```
podman exec -it wc bash  // enter the container
podman exec wc pip install xxx // install package, or run other command
podman start -a wc // start the container with attach mode (if you want to see the stdout)
```