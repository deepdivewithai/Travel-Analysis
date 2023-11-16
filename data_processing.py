import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

def clean_and_process_data(file_path):
    # Read the data
    data = pd.read_csv(file_path, skiprows=3)
    
    # Drop columns with all NaN values
    data = data.dropna(axis=1, how="all")

    # Drop rows with all NaN values in subset columns
    subset_data = data.iloc[:, 4:]
    filtered_data = data.dropna(subset=subset_data.columns, how="all")

    # Reset index
    travel_data = filtered_data.reset_index(drop=True)

    # Drop unnecessary columns
    travel_data = travel_data.drop(columns=["Indicator Name", "Indicator Code"])

    # Drop additional columns and fill NaN values with 0
#     travel_data = travel_data.drop(columns=["Country_Code"])
    travel_data = travel_data.fillna(0)

    # Convert numeric columns to integers
    num_columns = travel_data.select_dtypes('number').columns
    for column in num_columns:
        travel_data[column] = travel_data[column].astype('int')
        
    obj_columns = travel_data.select_dtypes('object').columns
    for column in obj_columns:
        if len(column.split()) > 1:
            new_column = "_".join(column.split())
            travel_data.rename(columns={column:new_column}, inplace=True)
    
    codes_path = "codes.csv"
    
    codes = pd.read_csv(codes_path)

    ncon = []
    
    for country in travel_data['Country_Name']:
        pattern = re.compile(fr'\b{re.escape(country)}\b', flags=re.IGNORECASE)
        if not codes['Country'].str.contains(pattern).any():
            ncon.append(country)

    travel_data = travel_data[~travel_data['Country_Name'].isin(ncon)].reset_index(drop=True)

    return travel_data


def generate_report(data, year='2020'):
    # Sort the DataFrame by total arrivals in 2020
    top_10_countries = data.sort_values(by=year, ascending=False).head(10).drop(columns=["Country_Code"])

    # Create a bar plot for the top 10 countries in specified year
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Country_Name', y=year, data=top_10_countries)
    plt.title(f'Top 10 Countries by Total Arrivals in {year}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # Create a line plot for the trend of arrivals over the years for the top 10 countries
    plt.figure(figsize=(16, 8))
    sns.lineplot(data=top_10_countries.set_index('Country_Name').T)
    plt.title('Trend of Total Arrivals Over the Years for Top 10 Countries')
    plt.xlabel('Year')
    plt.ylabel('Total Arrivals')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()
    
def top_revenue_countries(data, year='2020', top_n=5):
    # Sort the DataFrame by revenue in the specified year
    top_countries = data.sort_values(by=year, ascending=False).head(top_n)[["Country_Name", year]]

    # Create a bar plot for the top revenue-generating countries in the specified year
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Country_Name', y=year, data=top_countries)
    plt.title(f'Top {top_n} Revenue Generating Countries in {year}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    
def calculate_growth_rate(data, method='median'):
    """
    Calculate growth rates for each country in the provided DataFrame.

    Parameters:
    - data: DataFrame containing columns 'Country_Name' and years from 1995 to 2020.
    - method: Method for aggregating growth rates ('median', 'mean', 'std').

    Returns:
    - DataFrame with growth rates and additional statistics.
    """
    # Calculate the growth rate for each country
    growth_rates = data.loc[:, '1995':'2020'].pct_change(axis=1)

    # Handle missing values by filling them with 0
    growth_rates = growth_rates.fillna(0)

    # Aggregate growth rates based on the specified method
    if method == 'median':
        data['Growth_Rate'] = growth_rates.median(axis=1)
    elif method == 'mean':
        data['Growth_Rate'] = growth_rates.mean(axis=1)
    elif method == 'std':
        data['Growth_Rate'] = growth_rates.std(axis=1)
    else:
        raise ValueError("Invalid method. Use 'median', 'mean', or 'std'.")

    # Calculate additional statistics
    data['Mean_Growth_Rate'] = growth_rates.mean(axis=1)
    data['Std_Growth_Rate'] = growth_rates.std(axis=1)

    return data

def generate_growth_report(data, start_year="1995", end_year="2020"):
    # Calculate growth rate for the specified range of years
    data['Growth_Rate'] = data.loc[:, start_year:end_year].pct_change(axis=1).median(axis=1)

    # Sort the DataFrame by growth rate
    data_sorted = data.sort_values('Growth_Rate', ascending=False)
    top_10_countries = data_sorted.head(10)

    # Create a bar plot for the top 10 countries with the highest growth rates
    plt.figure(figsize=(12, 8))
    colors = sns.color_palette("viridis", len(top_10_countries))
    sns.barplot(x='Country_Name', y='Growth_Rate', data=top_10_countries, palette=colors)
    plt.xlabel('Country')
    plt.ylabel('Growth Rate (%)')
    plt.title(f'Top 10 Countries with Highest Growth in International Tourist Arrivals ({start_year}-{end_year})')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    
    
def compare_events_impact(data, economic_crisis_years, pandemic_years):
    """
    Compare the impact of economic crises and pandemics on tourist arrivals.

    Parameters:
    - data: DataFrame containing columns 'Country_Name' and years from 1995 to 2020.
    - economic_crisis_years: List of years for economic crises.
    - pandemic_years: List of years for pandemics.

    Returns:
    - DataFrame with comparative analysis results.
    """
    # Convert relevant columns to numeric
    travel_numeric = data.loc[:, '1995':].apply(pd.to_numeric, errors='coerce')

    # Calculate average tourist arrivals before and after economic crises
    average_before_economic_crisis = travel_numeric.loc[:, :'{}'.format(economic_crisis_years[0]-1)].mean(axis=1)
    average_after_economic_crisis = travel_numeric.loc[:, '{}'.format(economic_crisis_years[0]):].mean(axis=1)

    # Calculate average tourist arrivals before and after pandemics
    average_before_pandemic = travel_numeric.loc[:, :'{}'.format(pandemic_years[-1]-1)].mean(axis=1)
    average_after_pandemic = travel_numeric.loc[:, '{}:'.format(pandemic_years[-1]):].mean(axis=1)  # Fixed the indexing here

    # Create a DataFrame for comparative analysis
    comparative_analysis = pd.DataFrame({
        'Country_Name': data['Country_Name'],
        'Average Before Economic Crisis': average_before_economic_crisis,
        'Average After Economic Crisis': average_after_economic_crisis,
        'Average Before Pandemic': average_before_pandemic,
        'Average After Pandemic': average_after_pandemic
    })

    return comparative_analysis

def plot_comparative_analysis(comparative_data):
    """
    Plot the comparative analysis results.

    Parameters:
    - comparative_data: DataFrame containing comparative analysis results.
    """
    sns.set(style="whitegrid")

    plot_data = pd.DataFrame({
        'Event': ['Economic Crisis', 'Pandemic'],
        'Average Before': [
            comparative_data['Average Before Economic Crisis'].mean(),
            comparative_data['Average Before Pandemic'].mean()
        ],
        'Average After': [
            comparative_data['Average After Economic Crisis'].mean(),
            comparative_data['Average After Pandemic'].mean()
        ]
    })

    plot_data_melted = pd.melt(plot_data, id_vars='Event', var_name='Period', value_name='Average Tourist Arrivals')

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Event', y='Average Tourist Arrivals', hue='Period', data=plot_data_melted, palette="viridis")
    plt.title('Average Tourist Arrivals Before and After Global Events')
    plt.show()