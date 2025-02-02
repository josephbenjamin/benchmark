import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import calendar
import re  # For regex-based name processing


def format_gilt_labels(df):
    """
    Extracts the existing instrument name, removes the year at the end,
    and appends the redemption date in 'MMM-YY' format.

    Parameters:
        df (pd.DataFrame): DataFrame containing 'INSTRUMENT_NAME' and 'REDEMPTION_DATE'.

    Returns:
        list: Formatted gilt labels.
    """
    formatted_labels = []

    for name, date in zip(df['INSTRUMENT_NAME'], df['REDEMPTION_DATE']):
        # Extract name without year (assumes year is 4 digits at the end)
        stripped_name = re.sub(r'\s\d{4}$', '', name)  # Removes year if present

        if pd.notna(date):  # Ensure date is valid
            formatted_date = f"{calendar.month_abbr[date.month]}-{str(date.year)[-2:]}"
            formatted_labels.append(f"{stripped_name} {formatted_date}")
        else:
            formatted_labels.append(stripped_name)  # Use original name if date is NaT

    return formatted_labels

def show_gilts(df, new_issue_maturity_str):
    """
    Plots a bar chart of total amount in issue for each gilt
    and a corresponding table with benchmark rules.

    Parameters:
        df (pd.DataFrame): DataFrame containing gilt data.
        new_issue_maturity_str (str): New issue maturity date as a string ('YYYY-MM-DD').
    """
    gilt_labels = format_gilt_labels(df)
    amounts = df['TOTAL_AMOUNT_IN_ISSUE']
    bar_positions = range(len(gilt_labels))

    bar_colors = ['lime' if status else 'crimson' for status in df['IS_BENCHMARK']]

    fig, (ax_chart, ax_table) = plt.subplots(
        2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}
    )

    # ----- Bar Chart -----
    ax_chart.bar(bar_positions, amounts, color=bar_colors, edgecolor='k')
    ax_chart.axhline(10_000, color='crimson', linestyle='--', linewidth=1)
    ax_chart.set_xlim(-0.5, len(gilt_labels) - 0.5)
    ax_chart.set_xticks(bar_positions)
    ax_chart.set_xticklabels(gilt_labels, rotation=90, fontsize=8)
    ax_chart.set_ylabel("Amount Outstanding (£bn)")

    def billions_formatter(x, _):
        return f"£{x / 1000:.0f} bn"

    ax_chart.yaxis.set_major_formatter(ticker.FuncFormatter(billions_formatter))
    ax_chart.grid(axis='y', linestyle='--', alpha=0.7)

    # ----- Overlay New Issue Date on Benchmark -----
    # Convert new issue date for labeling
    new_issue_date = pd.to_datetime(new_issue_maturity_str)
    # Identify the ICMA Benchmark gilt
    benchmark_idx = df[df['ICMA_BENCHMARK']].index
    if not benchmark_idx.empty:
        benchmark_idx = benchmark_idx[0]  # Take the first benchmark (should only be one)
        benchmark_position = list(df.index).index(benchmark_idx)  # Find its position in the bar chart
        benchmark_redemption_date = df.loc[benchmark_idx, 'REDEMPTION_DATE']
    else:
        benchmark_position = None  # No benchmark found

    if benchmark_position is not None:
        ax_chart.scatter(benchmark_position, amounts[benchmark_position] + 1500,  # Place marker slightly above bar
                         color='blue', marker='v', s=100, label="New Issue Date")
        ax_chart.text(benchmark_position, amounts[benchmark_position] + 3000,  # Add text above marker
                      f"New Issue:\n{new_issue_date.strftime('%b-%y')}", color='blue', ha='center', fontsize=9)

    # ----- Table -----
    table_cols = ['IS_BENCHMARK', 'IS_APPROPRIATE', 'IS_AB',
                  'SAME_YEAR',
                  'UNIQUE_SAME_YEAR',
                  'NEAREST_SHORTER',
                  'SAME_YEAR_AND_MONTH', 'NEAREST_SHORTER_CAL_YR', 'NEAREST_LONGER_CAL_YR',
                  'ICMA_BENCHMARK']

    # Create a display matrix for symbols
    table_data = []
    other_true_symbol = "•"
    other_false_symbol = ""

    for i, row_name in enumerate(table_cols):
        if i < 3:  # First three rows use ✓ and ✗
            table_data.append(['✓' if val else '✗' for val in df[row_name].values])
        else:  # Other rows use custom symbols
            table_data.append([other_true_symbol if val else other_false_symbol for val in df[row_name].values])

    # Define colors: First three rows green/red, remaining rows green/whitesmoke, ICMA_BENCHMARK purple
    cell_colors = []
    for i, row_name in enumerate(table_cols):
        if row_name == 'ICMA_BENCHMARK':  # Purple for ICMA_BENCHMARK
            cell_colors.append(['blue' if val == other_true_symbol else 'whitesmoke' for val in table_data[i]])
        elif i < 3:  # First three rows (benchmarking) use green/red
            cell_colors.append(['lime' if val == '✓' else 'red' for val in table_data[i]])
        else:  # Remaining rows use green/whitesmoke
            cell_colors.append(['lime' if val == other_true_symbol else 'whitesmoke' for val in table_data[i]])

    ax_table.axis('tight')
    ax_table.axis('off')

    the_table = ax_table.table(
        cellText=table_data,
        cellColours=cell_colors,
        rowLabels=table_cols,
        colLabels=None,
        cellLoc='center',
        loc='center'
    )

    the_table.auto_set_font_size(False)
    the_table.set_fontsize(8)
    the_table.scale(1, 1)

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.7)
    plt.savefig("figures/plot.svg")
    plt.show()