import dearpygui.dearpygui as dpg
import json
import copy
import threading
from tkinter import filedialog
from src.EditTextTk import *

class DialogueNodeEditor:
    def __init__(self):
        self.nodes = {}       # { node_uuid: ui_refs_dict }
        self.links = []       # [ (link_id, sender_pin, receiver_pin) ]
        self.node_counter = 0
        
        # 전역 함수 리스트 관리
        self.function_list = [""] 

        # 복사/붙여넣기용 클립보드 데이터
        self.copied_node_data = None 

        # 줌(Zoom) 시스템 상태 관리 변수
        self.zoom_scale = 1.0
        self.node_positions = {}  # { node_id: [original_x, original_y] }

        # Undo / Redo 스택 시스템
        self.undo_stack = []
        self.redo_stack = []
        self._is_restoring = False     
        self.last_stable_state = None  
        self.change_timer = 0          

        # 주황색 연결선(Link) 테마 등록
        with dpg.theme() as self.orange_link_theme:
            with dpg.theme_component(dpg.mvNodeLink):
                dpg.add_theme_color(dpg.mvNodeCol_Link, [240, 130, 50, 255], category=dpg.mvThemeCat_Nodes)
                dpg.add_theme_color(dpg.mvNodeCol_LinkHovered, [255, 160, 70, 255], category=dpg.mvThemeCat_Nodes)
                dpg.add_theme_color(dpg.mvNodeCol_LinkSelected, [255, 180, 100, 255], category=dpg.mvThemeCat_Nodes)

        self.zoom_fonts = {}
        self.zoom_themes = {}  # { (scale_key, "type_string"): theme_id }

        # 폰트 등록
        self.font_path = "c:/Windows/Fonts/malgun.ttf"  # <- 폰트 경로
        self.base_font_size = 14

    def update_link_colors(self):
        """ 응답(Response)의 타입이 함수(1)인 핀에서 출발한 링크를 주황색으로 변경"""
        function_pins = set()
        for node_id, ui_refs in self.nodes.items():
            if not dpg.does_item_exist(node_id): 
                continue
            for res in ui_refs.get("responses", []):
                if dpg.does_item_exist(res["type"]):
                    rtype_str = dpg.get_value(res["type"])
                    if rtype_str.startswith("1"):  
                        function_pins.add(res["pin_id"])

        for link_id, sender_pin, receiver_pin in self.links:
            if dpg.does_item_exist(link_id):
                if sender_pin in function_pins:
                    dpg.bind_item_theme(link_id, self.orange_link_theme)
                else:
                    dpg.bind_item_theme(link_id, 0)

    def get_or_create_zoom_theme(self, scale, node_type="normal"):
        """ 
        배율(Scale)과 노드 타입(상태)을 조합하여 가변 스타일/색상 테마를 동적 생성
        node_type 종류: "normal", "warning", "start", "end", "function"
        """
        scale_key = round(scale * 20) / 20
        if scale_key < 0.1: scale_key = 0.1
        
        # 캐싱 키 조합
        cache_key = (scale_key, node_type)
        if cache_key in self.zoom_themes:
            return self.zoom_themes[cache_key]

        # 기본 색상 정의 데이터베이스
        colors = {
            "normal": {
                "bg": [45, 45, 45, 230], "bg_h": [60, 60, 60, 240], "bg_s": [75, 75, 75, 255],
                "title": [30, 30, 30, 255], "title_h": [40, 40, 40, 255], "title_s": [50, 50, 50, 255]
            },
            "warning": {
                "bg": [200, 120, 120, 255], "bg_h": [220, 140, 140, 255], "bg_s": [210, 100, 100, 255],
                "title": [150, 80, 80, 255], "title_h": [170, 100, 100, 255], "title_s": [190, 110, 110, 255]
            },
            "start": {
                "bg": [45, 45, 45, 230], "bg_h": [60, 60, 60, 240], "bg_s": [75, 75, 75, 255], # 배경은 기본 유지
                "title": [40, 100, 180, 255], "title_h": [50, 120, 210, 255], "title_s": [60, 140, 240, 255]
            },
            "end": {
                "bg": [45, 45, 45, 230], "bg_h": [60, 60, 60, 240], "bg_s": [75, 75, 75, 255],
                "title": [180, 160, 40, 255], "title_h": [210, 190, 50, 255], "title_s": [240, 220, 60, 255]
            },
            "function": {
                "bg": [45, 45, 45, 230], "bg_h": [60, 60, 60, 240], "bg_s": [75, 75, 75, 255],
                "title": [180, 90, 30, 255], "title_h": [210, 110, 40, 255], "title_s": [240, 130, 50, 255]
            }
        }

        cfg = colors.get(node_type, colors["normal"])

        with dpg.theme() as new_theme:
            with dpg.theme_component(dpg.mvNode):
                # 1줌 배율 분할 레이아웃 패딩 적용
                pad_x = max(0, int(8 * scale_key))
                pad_y = max(0, int(8 * scale_key))
                dpg.add_theme_style(dpg.mvNodeStyleVar_NodePadding, pad_x, pad_y, category=dpg.mvThemeCat_Nodes)
                
                # 타입별 고유 색상 바인딩
                dpg.add_theme_color(dpg.mvNodeCol_NodeBackground, cfg["bg"], category=dpg.mvThemeCat_Nodes)
                dpg.add_theme_color(dpg.mvNodeCol_NodeBackgroundHovered, cfg["bg_h"], category=dpg.mvThemeCat_Nodes)
                dpg.add_theme_color(dpg.mvNodeCol_NodeBackgroundSelected, cfg["bg_s"], category=dpg.mvThemeCat_Nodes)
                dpg.add_theme_color(dpg.mvNodeCol_TitleBar, cfg["title"], category=dpg.mvThemeCat_Nodes)
                dpg.add_theme_color(dpg.mvNodeCol_TitleBarHovered, cfg["title_h"], category=dpg.mvThemeCat_Nodes)
                dpg.add_theme_color(dpg.mvNodeCol_TitleBarSelected, cfg["title_s"], category=dpg.mvThemeCat_Nodes)
            
            with dpg.theme_component(dpg.mvAll):
                # 내부 아이템 패딩 배율 축소
                item_x = max(0, int(8 * scale_key))
                item_y = max(0, int(4 * scale_key))
                frame_x = max(0, int(4 * scale_key))
                frame_y = max(0, int(3 * scale_key))
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, item_x, item_y)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, frame_x, frame_y)

        self.zoom_themes[cache_key] = new_theme
        return new_theme
    
    def get_or_create_zoom_resources(self, scale):
        """ 배율별로 균등한 비율 유지를 위한 폰트 크기를 생성합니다. """
        scale_key = round(scale * 20) / 20
        if scale_key < 0.1: scale_key = 0.1 

        if scale_key in self.zoom_fonts:
            return self.zoom_fonts[scale_key]

        target_font_size = max(4, int(self.base_font_size * scale_key))
        with dpg.font_registry():
            try:
                new_font = dpg.add_font(self.font_path, target_font_size)
            except:
                new_font = dpg.default_font()
        
        self.zoom_fonts[scale_key] = new_font
        return new_font

    def set_zoom_scale_at_mouse(self, new_scale):
        self.zoom_scale = new_scale

        for node_id in list(self.nodes.keys()):
            if not dpg.does_item_exist(node_id):
                continue
            orig_pos = self.node_positions.get(node_id, [100.0, 100.0])
            scaled_x = orig_pos[0] * self.zoom_scale
            scaled_y = orig_pos[1] * self.zoom_scale
            dpg.set_item_pos(node_id, [scaled_x, scaled_y])

        self.update_node_layouts_uniformly()

    def update_original_positions_from_viewport(self):
        if self._is_restoring: return
        for node_id in list(self.nodes.keys()):
            if dpg.does_item_exist(node_id):
                current_pos = dpg.get_item_pos(node_id)
                if current_pos:
                    self.node_positions[node_id] = [
                        current_pos[0] / self.zoom_scale,
                        current_pos[1] / self.zoom_scale
                    ]

    def synchronize_positions_to_screen(self):
        for node_id, original_pos in list(self.node_positions.items()):
            if dpg.does_item_exist(node_id):
                scaled_x = original_pos[0] * self.zoom_scale
                scaled_y = original_pos[1] * self.zoom_scale
                dpg.set_item_pos(node_id, [scaled_x, scaled_y])

    def update_node_layouts_uniformly(self):
        """모든 위젯의 크기 스케일링 및 가변 상태 색상 테마를 동시에 새로고침합니다. """
        current_font = self.get_or_create_zoom_resources(self.zoom_scale)

        # 색상 및 스타일 테마 일괄 리프레시 처리 유도
        self.update_node_colors()

        for node_id, ui_refs in self.nodes.items():
            if not dpg.does_item_exist(node_id):
                continue
            
            # 폰트 바인딩
            dpg.bind_item_font(node_id, current_font)

            # 위젯 가로/세로폭 정비례 축소
            w_idx = int(100 * self.zoom_scale)
            w_type = int(120 * self.zoom_scale)
            w_text = int(250 * self.zoom_scale)
            h_text = int(70 * self.zoom_scale)
            w_btn = int(250 * self.zoom_scale)

            if dpg.does_item_exist(ui_refs["index"]):
                dpg.configure_item(ui_refs["index"], width=w_idx)
            if dpg.does_item_exist(ui_refs["type"]):
                dpg.configure_item(ui_refs["type"], width=w_type)
            if dpg.does_item_exist(ui_refs["text"]):
                dpg.configure_item(ui_refs["text"], width=w_text, height=h_text)
            if dpg.does_item_exist(ui_refs["add_response_btn"]):
                dpg.configure_item(ui_refs["add_response_btn"], width=w_btn)
                
            if dpg.does_item_exist(ui_refs["special_code_text"]):
                dpg.configure_item(ui_refs["special_code_text"], width=int(150 * self.zoom_scale))
            if dpg.does_item_exist(ui_refs["special_code_int"]):
                dpg.configure_item(ui_refs["special_code_int"], width=int(150 * self.zoom_scale))

            for res in ui_refs["responses"]:
                if dpg.does_item_exist(res["text"]):
                    dpg.configure_item(res["text"], width=int(150 * self.zoom_scale))
                if dpg.does_item_exist(res["type"]):
                    dpg.configure_item(res["type"], width=int(110 * self.zoom_scale))
                if dpg.does_item_exist(res["code"]):
                    dpg.configure_item(res["code"], width=int(150 * self.zoom_scale))

    def capture_raw_snapshot(self):
        self.update_original_positions_from_viewport()
        compiled = self.get_compiled_data()
        return {
            "Functions": copy.deepcopy(self.function_list),
            "Dialogues": list(compiled.values()) if compiled else [],
            "node_counter": self.node_counter,
            "zoom_scale": self.zoom_scale
        }

    def save_state(self):
        if self._is_restoring: return
        current_state = self.capture_raw_snapshot()
        if self.undo_stack and self.undo_stack[-1] == current_state: return
        self.undo_stack.append(current_state)
        self.redo_stack.clear()
        self.last_stable_state = copy.deepcopy(current_state)
        if len(self.undo_stack) > 50: self.undo_stack.pop(0)

    def monitor_changes(self):
        if self._is_restoring or not dpg.does_item_exist("node_editor"): return
        current_snapshot = self.capture_raw_snapshot()
        if self.last_stable_state is None:
            self.last_stable_state = copy.deepcopy(current_snapshot)
            return
        if current_snapshot != self.last_stable_state:
            if not self._is_restoring:
                self.change_timer += 1
                if self.change_timer > 20 and not dpg.is_mouse_button_down(dpg.mvMouseButton_Left):
                    self.undo_stack.append(copy.deepcopy(self.last_stable_state))
                    self.redo_stack.clear()
                    self.last_stable_state = copy.deepcopy(current_snapshot)
                    self.change_timer = 0
                    if len(self.undo_stack) > 50: self.undo_stack.pop(0)
        else:
            self.change_timer = 0
            self.last_stable_state = copy.deepcopy(current_snapshot)

    def edit_text_popup(self, sender, app_data, user_data):
        text_item = user_data[0]
        initial_text = dpg.get_value(text_item)
        mainIt = user_data[1]
        def tk_worker():
            dialog = TextEditorDialog(text=initial_text, text_item=text_item, mainIteam=mainIt)
            dialog.root.mainloop()
        threading.Thread(target=tk_worker, daemon=True).start()

    def process_text_queue(self):
        while not text_queue.empty():
            text_item, text, Mi = text_queue.get()
            if dpg.does_item_exist(text_item): dpg.set_value(text_item, text)
            if dpg.does_item_exist(Mi): 
                index = dpg.get_item_label(Mi)
                number = str(index[5:index.find(":") - 1])
                dpg.configure_item(Mi, label=f"Node {number} : {'/'.join(text.split('\n'))}")

    def undo(self):
        if self._is_restoring: return
        if not self.undo_stack: return
        self._is_restoring = True
        current_snapshot = self.capture_raw_snapshot()
        self.redo_stack.append(current_snapshot)
        previous_state = self.undo_stack.pop()
        self.restore_snapshot(previous_state)
        actual_current = self.capture_raw_snapshot()
        self.last_stable_state = copy.deepcopy(actual_current)
        self.change_timer = 0
        self._is_restoring = False

    def redo(self):
        if self._is_restoring: return
        if not self.redo_stack: return
        self._is_restoring = True
        current_snapshot = self.capture_raw_snapshot()
        self.undo_stack.append(current_snapshot)
        next_state = self.redo_stack.pop()
        self.restore_snapshot(next_state)
        actual_current = self.capture_raw_snapshot()
        self.last_stable_state = copy.deepcopy(actual_current)
        self.change_timer = 0
        self._is_restoring = False

    def restore_snapshot(self, state_data):
        self.nodes.clear()
        self.links.clear()
        self.node_positions.clear()
        dpg.delete_item("node_editor", children_only=True)
        
        self.function_list = state_data.get("Functions", [""])
        self.update_function_ui_elements()
        self.node_counter = state_data.get("node_counter", 0)
        self.zoom_scale = state_data.get("zoom_scale", 1.0)

        pin_mapping = {}   
        response_pins = [] 

        for dialogue in state_data.get("Dialogues", []):
            node_id = self.add_node((int)(dialogue["DialogueIndex"]), True)
            dpg.configure_item(node_id, label=f"Node {dialogue['DialogueIndex']} : {'/'.join(dialogue['DialogueText'].split('\n'))}")
            ui_refs = self.nodes[node_id]
            dpg.set_value(ui_refs["index"], dialogue["DialogueIndex"])
            dpg.set_value(ui_refs["text"], dialogue["DialogueText"])
            dpg.set_value(ui_refs["has_response"], dialogue["HasResponse"])
            
            dtype_int = dialogue["DialogueType"]
            dtype_str = ["0: Normal", "1: Function", "2: Start", "3: End"][dtype_int]
            dpg.set_value(ui_refs["type"], dtype_str)
            self.on_dialogue_type_change(None, dtype_str, node_id)

            if dtype_int == 1:
                dpg.set_value(ui_refs["special_code_text"], dialogue["SpecialCode"])
            elif dtype_int == 2:
                dpg.set_value(ui_refs["special_code_int"], int(dialogue["SpecialCode"]) if dialogue["SpecialCode"] else 0)

            if "Position" in dialogue:
                self.node_positions[node_id] = dialogue["Position"]

            d_idx = dialogue["DialogueIndex"]
            pin_mapping[d_idx] = ui_refs["input_pin"]

            for r_idx, res in enumerate(dialogue.get("Responses", [])):
                self.add_response(None, None, node_id)
                res_ref = ui_refs["responses"][-1]
                dpg.set_value(res_ref["text"], res["ResponseText"])
                rtype_int = res["ResponseType"]
                rtype_str = ["0: No Effect", "1: Function"][rtype_int]
                dpg.set_value(res_ref["type"], rtype_str)
                self.on_response_type_change(None, rtype_str, res_ref["code"])

                if rtype_int == 1:
                    dpg.set_value(res_ref["code"], res["ResponseCode"])
                if res["NextDialogueIndex"] != -1:
                    response_pins.append((node_id, r_idx, res_ref["pin_id"], res["NextDialogueIndex"]))

        for node_id, r_idx, src_pin, next_idx in response_pins:
            if next_idx in pin_mapping:
                dest_pin = pin_mapping[next_idx]
                link_id = dpg.add_node_link(src_pin, dest_pin, parent="node_editor")
                self.links.append((link_id, src_pin, dest_pin))
                
        # 위치 정렬 및 크기 정렬 동시 리프레시
        self.synchronize_positions_to_screen()
        self.update_node_layouts_uniformly()
        self.update_link_colors()

    def add_global_function(self):
        if self._is_restoring: return
        func_name = dpg.get_value("new_func_input").strip()
        if func_name and func_name not in self.function_list:
            self.save_state()
            self.function_list.append(func_name)
            dpg.set_value("new_func_input", "")
            self.update_function_ui_elements()

    def delete_global_function(self):
        if self._is_restoring: return
        selected_func = dpg.get_value("global_func_combo")
        if selected_func in self.function_list:
            self.save_state()
            self.function_list.remove(selected_func)
            self.update_function_ui_elements()

    def update_function_ui_elements(self):
        dpg.configure_item("global_func_combo", items=self.function_list)
        if self.function_list: dpg.set_value("global_func_combo", self.function_list[0])
        else: dpg.set_value("global_func_combo", "")

        for node_id, ui_refs in self.nodes.items():
            if dpg.does_item_exist(node_id):
                dpg.configure_item(ui_refs["special_code_text"], items=self.function_list)
                for res in ui_refs["responses"]:
                    if dpg.does_item_exist(res["code"]):
                        dpg.configure_item(res["code"], items=self.function_list)

    def update_node_colors(self):
        """가변 스케일링이 포함된 테마 팩토리를 호출하여 바인딩"""
        index_counts = {}
        valid_nodes = []
        start_node_code_counts = {}
        
        # 데이터 수집 및 중복 체크용 카운팅
        for node_id, ui_refs in self.nodes.items():
            if dpg.does_item_exist(node_id):
                try:
                    idx_val = dpg.get_value(ui_refs["index"])
                    index_counts[idx_val] = index_counts.get(idx_val, 0) + 1
                    valid_nodes.append((node_id, idx_val))
                    
                    node_type = dpg.get_value(ui_refs["type"])
                    if int(node_type[0]) == 2:  # Start Node
                        special_code = dpg.get_value(ui_refs.get("special_code_int", None))
                        if special_code is not None:
                            start_node_code_counts[special_code] = start_node_code_counts.get(special_code, 0) + 1
                except Exception: 
                    continue
                    
        # 줌 배율 상태(self.zoom_scale)와 결합된 가변 테마 할당
        for node_id, idx_val in valid_nodes:
            try:
                ui_refs = self.nodes[node_id]
                node_type = dpg.get_value(ui_refs["type"])
                dtype_int = int(node_type[0])
                special_code = dpg.get_value(ui_refs.get("special_code_int", None))
                
                # 중복 에러가 발생한 경우
                if dtype_int == 2 and start_node_code_counts.get(special_code, 0) > 1:
                    target_theme = self.get_or_create_zoom_theme(self.zoom_scale, "warning")
                elif index_counts[idx_val] > 1: 
                    target_theme = self.get_or_create_zoom_theme(self.zoom_scale, "warning")
                    
                # 대화 Type에 따른 색상 + 가변 레이아웃 지정
                elif dtype_int == 1:   # 가변 Function 테마
                    target_theme = self.get_or_create_zoom_theme(self.zoom_scale, "function")
                elif dtype_int == 2: # 가변 Start 테마
                    target_theme = self.get_or_create_zoom_theme(self.zoom_scale, "start")
                elif dtype_int == 3: # 가변 End 테마
                    target_theme = self.get_or_create_zoom_theme(self.zoom_scale, "end")
                    
                # 일반(Normal) 노드
                else: 
                    target_theme = self.get_or_create_zoom_theme(self.zoom_scale, "normal")
                
                dpg.bind_item_theme(node_id, target_theme)
                
            except Exception: 
                pass
        

    def link_callback(self, sender, app_data):
        if self._is_restoring: return  
        self.save_state()
        sender_pin, receiver_pin = app_data
        existing_links = [link for link in self.links if link[1] == sender_pin]
        for old_link in existing_links:
            old_link_id = old_link[0]
            if dpg.does_item_exist(old_link_id): dpg.delete_item(old_link_id)
            self.links.remove(old_link)
        link_id = dpg.add_node_link(sender_pin, receiver_pin, parent=sender)
        self.links.append((link_id, sender_pin, receiver_pin))
        self.update_link_colors()

    def delink_callback(self, sender, app_data):
        if self._is_restoring: return  
        self.save_state()
        dpg.delete_item(app_data)
        self.links = [link for link in self.links if link[0] != app_data]

    def delete_selected_node(self):
        if self._is_restoring: return
        selected_nodes = dpg.get_selected_nodes("node_editor")
        if not selected_nodes: return
        self.save_state()
        for node_id in selected_nodes:
            if not dpg.does_item_exist(node_id): continue
            ui_refs = self.nodes.get(node_id)
            if not ui_refs: continue
            all_node_pins = [ui_refs["input_pin"]] + [res["pin_id"] for res in ui_refs["responses"]]
            links_to_remove = [l for l in self.links if l[1] in all_node_pins or l[2] in all_node_pins]
            for link in links_to_remove:
                if dpg.does_item_exist(link[0]): dpg.delete_item(link[0])
                if link in self.links: self.links.remove(link)
            dpg.delete_item(node_id)
            self.nodes.pop(node_id, None)
            self.node_positions.pop(node_id, None)
        self.update_node_colors()

    def delete_selected_links(self):
        if self._is_restoring: return
        selected_links = dpg.get_selected_links("node_editor")
        if not selected_links: return
        self.save_state()
        for link_id in selected_links:
            if dpg.does_item_exist(link_id): dpg.delete_item(link_id)
            self.links = [link for link in self.links if link[0] != link_id]

    def _get_file_path(self, mode="open"):
        root = tk.Tk()
        root.withdraw()
        file_path = ""
        if mode == "open": file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        elif mode == "save": file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        root.destroy()
        return file_path

    def import_from_json(self):
        file_path = self._get_file_path("open")
        if not file_path: return
        self.save_state()
        with open(file_path, "r", encoding="utf-8") as f: data = json.load(f)
        self.load_json(data)

    def load_json(self, data):
        snapshot_format = {
            "Functions": data.get("Functions", ["PlaySound", "GiveItem", "SpawnMonster"]),
            "Dialogues": data.get("Dialogues", []),
            "node_counter": max([int(d["DialogueIndex"]) for d in data.get("Dialogues", [])]) if data.get("Dialogues") else 0,
            "zoom_scale": 1.0
        }
        self.restore_snapshot(snapshot_format)

    def get_compiled_data(self):
        pin_to_index = {}
        compiled_dialogues = {}
        for node_id, ui_refs in list(self.nodes.items()):
            if dpg.does_item_exist(node_id):
                index_val = dpg.get_value(ui_refs["index"])
                pin_to_index[ui_refs["input_pin"]] = index_val

        for node_id, ui_refs in list(self.nodes.items()):
            if not dpg.does_item_exist(node_id): continue
            try:
                d_idx = dpg.get_value(ui_refs["index"])
                dtype_str = dpg.get_value(ui_refs["type"])
                dtype_int = int(dtype_str.split(":")[0])

                if dtype_int == 1: special_code = str(dpg.get_value(ui_refs["special_code_text"]))
                elif dtype_int == 2: special_code = str(dpg.get_value(ui_refs["special_code_int"]))
                else: special_code = ""

                pos = self.node_positions.get(node_id, [100, 100])

                node_data = {
                    "DialogueIndex": d_idx,
                    "DialogueType": dtype_int,
                    "DialogueText": dpg.get_value(ui_refs["text"]),
                    "HasResponse": dpg.get_value(ui_refs["has_response"]),
                    "SpecialCode": special_code,
                    "Position": pos, 
                    "Responses": []
                }

                for res in ui_refs["responses"]:
                    rtype_str = dpg.get_value(res["type"])
                    rtype_int = int(rtype_str.split(":")[0])
                    res_code = dpg.get_value(res["code"]) if rtype_int == 1 else ""

                    res_data = {
                        "ResponseText": dpg.get_value(res["text"]),
                        "ResponseType": rtype_int,
                        "ResponseCode": res_code,
                        "NextDialogueIndex": -1
                    }

                    for link_id, sender_pin, receiver_pin in self.links:
                        if sender_pin == res["pin_id"]:
                            if receiver_pin in pin_to_index: res_data["NextDialogueIndex"] = pin_to_index[receiver_pin]
                            break
                    node_data["Responses"].append(res_data)

                compiled_dialogues[d_idx] = node_data
            except Exception: pass
        return compiled_dialogues

    def export_to_json(self):
        self.update_original_positions_from_viewport()
        compiled = self.get_compiled_data()
        export_data = list(compiled.values())
        file_path = self._get_file_path("save")
        if not file_path: return
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"Functions": self.function_list, "Dialogues": export_data}, f, ensure_ascii=False, indent=4)

    def on_dialogue_type_change(self, sender, app_data, user_data):
        node_id = user_data
        ui_refs = self.nodes[node_id]
        dpg.hide_item(ui_refs["special_code_text"])
        dpg.hide_item(ui_refs["special_code_int"])
        if app_data.startswith("1"): dpg.show_item(ui_refs["special_code_text"])
        elif app_data.startswith("2"): dpg.show_item(ui_refs["special_code_int"])
        self.update_node_colors()

    def on_response_type_change(self, sender, app_data, user_data):
        code_input_id = user_data
        if app_data.startswith("1"): dpg.show_item(code_input_id)
        else: dpg.hide_item(code_input_id)
        self.update_link_colors()

    def on_index_change(self, sender, app_data, user_data):
        if self._is_restoring: return
        node_id = user_data
        try:
            new_idx = int(app_data)
        except Exception:
            return

        label_text = ""
        ui_refs = self.nodes.get(node_id)
        try:
            if ui_refs and dpg.does_item_exist(ui_refs.get("text")):
                label_text = dpg.get_value(ui_refs["text"]) or ""
                label_text = label_text.split("\n")[0]
        except Exception:
            label_text = ""

        if dpg.does_item_exist(node_id):
            dpg.configure_item(node_id, label=f"Node {new_idx} : {label_text}")
        self.update_node_colors()

    def remove_response(self, sender, app_data, user_data):
        if self._is_restoring: return
        self.save_state()
        node_id, pin_id = user_data
        ui_refs = self.nodes[node_id]
        res_to_remove = next((r for r in ui_refs["responses"] if r["pin_id"] == pin_id), None)
        if res_to_remove:
            links_to_remove = [l for l in self.links if l[1] == pin_id or l[2] == pin_id]
            for link in links_to_remove:
                if dpg.does_item_exist(link[0]): dpg.delete_item(link[0])
                self.links.remove(link)
            if dpg.does_item_exist(pin_id): dpg.delete_item(pin_id)
            ui_refs["responses"].remove(res_to_remove)

    def add_node(self, cout = None, bol = False, text = ""):
        if not self._is_restoring and not bol: self.save_state()

        self.node_counter += 1
        node_index_id = 1
        if bol and cout is not None: node_index_id = cout

        if text == None:
            text = ""

        while any(dpg.get_value(ui_refs["index"]) == node_index_id for ui_refs in self.nodes.values()):
            node_index_id += 1

        with dpg.node(label=f"Node {node_index_id} : {text}", parent="node_editor") as node_id:
            ui_refs = {
                "input_pin": None, "index": None, "type": None, "text": None,
                "has_response": None, "special_code_text": None, "special_code_int": None, 
                "responses": [],
                "add_response_btn": None # 👈 버튼을 추적할 수 있도록 키 추가
            }

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input) as in_pin:
                dpg.add_text("Input (From Previous)")
                ui_refs["input_pin"] = in_pin

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                ui_refs["index"] = dpg.add_input_int(label="Index", width=100, default_value=node_index_id,
                                                     callback=self.on_index_change, user_data=node_id)
                
                dialogue_types = ["0: Normal", "1: Function", "2: Start", "3: End"]
                ui_refs["type"] = dpg.add_combo(dialogue_types, label="Type", width=120, default_value="0: Normal", 
                                                callback=self.on_dialogue_type_change, user_data=node_id)
                
                dpg.add_spacer(height=5)
                dpg.add_text("Dialogue Text:")
                ui_refs["text"] = dpg.add_input_text(multiline=True, width=250, height=70, readonly=True)

                dpg.add_button(label="Edit", callback=self.edit_text_popup, user_data=(ui_refs["text"], node_id))
                
                dpg.add_spacer(height=5)
                ui_refs["has_response"] = dpg.add_checkbox(label="Has Response")
                
                ui_refs["special_code_text"] = dpg.add_combo(self.function_list, label="Func Select", width=150, show=False)
                ui_refs["special_code_int"] = dpg.add_input_int(label="Code (Start ID)", width=150, show=False, step=1, callback=self.update_node_colors)
                
                dpg.add_spacer(height=10)
                ui_refs["add_response_btn"] = dpg.add_button(
                    label="+ Add Response", user_data=node_id, callback=self.add_response, width=250
                )

            self.nodes[node_id] = ui_refs
            
            if node_id not in self.node_positions:
                self.node_positions[node_id] = [100.0, 100.0]
            
            # 생성될 때 현재 배율의 테마와 위젯 크기를 강제로 매핑
            current_theme = self.get_or_create_zoom_theme(self.zoom_scale)
            dpg.bind_item_theme(node_id, current_theme)

            scaled_x = self.node_positions[node_id][0] * self.zoom_scale
            scaled_y = self.node_positions[node_id][1] * self.zoom_scale
            dpg.set_item_pos(node_id, [scaled_x, scaled_y])

        # 크기 리프레시 강제 유도
        self.synchronize_positions_to_screen()
        self.update_node_colors()
        self.set_zoom_scale_at_mouse(self.zoom_scale)
        self.update_node_colors()
        return node_id

    def add_response(self, sender, app_data, user_data):
        if not self._is_restoring and sender is not None: self.save_state()

        node_id = user_data
        ui_refs = self.nodes[node_id]

        with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, parent=node_id) as out_pin:
            dpg.add_spacer(height=5)
            with dpg.group(horizontal=True):
                dpg.add_text("Response", color=[100, 255, 100])
                dpg.add_button(label="[X]", user_data=(node_id, out_pin), callback=self.remove_response)
            
            with dpg.group(horizontal=True):
                res_text = dpg.generate_uuid()
                dpg.add_button(label="Edit", callback=self.edit_text_popup, user_data=(res_text,None))
                dpg.add_input_text(label="Text", width=150, readonly=True, tag=res_text)

            res_code_id_placeholder = dpg.generate_uuid()
            res_type = dpg.add_combo(["0: No Effect", "1: Function"], label="Type", width=110, default_value="0: No Effect",
                                     callback=self.on_response_type_change, user_data=res_code_id_placeholder)
            
            res_code = dpg.add_combo(self.function_list, tag=res_code_id_placeholder, label="Func Select", width=150, show=False)

            ui_refs["responses"].append({
                "pin_id": out_pin, "text": res_text, "type": res_type, "code": res_code
            })
            if dpg.does_item_exist(res_text): dpg.configure_item(res_text, width=int(150 * self.zoom_scale))
            if dpg.does_item_exist(res_type): dpg.configure_item(res_type, width=int(110 * self.zoom_scale))
            if dpg.does_item_exist(res_code): dpg.configure_item(res_code, width=int(150 * self.zoom_scale))

    def copy_selected_node(self):
        self.update_original_positions_from_viewport()
        selected_nodes = dpg.get_selected_nodes("node_editor")
        if not selected_nodes: return
        target_node = selected_nodes[0]
        ui_refs = self.nodes.get(target_node)
        if not ui_refs: return

        responses_backup = []
        for res in ui_refs["responses"]:
            responses_backup.append({
                "text": dpg.get_value(res["text"]), "type": dpg.get_value(res["type"]), "code": dpg.get_value(res["code"])
            })

        self.copied_node_data = {
            "type": dpg.get_value(ui_refs["type"]),
            "text": dpg.get_value(ui_refs["text"]),
            "has_response": dpg.get_value(ui_refs["has_response"]),
            "special_code_text": dpg.get_value(ui_refs["special_code_text"]),
            "special_code_int": dpg.get_value(ui_refs["special_code_int"]),
            "responses": responses_backup,
            "pos" : self.node_positions.get(target_node, [100, 100]).copy(),
            "index" : dpg.get_value(ui_refs["index"])
        }