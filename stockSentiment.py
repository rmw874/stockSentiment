import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def FMPNews(page=0, size=5):
    key = config.get('FMP','API_KEY')
    return f'https://financialmodelingprep.com/api/v3/fmp/articles?page={page}&size={size}&apikey={key}'

print(FMPNews())