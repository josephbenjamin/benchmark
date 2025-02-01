import dmoxml
import matplotlib.pyplot as plt
import pandas as pd

def main(verbose=True):
    # fetch_dmo_xml() # scrapes from DMO website
    df = dmoxml.process_dmo_xml() # processes XML and saves CSV
    df = dmoxml.load_df_from_csv() # loads CSV back into a DataFrame

    # print a list of all the columns
    if verbose:
        print(f"Printing list of data columns:")
        for i, name in enumerate(df.columns): print(i, name)

    # filter out the non Conventional Gilts
    df_conventional = df.loc[df['INSTRUMENT_TYPE'] == 'Conventional '] # SPACE NEEDED AFTER CONVENTIONAL!!!!
    df = df_conventional

    # Create colums for BENCHMARK, APPROPRIATE and both
    df['IS_BENCHMARK'] = df.apply(benchmark, axis=1)
    df['IS_APPROPRIATE'] = df.apply(appropriate, axis=1)
    df['IS_AB'] = (df['IS_BENCHMARK'] & df['IS_APPROPRIATE'])

    if verbose: print(df)

    # Define the maturity of the anticipated new issue bond
    new_issue_maturity = '2050-01-01'

    # Create columns in the dataframe for the rules engine to use.

    # 'SAME_YEAR' column is True for all gilts redeeming in new_issue_ year
    df['SAME_YEAR'] = df.apply(lambda row: same_year(row, new_issue_maturity), axis=1)

    # Create 'UNIQUE_SAME_YEAR' column. Only shows a true if a unique bond found
    df = find_unique_same_year(df, new_issue_maturity)

    # Create 'NEAREST_SHORTER' column. Always shows the next shortest bond
    df = find_nearest_shorter(df, new_issue_maturity)

    # Create 'SAME_YEAR_AND_MONTH' column. Shows true if a bond maturing in same month is found
    df['SAME_YEAR_AND_MONTH'] = df.apply(lambda row: same_year_and_month(row, new_issue_maturity), axis=1) \

    # Create 'NEAREST_SHORTER_CAL_YR' column. Shows the nearest short bond in the calendar year if one exists.
    df = find_nearest_shorter_cal_yr(df, new_issue_maturity)

    # Create 'NEAREST_LONGER_CAL_YR' column. Shows the nearest longest bond in the calendar year if one exists.
    df = find_nearest_longer_cal_yr(df, new_issue_maturity)

    # Create 'ICMA_BENCHMARK' column, applies rules engine on other columns
    df = find_ICMA_benchmark(df)

    if verbose: print(df)
    show_gilts(df)


def benchmark(gilt):

    # Return True if a gilt is benchmark size (>=10bn out)
    if gilt['TOTAL_AMOUNT_IN_ISSUE'] >= 10_000:
        return True
    else:
        return False

def appropriate(gilt):

    # manually exclude inappropriate gilts
    # "extreme" high coupon gilts are mentioned by ICMA
    # potentially also low coupon gilts
    inappropriate_gilts = []

    if gilt['ISIN_CODE'] not in inappropriate_gilts:
        return True
    else:
        return False


def same_year(row, input_date_str):
    """
    Checks if the given row's REDEMPTION_DATE year matches the input date year.

    Parameters:
        row (pd.Series): A row from the DataFrame.
        input_date_str (str): The input date in 'YYYY-MM-DD' format.

    Returns:
        bool: True if the years match, False otherwise.
    """
    input_date = pd.to_datetime(input_date_str)  # Convert string to datetime
    input_year = input_date.year  # Extract year

    if pd.notna(row['REDEMPTION_DATE']):  # Ensure the date is valid
        return row['REDEMPTION_DATE'].year == input_year
    return False

def same_year_and_month(row, input_date_str):
    """
    Checks if the given row's REDEMPTION_DATE year matches the input date year.

    Parameters:
        row (pd.Series): A row from the DataFrame.
        input_date_str (str): The input date in 'YYYY-MM-DD' format.

    Returns:
        bool: True if the years match, False otherwise.
    """
    input_date = pd.to_datetime(input_date_str)  # Convert string to datetime
    input_year = input_date.year  # Extract year
    input_month = input_date.month  # Extract year

    if pd.notna(row['REDEMPTION_DATE']):  # Ensure the date is valid
        return (row['REDEMPTION_DATE'].year == input_year & row['REDEMPTION_DATE'].month == input_month)
    return False

