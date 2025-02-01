import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


def show_gilts(df):
    """
    Plots a bar chart of total amount in issue for each gilt
    and a corresponding table with benchmark rules.

    Parameters:
        df (pd.DataFrame): DataFrame containing gilt data.
        other_true_symbol (str): Symbol to use for True values in non-benchmark rows.
        other_false_symbol (str): Symbol to use for False values in non-benchmark rows.
    """
    gilts = df['INSTRUMENT_NAME']
    amounts = df['TOTAL_AMOUNT_IN_ISSUE']
    bar_positions = range(len(gilts))

    bar_colors = ['lime' if status else 'crimson' for status in df['IS_BENCHMARK']]

    fig, (ax_chart, ax_table) = plt.subplots(
        2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}
    )

    # ----- Bar Chart -----
    ax_chart.bar(bar_positions, amounts, color=bar_colors, edgecolor='k')
    ax_chart.axhline(10_000, color='crimson', linestyle='--', linewidth=1)
    ax_chart.set_xlim(-0.5, len(gilts) - 0.5)
    ax_chart.set_xticks(bar_positions)
    ax_chart.set_xticklabels(gilts, rotation=90, fontsize=8)
    ax_chart.set_ylabel("Amount Outstanding (£bn)")

    def billions_formatter(x, _):
        return f"£{x / 1000:.0f} bn"

    ax_chart.yaxis.set_major_formatter(ticker.FuncFormatter(billions_formatter))
    ax_chart.grid(axis='y', linestyle='--', alpha=0.7)

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
            cell_colors.append(['magenta' if val == other_true_symbol else 'whitesmoke' for val in table_data[i]])
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
    plt.show()
