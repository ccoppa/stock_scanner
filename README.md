# Stock scanner

## Introduction
There are way too many stocks, their price movements and balance sheets to keep track of. 
As a lone investor, I want to automate some of the screening process and leave the heavy liftings to algorithms.
Here in this project, I created a module that would connect to the database of yahoo finance API, query the data based on certain fundamental stock screening criteria (e.g. P/E, gross/operating/profit margin, market cap, industry, etc.), and deliver the results in anice format directly to my inbox every morning.
This auto-screening would greatly help me reducing the load off my shoulder and narrowing my targets, and allow me to be more efficient working on more interesting tasks -- stock analysis.   

Data used: IEX Getting starter guide can be found here https://algotrading101.com/learn/iex-api-guide/



## Stock Analysis
The methodology used to analyze stocks is consisted of four aspects:

# Method 1: Corporate profitability -- Profit analysis
1. long term ROE > 15%
2. Long term profit margin > 10%

# Method 2: Corporate health -- Cash flow analysis
1. Operating cash flow (CFO) to net income(NI) > 50%
CFO/NI: If the indicator’s value is higher than 100%, it means the company is able to finance its performance at the expense of the operating activity. Higher figures indicate the company’s profit is of higher quality.
2. Long term free cash flow(FCF) > 0

# Method 3: Corporate value -- pricing analysis
1. Dividend discount model (DDM): DDM is one of the oldest and conservative methods of valuing stocks.
Digging into DDM: https://www.investopedia.com/articles/fundamental/04/041404.asp
    - An appropriate buy point during normal times is when DDM > 10% ; 
    - A better buy poiint during economy downturn is when DDM > 15% 

# Method 4: Corporate Growth -- Revenue analysis
We'll compare YoY quarterly revenue growth rate, which is referred to as the short-term growth rate, to YoY annual revenue growth rate, which is referred to as the long-term growth rate.
The company shows an upward momentum when its short-term growth rate surpasses its long-term growth rate.


    