def find_unique_same_year(df, input_date_str):
    """
    Marks the row that has the unique REDEMPTION_DATE within the same calendar year
    as the given input_date. If no unique gilt exists, marks all rows as False.

    Parameters:
        df (pd.DataFrame): DataFrame containing the 'REDEMPTION_DATE' column.
        input_date_str (str): Date string in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: The updated DataFrame with a new 'UNIQUE_SAME_YEAR' column.
    """
    # Convert input_date to datetime
    input_date = pd.to_datetime(input_date_str)

    # Filter rows in the same calendar year as the input_date
    filtered_df = df[df['REDEMPTION_DATE'].dt.year == input_date.year]

    # Check if there's exactly one gilt in the filtered DataFrame
    if len(filtered_df) == 1:
        # Get the unique redemption date
        unique_same_year = filtered_df['REDEMPTION_DATE'].iloc[0]
        # Mark True for the matching gilt and False for others
        df['UNIQUE_SAME_YEAR'] = df['REDEMPTION_DATE'] == unique_same_year
    else:
        # No unique gilt or multiple gilts; mark all as False
        df['UNIQUE_SAME_YEAR'] = False

    return df


def find_nearest_shorter(df, input_date_str):
    """
    Returns a DataFrame with a new column marking the row that has the latest REDEMPTION_DATE
    before the given input_date.

    Parameters:
    df (pd.DataFrame): DataFrame containing the 'REDEMPTION_DATE' column.
    input_date_str (str): Date string in 'YYYY-MM-DD' format.

    Returns:
    pd.DataFrame: The updated DataFrame with a new 'NEAREST_SHORTER' column.
    """
    # Convert input_date to datetime
    input_date = pd.to_datetime(input_date_str)

    # Filter only the rows where REDEMPTION_DATE is before input_date
    filtered_df = df[df['REDEMPTION_DATE'] < input_date]

    if filtered_df.empty:
        df['NEAREST_SHORTER'] = False  # No valid bonds, return all False
        return df

    # Find the latest (max) redemption date among filtered rows
    nearest_shorter = filtered_df['REDEMPTION_DATE'].max()

    # Assign True to the row with the latest redemption date, else False
    df['NEAREST_SHORTER'] = df['REDEMPTION_DATE'] == nearest_shorter

    return df

def find_nearest_shorter_cal_yr(df, input_date_str):
    """
    Returns a DataFrame with a new column marking the row that has the latest REDEMPTION_DATE
    before the given input_date, within the same calendar year

    Parameters:
    df (pd.DataFrame): DataFrame containing the 'REDEMPTION_DATE' column.
    input_date_str (str): Date string in 'YYYY-MM-DD' format.

    Returns:
    pd.DataFrame: The updated DataFrame with a new 'NEAREST_SHORTER_CAL_YR' column.
    """
    # Convert input_date to datetime
    input_date = pd.to_datetime(input_date_str)

    # Filter rows which are not in the same calendar year
    filtered_df = df[df['REDEMPTION_DATE'].dt.year == input_date.year]

    # Filter only the rows where REDEMPTION_DATE is before input_date
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'] < input_date]

    if filtered_df.empty:
        df['NEAREST_SHORTER_CAL_YR'] = False  # No valid bonds, return all False
        return df

    # Find the latest (max) redemption date among filtered rows
    nearest_shorter_cal_yr = filtered_df['REDEMPTION_DATE'].max()

    # Assign True to the row with the latest redemption date, else False
    df['NEAREST_SHORTER_CAL_YR'] = df['REDEMPTION_DATE'] == nearest_shorter_cal_yr

    return df

