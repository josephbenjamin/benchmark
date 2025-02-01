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
    """Mark True for the only AB gilt that matures in the same year, if unique."""
    input_date = pd.to_datetime(input_date_str)
    filtered_df = df[df['IS_AB'] == True]
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'].dt.year == input_date.year]

    df['UNIQUE_SAME_YEAR'] = False
    if len(filtered_df) == 1:
        df.loc[df['REDEMPTION_DATE'] == filtered_df['REDEMPTION_DATE'].iloc[0], 'UNIQUE_SAME_YEAR'] = True
    return df

def find_nearest_shorter(df, input_date_str):
    """Mark True for the AB gilt with the latest redemption date before input_date."""
    input_date = pd.to_datetime(input_date_str)
    filtered_df = df[df['IS_AB'] == True]
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'] < input_date]

    df['NEAREST_SHORTER'] = False
    if not filtered_df.empty:
        nearest_shorter = filtered_df['REDEMPTION_DATE'].max()
        df.loc[df['REDEMPTION_DATE'] == nearest_shorter, 'NEAREST_SHORTER'] = True
    return df

def find_nearest_shorter_cal_yr(df, input_date_str):
    """Mark True for the latest AB gilt before input_date within the same calendar year."""
    input_date = pd.to_datetime(input_date_str)
    filtered_df = df[df['IS_AB'] == True]
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'].dt.year == input_date.year]
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'] < input_date]

    df['NEAREST_SHORTER_CAL_YR'] = False
    if not filtered_df.empty:
        nearest_shorter_cal_yr = filtered_df['REDEMPTION_DATE'].max()
        df.loc[df['REDEMPTION_DATE'] == nearest_shorter_cal_yr, 'NEAREST_SHORTER_CAL_YR'] = True
    return df

def find_nearest_longer_cal_yr(df, input_date_str):
    """Mark True for the shortest AB gilt after input_date within the same calendar year."""
    input_date = pd.to_datetime(input_date_str)
    filtered_df = df[df['IS_AB'] == True]
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'].dt.year == input_date.year]
    filtered_df = filtered_df[filtered_df['REDEMPTION_DATE'] > input_date]

    df['NEAREST_LONGER_CAL_YR'] = False
    if not filtered_df.empty:
        nearest_longer_cal_yr = filtered_df['REDEMPTION_DATE'].min()
        df.loc[df['REDEMPTION_DATE'] == nearest_longer_cal_yr, 'NEAREST_LONGER_CAL_YR'] = True
    return df

# ---- ICMA Benchmark Selection ----
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
    ab_df = df[df['IS_AB'] == True].copy()

    if verbose:
        g_count = len(df)
        ab_count = len(ab_df)
        print(f'Count of Conventional Gilts in issue: {g_count}')
        print(f'First, we must eliminate all below Benchmark size (<£10bn) as well as those deemed inappropriate')
        print(f'Removed {g_count - ab_count}, leaving {ab_count} Appropriate Benchmarks (ABs)')

    df['ICMA_BENCHMARK'] = False
    same_year_df = ab_df[ab_df['SAME_YEAR'] == True]
    sy_count = len(same_year_df)

    if verbose:
        print(f'Count of ABs maturing in same calendar year as New Issue Bond Maturity: {sy_count}\n')
        print(f'ICMA RULES ENGINE')
        print(f'R7.4(a) If only one benchmark maturing in the same calendar year, take that benchmark.')
    # R7.4(a) If only one benchmark maturing in the same calendar year, that benchmark.
    if len(same_year_df) == 1:
        if verbose: print(f'>>#ABs is 1, therefore we have found the benchmark.')
        df.loc[df['REDEMPTION_DATE'] == same_year_df['REDEMPTION_DATE'].iloc[0], 'ICMA_BENCHMARK'] = True
        return df

    # R7.4(b) If there are none maturing in the calendar year, then the nearest shorter
    if verbose:
        print(f'#ABs is not 1, therefore proceeding to next rule R7.4(b).\n')
        print(f'R7.4(b) If there are no ABs maturing in the calendar year, then take the nearest shorter AB')

    if len(same_year_df) == 0:
        if verbose:
            print(f'>>#ABs is 0, therefore we take the nearest shorter AB. Benchmark identified.')
        nearest_shorter = ab_df[ab_df['NEAREST_SHORTER'] == True]
        if len(nearest_shorter) == 1:
            df.loc[df['REDEMPTION_DATE'] == nearest_shorter['REDEMPTION_DATE'].iloc[0], 'ICMA_BENCHMARK'] = True
        return df

    if verbose:
        print(f'#ABs is not 0, therefore proceeding to next rule R7.4(c).\n')
        print(f'R7.4(c) If there is more than one AB maturing in the calendar year, then:')
        print(f'    R7.4(c)(i) First use an AB maturing in the same month if one exists, otherwise')
        print(f'    R7.4(c)(ii) Take the nearest shorter AB in the same calendar year')
        print(f'    R7.4(c)(iii) Take the nearest longer AB in the same calendar year\n')

    # R7.4(c) If there are more than one maturing in the calendar year then....
    if len(same_year_df) > 1:

        # R7.4(c)(i) First use a bond maturing in the same month, if it exists
        same_month_df = ab_df[ab_df['SAME_YEAR_AND_MONTH'] == True]
        if len(same_month_df) == 1:
            if verbose: print(f'>>R7.4(c)(i) satisfied. Benchmark identified.')
            df.loc[df['REDEMPTION_DATE'] == same_month_df['REDEMPTION_DATE'].iloc[0], 'ICMA_BENCHMARK'] = True
            return df

        # R7.4(c)(ii) If nothing maturing in same month, find nearest shorter in calendar year
        if verbose: print(f'R7.4(c)(i) not satisfied, proceeding to R7.4(c)(ii): nearest shorter AB.')
        nearest_shorter_cal_yr_df = ab_df[ab_df['NEAREST_SHORTER_CAL_YR'] == True]
        if len(nearest_shorter_cal_yr_df) == 1:
            if verbose: print(f'>>R7.4(c)(ii) satisfied. Benchmark identified.')
            df.loc[df['REDEMPTION_DATE'] == nearest_shorter_cal_yr_df['REDEMPTION_DATE'].iloc[0], 'ICMA_BENCHMARK'] = True
            return df

        # R7.4(c)(iii) If nothing shorter in calendar year, then nearest longest in calendar year
        if verbose: print(f'R7.4(c)(ii) not satisfied, proceeding to R7.4(c)(iii): nearest longer AB.')
        nearest_longer_cal_yr_df = ab_df[ab_df['NEAREST_LONGER_CAL_YR'] == True]
        if len(nearest_longer_cal_yr_df) == 1:
            if verbose: print(f'>>R7.4(c)(iii) satisfied. Benchmark identified.')
            df.loc[df['REDEMPTION_DATE'] == nearest_longer_cal_yr_df['REDEMPTION_DATE'].iloc[0], 'ICMA_BENCHMARK'] = True
            return df

        else: # no rules satisfied
            print(f"No ICMA Rules satisfied!?! Check the code...")
            df['ICMA_BENCHMARK'] = False # Return all False
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


