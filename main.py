from enum import Enum
from operator import itemgetter, attrgetter
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from get_data import from_hotels_com, from_naver, Hotel
import webbrowser

BACKGROUND_COLOR = "#B1DDC6"

SITE_LIST = [
    {'name': 'HOTEL.COM', 'func': from_hotels_com},
    {'name': 'NAVER', 'func': from_naver},
]


class Columns(Enum):
    NUM = '번호'
    NAME = '호텔 이름'
    GRADE = '호텔등급'
    RATING = '평점'
    PRICE = '가격'


start_date = '2023-05-20'
end_date = '2023-05-21'
destination = '경기'

service = Service(ChromeDriverManager().install())
options = Options()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument(
    'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36')


# -------- UI ----------#
class App:
    def __init__(self) -> None:
        self.driver: WebDriver
        self.result_list: list[list[Hotel]]
        self.column_len = len(Columns)
        self.sort_toggle = True

        # root window
        self.root = tk.Tk()
        self.root.title('호텔 찾기')
        self.root.geometry('960x640')
        self.root.config(padx=20, pady=20)

        # scrollbar 생성을 위한 frame 작업
        self.outer_frame = tk.Frame(self.root)
        self.outer_frame.pack(fill='both', expand=1)

        self.canvas = tk.Canvas(self.outer_frame)
        self.canvas.pack(side='left', fill='both', expand=1)

        self.scrollbar = tk.Scrollbar(
            self.outer_frame, orient='vertical', command=self.canvas.yview)
        self.scrollbar.pack(side='right', fill='y')

        self.canvas.config(yscrollcommand=self.scrollbar.set)
        self.canvas.bind(
            '<Configure>',
            lambda e: self.canvas.config(scrollregion=self.canvas.bbox('all'))
        )
        self.canvas.bind_all('<MouseWheel>', self.on_mouse_wheel)

        # -------- 실제 내용 ----------#
        self.main_frame = tk.Frame(
            self.canvas, width=960, height=640, padx=10, pady=10, bg='green')

        self.btn_start = tk.Button(self.main_frame,
                                   text='시작',
                                   command=self.get_data,
                                   )
        self.btn_start.pack()

        self.result_widget_list = [self.set_result_widget(site)
                                   for site in SITE_LIST]

        self.canvas.create_window((0, 0), window=self.main_frame, anchor='nw')

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta), 'units')

    def set_result_widget(self, site):
        result_frame = tk.LabelFrame(self.main_frame, text=site['name'])
        result_frame.pack()

        col_widget_list: list[tk.Listbox] = []

        for column in Columns:
            col_widget = tk.Listbox(result_frame, width=0, height=0)
            col_widget.insert(0, column.value)
            col_widget.bind('<Double-Button-1>', self.web_link)
            col_widget_list.append(col_widget)

        # -------- 위젯 배치 ----------#
        for i in range(self.column_len):
            col_widget_list[i].grid(row=0, column=i)

        return col_widget_list

    def web_link(self, *args):
        # 사이트 결과마다 반복
        for result_idx, result_widget in enumerate(self.result_widget_list):
            # 항목(칼럼)마다 반복
            for col_widget in result_widget:
                try:
                    selected_row_idx = col_widget.curselection()[0]
                    if selected_row_idx == 0:
                        col_name = col_widget.get(0)
                        self.sort_results(result_idx, col_name)
                    else:
                        webbrowser.open(
                            url=self.result_list[result_idx][selected_row_idx-1].link, new=2)
                    break
                except IndexError:
                    pass

    def clear_list(self):
        for result_widget in self.result_widget_list:
            for i in range(self.column_len):
                col_widget = result_widget[i]
                col_widget.delete(1, col_widget.size() - 1)

        self.root.update()

    def get_data(self):
        # 기존 리스트 정리
        self.clear_list()

        # 검색 시작
        self.driver = webdriver.Chrome(
            service=service,
            options=options,
        )

        # 검색 결과 저장
        self.result_list = [
            site['func'](self.driver, start_date, end_date, destination)
            for site in SITE_LIST
        ]

        self.display()

    def display(self):
        # 사이트 결과마다 반복
        for result_idx, result in enumerate(self.result_list):
            result_widget = self.result_widget_list[result_idx]
            # 결과 중에서 호텔마다 반복
            for ht_idx, hotel in enumerate(result):
                row_num = ht_idx + 1
                # 각 항목 배치
                for col_widget in result_widget:
                    col_name = col_widget.get(0)
                    if col_name == Columns.NUM.value:
                        col_widget.insert(row_num, row_num)
                    elif col_name == Columns.PRICE.value:
                        price = getattr(hotel, Columns(col_name).name.lower())
                        price = f'{price:9,}원'
                        col_widget.insert(row_num, price)
                    else:
                        col_widget.insert(
                            row_num,
                            getattr(hotel, Columns(col_name).name.lower())
                        )

    def sort_results(self, result_idx, col_name):
        if col_name == Columns.NUM.value:
            return

        self.clear_list()

        # col_name = self.column_names[col_name]
        col_name = Columns(col_name).name.lower()
        self.sort_toggle = not self.sort_toggle

        self.result_list[result_idx].sort(
            key=attrgetter(col_name), reverse=self.sort_toggle)

        self.display()


app = App()
app.root.mainloop()

app.driver.quit()
print('크롬 종료')