def find_nearest_longer_cal_yr(df, input_date_str):
    """
    Returns a DataFrame with a new column marking the row that has the latest REDEMPTION_DATE
    before the given input_date, within the same calendar year

    Parameters:
    df (pd.DataFrame): DataFrame containing the 'REDEMPTION_DATE' column.
    input_date_str (str): Date string in 'YYYY-MM-DD' format.

    Returns:
    pd.DataFrame: The updated DataFrame with a new 'NEAREST_LONGER_CAL_YR' column.
    """
    # Convert input_date to datetime
    input_date = pd.to_datetime(input_date_str)

    # Filter rows which are not in the same calendar year
    filtered_df = df[df['REDEMPTION_DATE'].dt.year == input_date.year]

    # Filter only the rows where REDEMPTION_DATE is after input_date
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'] > input_date]

    if filtered_df.empty:
        df['NEAREST_LONGER_CAL_YR'] = False  # No valid bonds, return all False
        return df

    # Find the latest (max) redemption date among filtered rows
    nearest_longer_cal_yr = filtered_df['REDEMPTION_DATE'].min()

    # Assign True to the row with the latest redemption date, else False
    df['NEAREST_LONGER_CAL_YR'] = df['REDEMPTION_DATE'] == nearest_longer_cal_yr

    return df

def find_ICMA_benchmark(df, verbose=True):
    """
    Returns a DataFrame with a new column marking the gilt that should be selected
    as the benchmamk consistent with ICMA Pricing Rules

    Parameters:
    df (pd.DataFrame): DataFrame containing the following columns:
        'IS_AB'
        'SAME_YEAR'
        'UNIQUE_SAME_YEAR'
        'NEAREST SHORTER'
        'SAME_YEAR_AND_MONTH'
        'NEAREST_SHORTER_CAL_YR'
        'NEAREST_LONGER_CAL_YR'
    input_date_str (str): Date string in 'YYYY-MM-DD' format.

    Returns:
    pd.DataFrame: The updated DataFrame with a new 'ICMA_BENCHMARK' column.
    """

    # R7.3 Only consider appropriate benchmarks
    ab_df = df[df['IS_AB'] == True]

    if verbose:
        g_count = len(df)
        ab_count = len(ab_df)
        print(f'There are {g_count} conventional gilts in issue')
        print(f'First, removing non-Benchmark and inappropriate gilts.')
        print(f'Removed {g_count - ab_count}, leaving {ab_count} Appropriate Benchmarks')

    # create a DataFrame of all the appropriate benchmarks maturing in the same calendar year
    same_year_df = ab_df[ab_df['SAME_YEAR'] == True]
    sy_count = len(same_year_df)

    if verbose:
        print(f'Next, we count the number of Appropriate Benchmark gilts (ABs) maturing in the same calendar year.')
        print(f'#ABs: {sy_count}\n')

    # R7.4(a) If only one benchmark maturing in the same calendar year, that benchmark.
    if len(same_year_df) == 1:
        if verbose:
            print(f'R7.4(a) If only one Appropriate Benchmark maturing in the same calendar year, that benchmark.')
            print(f'#ABs is 1, therefore we have found the benchmark.')
        icma_benchmark = same_year_df['REDEMPTION_DATE'].iloc[0]
        df['ICMA_BENCHMARK'] = df['REDEMPTION_DATE'] == icma_benchmark
        return df

    # R7.4(b) If there are none maturing in the calendar year, then the nearest shorter
    if len(same_year_df) == 0:
        if verbose:
            print(f'R7.4(b) If no Appropriate Benchmarks maturing in the same calendar year, then the nearest shorter.')
            print(f'#ABs is 0, therefore we take the nearest shorter Appropriate Benchmark.')
        icma_benchmark = ab_df[ab_df['NEAREST_SHORTER'] == True].iloc[0]
        df['ICMA_BENCHMARK'] = df['REDEMPTION_DATE'] == icma_benchmark
        return df

    # R7.4(c) If there are more than one maturing in the calendar year then....
    if len(same_year_df) > 1:

        # R7.4(c)(i) First use a bond maturing in the same month, if it exists
        same_month_df = ab_df[ab_df['SAME_YEAR_AND_MONTH'] == True]
        if len(same_month_df) == 1:
            icma_benchmark = same_month_df['REDEMPTION_DATE'].iloc[0]
            df['ICMA_BENCHMARK'] = df['REDEMPTION_DATE'] == icma_benchmark
            return df

        nearest_shorter_cal_yr = ab_df[ab_df['NEAREST_SHORTER_CAL_YR'] == True]
        if len(nearest_shorter_cal_yr) == 1:
            icma_benchmark = nearest_shorter_cal_yr['REDEMPTION_DATE'].iloc[0]
            df['ICMA_BENCHMARK'] = df['REDEMPTION_DATE'] == icma_benchmark
            return df


        nearest_longer_cal_yr = ab_df[ab_df['NEAREST_LONGER_CAL_YR'] == True]
        if len(nearest_longer_cal_yr) == 1:
            icma_benchmark = nearest_longer_cal_yr['REDEMPTION_DATE'].iloc[0]
            df['ICMA_BENCHMARK'] = df['REDEMPTION_DATE'] == icma_benchmark
            return df

    else: # no rules satisfied
        print(f"No ICMA Rules satisfied!?! Check the code...")
        df['ICMA_BENCHMARK'] = False # Return all False
        return df

