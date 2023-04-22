# class로 만들기(객체지향)
# 변수는 지역, 날짜(요일)
# 서버에서 매일 또는 매주 실행해서 DB에 저장(2주~2달 사이 날짜 중 금토, 토일, 일월 최저가)
# 서버에서 하니 봇이라 안되는 경우 생기는 듯. 그냥 로컬 환경에서 실행하고 서버 DB에 저장하는 방법?

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from dataclasses import dataclass
import time


@dataclass
class Hotel:

    name: str = ''
    grade: str = ''
    rating: str = ''
    price: str = ''
    link: str = ''
    err_msg: str = ''


# 호텔스닷컴

def from_hotels_com(driver: WebDriver, start_date, end_date, destination):

    # 4세 아이 옵션으로 포함하려면 -> &children=1_4
    url = f'https://kr.hotels.com/Hotel-Search?adults=2&startDate={start_date}&endDate={end_date}&destination={destination}&mealPlan=FREE_BREAKFAST&star=40&star=50&guestRating=40&amenities=POOL&travelerType=FAMILY&sort=RECOMMENDED'

    data_list: list[Hotel] = []

    driver.get(url)
    time.sleep(2)

    hotel_elem_list = driver.find_elements(
        By.XPATH, '//div[@data-stid="property-listing-results"]/div')

    for hotel_elem in hotel_elem_list:
        hotel = Hotel()
        try:
            hotel.name = hotel_elem.find_element(By.TAG_NAME, 'h4').text
            hotel.grade = hotel_elem.find_element(By.XPATH,
                                                  ".//div[@class='uitk-rating']").text
            hotel.rating = hotel_elem.find_element(By.XPATH,
                                                   ".//span[@class='is-visually-hidden' and contains(text(), '이용 후기')]").text
            hotel.price = hotel_elem.find_element(By.XPATH,
                                                  ".//div[contains(text(), '현재 요금')]").text
            hotel.link = hotel_elem.find_element(By.XPATH,
                                                 ".//a[@data-stid='open-hotel-information']").get_attribute('href')
        except NoSuchElementException as e:
            hotel.err_msg = e.msg
        finally:
            data_list.append(hotel)
    # print(data_list)
    # driver.close()
    return data_list


# 네이버

def from_naver(driver, start_date, end_date, destination):
    if destination == '강원':
        destination = 'Gangwon_Province'
    elif destination == '경기':
        destination = 'Gyeonggi_Province'

    url = f'https://hotels.naver.com/list?placeFileName=place:{destination}&adultCnt=2&checkIn={start_date}&checkOut={end_date}&includeTax=true&facilities=7&starRatings=4%2C5&propertyTypes=0%2C7&guestRatings=8'

    data_list: list[Hotel] = []

    driver.get(url)
    time.sleep(2)

    hotel_elem_list = driver.find_elements(
        By.XPATH, "//li[contains(@class, 'SearchList_HotelItem')]")

    for hotel_elem in hotel_elem_list:
        hotel = Hotel()
        try:
            hotel.name = hotel_elem.find_element(By.TAG_NAME, 'h4').text
            hotel.grade = hotel_elem.find_element(By.XPATH,
                                                  ".//i[contains(@class, 'Detail_grade')]").text
            hotel.rating = hotel_elem.find_element(By.XPATH,
                                                   ".//i[contains(@class, 'Detail_score')]").text
            hotel.price = hotel_elem.find_element(By.XPATH,
                                                  ".//em[contains(@class, 'Price_show_price')]").text
            hotel.link = hotel_elem.find_element(By.XPATH,
                                                 ".//a[contains(@class, 'SearchList_anchor')]").get_attribute('href')
        except NoSuchElementException as e:
            hotel.err_msg = e.msg
        finally:
            data_list.append(hotel)

    return data_list


# result["hotels.com"] = get_data_from_hotels_com(
#     start_date, end_date, destination)

# result['naver'] = get_data_from_naver(start_date, end_date, destination)

# pprint(result)
