# Strava Explorer

## About

An app to analyze/visualize Strava (a social network for athletes) data.

Quick breakdown of the features:
- Explorer: creates a heatmap of your activities in various time range/heat criteria combinations;
- Leaderboards: shows all of your segment efforts for particular activity split by time ranges;
- Have I been there?: visualizes the frequency of your visits to specific locations based on uploaded GPX file. All of your acitivities are taken into account during the analysis. 

## Usage

Live version [here](http://139.59.157.188).

You have a choice to try the demo mode with some data prepopulated if you do not have a Strava account.

## How does it work?

Users are authenticated to Strava via OAuth. 

Bike data is pulled from Strava API.

"Have I been there?" feature utilizes a kdtree data structure for fast spatial indexing (as opposed to comparing each of the analyzed GPX coordinates against each other). 

## Technology stack

Backend: Python & Django
Frontend: vanilla JS

## Screenshots:
![Alt text](/screenshots/explorer2.png?raw=true)
![Alt text](/screenshots/explorer1.png?raw=true)
![Alt text](/screenshots/leaderboards.png?raw=true)
![Alt text](/screenshots/have_I_been_there.png?raw=true)
