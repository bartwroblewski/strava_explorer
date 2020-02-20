# Strava Explorer

An app to analyze/visualize Strava (a social network for athletes) data.

Users are authorized via OAuth. Data is pulled from Strava API.

Live version [here](http://139.59.157.188) (you can try the demo mode if you do not have a Strava account).

Here's a quick breakdown of the features:
- Explorer: creates a heatmap of your activities in various time range/heat criteria combinations;
- Leaderboards: Strava does not natively offer a quick way of seeing all of your segment efforts for particular activity split by time ranges, so here it is!;
- Have I been there?: upload any GPX file and visualize the frequency of your visits to specific places. All of your acitivities are taken into account during the analysis. A kdtree structure is used for fast spatial indexing (as opposed to comparing each of the analyzed GPX coordinates against each other). 

## Screenshots:
![Alt text](/screenshots/explorer1.png?raw=true)
![Alt text](/screenshots/explorer1.png?raw=true)
![Alt text](/screenshots/leaderboards.png?raw=true)
![Alt text](/screenshots/have_I_been_there.png?raw=true)