def show_gilts(df):
    import numpy as np
    import matplotlib.ticker as ticker

    # Extract data for the bar chart
    gilts = df['INSTRUMENT_NAME']
    amounts = df['TOTAL_AMOUNT_IN_ISSUE']

    # Define colors for bars (Benchmark = green, Non-benchmark = red)
    bar_colors = ['lime' if status else 'crimson' for status in df['IS_BENCHMARK']]
    bar_positions = range(len(gilts))

    # Create figure and axes
    fig, (ax_chart, ax_table) = plt.subplots(
        2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}  # Ratio between chart and table
    )

    # ----- BAR CHART AXIS -----
    ax_chart.bar(bar_positions, amounts, color=bar_colors, edgecolor='k')
    ax_chart.axhline(10000, color='crimson', linestyle='--', linewidth=2)
    ax_chart.set_xlim(-0.5, len(gilts) - 0.5)
    ax_chart.set_xticks(bar_positions)
    ax_chart.set_xticklabels(gilts, rotation=90, fontsize=8)
    ax_chart.set_title("Gilts: Total Amount in Issue")
    ax_chart.set_ylabel("Amount Outstanding (£bn)")

    # Format the Y-axis to show billions
    def billions_formatter(x, _):
        return f"£{x / 1000:.1f} bn"

    ax_chart.yaxis.set_major_formatter(ticker.FuncFormatter(billions_formatter))
    ax_chart.grid(axis='y', linestyle='--', alpha=0.7)

    # ----- TABLE AXIS -----
    ax_table.axis('tight')  # Tight layout for the table axis
    ax_table.axis('off')  # Turn off the axis display for the table

    # Columns to display in the table
    table_cols = ['IS_BENCHMARK', 'IS_APPROPRIATE', 'IS_AB',
                  'SAME_YEAR',
                  'UNIQUE_SAME_YEAR',
                  'NEAREST_SHORTER', 'SAME_YEAR_AND_MONTH',
                  'NEAREST_SHORTER_CAL_YR', 'NEAREST_LONGER_CAL_YR',
                  'ICMA_BENCHMARK']

    # Transpose: rows = rule names, columns = gilts
    table_data = df[table_cols].T.values  # Transpose for correct orientation

    # Replace True/False with ✓/✗
    table_data = np.where(table_data, '✓', '✗')

    # Define colors: First three rows green/red, remaining rows green/light-grey
    cell_colors = []
    for i, row_name in enumerate(table_cols):
        if i < 3:  # First three rows
            cell_colors.append(['lime' if val == '✓' else 'red' for val in table_data[i]])
        else:  # Remaining rows
            cell_colors.append(['lime' if val == '✓' else 'lightgrey' for val in table_data[i]])

    # Create table
    the_table = ax_table.table(
        cellText=table_data,
        cellColours=cell_colors,
        rowLabels=table_cols,
        colLabels=None,  # No column labels since gilts names are on the chart
        cellLoc='center',
        loc='center'
    )

    # Adjust table appearance
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(8)
    the_table.scale(1, 1)

    # Adjust layout to ensure the two axes fit nicely
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.7)  # Add spacing between the two axes
    plt.show()



def insert_blank_rows(df, positions):
    """
    Inserts blank rows into a DataFrame at specified positions.

    Parameters:
        df (pd.DataFrame): The DataFrame to modify.
        positions (list): List of indices where blank rows should be inserted.

    Returns:
        pd.DataFrame: The modified DataFrame with blank rows.
    """
    # Create a blank row with the same columns as the DataFrame
    blank_row = {col: None for col in df.columns}

    # Insert blank rows at the specified positions
    for pos in sorted(positions, reverse=True):
        df = pd.concat([df.iloc[:pos], pd.DataFrame([blank_row]), df.iloc[pos:]]).reset_index(drop=True)

    return df

if __name__ == '__main__':
    main()
