import pandas as pd

# ---- Benchmark and Appropriateness Rules ----
def benchmark(gilt):
    """Return True if a gilt is benchmark size (>=10bn out)."""
    return gilt['TOTAL_AMOUNT_IN_ISSUE'] >= 10_000

def appropriate(gilt):
    """Return True if a gilt is appropriate based on ISIN exclusion list."""
    inappropriate_gilts = []  # Define exclusions if needed
    return gilt['ISIN_CODE'] not in inappropriate_gilts

# ---- Date Matching Rules ----
def same_year(row, input_date_str):
    input_date = pd.to_datetime(input_date_str)
    return pd.notna(row['REDEMPTION_DATE']) and row['REDEMPTION_DATE'].year == input_date.year

def same_year_and_month(row, input_date_str):
    input_date = pd.to_datetime(input_date_str)
    return pd.notna(row['REDEMPTION_DATE']) and row['REDEMPTION_DATE'].year == input_date.year and row['REDEMPTION_DATE'].month == input_date.month

# ---- Finding Specific Gilts ----
def find_unique_same_year(df, input_date_str):
    """Mark True for the only gilt that matures in the same year, if unique."""
    input_date = pd.to_datetime(input_date_str)
    filtered_df = df[df['REDEMPTION_DATE'].dt.year == input_date.year]

    df['UNIQUE_SAME_YEAR'] = False
    if len(filtered_df) == 1:
        df.loc[df['REDEMPTION_DATE'] == filtered_df['REDEMPTION_DATE'].iloc[0], 'UNIQUE_SAME_YEAR'] = True
    return df

def find_nearest_shorter(df, input_date_str):
    """Mark True for the gilt with the latest redemption date before input_date."""
    input_date = pd.to_datetime(input_date_str)
    filtered_df = df[df['REDEMPTION_DATE'] < input_date]

    df['NEAREST_SHORTER'] = False
    if not filtered_df.empty:
        nearest_shorter = filtered_df['REDEMPTION_DATE'].max()
        df.loc[df['REDEMPTION_DATE'] == nearest_shorter, 'NEAREST_SHORTER'] = True
    return df

def find_nearest_shorter_cal_yr(df, input_date_str):
    """Mark True for the latest gilt before input_date within the same calendar year."""
    input_date = pd.to_datetime(input_date_str)
    filtered_df = df[df['REDEMPTION_DATE'].dt.year == input_date.year]
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'] < input_date]

    df['NEAREST_SHORTER_CAL_YR'] = False
    if not filtered_df.empty:
        nearest_shorter_cal_yr = filtered_df['REDEMPTION_DATE'].max()
        df.loc[df['REDEMPTION_DATE'] == nearest_shorter_cal_yr, 'NEAREST_SHORTER_CAL_YR'] = True
    return df

def find_nearest_longer_cal_yr(df, input_date_str):
    """Mark True for the shortest gilt after input_date within the same calendar year."""
    input_date = pd.to_datetime(input_date_str)
    filtered_df = df[df['REDEMPTION_DATE'].dt.year == input_date.year]
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'] > input_date]

    df['NEAREST_LONGER_CAL_YR'] = False
    if not filtered_df.empty:
        nearest_longer_cal_yr = filtered_df['REDEMPTION_DATE'].min()
        df.loc[df['REDEMPTION_DATE'] == nearest_longer_cal_yr, 'NEAREST_LONGER_CAL_YR'] = True
    return df

# ---- ICMA Benchmark Selection ----
def find_ICMA_benchmark(df):
    """Determine the benchmark gilt based on ICMA rules."""
    ab_df = df[df['IS_AB'] == True].copy()

    df['ICMA_BENCHMARK'] = False
    same_year_df = ab_df[ab_df['SAME_YEAR'] == True]

    if len(same_year_df) == 1:
        df.loc[df['REDEMPTION_DATE'] == same_year_df['REDEMPTION_DATE'].iloc[0], 'ICMA_BENCHMARK'] = True
        return df

    if len(same_year_df) == 0:
        nearest_shorter = ab_df[ab_df['NEAREST_SHORTER'] == True]
        if len(nearest_shorter) == 1:
            df.loc[df['REDEMPTION_DATE'] == nearest_shorter['REDEMPTION_DATE'].iloc[0], 'ICMA_BENCHMARK'] = True
        return df

    same_month_df = ab_df[ab_df['SAME_YEAR_AND_MONTH'] == True]
    if len(same_month_df) == 1:
        df.loc[df['REDEMPTION_DATE'] == same_month_df['REDEMPTION_DATE'].iloc[0], 'ICMA_BENCHMARK'] = True
        return df

    return df


import pandas as pd

def apply_rules(df, new_issue_maturity):
    """
    Apply all rules in sequence to prepare the DataFrame for benchmark selection.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        new_issue_maturity (str): The input maturity date as a string ('YYYY-MM-DD').

    Returns:
        pd.DataFrame: The updated DataFrame with all rule columns added.
    """

    # Create columns for BENCHMARK, APPROPRIATE, and combined criteria
    df['IS_BENCHMARK'] = df.apply(benchmark, axis=1)
    df['IS_APPROPRIATE'] = df.apply(appropriate, axis=1)
    df['IS_AB'] = df['IS_BENCHMARK'] & df['IS_APPROPRIATE']

    # Date-based rules
    df['SAME_YEAR'] = df.apply(lambda row: same_year(row, new_issue_maturity), axis=1)
    df['SAME_YEAR_AND_MONTH'] = df.apply(lambda row: same_year_and_month(row, new_issue_maturity), axis=1)

    # Nearest gilt selection rules
    df = find_unique_same_year(df, new_issue_maturity)
    df = find_nearest_shorter(df, new_issue_maturity)
    df = find_nearest_shorter_cal_yr(df, new_issue_maturity)
    df = find_nearest_longer_cal_yr(df, new_issue_maturity)

    # Apply ICMA benchmark selection rule
    df = find_ICMA_benchmark(df)

    return df
