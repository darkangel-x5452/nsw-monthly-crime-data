#########################################################################################################
#   Program Name : NSW_SUBURB_CRIME_FIGURES_LOAD.py                                                     #
#   Data Source:                                                                                        #
#       Crime Figures: "https://data.nsw.gov.au/data/dataset/crime-data-by-offence"                     #
#       Postcodes: "https://auspost.com.au/business/marketing-and-communications/                       #
#                  access-data-and-insights/address-data/postcode-data",                                #
#                  "https://postcodes-australia.com/state-postcodes/nsw"                                #
#   Program Description:                                                                                #
#   This program transforms csv data into a sql db for NSW monthly crime data figures.                  #
#   Also adds in postcodes to the suburbs that match the name                                           #
#                                                                                                       #
#   Comment                                         Date                  Author                        #
#   ================================                ==========            ================              #
#   Initial Version                                 23/06/2019            Samson Leung                  #
#########################################################################################################


import logging
import json
import sqlite3
import pandas as pd

logging.basicConfig(format="%(asctime)s [%(levelname)s]: %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


FILE_DATA = "SuburbData2018.csv"
FILE_PC = "nsw_postcodes.json"
FILE_SQL = "NSW_Suburb_Crime_Data_Jan-95_Dec-18.sqlite"
TABLE_NAME = "NSW_Suburb_Crime_Data_Jan-95_Dec-18"

DATES = ["Jan 1995", "Feb 1995", "Mar 1995", "Apr 1995", "May 1995", "Jun 1995", "Jul 1995", "Aug 1995", "Sep 1995", "Oct 1995", "Nov 1995", "Dec 1995", "Jan 1996", "Feb 1996", "Mar 1996", "Apr 1996", "May 1996", "Jun 1996", "Jul 1996", "Aug 1996", "Sep 1996", "Oct 1996", "Nov 1996", "Dec 1996", "Jan 1997", "Feb 1997", "Mar 1997", "Apr 1997", "May 1997", "Jun 1997", "Jul 1997", "Aug 1997", "Sep 1997", "Oct 1997", "Nov 1997", "Dec 1997", "Jan 1998", "Feb 1998", "Mar 1998", "Apr 1998", "May 1998", "Jun 1998", "Jul 1998", "Aug 1998", "Sep 1998", "Oct 1998", "Nov 1998", "Dec 1998", "Jan 1999", "Feb 1999", "Mar 1999", "Apr 1999", "May 1999", "Jun 1999", "Jul 1999", "Aug 1999", "Sep 1999", "Oct 1999", "Nov 1999", "Dec 1999", "Jan 2000", "Feb 2000", "Mar 2000", "Apr 2000", "May 2000", "Jun 2000", "Jul 2000", "Aug 2000", "Sep 2000", "Oct 2000", "Nov 2000", "Dec 2000", "Jan 2001", "Feb 2001", "Mar 2001", "Apr 2001", "May 2001", "Jun 2001", "Jul 2001", "Aug 2001", "Sep 2001", "Oct 2001", "Nov 2001", "Dec 2001", "Jan 2002", "Feb 2002", "Mar 2002", "Apr 2002", "May 2002", "Jun 2002", "Jul 2002", "Aug 2002", "Sep 2002", "Oct 2002", "Nov 2002", "Dec 2002", "Jan 2003", "Feb 2003", "Mar 2003", "Apr 2003", "May 2003", "Jun 2003", "Jul 2003", "Aug 2003", "Sep 2003", "Oct 2003", "Nov 2003", "Dec 2003", "Jan 2004", "Feb 2004", "Mar 2004", "Apr 2004", "May 2004", "Jun 2004", "Jul 2004", "Aug 2004", "Sep 2004", "Oct 2004", "Nov 2004", "Dec 2004", "Jan 2005", "Feb 2005", "Mar 2005", "Apr 2005", "May 2005", "Jun 2005", "Jul 2005", "Aug 2005", "Sep 2005", "Oct 2005", "Nov 2005", "Dec 2005", "Jan 2006", "Feb 2006", "Mar 2006", "Apr 2006", "May 2006", "Jun 2006", "Jul 2006", "Aug 2006", "Sep 2006", "Oct 2006", "Nov 2006", "Dec 2006", "Jan 2007", "Feb 2007", "Mar 2007", "Apr 2007", "May 2007", "Jun 2007", "Jul 2007", "Aug 2007", "Sep 2007", "Oct 2007", "Nov 2007", "Dec 2007", "Jan 2008", "Feb 2008", "Mar 2008", "Apr 2008", "May 2008", "Jun 2008", "Jul 2008", "Aug 2008", "Sep 2008", "Oct 2008", "Nov 2008", "Dec 2008", "Jan 2009", "Feb 2009", "Mar 2009", "Apr 2009", "May 2009", "Jun 2009", "Jul 2009", "Aug 2009", "Sep 2009", "Oct 2009", "Nov 2009", "Dec 2009", "Jan 2010", "Feb 2010", "Mar 2010", "Apr 2010", "May 2010", "Jun 2010", "Jul 2010", "Aug 2010", "Sep 2010", "Oct 2010", "Nov 2010", "Dec 2010", "Jan 2011", "Feb 2011", "Mar 2011", "Apr 2011", "May 2011", "Jun 2011", "Jul 2011", "Aug 2011", "Sep 2011", "Oct 2011", "Nov 2011", "Dec 2011", "Jan 2012", "Feb 2012", "Mar 2012", "Apr 2012", "May 2012", "Jun 2012", "Jul 2012", "Aug 2012", "Sep 2012", "Oct 2012", "Nov 2012", "Dec 2012", "Jan 2013", "Feb 2013", "Mar 2013", "Apr 2013", "May 2013", "Jun 2013", "Jul 2013", "Aug 2013", "Sep 2013", "Oct 2013", "Nov 2013", "Dec 2013", "Jan 2014", "Feb 2014", "Mar 2014", "Apr 2014", "May 2014", "Jun 2014", "Jul 2014", "Aug 2014", "Sep 2014", "Oct 2014", "Nov 2014", "Dec 2014", "Jan 2015", "Feb 2015", "Mar 2015", "Apr 2015", "May 2015", "Jun 2015", "Jul 2015", "Aug 2015", "Sep 2015", "Oct 2015", "Nov 2015", "Dec 2015", "Jan 2016", "Feb 2016", "Mar 2016", "Apr 2016", "May 2016", "Jun 2016", "Jul 2016", "Aug 2016", "Sep 2016", "Oct 2016", "Nov 2016", "Dec 2016", "Jan 2017", "Feb 2017", "Mar 2017", "Apr 2017", "May 2017", "Jun 2017", "Jul 2017", "Aug 2017", "Sep 2017", "Oct 2017", "Nov 2017", "Dec 2017", "Jan 2018", "Feb 2018", "Mar 2018", "Apr 2018", "May 2018", "Jun 2018", "Jul 2018", "Aug 2018", "Sep 2018", "Oct 2018", "Nov 2018", "Dec 2018"]
DATE_FORMAT = '%b %Y'


def load_csv():
    logger.info("Loading csv")
    data = pd.read_csv(FILE_DATA)
    return data


def add_postcodes(data, pc_data):
    logger.info("Adding postcode")

    # Make the Postcode Column initially with uppercase Suburb,then replace with postcode later.
    data['RELATIVE_POSTCODE(S)'] = data.loc[:, "Suburb"].str.upper()
    for key, val in pc_data['result'].items():
        key_upper = key.upper()
        check_suburb = data['RELATIVE_POSTCODE(S)'].str.contains(key_upper)

        if any(check_suburb):
            idx_list = data.index[data['RELATIVE_POSTCODE(S)'] == key_upper].tolist()
        else:
            continue
        for i in idx_list:
            data.at[i, 'RELATIVE_POSTCODE(S)'] = ", ".join(val)
    return data


def load_pc():
    logger.info("Loading postcode file")
    with open(FILE_PC) as f:
        f_json = json.load(f)
    return f_json


def melt_csv(csv_updated):
    logger.info("Melting and cleaning dataframe")
    data_melt = pd.melt(csv_updated, id_vars=['Suburb', 'RELATIVE_POSTCODE(S)', 'Offence category', 'Subcategory'],
                        value_vars=DATES)

    data_melt['variable'] = pd.to_datetime(data_melt['variable'].astype(str), format=DATE_FORMAT)
    data_melt['variable'] = data_melt['variable'].dt.strftime('%B %Y')
    data_melt.rename(columns={'variable': 'PERIOD',
                              'value': 'COUNT'},
                     inplace=True)
    data_melt.columns = data_melt.columns.str.upper()
    data_melt.columns = data_melt.columns.str.replace(" ", "_")

    return data_melt


def create_sql(data_melt):
    logger.info("Saving dataframe to sqlite")
    conn = sqlite3.connect(FILE_SQL)

    data_melt.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)


if __name__ == '__main__':
    data = load_csv()
    pc_data = load_pc()
    csv_updated = add_postcodes(data, pc_data)
    csv_melted = melt_csv(csv_updated)
    create_sql(csv_melted)

