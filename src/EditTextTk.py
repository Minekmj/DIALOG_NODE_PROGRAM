import tkinter as tk

import queue

text_queue = queue.Queue()

input_text = ""
input_change = False

class TextEditorDialog:
    def __init__(self, text="", text_item=None, mainIteam = None, font=("맑은 고딕", 12)): #<-글꼴 정의
        self.text_item = text_item
        self.MainIteam = mainIteam

        self.root = tk.Tk()
        self.root.title("대사 편집")
        # 창을 마우스 위치에 표시 (기본 크기 300x150)
        self.root.withdraw()
        self.root.update()

        mx = self.root.winfo_pointerx()
        my = self.root.winfo_pointery()

        w, h = 300, 150

        x = mx
        y = my

        self.root.deiconify()  # 다시 표시
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        self.font = font

        self.txt = tk.Text(
            self.root,
            background="#202020",
            foreground="#FFFFFF",
            insertbackground="#FFFFFF",
            font=self.font
        )
        self.txt.pack(fill="both", expand=True)
        self.txt.insert("1.0", text)

        self.last_text = text

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_text()

    def update_text(self):
        if not self.root.winfo_exists():
            return

        new_text = self.txt.get("1.0", "end-1c")

        if new_text != self.last_text:
            self.last_text = new_text
            text_queue.put((self.text_item, new_text, self.MainIteam))

        self.root.after(10, self.update_text)

    def on_close(self):
        self.root.destroy()