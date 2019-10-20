# -*- coding: utf-8 -*-
"""
提示： 
1. 默认是 《头号玩家》电影，如果要换其它电影，请上 https://movie.douban.com/
选择自己喜欢的书，将网址中的选择自己喜欢的书，将网址中的4920389 替换为 新数目网址中的7位数字id。
在这一行代码进行替换     requrl = 'https://movie.douban.com/subject/4920389/comments/'+'?' +'start=' + str(start) + '&limit=20' 

2. 在第73行： for i in range(10): 语句中可以修改数字10，表示爬取多少页的评论，默认为10页。

3. 如果不想其中某个词出现，请在程序所在文件夹中的stopwords.txt文件中增加对应内容。

4. 所抓取的评论以excel形式存在程序目录下的text-movie.xls文件中，可自己修改文件名
在代码行修改保存的excel文件名称： pd.DataFrame(df2).to_excel("text-movie.xls",sheet_name="sheet1",index=False,header=True)
"""

# coding: utf-8  有中文，所以这样，不然乱码
import datetime
import jieba  # 分词包
import numpy  # numpy计算包
import codecs  # codecs提供的open方法来指定打开的文件的语言编码，它会在读取的时候自动转换为内部unicode
import re
import pandas as pd
import matplotlib.pyplot as plt
from urllib import request
from bs4 import BeautifulSoup as bs
import matplotlib
import xlwt
import operator
from functools import reduce
from wordcloud import WordCloud


def getComments(pageNum):
    eachCommentList = []
    eachDateList = []
    eachRatingList = []
    if pageNum > 0:
        start = (pageNum-1) * 20
    else:
        return False
    requrl = 'https://movie.douban.com/subject/26794435/comments' + \
        '?' + 'start=' + str(start) + '&limit=20' + '&sort=new_score&status=P'

    #requrl = 'https://movie.douban.com/subject/26794435/comments' + \
    #    '?' + 'start=' + str(start) + '&limit=20' + '&sort=time&status=P'
    print(requrl)

    resp = request.urlopen(requrl)
    html_data = resp.read().decode('utf-8')  # 有中文，所以要转码
    
    soup = bs(html_data, 'html.parser')  # 用美丽汤先进先进行分析
    # 找到所有<div, class = 'comment'>的部分
    comment_div_lits = soup.find_all('div', class_='comment')
    for item in comment_div_lits:
        if item.find_all('p'):
            # 准确的找到comment所在的那个<span>
            eachCommentList.append(item.find_all('span', class_='short')[0].string.string.strip('\n '))#crop /n and space
            tmpDate = item.find_all('span')[-2].string.strip('\n ')
            eachDateList.append(tmpDate)
            Rating = str(item.find_all('span')[-3])
            position_rating = Rating.find('rating')
            #print(position_rating)
            
            eachRatingList.append(str(Rating[position_rating-3:position_rating-1]))
    #print (eachCommentList[0], eachDateList[0])
    #print(eachRatingList)
    return eachCommentList, eachDateList, eachRatingList  # 组合评论


