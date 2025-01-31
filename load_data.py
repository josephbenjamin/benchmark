import pandas as pd
# from pandasgui import show

DIRECTORY = 'data/'
FILENAME = '20250130 - Gilts in Issue.xlsx'

def gilts():
    # Reload the data to start fresh
    df_xlsx = pd.read_excel(DIRECTORY+FILENAME, sheet_name="Sheet1", header=None)

    # Step 1: Find the location of "Conventional Gilts"
    conv_gilts_loc = None

    for i in range(df_xlsx.shape[0]):
        for j in range(df_xlsx.shape[1]):
            if isinstance(df_xlsx.iloc[i, j], str) and "Conventional Gilts" in df_xlsx.iloc[i, j]:
                conv_gilts_loc = (i, j)
                break
        if conv_gilts_loc:
            break

    # Step 2: Extract the headers from the same row as "Conventional Gilts"
    header_row, header_col = conv_gilts_loc
    headers = df_xlsx.iloc[header_row, header_col:].dropna().tolist()

    # Count the number of headers to define the dataframe width
    num_columns = len(headers)

    # Step 3: Find the end of the Conventional Gilts table
    end_row = None

    for i in range(header_row + 1, df_xlsx.shape[0] - 1):
        if df_xlsx.iloc[i].isna().all() and df_xlsx.iloc[i + 1].isna().all():
            end_row = i
            break

    # Step 4: Extract the Conventional Gilts dataframe
    df_conventional = df_xlsx.iloc[header_row + 1:end_row, header_col:header_col + num_columns]
    df_conventional.columns = headers

    # Step 5: Insert a new column for Maturity Bucket
    df_conventional.insert(0, "MATURITY_BRACKET", None)
    df_conventional = df_conventional.reset_index(drop=True)
    # Step 6: Identify and assign Maturity Buckets (Ultra-Short, Short, Medium, Long)
    maturity_labels = ["Ultra-Short", "Short", "Medium", "Long"]
    maturity_rows = {}

    for i in range(df_conventional.shape[0]):
        if isinstance(df_conventional.iloc[i, 1], str) and df_conventional.iloc[i, 1] in maturity_labels:
            maturity_rows[df_conventional.iloc[i, 1]] = i

    # Assign Maturity Bucket values
    previous_label = None

    for label in maturity_labels:
        if label in maturity_rows:
            row_idx = maturity_rows[label]
            if previous_label is not None:
                df_conventional.loc[previous_label:row_idx-1, "MATURITY_BRACKET"] = previous_label_label
            previous_label = row_idx
            previous_label_label = label

    # Assign the last maturity bucket
    if previous_label is not None:
        df_conventional.loc[previous_label:, "MATURITY_BRACKET"] = previous_label_label

    # Step 7: Remove rows containing only maturity labels
    df_conventional = df_conventional[~df_conventional.iloc[:, 1].isin(maturity_labels)].reset_index(drop=True)

    # Step 8: Convert all date columns to datetime objects
    date_columns = [col for col in headers if "Date" in col]
    for col in date_columns:
        df_conventional[col] = pd.to_datetime(df_conventional[col], errors='coerce')

    # Display processed data
    data = df_conventional
    sum_amount_outstanding = data.iloc[:, -1].sum()
    formatted_sum = f"£{sum_amount_outstanding:,.2f} million conventional gilts outstanding"
    print(formatted_sum)
    return df_conventional

def main():
    df = gilts()
    print(df)

if __name__ == '__main__':
    main()