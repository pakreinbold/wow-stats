# WoWStats

Contained here is a notebook investigating the effect of different factors in performance in World of Warcraft's competitive Player vs Player (PvP) game mode. Namely, how the 3v3 rating depends on player class and equipment quality.

# Analyzing Solo Shuffle
Contained in `solo-shuffle/`, you can analyze the state of the solo-shuffle ladders. First, run `state_of_the_ladder.py` in order to scrape the ratings from the WoW website. Then run `analysis.py`, either directly or using its functions independently, to analyze the solo-shuffle ratings. Analysis includes:
1. Rating Histgram
2. Data-driven Tier List(s)
3. 3D Statistics Visualizations

![Quantile Tier List](/solo-shuffle/quantile_tier_list.html)