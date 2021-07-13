

def simple_rnn_model(input_dim, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    simp_rnn = GRU(output_dim, return_sequences=True, 
                 implementation=2, name='rnn')(input_data)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(simp_rnn)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model





def growth(_symbol, _url='sandbox', _last=12):
    # TODO
    """ update and keep stock price to current date
    other indicators can be lagging but it's a good idea to keep price chart current
    this helps verifying whether the price movement goes along with the identified trend"""
    
    """ Corporate revenue growth analysis"""
    # define parameters
    base_url = 'https://cloud.iexapis.com/v1'
    sandbox_url = 'https://sandbox.iexapis.com/stable'

    base_token = os.environ.get('IEX_TOKEN')
    sandbox_token = os.environ.get('IEX_SANDBOX_TOKEN')
    base_params = {'token': base_token}
    sandbox_params = {'token': sandbox_token}
    
    ticker_lower = f'{_symbol}'.lower() #IEX only accepts lower case ticker
    ticker_upper = f'{_symbol}'.upper() #Use upper case ticker for plotting
    
    # _last defaul is 12; min is 1 (quarters)
    if _url == 'sandbox':
        endpoint = f'{sandbox_url}/stock/{ticker_lower}/income/10-Q/?last={_last}'
        resp = requests.get(endpoint, params=sandbox_params)
    else:
        endpoint = f'{base_url}/stock/{ticker_lower}/income/10-Q/?last={_last}'
        resp = requests.get(endpoint, params=base_params) # need IEX subscription in order to support this url
    resp.raise_for_status()
    resp = resp.json()
    
    # Halt operation & return a statement in insufficient financial data scenario 
    if _last == 12 and len(resp['income']) < 12:
        print(f'Hey! {ticker_upper} is a relatively new IPO.\nThe company has published less than 3 years worth of financial data for us to perform a meaningful analysis.')
        return None
        
    rev = []
    rev_qrt = {}
    
    # extract date / quarter_number / quarterly_revenue
    for num in range(0,len(resp['income'])):
        for key in ('fiscalDate','fiscalQuarter','totalRevenue'):
            rev_qrt[key] = resp['income'][num].setdefault(key)
        rev.append(rev_qrt)
        rev_qrt = {}
    
    # add TTM_Revenue
    # the last 3 TTM Revenue would not be available
    for i in range(0,len(rev)):
        if (i+3) < len(rev):
            rev[i]['TTM_Revenue'] = rev[i]['totalRevenue'] + rev[i+1]['totalRevenue'] + rev[i+2]['totalRevenue'] + rev[i+3]['totalRevenue']
   
    # Calculate YoY quarterly & yearly revenue growth rate
    q=0
    y=0
    while q < 8: # YOY quarterly growth is calculated every 4 quarters, so 12 quarters of data can only derive 8 data points
        rev[q]['Quarterly_Revenue_Growth'] = round((rev[q]['totalRevenue']/rev[q+4]['totalRevenue']-1)*100,2)
        q += 1
    while y < 5: # YOY same period growth is calculated every 4 data points, so 12 quarters of data can only derive 5 data points   
        rev[y]['TTM_Revenue_Growth'] = round((rev[y]['TTM_Revenue']/rev[y+4]['TTM_Revenue']-1)*100,2)
        y += 1
    
    # Convert to pandas DF
    rev_df = pd.DataFrame(rev)  
    # rename totalRevenue to Quarterly_Revenue
    rev_df = rev_df.rename(columns={'totalRevenue': 'Quarterly_Revenue'})
    
    # remove df rows where quarterly_revenue_growth is NaN
    rev_df = rev_df.loc[0:7]
    # use datetime format and sort df by date
    rev_df['fiscalDate'] = pd.to_datetime(rev_df['fiscalDate'], format='%Y/%m/%d')
    rev_df = rev_df.sort_values('fiscalDate')
    # transform date to year-month format
    rev_df["date_yrmo"] = rev_df['fiscalDate'].dt.strftime('%Y-%m')
    
    # calculate monthly average stock price 
    if _url == 'sandbox':
        endpoint = f'{sandbox_url}/stock/{ticker_lower}/chart/39m'
        resp = requests.get(endpoint, params=sandbox_params)
    else:
        endpoint = f'{base_url}/stock/{ticker_lower}/chart/39m'
        resp = requests.get(endpoint, params=base_params) # need IEX subscription in order to support this url
    
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df = df[["symbol","date","fClose","fVolume"]]
    # transform date to year-month format
    df["date"] = pd.to_datetime(df['date'], format='%Y/%m/%d')
    df["date_yrmo"] = df['date'].dt.strftime('%Y-%m')
    # average close price by month
    df1 = df.groupby('date_yrmo')['fClose'].mean().reset_index(name='avg_monthly_price')
    df1['avg_monthly_price'] = round(df1['avg_monthly_price'],2)
    df = pd.merge(df, df1, on='date_yrmo', how='left')
    # merge df
    rev_df = pd.merge(rev_df, df, on='date_yrmo', how='left')
    
    
    #---------------------------------------------------------------------------------------------------------------------------------------------
    # Plotting
    fig = plt.figure(figsize=(16,9), dpi=100)
    ax = fig.add_subplot(111)

    ln1 = ax.plot(rev_df.date_yrmo, rev_df.Quarterly_Revenue_Growth, '-', label = 'Quarterly Revenue Growth Rate', color='tab:blue', linewidth=3)
    ln2 = ax.plot(rev_df.date_yrmo, rev_df.TTM_Revenue_Growth, '-', label = 'TTM Revenue Growth Rate', color='tab:green', linewidth=3)
    ax2 = ax.twinx()
    ln3 = ax2.plot(rev_df.date_yrmo, rev_df.avg_monthly_price, 'r', label = 'Monthly Avg Stock Price', color='tab:red', linewidth=3)

    # combine three lines
    ln = ln1+ln2+ln3
    labs = [l.get_label() for l in ln]

    ax.legend(ln, labs, loc='upper right')#, ncol=3, mode = "expand")
    ax.set_title(f'{ticker_upper}: YoY Quarterly vs TTM Revenue Growth Rate and Stock Price', fontsize=16)
    ax.grid(alpha=.2)
    ax.set_xlabel('Fiscal Year', fontsize=16)
    ax.set_ylabel('Revenue Growth Rate (%)', fontsize=16)
    ax2.set_ylabel('Monthly Average Stock Price ($)', fontsize=16)
    fig.tight_layout()
    plt.show()
    #----------------------------------------------------------------------------------------------------------------------------------------------
   
    # return simple revenue history
    rev = pd.DataFrame(rev)
    rev = rev.sort_values('fiscalDate')
    return rev
    