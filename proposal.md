# Proposal

## Section 1: Motivation and Purpose

Our role: The Data Analytics Department in a Market Research Company

Target audience: Movie Production Companies

Our customer is a movie production company and plan to produce several movies this year. If we could understand the profitability and popularity of movies in the past few years, it may help our customer to make decisions. To address this question, we propose to build a data visualization app that allows the investment managers in a production company to visually explore a dataset of movies to identify common factors. Our app will show the distribution of movie budgets, revenue, profits, and popularity across different variables in order to help identify factors that contribute to these key aspects.

## Section 2: Description of the data

We will be visualizing a dataset of approximately 10,000 movies. Each movie has 21 associated variables that describe the basic information of the movie (`genres`, `runtime`, `release_date`), the financial status (`budget`, `revenue`), the staff (`casts`, `directors`, `production company`), and the performance (`popularity`) associated with each movie. Using this data we will also derive a new variable, which is the `gross_profit` that is calculated using the simple expression profit = revenue - budget.

## Section 3: Research and usage scenarios

J. Lambert runs a start-up movie production company in North America. Due to the limited venture capital in the entertainment industry in 2020-2021, J. Lambert wants to ensure that he only selects profitable movies for production in his company. He wants to be able to explore a dataset in order to compare how different movie attributes are related to the gross profit. When J. Lambert logs on to the “Movie Producer App”, he will see a heatmap showing the distribution of movie rating across different genres. Also, he can compare movie budgets across different genres and years. There are some additional functions included in our app. For example, J. Lambert can use “actor filter” to see a list of suggested actors for a specific genre and based on a specified budget range. Finally, he can use “Release Date Recommendation” to see what time of the year it might be best to release a new movie for the purpose of generating higher profit. He hypothesizes that action movie is the most profitable genre in the past few years and he plan to release it during summer time.
