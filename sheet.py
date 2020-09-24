from oauth2client.service_account import ServiceAccountCredentials
import gspread
from secrets import GOOGLE_CREDENTIALS

# open the sheet using API
def open_sheet(sheet_url):

    json_key = GOOGLE_CREDENTIALS
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDENTIALS, scope)

    gc = gspread.authorize(credentials)

    wks = gc.open_by_url(sheet_url).get_worksheet(0)
    # connection established
    print("Connection to sheet established")
    return wks


def next_available_row(wks):
    str_list = list(filter(None, wks.col_values(1)))  # fastest
    return str(len(str_list)+1)

def get_last_N_rows(wks,N):
    curr_last=int(next_available_row(wks))-1
    values_list = []
    for row_num in range(curr_last-N,curr_last):
        row_val=wks.row_values(row_num)
        if row_val is not None:
            values_list.append(wks.row_values(row_num))

    return values_list
