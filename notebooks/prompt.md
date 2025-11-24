1. Geographical Heatmap

2. Time series chart::
   For time-series sales chart, we want to annotate the policy to identify what policy causes the surge growth of coming years. The output is a chart alike #output/ev_dual_axis_chart_recent.png. For example of China sales we observed a huge surge from 2019 sales, which then we suspect previous policy might affect the boost of sales in concurrent year. As a data visualization experts which excels at telling users stories and deliver good quality time-series chart with clear labels and assessbility checks. Update current chart to not apply log scale and notice how each growth in market then annoate possible policy that led to EV growth (e.g. China National Legislation NEVs are exempted from China's annual vehicle and vessel tax 2018 Taxation China, State Taxation Administration)

3. Sunburst Pie Chart:
   As a data visualization expert, help me integrates the goal with context below:
   For our sunburst pie chart to sumarrize and highlight the top 3 largest market for EV globally, we want to include the EV sales (level1 ), and its powertrain (level 2), then its car type ('mode' column) to discern what type of EV are widely used within the country market.
   In ev.ipynb use Y2023 only

   Task:
   You are a data visualization expert. Create a clear and informative sunburst pie chart using Plotly.

   Goal: Visualize and compare the top 3 largest EV markets globally in 2023, broken down by:

   Level 1: EV Sales by Country (Y2023 only)

   Level 2: Powertrain type

   Level 3: Car type (column: mode)

   The purpose is to help users understand which countries lead in EV adoption, which powertrains dominate those markets, and what car types (mode) are most widely used.

   Data:
   Use data from ev.ipynb, filtered to Y2023 only.
   Identify the top 3 countries with the highest total EV sales in 2023.

   Sunburst Chart Requirements:

   Hierarchy: country → powertrain → mode

   Values: Use EV sales volume to size each sector.

   Color Requirements:

   - Powertrain categories must be visually distinct (clear contrasting colors).
   - Car types within a powertrain can share variations of the same hue to reinforce grouping.
   - Top 3 markets should appear noticeably segmented but not visually overwhelming.

   Labels:

   - Use readable labels for each level.
   - Show: country name, powertrain, car type (mode), and numerical sales in hover labels.

   Plotly Styling:

   - Ensure the figure is user-friendly and easy to interpret.
   - Include title: "Top 3 Global EV Markets in 2023 — Sales Breakdown by Powertrain and Car Type".
   - Use plotly.express.sunburst.

   Output:
   Return only the final Plotly code block, fully executable, including:

   - Data filtering
   - Aggregation
   - Sunburst creation
   - Custom color mapping
   - Title, labels, and hover settings
