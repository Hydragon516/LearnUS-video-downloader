from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import QLabel, QListWidget, QLineEdit, QDialog, QPushButton, QHBoxLayout, QVBoxLayout, QApplication
from selenium import webdriver
import chromedriver_autoinstaller
import webbrowser
from selenium.webdriver.common.action_chains import ActionChains
import time
import m3u8
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES
import requests
import binascii

search_url = ""
video_title = ""
id = ""
pw = ""

segmanet_list = []

class MyMainGUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.search_button = QPushButton("검색")
        self.github_button = QPushButton("Github")

        self.id_input = QLineEdit(self)
        self.pw_input = QLineEdit(self)
        self.pw_input.setEchoMode(QLineEdit.Password)
        
        self.search_input = QLineEdit(self)
        self.url_list = QListWidget(self)

        self.status_label = QLabel("", self)

        self.id_label = QLabel("ID : ", self)
        self.pw_label = QLabel("PW : ", self)

        self.url_label = QLabel("동영상 링크 : ", self)

        self.title_label = QLabel("파일 제목 : ", self)
        self.title_input = QLineEdit(self)
        self.download_button = QPushButton("동영상 다운로드")

        id_box = QHBoxLayout()
        id_box.addWidget(self.id_label)
        id_box.addWidget(self.id_input)
        id_box.addWidget(self.pw_label)
        id_box.addWidget(self.pw_input)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.url_label)
        hbox.addWidget(self.search_input)
        hbox.addWidget(self.search_button)
        hbox.addWidget(self.github_button)
        hbox.addStretch(1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.url_list)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.title_label)
        hbox3.addWidget(self.title_input)
        hbox3.addWidget(self.download_button)

        vbox1 = QVBoxLayout()
        vbox1.addStretch(1)
        vbox1.addLayout(id_box)
        vbox1.addStretch(1)
        vbox1.addLayout(hbox)
        vbox1.addStretch(1)
        vbox1.addLayout(hbox2)
        vbox1.addStretch(1)
        vbox1.addLayout(hbox3)
        vbox1.addStretch(1)
        vbox1.addWidget(self.status_label)

        self.setLayout(vbox1)

        self.setWindowTitle('LearnUS Downloader (v1.1)')
        self.setGeometry(300, 300, 500, 350)


class MyMain(MyMainGUI):
    add_sec_signal = pyqtSignal()
    send_instance_singal = pyqtSignal("PyQt_PyObject")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.search_button.clicked.connect(self.search)
        self.download_button.clicked.connect(self.download)
        self.github_button.clicked.connect(lambda: webbrowser.open('https://github.com/Hydragon516/Bugs-Music-Downloader'))

        self.search_input.textChanged[str].connect(self.url_update)
        
        self.id_input.textChanged[str].connect(self.id_update)
        self.pw_input.textChanged[str].connect(self.pw_update)
        self.title_input.textChanged[str].connect(self.title_update)
        
        self.url_list.itemClicked.connect(self.chkItemClicked)

        self.th_search = searcher(parent=self)
        self.th_search.updated_list.connect(self.list_update)
        self.th_search.updated_label.connect(self.status_update)

        self.th_download = downloadr(parent=self)
        self.th_download.updated_label.connect(self.status_update)

        self.show()
    
    def url_update(self, input):
        global search_url
        search_url = input
    
    def id_update(self, input):
        global id
        id = input
    
    def pw_update(self, input):
        global pw
        pw = input
    
    def title_update(self, input):
        global video_title
        video_title = input
    
    def chkItemClicked(self) :
        global keyword
        keyword = self.url_list.currentItem().text() 

    @pyqtSlot()
    def search(self):
        self.url_list.clear()
        self.th_search.start()

    @pyqtSlot()
    def download(self):
        self.th_download.start()

    @pyqtSlot(str)
    def list_update(self, msg):
        self.url_list.addItem(msg)
    
    @pyqtSlot(str)
    def status_update(self, msg):
        self.status_label.setText(msg)


