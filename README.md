# Travel weather insurance

## Overview
It sucks to travel in bad weather, just like our recent trip to Norway and Iceland. This calculator calculates the chance of weather related cancellation and unpleasant experience and calculate a fair price for cancellation. Retail hotels, event vandors, and travelers alike, all can benefit from this calculator. 

### How we do it

We use streamlit to do this as it's both front-end and back-end, which is perfect for quick prototyping. We downloaded a sample 3-city, 18-years historical weather data from NOAA (https://www.ncdc.noaa.gov/cdo-web/).

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