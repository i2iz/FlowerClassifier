import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class FlowerClientUI:
    def __init__(self, root):
        self.root = root
        self.root.title("클라이언트")
        self.root.geometry("800x800")

        # 스타일 설정
        style = ttk.Style()
        style.theme_use('aqua')

        # 파일 경로 저장을 위한 변수
        self.file_path = tk.StringVar(value="")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 이미지 프레임
        image_frame = ttk.LabelFrame(main_frame, text="이미지 미리보기", padding="10")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.canvas = tk.Canvas(image_frame, bg="white", width=600, height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 컨트롤 프레임
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.X)
        control_frame.columnconfigure(1, weight=1)

        self.file_button = ttk.Button(control_frame, text="이미지 선택", command=self.select_file)
        self.file_button.grid(row=0, column=0, padx=(0, 5))

        self.path_entry = ttk.Entry(control_frame, textvariable=self.file_path, state="readonly")
        self.path_entry.grid(row=0, column=1, sticky="ew", padx=5)

        self.send_button = ttk.Button(control_frame, text="서버로 전송", command=self.send_data, state=tk.DISABLED)
        self.send_button.grid(row=0, column=2, padx=(5, 0))
        
        # 종료 버튼
        bottom_frame = ttk.Frame(main_frame, padding=(10, 20, 10, 10))
        bottom_frame.pack(fill=tk.X)
        
        # 프레임의 중앙에 오도록 column 0을 확장
        bottom_frame.columnconfigure(0, weight=1) 
        
        self.exit_button = ttk.Button(bottom_frame, text="종료", command=self.close_app)
        self.exit_button.grid(row=0, column=0, sticky="e") # 동쪽(e)에 붙이기

        # 결과 프레임
        result_frame = ttk.LabelFrame(main_frame, text="분석 결과", padding="10")
        result_frame.pack(fill=tk.X, pady=5)
        self.result_label = ttk.Label(result_frame, text="분석할 이미지를 선택해 주세요.", font=("NanumGothic", 12))
        self.result_label.pack()

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[('이미지 파일', '*.jpg *.jpeg')])
        if path:
            self.file_path.set(path)
            
            image = Image.open(path)
            image.thumbnail((self.canvas.winfo_width(), self.canvas.winfo_height()))
            self.image_tk = ImageTk.PhotoImage(image)

            self.canvas.delete("all")
            self.canvas.create_image(
                self.canvas.winfo_width() / 2, 
                self.canvas.winfo_height() / 2, 
                anchor=tk.CENTER, 
                image=self.image_tk
            )

            self.send_button.config(state=tk.NORMAL) # 전송 버튼 활성화
            self.result_label.config(text="이미지가 선택되었습니다. 전송 버튼을 눌러주세요.")


    def send_data(self):
        if not self.file_path.get():
            return
        
        self.result_label.config(text="서버가 이미지를 분석하는 중입니다. 잠시만 기다려주세요.")
        
        # 통신 시작 시 버튼 비활성화
        self.file_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

    def close_app(self):
        """프로그램을 안전하게 종료하는 함수"""
        if messagebox.askokcancel("종료 확인", "프로그램을 종료하시겠습니까?"):
            self.root.quit()
            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = FlowerClientUI(root)
    root.update_idletasks()
    root.mainloop()