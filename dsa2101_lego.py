# -*- coding: utf-8 -*-
"""dsa2101_lego.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1s1kzP8xQ6dnWsT5vQ9FcrhaskKFqrb8h

# DSA2101 project LEGGO

## Introduction
### The LEGO dataset is a comprehensive collection of information containing various aspects of LEGO products. this emcompasses elements, colors, inventories, minifigures, parts, sets, themes and their relationships. There are 12 interrelated datasets that include details about LEGO products such as types of element, inventories of sets and parts and attributes of minifigures.

## Data cleaning and summary

### Cleaning: Our group has chosen to use data from the ‘inventory_parts’ ,’inventories’,’sets’ and ‘colors’ dataset to come up with the three visualisations in the following portion. In df1, we used left_join() to join the first two datasets (namely the inventory_parts and colors dataset) using their color_id and omitted the na values to keep the relevant rows only, then we used the select() to omit columns which were redundant and would not be required in the visualisations. The similar process was done to obtain df2 but this time the left_join was used to join df1 with an additional dataset(inventories),and repeated once more to get df3( by joining df2 to the final dataset we will use, which is the sets dataset)

### Summary: Upon analysis of our cleaned dataset, we found that there are 13509 unique sets across 436 distinct themes. There are 204 unique colours, and amidst this, the colour "Black" stands as the colour most frequently used, while "Duplo Medium Green" is the rarest. The LEGO sets span from 1949 to 2022, with the average number of parts hovering around 694. Interestingly, we also found that there are some sets with 0 parts. This suggests anomalies or inaccurate data collection.

## Question: How has colors in the Lego sets changed across the years?
"""

library(tidyverse)
colors = readr::read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-09-06/colors.csv.gz')
inventory_parts = readr::read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-09-06/inventory_parts.csv.gz')
inventories = readr::read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-09-06/inventories.csv.gz')
sets = readr::read_csv('https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-09-06/sets.csv.gz')

"""### Data Cleaning"""

part_colors = inventory_parts %>%
  left_join(colors, by = c("color_id" = "id")) %>%
  select(-is_spare, -img_url, -is_trans)

sum(is.na(part_colors)) #no missing values

part_colors_set = part_colors %>%
  left_join(inventories, by = c("inventory_id" = "id")) %>% #added "version" and "set_num"
  left_join(sets, by = "set_num", suffix = c("_color", "_set")) %>% #added "name_set" "year" "theme_id" "num_parts" "img_url"
  select(-version, -img_url)
head(part_colors_set)

"""### Summary Statistics"""

summary_stats = part_colors_set %>%
  summarise(
    num_of_uniq_themes = n_distinct(theme_id),
    num_of_uniq_sets = n_distinct(name_set),
    num_of_uniq_colors = n_distinct(color_id),
    least_color = names(which.min(table(name_color))),
    most_color = names(which.max(table(name_color))),
    year_range = paste(min(year, na.rm = TRUE), "-", max(year, na.rm = TRUE)),
    min_num_parts = min(num_parts, na.rm = TRUE),
    max_num_parts = max(num_parts, na.rm = TRUE),
    avg_num_parts = mean(num_parts, na.rm = TRUE)
  )
summary_stats

"""## Visualisations

### Scatter Plot
"""

# find most popular x colours from the entire data set
top_10_colors = part_colors_set %>%
  count(name_color, rgb) %>%
  arrange(desc(n)) %>%
  head(10)

top_10_colors_names = top_10_colors %>% pull(name_color)
top_10_colors_rgb = top_10_colors %>% arrange(name_color) %>% pull(rgb)

# df that contains the number of observations, for the above top 10 colours, for each year
data = part_colors_set %>%
  filter(name_color %in% top_10_colors_names) %>%
  count(year, name_color, wt = quantity)
head(data)

ggplot(data = data) +
  geom_point(aes(x = year, y = n, color = name_color)) +
  xlim(1980, 2022) +
  scale_color_manual(values = paste0("#", top_10_colors_rgb)) +
  geom_smooth(aes(x = year, y = n, color = name_color), se = FALSE, size = 0.5) +
  labs(x = "Year", y = "Count", title = "Distribution of the top 10 colors across the year") +
  theme(legend.position = "none")

