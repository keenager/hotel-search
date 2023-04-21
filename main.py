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
    {'name': 'hotels_com', 'func': from_hotels_com},
    {'name': 'naver', 'func': from_naver},
]

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
        self.column_name_list = ['번호', '호텔 이름', '호텔등급', '평점', '가격']
        self.column_len = len(self.column_name_list)

        self.root = tk.Tk()
        self.root.title('호텔 찾기')
        self.root.geometry('1280x960')
        self.root.config(padx=20, pady=20)

        # -------- 프레임 ----------#
        self.top_frame = tk.Frame(
            self.root, width=1000, height=50, padx=10, pady=10, bg='red')
        self.main_frame = tk.Frame(
            self.root, width=1000, height=500, padx=10, pady=10, bg='green')

        self.top_frame.pack()
        self.main_frame.pack()

        self.btn_start = tk.Button(self.top_frame,
                                   text='시작',
                                   command=self.get_data,
                                   )

        self.btn_start.place(x=500)

        self.result_widget_list = [self.set_result_widget(site)
                                   for site in SITE_LIST]

    def set_result_widget(self, site):
        result_frame = tk.LabelFrame(self.main_frame, text=site['name'])
        result_frame.pack()

        column_list: list[tk.Listbox] = []

        for i in range(self.column_len):
            column = tk.Listbox(result_frame, width=0, height=0)
            column.insert(0, self.column_name_list[i])
            column_list.append(column)

        # self.listbox = tk.Listbox(self.root, width=0)
        # self.scrollbar = tk.Scrollbar(self.listbox, orient='vertical')
        # self.listbox.config(yscrollcommand=self.scrollbar.set)
        # self.scrollbar.config(command=self.listbox.yview)
        # self.listbox.insert(0, '결과 리스트 입니다.')
        # # '<<ListboxSelect>>'
        # self.listbox.bind('<Double-Button-1>', self.weblink)

        # self.btn_1.grid(column=0, row=0, columnspan=2)
        # self.listbox.grid(column=1, row=1)

        # -------- 위젯 배치 ----------#

        for i in range(self.column_len):
            column_list[i].grid(row=0, column=i)

        return column_list

    def weblink(self, *args):
        idx = self.listbox.curselection()[0]
        webbrowser.open(url=self.result[idx].link, new=2)

    def get_data(self):
        # 기존 리스트 정리
        for result_widget in self.result_widget_list:
            for i in range(self.column_len):
                listbox = result_widget[i]
                listbox.delete(1, listbox.size() - 1)

        self.root.update()

        # 검색 시작
        self.driver = webdriver.Chrome(
            service=service,
            options=options,
        )

        result_list = [
            site['func'](self.driver, start_date, end_date, destination)
            for site in SITE_LIST
        ]

        # self.result = from_hotels_com(
        #     self.driver, start_date, end_date, destination)
        print('검색 종료')
        # print(len(self.result))

        self.display(result_list)

    def display(self, result_list: list[list[Hotel]]):
        # 새 리스트 생성
        for result_idx, result in enumerate(result_list):
            for ht_idx, hotel in enumerate(result):
                row_num = ht_idx + 1
                col = [row_num, hotel.name, hotel.grade,
                       hotel.rating, hotel.price]
                for col_idx in range(self.column_len):
                    self.result_widget_list[result_idx][col_idx].insert(
                        row_num,
                        col[col_idx],
                    )


app = App()
app.root.mainloop()

# driver.quit()
# print('크롬 종료')