class searcher(QThread):
    updated_list = pyqtSignal(str)
    updated_label = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent

    def __del__(self):
        self.wait()

    def run(self):
        global search_url
        global video_title
        global id
        global pw
        global keyword

        global segmanet_list
        
        if search_url != "":
            chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
            self.updated_label.emit("크롬 드라이버 버전 확인 완료! : {}".format(chrome_ver))

            options = webdriver.ChromeOptions()
                    
            try:
                driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=options)   
            except:
                chromedriver_autoinstaller.install(True)
                driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', options=options)

            self.updated_label.emit("서버에 접속하는 중...")

            try:
                driver.get(url=search_url)
                driver.implicitly_wait(time_to_wait=5)

                self.updated_label.emit("LearnUS 로그인 시도 중...")


                id_target = driver.find_element_by_xpath('//*[@id="ssoLoginForm"]/div/div[1]/input[3]')
                pw_target = driver.find_element_by_xpath('//*[@id="ssoLoginForm"]/div/div[1]/input[4]')

                id_target.send_keys(id)
                pw_target.send_keys(pw)

                login_button = driver.find_element_by_xpath('//*[@id="ssoLoginForm"]/div/div[2]/input')
                login_button.click()

                self.updated_label.emit("동영상 정보 불러오는 중 ...")
                driver.get(url=search_url)
                driver.implicitly_wait(5)

                self.updated_label.emit("동영상 실행 중 ...")
                play_button = driver.find_element_by_xpath('//*[@id="my-video"]/button/span[1]')
                
                act = ActionChains(driver)
                act.move_to_element(play_button).click().perform()

                time.sleep(2)

                self.updated_label.emit("다운로드 가능한 링크 확인 중 ...")
                network_logs = driver.execute_script("var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;")
                network_log_names = [x['name'] for x in network_logs]

                segmanet_list.clear()
                
                for target_url in network_log_names:
                    if "v1-a1.ts" in target_url:
                        download_url = target_url
                        segmanet_list.append(download_url)
                
                for i in range(len(segmanet_list)):
                    self.updated_list.emit(segmanet_list[i])
                
                self.updated_label.emit("검색 완료! 다운로드 버튼을 누르세요...")
            
            except:
                self.updated_label.emit("알 수 없는 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

        else:
            self.updated_label.emit("검색 Url을 입력하세요")


class downloadr(QThread):
    updated_label = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent

    def __del__(self):
        self.wait()

    def get_base_url(self, raw_url):
        if ".ts" in raw_url:
            raw_url = "/".join(raw_url.split("/")[:-1])
        
        return raw_url

    def get_playlist(self, base_url):
        tmp_playlist = m3u8.load(uri=base_url+"/index.m3u8")
        
        return tmp_playlist

    def decrypt_video(self, encrypted_data, key, iv):
        encrypted_data = pad(data_to_pad=encrypted_data, block_size=AES.block_size)
        aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
        decrypted_data = aes.decrypt(encrypted_data)
        
        return decrypted_data

    def binify(self, x):
        h = hex(x)[2:].rstrip('L')
        
        return binascii.unhexlify('0'*(32-len(h))+h)

    def run(self):
        global segmanet_list
        global video_title

        raw_url = segmanet_list[0]
        base_url = self.get_base_url(raw_url)
        playlist = self.get_playlist(base_url)
        key = requests.get(playlist.keys[-1].absolute_uri).content
        seq_len = len(playlist.segments)
        
        for i in range(seq_len):
            self.updated_label.emit("다운로드 중 입니다... ({}%)".format(round(i/seq_len*100, 2)))
            seg = playlist.segments[i]
            data = requests.get(seg.absolute_uri).content
            iv = self.binify(i + 1)
            data = self.decrypt_video(data, key, iv)
            
            with open("{}.mp4".format(video_title), "ab" if i != 0 else "wb") as f:
                f.write(data)
        
        self.updated_label.emit("다운로드 완료!")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = MyMain()
    app.exec_()
