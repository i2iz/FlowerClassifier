import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import datetime
import tensorflow as tf
import numpy as np
import pandas as pd


class FlowerServerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("서버")
        self.root.geometry("800x600")

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # 스타일 설정
        style = ttk.Style()
        style.theme_use('aqua')
        style.configure("Treeview.Heading", font=("NanumGothic", 10, 'bold'))

        self.create_widgets()

        # 모델 로드
        self.model = None
        self.df = None
        self.infer = None

        self.load_model_and_labels()

    def create_widgets(self):
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # 상단 프레임 (상태 + 제어)
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        top_frame.columnconfigure(0, weight=1)

        # 서버 상태 프레임
        status_frame = ttk.LabelFrame(top_frame, text="서버 상태", padding="10")
        status_frame.grid(row=0, column=0, sticky="ewns")
        
        ttk.Label(status_frame, text="IP 주소:").grid(row=0, column=0, sticky="w")
        self.ip_label = ttk.Label(status_frame, text="0.0.0.0", font=("NanumGothic", 10))
        self.ip_label.grid(row=0, column=1, sticky="w")

        ttk.Label(status_frame, text="포트:").grid(row=1, column=0, sticky="w")
        self.port_label = ttk.Label(status_frame, text="8080", font=("NanumGothic", 10))
        self.port_label.grid(row=1, column=1, sticky="w")

        ttk.Label(status_frame, text="상태:").grid(row=2, column=0, sticky="w")
        self.status_label = ttk.Label(status_frame, text="Stopped", foreground="red", font=("NanumGothic", 10))
        self.status_label.grid(row=2, column=1, sticky="w")

        # 서버 제어 프레임
        control_frame = ttk.LabelFrame(top_frame, text="서버 제어", padding="10")
        control_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        
        # 버튼들이 프레임 너비에 맞게 확장되도록 설정
        self.start_button = ttk.Button(control_frame, text="서버 시작", command=self.start_server)
        self.start_button.pack(pady=5, fill=tk.X)
        self.stop_button = ttk.Button(control_frame, text="서버 중지", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=5, fill=tk.X)

        # 프로그램 종료 버튼
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=10)
        self.exit_button = ttk.Button(control_frame, text="프로그램 종료", command=self.close_app)
        self.exit_button.pack(pady=5, fill=tk.X)


        # 클라이언트 목록 프레임
        clients_frame = ttk.LabelFrame(main_frame, text="연결된 클라이언트", padding="10")
        clients_frame.grid(row=1, column=0, sticky="ew", pady=5)
        clients_frame.columnconfigure(0, weight=1)
        clients_frame.rowconfigure(0, weight=1)

        self.client_tree = ttk.Treeview(
            clients_frame, 
            columns=("ip", "port", "time"), 
            show="headings",
            height=5
        )
        self.client_tree.grid(row=0, column=0, sticky="ew")
        
        self.client_tree.heading("ip", text="IP 주소")
        self.client_tree.heading("port", text="포트")
        self.client_tree.heading("time", text="연결 시간")
        
        self.client_tree.column("ip", width=150)
        self.client_tree.column("port", width=100)
        self.client_tree.column("time", width=200)

        # 상세 로그 프레임
        log_frame = ttk.LabelFrame(main_frame, text="상세 로그", padding="10")
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(5, 0))
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED, font=("NanumGothic", 9))
        self.log_text.grid(row=0, column=0, sticky="nsew")

        # 로그 타입별 색상 설정
        self.log_text.tag_config("INFO", foreground="royalblue")
        self.log_text.tag_config("SUCCESS", foreground="green")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("WARNING", foreground="orange")

    def load_model_and_labels(self):
        """모델 및 라벨 파일 로드"""
        try:
            self.model = tf.saved_model.load('./model')
            self.df = pd.read_excel('./label.xlsx')
            
            # 추론을 위한 함수 시그니처
            self.infer = self.model.signatures['serving_default']
            self.add_log("모델/라벨 로드 완료", "SUCCESS")
        except Exception as e:
            msg = f"모델 또는 라벨 파일 로드 실패: {str(e)}"
            self.add_log(msg, "ERROR")
            self.model = None
            self.df = None
            self.infer = None

    def start_server(self):
        """서버 시작"""
        self.status_label.config(text="Running", foreground="green")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # 테스트 로그
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_log("서버가 0.0.0.0:8080에서 시작되었습니다.", "INFO")
        self.add_client_to_tree("192.168.0.10", "54321", now)

    def stop_server(self):
        """서버 중지"""
        self.status_label.config(text="Stopped", foreground="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.add_log("서버가 중지되었습니다.")
        self.clear_client_tree()

    def add_log(self, message, msg_type="INFO"):
        """로그 표시"""
        self.log_text.config(state=tk.NORMAL)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{msg_type.upper()}] {message}\n"
        
        # 로그 삽입
        self.log_text.insert(tk.END, log_entry, msg_type.upper())
        
        # 스크롤을 맨 아래로 이동
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def add_client_to_tree(self, ip, port, time):
        """클라이언트 정보를 Treeview에 추가"""
        self.client_tree.insert("", tk.END, values=(ip, port, time))

    def clear_client_tree(self):
        """TreeView의 모든 항목 삭제"""
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

    def close_app(self):
        """프로그램 종료"""
        if messagebox.askokcancel("종료 확인", "프로그램을 종료하시겠습니까?"):
            self.root.quit()
            self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = FlowerServerUI(root)
    root.mainloop()