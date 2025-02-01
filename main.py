import data_processing as dp
import rules_engine as re
import visualisation as vis
from rules_engine import get_icma_benchmark


def main():

    # Scrape or load date
    # df = dp.scrape_data()
    df = dp.load_data()
    df = dp.filter_conventional_gilts(df)

    nim = '2030-01-01' # New Issue Maturity
    print('Test get_icma_benchmark')
    print(get_icma_benchmark(df, nim))
    df = re.apply_rules(df, nim)

    vis.show_gilts(df, nim)

if __name__ == '__main__':
    main()