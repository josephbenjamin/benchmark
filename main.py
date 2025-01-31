import load_data
import matplotlib.pyplot as plt
import pandas as pd

def main():
    df = load_data.gilts()
    for name in df.columns: print(name)

    df.rename(columns={
        'Total Amount in Issue \n(£ million nominal)': 'Amount Out m',
    }, inplace=True)

    df['Benchmark'] = df.apply(benchmark, axis=1)
    cg_count = len(df)
    cgb_count = df['Benchmark'].sum()

    print(f'Total of {cgb_count} benchmarks found of of {cg_count} conventional gilts.')

    # Implement Rule 1
    maturity_date_str = '2035-07-01'
    df = ruleOne(df,maturity_date_str)
    print(df[df['same_year']==True])

    fig, ax = plt.subplots(figsize=(10,6), layout='constrained')
    gilts = df['Conventional Gilts']
    amounts = df['Amount Out m']

    bar_colors = []
    for status in df['Benchmark']:
        if status == True:
            bar_colors.append('lime')  # Color for 'med'
        else:
            bar_colors.append('crimson')  # Default color

    ax.bar(gilts,amounts, color=bar_colors, edgecolor='k')

    ax.axhline(10000, color='crimson', linestyle='--', linewidth=2)
    ax.tick_params(axis='x', labelrotation=90)

    plt.title("Gilts: Amount Outstanding")
    plt.show()



def benchmark(gilt):

    # Return True if a gilt is benchmark
    if gilt['Amount Out m'] >= 10_000:
        return True
    else:
        return False

def appropriate(gilt):

    # manually exclude inappropriate gilts
    # "extreme" high coupon gilts are mentioned by ICMA
    # potentially also low coupon gilts
    inappropriate_gilts = []

    if gilt['ISIN Code'] not in inappropriate_gilts:
        return True
    else:
        return True

def ruleOne(df, input_date_str):
    """
     Loops through the DataFrame rows and marks a new column 'same_year' as True
     if the gilt's maturity_date is in the same calendar year as input_date_str.

     Parameters:
         df (pd.DataFrame): DataFrame containing a 'Redemption Date' column.
         input_date_str (str): Input date string in 'yyyy-mm-dd' format.

     Returns:
         pd.DataFrame: The DataFrame with an added 'same_year' column.
     """
    # Convert the input date string to a datetime object and extract the year
    input_date = pd.to_datetime(input_date_str)
    input_year = input_date.year

    # Initialize the new column with False for all rows
    df['same_year'] = False

    # Loop through each row in the DataFrame
    for idx, row in df.iterrows():
        # Convert the redemption_date of the current row to a datetime object
        redemption_date = pd.to_datetime(row['Redemption Date'])
        # Check if the year matches the input year and update the column if so
        if redemption_date.year == input_year:
            df.at[idx, 'same_year'] = True

    return df

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
