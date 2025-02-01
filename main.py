import data_processing as dp
import rules_engine as re
import visualisation as vis

def main():

    # Scrape or load date
    # df = dp.scrape_data()
    df = dp.load_data()
    df = dp.filter_conventional_gilts(df)
    df = re.apply_rules(df, '2025-01-01')
    vis.show_gilts(df)

if __name__ == '__main__':
    main()