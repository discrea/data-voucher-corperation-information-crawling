# Modules Import
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import datetime
'''
아래 라이브러리는 
"파이썬 SELENIUM 으로 다나와 제품 리스트 크롤링":https://link2me.tistory.com/2002 참조
'''
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
'''
아래 라이브러리는 
"tkinter를 이용한 메시지 박스 (message box) 위젯 만들기":https://blog.naver.com/PostView.nhn?isHttpsRedirect=true&blogId=amethyst_lee&logNo=222021293449&parentCategoryNo=&categoryNo=&viewDate=&isShowPopularPosts=false&from=postView 참조
'''
import tkinter.messagebox as msgbox
'''
아래 라이브러리는 
"Python - 문자열에서 숫자만 추출하는 방법":https://codechacha.com/ko/python-extract-integers-from-string/ 참조
'''
import re
'''
아래 라이브러리는 
"json.loads() 함수 사용하기":https://www.freecodecamp.org/korean/news/pythonyi-json-munjayeoleul-jsoneuro-byeonhwanhaneun-bangbeob/ 참조
'''
import json
import pickle


'''[func] 로그 저장'''
def save_log(subject = 'unTitled', log = 'None', format = 'txt'):
  timeNow = str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
  fileName = './log/' + timeNow + '-' + subject + '.' + format
  with open(fileName,'a+', encoding='utf-8') as f:
    f.write(log)
  
  # print(fileName+' <== created')
  return 0

'''[func] 각 상품 호출 함수 리스트로 뽑는 함수'''
def get_func_lst(soup):
  WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="listType"]')))

  targetListMetaInfo = soup.find(id = "listType")
  targetListFunctionInfo = targetListMetaInfo.find_all('a', href="#")
  rdrctFunctionPramLst = []
  
  for tgtFuncInfo in targetListFunctionInfo:
    singleRedirectionFunction = str(tgtFuncInfo)
    start = singleRedirectionFunction.find('fn_prdcDetail')
    end = singleRedirectionFunction.find('; return false;">')
    singleRdctFuncPram = singleRedirectionFunction[start:end+1]
    rdrctFunctionPramLst.append(singleRdctFuncPram)
    
  '''중복, 널 제거, 리스트 타입'''
  result = list(filter(None, set(rdrctFunctionPramLst)))
  
  return result


'''에러로그 숨기기
[3536:9380:1214/155851.502:ERROR:device_event_log_impl.cc(215)] [15:58:51.502] USB: 
usb_device_handle_win.cc:1045 Failed to read descriptor from node connection: ýۿ  ġ 
۵ ʽ��ϴ. (0x1F)

[32296:40388:1214/155728.758:ERROR:ssl_client_socket_impl.cc(982)] handshake failed; returned -1, SSL error code 1, net_error -200

터미널에 표시되는 것 숨기는 옵션
'''
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome('chromedriver.exe', options=options)
driver.implicitly_wait(3)
driver.get('https://kdata.or.kr/datavoucher/is/selectPortalSearch.do')

'''fn_prdcDetail 호출 test
  * "selenium 자바스크립트 함수 작동시켜서 웹크롤링하기":https://dev-dain.tistory.com/13
  * "selenium을 이용해 크롤링하기3 (자바스크립트 사용)":https://yukifox.tistory.com/6
    참조하여 fn_prdcDetail 호출 test

# time.sleep(3) 
driver.execute_script("fn_prdcDetail('2022', '6068611615', 'P01014002', '', 'P11014001');")

↑↑↑↑ 성공 ↑↑↑↑


'''
'''※ 데이터바우처 웹 함수 정리 ※

    1. fn_isTabType('prcs')                                   => 가공서비스
    2. fn_isTabType('file')                                   => 데이터상품
    3. fn_prdcDetail({연도}, {식별값}, {식별값}, '', {식별값})  => 가공서비스 타깃

'''
'''※ 가공서비스 파일 상품 리스트 path ※
selector
  #listType
xpath
  //*[@id="listType"]
full xpath
  /html/body/div[4]/form[1]/div[2]/div/div/div/div[8]/div[2]
'''

soup = BeautifulSoup(driver.page_source, 'html.parser') # web 파싱
pageSoup = soup.find(id='paging') # page 부분 찾기
lastPage = int(re.findall(r'\d+', str(pageSoup))[-1]) # 끝페이지 확인
# lastPage = 3

timeStamp = str(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
filePathService = './result/'+timeStamp+'-service.pickle'
filePathData = './result/'+timeStamp+'-data.pickle'
filePathLog = './result/'+timeStamp+'-log.txt'

'''각 페이지 순회 루프 시작'''
for pageNo in range(1,lastPage+1): 
  
  
  '''가공서비스 페이지 접근'''
  driver.execute_script("fn_isTabType('prcs');")  # 가공서비스
  # driver.execute_script("fn_isTabType('file');")  # 데이터상품
  '''상품리스트 로딩 대기'''
  WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="listType"]')))

  driver.execute_script("fn_egov_link_page("+str(pageNo)+");")
  WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="listType"]')))
  soup = BeautifulSoup(driver.page_source, 'html.parser')
  servicingCorpRedirectionList = get_func_lst(soup)
  # for result in servicingCorpRedirectionList:
  #   save_log('redirectionList', result, 'txt')  # chk
  '''페이지별 상품 순회 시작'''
  # print('page :',pageNo)  # chk
  
  processInfo = 'page : '+format(pageNo, '03')+'/'+format(lastPage+1, '03')+' | element : '+str(len(servicingCorpRedirectionList))
  
  print(processInfo)
  with open(filePathLog,'a+') as f:
    f.write(processInfo)
  
  if len(servicingCorpRedirectionList) == 0: break
  
  for servicingCorpRedirectionInfo in servicingCorpRedirectionList:
    # print(servicingCorpRedirectionInfo)  # chk
    driver.execute_script(servicingCorpRedirectionInfo)
    WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH,'//*[@id="frm"]/div[2]/div/div/div/div/div[1]/ul[2]/li[2]/dl/dd')))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    corpInfoListSoup = soup.find_all(class_="company_explanation")
    corpInfoDictionary = {}
    
    
    for corpInfo in corpInfoListSoup:
      infoPart = list(filter(len, corpInfo.get_text().split('\n')))
      if len(infoPart) < 2: infoPart.append('')
      corpInfoDictionary[infoPart[0]] = infoPart[1]
    
    with open(filePathService, 'ab+') as f:
      pickle.dump(corpInfoDictionary,f)


msgbox.showinfo("완료","확인")