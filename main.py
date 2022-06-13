import yaml
import logging
import requests
from lxml import etree

# 設置logging格式
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

def serializeString(string: str) -> str:
    """歸一化文字

    Args:
        string (str): 目標文字

    Returns:
        str: 歸一化文字
    """
    return string.replace(bytearray.fromhex("0d").decode(), '') \
                 .replace(bytearray.fromhex("0a").decode(), '') \
                 .replace(bytearray.fromhex("09").decode(), '') \
                 .replace(bytearray.fromhex("20").decode(), '')

if __name__ == '__main__':
    # 讀取設定檔
    with open('config.yaml', 'r', encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # 創建會話
    query_session = requests.Session()
    # 設置headers
    DEFAULT_HEADERS = {
        'user-agent': config['SETTINGS']['USER_AGENT'] #偽造User-Agent
        }
    query_session.headers = DEFAULT_HEADERS

    # 獲取考試預約頁面
    exam_data = {
        'dmvNo': config['EXAM_DATA']['DMV_NO'],
        'dmvNoLv1': config['EXAM_DATA']['DMV_NO_LV_1'],
        'expectExamDateStr': config['EXAM_DATA']['EXPECT_EXAM_DATE_STR'],
        'licenseTypeCode': config['EXAM_DATA']['LICENSE_TYPE_CODE'],
        'method': 'query',
        'onlyWeekend': config['EXAM_DATA']['ONLY_WEEKEND'],
        'secId': ''
    }
    exam_page = query_session.post(config['SETTINGS']['EXAM_RESERVE_URL'], data = exam_data)

    # 分析查詢結果頁面
    exam_page_etree = etree.HTML(exam_page.text)
    exam_day_list = exam_page_etree.xpath('//table[@id="trnTable"]/tbody/tr')

    # 分析查詢結果
    exams = list()
    for exam in exam_day_list:
        date = serializeString(exam.xpath('./td')[0].text)
        description = serializeString(exam.xpath('./td')[1].text)
        number = serializeString(exam.xpath('./td')[2].text)
        exams.append({
            'date': date,
            'description': description,
            'number': number
        })

    # 展示結果
    print('日期\t\t\t說明\t\t人數')
    for exam in exams:
        print("{}\t{}\t{}".format(exam['date'], exam['description'], exam['number']))