# author: Tiffany Timbers & Jordan Bourak
# date: 2021-11-22
# Adapted from github.com/ttimbers/equine_numbers_value_canada_parameters
# Conversion from R to Python done using ChatGPT

import click
import pandas as pd
import altair as alt
#from altair_saver import save
import os

# Ensure Altair charts can be saved as PNG
#alt.renderers.enable('altair_saver', fmts=['png', 'svg'])

# Function to create the directory if it doesn't exist
def create_dir_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Main function
@click.command()
@click.option('--input_dir', required=True, help='Path (including filename) to raw data')
@click.option('--out_dir', required=True, help='Path to directory where the results should be saved')
def main(input_dir, out_dir):
    create_dir_if_not_exists(out_dir)

    # Load the data and do some pre-processing
    horse_pop = pd.read_csv(input_dir)
    horse_pop = horse_pop.query('DATE == "At June 1 (x 1,000)" and GEO != "Canada"')
    horse_pop['GEO'] = horse_pop['GEO'].replace({"Prince Edward Island": "P.E.I."})
    horse_pop['Value'] = horse_pop['Value'] * 1000
    horse_pop['Ref_Date'] = horse_pop['Ref_Date'].astype(str)

    # Generate plot for historical number of horses per province in Canada
    chart = alt.Chart(horse_pop).mark_line().encode(
        x=alt.X('Ref_Date:T', title="Year"),
        y=alt.Y('Value:Q', title="Number of horses")
    ).properties(
        title='Historical number of horses per province in Canada'
    ).facet(
        'GEO:N',
        columns=3
    )

    chart.save(os.path.join(out_dir, 'horse_pops_plot.png'), scale_factor=2.0)
    #save(chart, os.path.join(out_dir, 'horse_pops_plot.png'))

    # Generate table with max, min, and standard deviation of number of horses
    horses_sd = horse_pop.groupby('GEO')['Value'].agg(Std='std').reset_index().rename(columns={'GEO': 'Province'}).sort_values(by='Std', ascending=False)
    horses_sd.to_csv(os.path.join(out_dir, 'horses_sd.csv'), index=False)

    # Generate plot for historical number of horses for the province
    # with the largest standard deviation only
    largest_sd_prov = horses_sd.iloc[0]['Province']
    horse_pop_largest_sd = horse_pop[horse_pop['GEO'] == largest_sd_prov]

    chart_largest_sd = alt.Chart(horse_pop_largest_sd).mark_line().encode(
        x=alt.X('Ref_Date:T', title="Year"),
        y=alt.Y('Value:Q', title="Number of horses")
    ).properties(
        title=f'Historical number of horses in {largest_sd_prov}'
    )

    chart_largest_sd.save(os.path.join(out_dir, 'horse_pops_plot_largest_sd.png'), scale_factor=2.0)
    #save(chart_largest_sd, os.path.join(out_dir, 'horse_pop_plot_largest_sd.png'))

if __name__ == '__main__':
    main()
