from __future__ import annotations
import datetime as dt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import plotly.express as px
import plotly.io as pio

from state_of_the_ladder import specializations

#########################
#   Common Objects
#########################
class_colors = {
    'deathknight': '#C41E3A',
    'demonhunter': '#A330C9',
    'druid': '#FF7C0A',
    'evoker': '#33937F',
    'hunter': '#AAD372',
    'mage': '#3FC7EB',
    'monk': '#00FF98',
    'paladin': '#F48CBA',
    # 'priest': '#FFFFFF',
    'priest': '#D6CFC7',
    'rogue': '#FFF468',
    'shaman': '#0070DD',
    'warlock': '#8788EE',
    'warrior': '#C69B6D',
}

pattern_seq = ['/', '\\', '.']
spec_patterns = {}
spec_colors = {}
for class_, specs in specializations.items():
    for n, spec in enumerate(sorted(specs)):
        spec_patterns[class_ + '-' + spec] = pattern_seq[n]
        spec_colors[class_ + '-' + spec] = class_colors[class_]

healer_classes = [
    'priest-holy', 'priest-discipline', 'druid-restoration', 'evoker-preservation',
    'shaman-restoration', 'monk-mistweaver', 'paladin-holy'
]


#########################
#       Analysis
#########################
def load_state_of_the_ladder(day: dt.date) -> pd.DataFrame:
    all_ratings = pd.read_csv(f'state_of_the_ladder_{day}.csv')
    all_ratings['class-spec'] = all_ratings['class'] + '-' + all_ratings['spec']
    return all_ratings


def analyze_performance(all_ratings: pd.DataFrame) -> pd.DataFrame:
    performance = compute_rating_stats(all_ratings)
    performance['score'] = score_specs(performance)
    performance['tier'] = performance['score'].apply(grade)
    performance['tier_clust'] = cluster_ratings(performance)

    # Add healer flag
    performance['healer'] = False
    performance.loc[performance.index.isin(healer_classes), 'healer'] = True

    return performance.sort_values('score', ascending=False)


def compute_rating_stats(all_ratings: pd.DataFrame) -> pd.DataFrame:
    performance = pd.DataFrame({
        'num_rivals': count_above_tier(all_ratings, 1800),
        'num_duelists': count_above_tier(all_ratings, 2100),
        'num_gladiators': count_above_tier(all_ratings, 2400),
        'max_rating': all_ratings.groupby('class-spec')['rating'].max(),
        'mean_rating': all_ratings.groupby('class-spec')['rating'].mean(),
    })
    quantiles = (
        all_ratings.groupby('class-spec').quantile([0.5, 0.95, 0.99], numeric_only=True)
        .reset_index().pivot(index='class-spec', columns='level_1', values='rating')
    )
    quantiles.columns = quantiles.columns.astype(str)
    return performance.merge(quantiles, on='class-spec')


def count_above_tier(all_ratings: pd.DataFrame, threshold: int = 1800) -> pd.Series:
    return (
        all_ratings[all_ratings['rating'] > threshold]
        .groupby('class-spec')['rating'].count()
    )


def score_specs(performance: pd.DataFrame) -> pd.Series:
    return (
        1/3 * performance['0.5'] / performance['0.5'].max()
        + 1/3 * performance['0.95'] / performance['0.95'].max()
        + 1/3 * performance['0.99'] / performance['0.99'].max()
    )


def cluster_ratings(
    performance: pd.DataFrame, cluster_cols: list[str] = ['0.5', '0.95', '0.99']
) -> np.ndarray:
    clustering = AgglomerativeClustering(n_clusters=5)
    clustering.fit(performance[cluster_cols])
    return clustering.labels_.astype(str)


def grade(score: float) -> str:
    score = round(score, 2)
    if score >= 0.93:
        return 'S'
    elif score >= 0.86:
        return 'A'
    elif score >= 0.79:
        return 'B'
    elif score >= 0.72:
        return 'C'
    else:
        return 'D'


#########################
#       Plotting
#########################
def plot_rating_hist(all_ratings: pd.DataFrame, save: bool = False):
    fig = px.histogram(
        all_ratings,
        x='rating',
        barmode='overlay',
        color='class-spec',
        color_discrete_map=spec_colors,
        pattern_shape='class-spec',
        pattern_shape_map=spec_patterns,
        # marginal='rug',
        opacity=0.5,
    )

    fig.update_layout(width=1500, height=600)

    if save:
        pio.write_html(fig, 'state_of_the_ladder.html')
    fig.show()


def plot_performance_scatter3(
    performance: pd.DataFrame, x: str = '0.5', y: str = '0.95', z: str = '0.99',
    color: str = 'class-spec', save: bool = False
):
    fig = px.scatter_3d(
        performance.reset_index(),
        x=x, y=y, z=z,
        symbol='healer',
        color=color, color_discrete_map=spec_colors,
        hover_data=['score', 'class-spec', 'tier']
    )
    fig.update_layout(
        width=1200, height=800,
        scene=dict(
            aspectmode='manual',  # can be 'data', 'cube', 'auto', 'manual'
            aspectratio=dict(x=1, y=1, z=0.95)
        )
    )
    if save:
        pio.write_html(fig, 'performance_scatter3.html')
    fig.show()


def plot_tier_list(performance: pd.DataFrame, save: bool = False):
    fig = px.bar(
        performance.reset_index().sort_values('score'),
        y='tier', color='class-spec', color_discrete_map=spec_colors,
        hover_data=['tier', 'score', 'class-spec']
    )
    fig.update_layout(
        width=1200, height=600,
        showlegend=False,
    )
    if save:
        pio.write_html(fig, 'quantile_tier_list.html')
    fig.show()


if __name__ == '__main__':
    all_ratings = load_state_of_the_ladder(dt.date(2022, 12, 27))
    performance = analyze_performance(all_ratings)
    plot_rating_hist(all_ratings)
    plot_tier_list(performance)
    plot_performance_scatter3(performance)