def main():
    commentList = []
    dateList = []
    ratingList = []
    for i in range(10):
        num = i + 1
        [commentList_temp, dateList_temp, ratingList_temp] = getComments(num)
        commentList.append(commentList_temp)
        dateList.append(dateList_temp)
        ratingList.append(ratingList_temp)

    commentList = reduce(operator.add, commentList)
    dateList = reduce(operator.add, dateList)
    ratingList = reduce(operator.add, ratingList)

    # write the original data
    dataTmp = {'comments': commentList[:], 'date': dateList[:], 'Rating': ratingList[:]}
    df2 = pd.DataFrame(dataTmp)
    #pd.DataFrame(df2).to_excel("text-movie.xls",
    #                           sheet_name="sheet1", index=False, header=True)
    writer = pd.ExcelWriter("text-movie.xls")
    df2.to_excel(excel_writer=writer,sheet_name='sheet1', index=False, header=True)
    
    

    # sorting data with date
    
    #print('date', dateList[-1],dateList[0])
    lst_lastDate = dateList[-1].split('-')
    lst_firstDate = dateList[0].split('-')
    
    dat_lastDate = datetime.date(int(lst_lastDate[0]),int(lst_lastDate[1]),int(lst_lastDate[2]))
    dat_firstDate = datetime.date(int(lst_firstDate[0]),int(lst_firstDate[1]),int(lst_firstDate[2]))
    if (dat_firstDate-dat_lastDate).days < 0:
        dat_lastDate, dat_firstDate = dat_firstDate, dat_lastDate
    dat_dateList = []
    for item in dateList:
        lst_tmp = item.split('-')
        dat_tmp = datetime.date(int(lst_tmp[0]),int(lst_tmp[1]),int(lst_tmp[2]))
        dat_dateList.append(dat_tmp)
        if (dat_firstDate-dat_tmp).days < 0:
            dat_firstDate = dat_tmp
        if (dat_lastDate-dat_tmp).days > 0:
            dat_lastDate = dat_tmp
    dat_interval = (dat_firstDate-dat_lastDate).days
    print('From ', dat_lastDate, ' to ', dat_firstDate, '. ', dat_interval, 'days.')
    dateList2 = []
    ratingList2 =[]
    countList2 = []
    for k in range(dat_interval):
        time = datetime.timedelta(days=k)

        dateList2.append (dat_firstDate-time)
        ratingList2.append (0)
        countList2.append (0)

    for k in range(len(dat_dateList)):
        dat_interval = (dat_firstDate-dat_dateList[k]).days
        dat_interval -= 1
        countList2[dat_interval] += 1
        if ratingList[k] == 'pa':
            ratingList[k] = '0'
        ratingList2[dat_interval] += (float(ratingList[k])-ratingList2[dat_interval])/countList2[dat_interval]
    dataTmp = {'Date': dateList2[:], 'Rating': ratingList2[:], 'Vote': countList2[:]}
    df2 = pd.DataFrame(dataTmp)
    df2.to_excel(excel_writer=writer, sheet_name='sheet2', index=False, header=True)
    writer.save()
    writer.close()
    #draw a histogramfor the variation of rating with time
    fig=plt.figure()
    ax1=fig.add_subplot(3,1,1)
    ax2=fig.add_subplot(3,1,2)
    ax3=fig.add_subplot(3,1,3)
    #index = numpy.arange(len(dat_dateList))
    bar_width = 0.35
    rects1=ax1.bar(dateList2, ratingList2, bar_width, color='b', label='Rating')
    rects2=ax2.bar(dateList2, countList2, bar_width, color='r', label='Voting')


   
    comments = ''
    for k in range(len(commentList)):
        comments = comments + (str(commentList[k])).strip()

    pattern = re.compile(r'[\u4e00-\u9fa5]+')
    filterdata = re.findall(pattern, comments)  # 过滤标点 用正则表达式
    cleaned_comments = ''.join(filterdata)

    segment = jieba.lcut(cleaned_comments)
    # 请实践 -- 调整分词
    #https://github.com/fxsjy/jieba  结巴分词的网站
    #使用 add_word(word, freq=None, tag=None) 和 del_word(word) 可在程序中动态修改词典。
    #使用 suggest_freq(segment, tune=True) 可调节单个词语的词频，使其能（或不能）被分出来。
    #jieba.add_word('孟晚舟')
    #jieba.del_word('今天天气')
    #jieba.suggest_freq(('今天', '天气'), True)
    
    words_df = pd.DataFrame({'segment': segment})  # 割词

    stopwords = pd.read_csv("stopwords.txt", index_col=False, quoting=3, sep="\t", names=['stopword'],
                            encoding='utf-8')
    # -- 请实践： 停止词， 在 stopwords.txt 文件中，可以添加和修改停止词。 
    # 例如将 “电影” 这个词加入到 stopwords文件中，
    words_df = words_df[~words_df.segment.isin(stopwords.stopword)]

    words_stat = words_df.groupby(by=['segment'])[
        'segment'].agg({"计数": numpy.size})
    words_stat = words_stat.reset_index().sort_values(
        by=["计数"], ascending=False)
    print(words_stat.head())  # 数词

    wordcloud = WordCloud(font_path="simhei.ttf",
                          background_color="white", max_font_size=80)
    word_frequence = {x[0]: x[1] for x in words_stat.head(1000).values}  # 画图

    word_frequence_list = []
    for key in word_frequence:
        temp = (key, word_frequence[key])
        word_frequence_list.append(temp)

    wordcloud = wordcloud.fit_words(dict(word_frequence_list))
    
    ax3.imshow(wordcloud)
    plt.show() 

main()
