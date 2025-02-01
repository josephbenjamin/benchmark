import pandas as pd
import rules_engine as re
import data_processing as dp

# Load and filter data
df = dp.load_data()
df = dp.filter_conventional_gilts(df)

# Generate a date range from today to a specified end date
start_date = pd.to_datetime("today").normalize()
end_date = pd.to_datetime('2030-01-01').normalize()
date_range = pd.date_range(start=start_date, end=end_date, freq='D')

# Create a new DataFrame to store results
benchmark_results = pd.DataFrame({'DATE': date_range})
icma_benchmarks = []

# Loop through each date and print progress
for i, date in enumerate(date_range):
    formatted_date = date.strftime('%Y-%m-%d')
    benchmark = re.get_icma_benchmark(df, formatted_date)

    # Print progress
    print(f"Processing {i + 1}/{len(date_range)}: Date = {formatted_date}, ICMA Benchmark = {benchmark}")

    icma_benchmarks.append(benchmark)

# Store results in DataFrame
benchmark_results['ICMA_BENCHMARK'] = icma_benchmarks

# Count how many dates have None as the ICMA benchmark result
none_count = benchmark_results['ICMA_BENCHMARK'].isna().sum()


# Identify which gilts have not been used as a benchmark
unused_gilts = df[~df['REDEMPTION_DATE'].isin(benchmark_results['ICMA_BENCHMARK'].dropna())]
used_gilts = df[df['REDEMPTION_DATE'].isin(benchmark_results['ICMA_BENCHMARK'].dropna())]
# Display results
print(f"Number of dates with no ICMA benchmark result: {none_count}")
none_pct = none_count / len(benchmark_results)
print(f'No benchmark found {none_pct} of the time.')
print(used_gilts.head(20))
print(unused_gilts.head(20))