# SINGLE OPTIMISED FUNCTION
def get_icma_benchmark(df, maturity_str: str) -> pd.Timestamp:
    """
    Given a maturity date, applies all ICMA benchmark selection rules and returns
    the Redemption_Date of the selected benchmark.

    Parameters:
        df (pd.DataFrame): Original DataFrame before any rule columns are created.
        maturity_str (str): The input maturity date as a string ('YYYY-MM-DD').

    Returns:
        pd.Timestamp or None: The Redemption_Date of the ICMA Benchmark, if found.
    """
    maturity_date = pd.to_datetime(maturity_str)

    # Apply filtering to find appropriate benchmarks (ABs)
    ab_df = df[
        (df['TOTAL_AMOUNT_IN_ISSUE'] >= 10_000) &  # Benchmark size
        (~df['ISIN_CODE'].isin([]))  # No inappropriate gilts (define exclusions if needed)
    ].copy()

    # Get same-year, same-month, and nearest-shorter/longer bonds
    same_year = ab_df[ab_df['REDEMPTION_DATE'].dt.year == maturity_date.year]
    same_month = same_year[same_year['REDEMPTION_DATE'].dt.month == maturity_date.month]

    nearest_shorter = ab_df[ab_df['REDEMPTION_DATE'] < maturity_date]
    nearest_shorter_cal_yr = same_year[same_year['REDEMPTION_DATE'] < maturity_date]
    nearest_longer_cal_yr = same_year[same_year['REDEMPTION_DATE'] > maturity_date]

    print(f"Processing date: {maturity_str}")
    print(f"Same year count: {len(same_year)}")
    print(f"Same month count: {len(same_month)}")
    print(f"Nearest shorter count: {len(nearest_shorter)}")
    print(f"Nearest shorter in calendar year count: {len(nearest_shorter_cal_yr)}")
    print(f"Nearest longer in calendar year count: {len(nearest_longer_cal_yr)}")

    # Apply ICMA rules in sequence
    if len(same_year) == 1:
        print("Rule R7.4(a) satisfied: Single gilt in same year")
        return same_year['REDEMPTION_DATE'].iloc[0]

    if same_year.empty and not nearest_shorter.empty:
        print("Rule R7.4(b) satisfied: No gilt in same year, using nearest shorter")
        return nearest_shorter['REDEMPTION_DATE'].max()

    if len(same_month) == 1:
        print("Rule R7.4(c)(i) satisfied: Single gilt in same month")
        return same_month['REDEMPTION_DATE'].iloc[0]

    if not nearest_shorter_cal_yr.empty:
        nearest_shorter_cal_yr_date = nearest_shorter_cal_yr['REDEMPTION_DATE'].max()
        print(f"Rule R7.4(c)(ii) satisfied: Using max nearest shorter gilt in same calendar year: {nearest_shorter_cal_yr_date}")
        return nearest_shorter_cal_yr_date

    if not nearest_longer_cal_yr.empty:
        nearest_longer_cal_yr_date = nearest_longer_cal_yr['REDEMPTION_DATE'].min()
        print(f"Rule R7.4(c)(iii) satisfied: Using min nearest longer gilt in same calendar year: {nearest_longer_cal_yr_date}")
        return nearest_longer_cal_yr_date

    print("No benchmark found")
    return None  # No benchmark found
