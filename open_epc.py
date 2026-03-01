import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class OpenBEM:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_data(self):
        self.df = pd.read_csv(self.file_path, low_memory=False)

    def process_data(self):
        energy_rating_order = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        self.df['CURRENT_ENERGY_RATING'] = pd.Categorical(self.df['CURRENT_ENERGY_RATING'], \
                                                          categories=energy_rating_order, ordered=True)

    def numberEPCs(self):
        log_by_la = self.df['LOCAL_AUTHORITY'].value_counts()
        la = self.df['LOCAL_AUTHORITY_LABEL'].value_counts()
        la_name = la.idxmax()
        sum_la_count = log_by_la.sum()
        no_EPCs = f'In the latest data release, there are {sum_la_count} EPC lodgments in \
                    {la_name}'

        return no_EPCs, la_name

    def save_plot(self, figure, plot_name):
        figure.savefig(os.path.join(plot_name))
        plt.close()

    def plot_energy_bands(self, authority_name):
        energy_rating_order = self.df['CURRENT_ENERGY_RATING'].cat.categories
        energy_rating_counts = self.df['CURRENT_ENERGY_RATING'].value_counts().reset_index()
        energy_rating_counts.columns = ['CURRENT_ENERGY_RATING', 'Number of Records']

        plt.figure(figsize= (10, 6))
        sns.barplot(x = 'Number of Records', y = 'CURRENT_ENERGY_RATING', data=energy_rating_counts, \
                    order=energy_rating_order)
        sns.barplot(x='Number of Records', y= 'CURRENT_ENERGY_RATING', data=energy_rating_counts,
                    order= energy_rating_order) 

        plt.xlabel('Number of Records')
        plt.ylabel('Current Energy Ratings')
        plt.title('Distribution of Energy Ratings in '+ str(authority_name))
        plt.tight_layout()

        self.save_plot(plt, 'plots/horizontal_bar_plot_rating_records in ' +str(authority_name)+'.png')

    def plot_property_type_count(self, authority_name):
        plt.figure(figsize=(12,6))
        sns.countplot(x='PROPERTY_TYPE', data=self.df)
        plt.xticks(rotation=45)
        plt.xlabel('Property Type')
        plt.ylabel('Count')
        plt.savefig(os.path.join('plots/bar_chart_count_prop_by_type in '+str(authority_name)+'.png'))
        plt.close()

    def make_report(self, authority_name):
        pdf_doc = SimpleDocTemplate("reports/open_epc_report_for_"+str(authority_name)+".pdf", pagesize=letter)
        content = []

        # Add title and sub title to report
        title = "Open EPC report for "+str(authority_name)
        content.append(Paragraph(title, getSampleStyleSheet()['Title']))
        content.append(Spacer(1, 12))
        content.append(Paragraph(numberEPC, getSampleStyleSheet()['BodyText']))

        # Add plots to report
        content.append(Image('plots/bar_chart_count_prop_by_type in ' +str(authority_name)+'.png', width =400, height=300))
        content.append(Image('plots/horizontal_bar_plot_rating_records in '+str(authority_name)+'.png', width= 400, height=300))

        # Make report
        pdf_doc.build(content)

# Use argparse to pass input file
parser = argparse.ArgumentParser(description='OpenEPC reports')
parser.add_argument('-i', '--input-file', help='path to certificates.csv file in open epc data')
args = parser.parse_args()
file_path = args.input_file

open_epc = OpenBEM(file_path)
open_epc.read_data()
open_epc.process_data()
numberEPC, local_authority_name = open_epc.numberEPCs()
open_epc.plot_energy_bands(local_authority_name)
open_epc.plot_property_type_count(local_authority_name)
open_epc.make_report(local_authority_name)
