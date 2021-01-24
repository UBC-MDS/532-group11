# Relection on Milestone2

## Apps Features 
Based on the Milestone 2 intructions and the proposal we wrote in Milestone 1, our target this week is to implement the dashboard with 4 plots. Here is the [link](https://moveymoney.herokuapp.com/) for the deployed app on Herokuapp.com.

The data visualization app contains a landing page with 4 key visualizations. The top left is a heatmap to see the distribution of ratings for a particular genre. The top right is a line plot to depict the average budget of a movie of a particular genre has changed over time. The bottom left is to present a actor suggestions based on genre and movie budget. 

In the proposal, we plan to make a scatter plot at bottom right to show the relationship between profit and release months for a specific genre, and add a tooltip to show the name of each movie. During the implementation process, we found it not intuitive to see the tendency, so we changed our plan and made a line plot to show the trend of profit among different month.

We also implemented two global filters on the top that we can filter the movies within a certain year range and select particular genres that users are interested in.

## Future Improvements and Additions

We'll unify the style of plots and filters. 

We would like to present the relationship between release month and profit for one particular genre at bottom right. Now it's hard to see the tendency for the genres with low profits. We might think about creating a "balloon plot" to replace it.