import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def FMPNews(page=0, num_articles=1):
    key = config.get('FMP','API_KEY')
    return f'https://financialmodelingprep.com/api/v3/fmp/articles?page={page}&size={size}&apikey={key}'

