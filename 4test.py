import json
import re
import pandas as pd
import requests
import time
import random

requests.packages.urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0',
           'Authorization': 'token c975d26b6bcf32ac062c917744bb7efa37bf9d25',# 自行配置
           # 需配置token的值,访问https://github.com/settings/tokens/new
           'Content-Type': 'application/json',
           'Retry-After': '30',
           'Accept': 'application/vnd.github.v3.text-match+json'  # 一般特殊请求头application/vnd.github.v3+json
           }


def search(query):
    start = time.time()
    matches_urls = []
    matches_contents = []
    for page in range(1, 11):  # 爬取前10页1000条
        # url = f'https://api.github.com/search/code?q={query}&page={page}&per_page=100&sort=stars&order=desc'  # per_page最大值只有100
        url = f'https://api.github.com/search/code?q={query}&page={page}&per_page=100&sort=stars&order=desc'
        print(url)
        resp = requests.get(url, headers = headers)
        resp_s = resp.status_code
        print(resp_s)
        resp_t = resp.text
        resp_tl = len(resp_t)
        print(resp_t)
        resp_j = resp.json()

        if resp_s == 401 and 'Bad credentials' in resp_t:
            print('Authorization失效、尝试配置正确的token···')
            break

        if resp_s == 403 and 'exceeded a secondary rate limit' in resp_t:
            print('API爬取过快、等个半分钟试试···')
            break

        if resp_s == 422:
            print('仅支持爬取搜索到前1000条哦···')
            break

        if resp_s == 200 and resp_j['total_count'] == 0:
            print('未搜到相关代码、换换关键字试试···')
            break

        if resp_s == 200 and resp_j['total_count']:
            total_num = resp_j['total_count']
            print(f'搜索结果总数为{total_num}')
            resp_num = len(resp_j['items'])
            if resp_num != 0:
                print(f'第{page}页爬取条目数为{resp_num}')
                for i in range(0, resp_num):
                    matches_url = resp_j['items'][i]['html_url']
                    text_num = len(resp_j['items'][i]['text_matches'])
                    for j in range(0, text_num):
                        matches_content = resp_j['items'][i]['text_matches'][j]['fragment']
                        matches_urls.append(matches_url)
                        matches_contents.append(matches_content)
            else:
                break
        else:
            print('其他原因导致GG···')
        # if page < 11:
        t = random.randint(60, 66)
        print(f'github-api rate limit,sleeping for {t} s···')
        time.sleep(t)

    create_csv(query, matches_urls, matches_contents)
    stop = time.time()
    cost_time = stop - start
    print('任务完成、花费时间' + str(cost_time))

    # result_re =re.compile(r'"fragment":"([\s\S]*?)"matches"')#正则获取匹配结果
    # result = re.findall(result_re,resp_t)
    # if len(result) > 0:
    #     print(result)


def get_time():
    now = time.strftime("%m%d-%H%M", time.localtime(time.time()))
    return now


# 为输出的文件转义字符
def escape_char(query):
    if ':' in query:
        query = query.replace(':', '：')
    if '?' in query:
        query = query.replace('?', '？')
    if '<' in query:
        query = query.replace('<', '《')
    if '>' in query:
        query = query.replace('>', '》')
    if '\\' in query:
        query = query.replace('\\', '。')
    if '/' in query:
        query = query.replace('/', '。')
    if '|' in query:
        query = query.replace('|', '。')
    if '*' in query:
        query = query.replace('*', '。')
    if '"' in query:
        query = query.replace('"', '\'')
    return query[0:30]


def create_csv(query, matches_urls, matches_contents):
    datess = pd.DataFrame({'url': matches_urls, 'content': matches_contents})
    datess.to_csv(f'{get_time()}' + '(' + f'{escape_char(query)}' + ').csv', encoding = 'utf_8_sig')


if __name__ == "__main__":
    # try:#读文件关键字
    #     data = open("target-git.txt", 'r', encoding = 'utf-8')
    # except Exception as e:
    #     data = open("target-git.txt", 'r', encoding = 'GBK')
    # get_querys = data.readlines()
    # data.close()
    # for query in get_querys:
    #     search(query.strip())

    query = '''baidu.com'''#查询关键字
    search(query)