"""For this scatterplot, our group has decided to focus on years after 1980 only, as the observations of those before 1980 were relatively small and cluttered, making it difficult to establish any meaningful relationships or trends. We  chose to focus on the top 10 most popular colors only for the same reasons.

This is a plot of count against time, with each data point representing the number of lego pieces of that color for a particular year. We added a LOESS curve for each color as well to make it easier for us to identify the general trends.

From the figure above, we can see a general increasing trend for all the colors, with Black being the all time most popular color, followed by the grays and white. Number of Light Gray legos increased from 1980 to 2000, before decreasing steeply and then later discontinued around 2007, while other colors such as Dark Bluish Gray, Light Bluish Gray and Reddish Brown were only introduced in the early 2000s. Another interesting observation would be that the most popular colors consist of mostly neutral colors such as monochromatic shades of black and primary colors.

###Line Plot
"""

# line plot: unique colours against time
num_unique_year = part_colors_set %>%
  distinct(name_color, year) %>%
  na.omit() %>%
  count(year)
head(num_unique_year)

ggplot(data = num_unique_year, aes(x = year, y = n)) +
  geom_line() +
  geom_point(color = "red", size = 1.2) +
  scale_x_continuous(breaks = seq(1940, 2023, 10)) +
  labs(title = "Unique Colours in Lego Sets",
       subtitle = "Yearly number of unique colours from 1949 to 2022",
       x = "Year", y = "Number of Unique Colours")

# do Exploratory Data Analysis to investigate peak in 1963
part_colors_set %>%
  filter(year == 1963) %>%
  distinct(name_color)
# many "Modulex" colour

color_id_year_range = part_colors_set %>%
  group_by(color_id) %>%
  summarise(year_range = paste(min(year, na.rm = TRUE), "-", max(year, na.rm = TRUE)))

color_id_life_span = color_id_year_range %>%
  separate(year_range, into = c("start_year", "end_year"), convert = TRUE ) %>%
  mutate(lifespan = `end_year` - `start_year` + 1 ) %>%
  arrange(lifespan) %>%
  select(color_id, start_year, end_year, lifespan)

color_theme_life_span = color_id_life_span %>%
  left_join(colors, by = c("color_id"="id")) %>%
  mutate(name = reorder(name, desc(lifespan))) %>%
  mutate(rgb = paste0("#", rgb))


ggplot(color_theme_life_span, aes(x = name, y = start_year)) +
  geom_segment(aes(xend = name, y = start_year, yend = end_year, color = I(rgb))) +
  geom_point(shape = ".", aes(color = I(rgb))) +
  coord_flip() +
  labs(title = "Life Span of Colours in Lego Dataset over the years",
       x = "Colours", y = "Years") +
  theme_minimal() +
  theme(axis.text.y = element_blank(),
        axis.ticks.y = element_blank())

"""For this line segment plot, we decided to look at the lifespan of the colors in the lego data set over the years from 1949 to 2022. For each color, we determined the year it was introduced to the end of its existence. From the plot, it is clear that even though the number of colors introduced over time has increased, the lifespan of the colors introduced later became shorter. The "Vintage" colors such as Black, White, Red, Yellow, Green, Blue were introduced as the first few lego colors and were kept.

From the plot, it shows an increase in the number of colours at the start of early 2000s however a sudden decrease after a few years around 2007.

### Visualisation Finding
#### useful link: https://groovyhistory.com/lego-modulex-architect-bricks-1963/4 (Modulex, a company under Lego, started then)
#### talk about trend from 2000 to 2010 too
"""



"""## Discussions

## References
### Georgios Karamanis. (2022). LEGO dataset [Data set]. TidyTuesday. https://github.com/rfordatascience/tidytuesday/tree/master/data/2022/2022-09-06
"""

# line plot: unique colours against time
num_unique_year = part_colors_set %>%
  mutate(rgb = paste0("#", rgb)) %>%
  distinct(name_color, rgb, year)
num_unique_year

all_rbg = num_unique_year$rgb
names(all_rbg) = all_rbg

num_unique_year %>%
  ggplot(aes(x=year, fill = I(rgb)))+
  geom_bar()
# +
  # ggplot(aes(x = year, fill = rgb)) +
  # scale_fill_manual(values = all_rbg)