# Proposal

## Section 1: Motivation and Purpose

Our role: The Data Analytics Department in a Marketing Research Company

Target audience: Movie Production Companies

Our customer is a movie production company and plan to produce several movies this year. If we could understand the profitability and popularity of movies in the past few years, it may help our customer to make decisions. To address this challenge, we propose to build a data visualization app that allows the investment managers to visually explore a dataset of movies to identify common factors. Our app will show the distribution of movie budget, revenue, profit and movie popularity by filtering different variables in order to compare factors that contribute to the trend of movies.

## Section 2: Description of the data

We will be visualizing a dataset of approximately 10,000 movies. Each movie has 21 associated variables that describe the basic information of the movie (`genres`, `runtime`, `release_date`), the financial status (`budget`, `revenue`), the staff (`casts`, `directors`, `production company`) associated in the movie, and the performance (`popularity`). Using this data we will also derive a new variable, which is the `gross_profit` that is calculated by revenue - budget.

## Section 3: Research and usage scenarios

J. Doe runs a start-up movie production company in North America. Due to the limited venture capital in the entertainment industry in 2020-2021, J. Doe want to ensure that he only selects profitable movies for production in his company. He wants to be able to explore a dataset in order to compare how different movie attributes are related to the gross profit. When J. Doe logs on to the “Movie Producer App”, he will see a heatmap describing the distribution of movie rating among different genres. Also, he can explore the distribution of budgets among different genres. There are some additional functions including in our app. For example, J. Doe can use “actor filter” to search possible actors for a specific genre with the similar range of budget. And he can use “Release Date Recommendation” to see what time is better to release the new movie for generating higher profit. He hypothesizes that action movie is the most profitable genre in the past few years and he plan to release it during summer time.
