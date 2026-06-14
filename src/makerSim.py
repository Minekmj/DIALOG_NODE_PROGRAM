# -*- coding: utf-8 -*-
import dearpygui.dearpygui as dpg

    
class DialogueNodeSim:
    def __init__(self):
        # 시뮬레이터 관리 변수
        self.current_sim_index = None
        self.sim_data = {}

        with dpg.theme() as self.sim_console_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, [25, 25, 25, 255])
                
        with dpg.theme() as self.sim_screen_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, [40, 40, 40, 255])

        with dpg.theme() as self.start_btn_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [40, 150, 40, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [50, 180, 50, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [30, 120, 30, 255])

    def get_compiled_data(self, data):
        pin_to_index = {}
        compiled_dialogues = {}
        for node_id, ui_refs in data.nodes.items():
            if dpg.does_item_exist(node_id):
                index_val = dpg.get_value(ui_refs["index"])
                pin_to_index[ui_refs["input_pin"]] = index_val

        for node_id, ui_refs in data.nodes.items():
            if not dpg.does_item_exist(node_id):
                continue
            try:
                d_idx = dpg.get_value(ui_refs["index"])
                dtype_str = dpg.get_value(ui_refs["type"])
                dtype_int = int(dtype_str.split(":")[0])

                if dtype_int == 1:
                    special_code = str(dpg.get_value(ui_refs["special_code_text"]))
                elif dtype_int == 2:
                    special_code = str(dpg.get_value(ui_refs["special_code_int"]))
                else:
                    special_code = ""

                pos = dpg.get_item_pos(node_id)
                if not pos: pos = [100, 100]

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

                    for link_id, sender_pin, receiver_pin in data.links:
                        if sender_pin == res["pin_id"]:
                            if receiver_pin in pin_to_index:
                                res_data["NextDialogueIndex"] = pin_to_index[receiver_pin]
                            break
                    node_data["Responses"].append(res_data)

                compiled_dialogues[d_idx] = node_data
            except Exception:
                pass
        return compiled_dialogues


    def open_simulation_window(self, data):
        if dpg.does_item_exist("sim_window"):
            dpg.delete_item("sim_window")

        self.sim_data = self.get_compiled_data(data)
        default_start_idx = 1
        for idx, nd in self.sim_data.items():
            if nd["DialogueType"] == 2:
                try:
                    default_start_idx = int(nd["SpecialCode"])
                except:
                    default_start_idx = idx
                break
        if default_start_idx == 1 and self.sim_data:
            default_start_idx = min(self.sim_data.keys())

        with dpg.window(label="Dialogue Simulator", tag="sim_window", width=450, height=520, pos=(400, 150), no_collapse=True, no_close=False):
            dpg.add_text("Function & System Console Log")
            with dpg.child_window(tag="sim_console", height=120):
                dpg.add_text("[LOG]: Simulator Ready.", color=[0, 255, 255])
            dpg.bind_item_theme("sim_console", self.sim_console_theme)
            dpg.add_separator()
            dpg.add_spacer(height=5)

            with dpg.group(tag="sim_launcher_group"):
                dpg.add_text("▼ Enter Start Special INT to Begin:", color=[255, 255, 255])
                dpg.add_input_int(tag="sim_start_index_input", label="Start Special INT", default_value=default_start_idx, width=150)
                dpg.add_button(label="Launch Dialogue", callback=self.start_sim_from_input, width=-1, height=30)

            with dpg.group(tag="sim_active_dialogue_group", show=False):
                dpg.add_text("Dialogue Screen", color=[255, 200, 0])
                with dpg.child_window(tag="dialogue_screen", height=120):
                    dpg.add_text("", tag="sim_dialogue_text", wrap=400)
                dpg.bind_item_theme("dialogue_screen", self.sim_screen_theme)
                dpg.add_spacer(height=10)
                dpg.add_text("Select Response")
                dpg.add_group(tag="sim_response_group")
            # 윈도우 창 위로
            try:
                dpg.bring_item_to_front("sim_window")
                dpg.focus_item("sim_window")
            except Exception:
                pass

    def start_sim_from_input(self):
        entered = dpg.get_value("sim_start_index_input")
        target_idx = None
        entered_str = str(entered) if entered is not None else ""
        try:
            entered_int = int(entered)
        except Exception:
            entered_int = None

        for idx, nd in self.sim_data.items():
            try:
                dt = int(nd.get("DialogueType", None))
            except Exception:
                dt = None
            if dt != 2:
                continue

            sc_raw = nd.get("SpecialCode", None)
            if sc_raw is None:
                continue

            try:
                sc_int = int(sc_raw)
            except Exception:
                sc_int = None

            if entered_int is not None and sc_int is not None and sc_int == entered_int:
                target_idx = idx
                break

            if str(sc_raw) == entered_str:
                target_idx = idx
                break

        if target_idx is None:
            self.log_to_sim_console(f"No start node with SpecialCode={entered} found.", color=[255,100,100])
            return

        dpg.hide_item("sim_launcher_group")
        dpg.show_item("sim_active_dialogue_group")
        self.go_to_sim_node(target_idx)

    def log_to_sim_console(self, text, color=[0, 255, 255]):
        if dpg.does_item_exist("sim_console"):
            dpg.add_text(f"[LOG]: {text}", parent="sim_console", color=color)
            dpg.set_y_scroll("sim_console", dpg.get_y_scroll_max("sim_console") + 50)

    def go_to_sim_node(self, node_index):
        self.current_sim_index = node_index
        if dpg.does_item_exist("sim_response_group"):
            dpg.delete_item("sim_response_group", children_only=True)

        if node_index not in self.sim_data:
            dpg.set_value("sim_dialogue_text", f"[끝 혹은 유효하지 않은 인덱스 노드입니다.]\n(입력되었던 인덱스: {node_index})")
            return

        node = self.sim_data[node_index]
        dpg.set_value("sim_dialogue_text", f"[Node {node_index}]\n{node['DialogueText']}")

        if node["DialogueType"] == 1:
            func_name = node["SpecialCode"] if node["SpecialCode"] else "UnknownFunction"
            self.log_to_sim_console(f"대화 함수 발동!! -> [ {func_name}() ]", color=[100, 255, 100])
        elif node["DialogueType"] == 3:
            self.log_to_sim_console(f"End-Node 도달 (Index: {node_index})", color=[255, 200, 0])
        else:
            self.log_to_sim_console(f"Moved to Dialogue Node {node_index}")

        if node["HasResponse"] and node["Responses"]:
            for res in node["Responses"]:
                btn_label = res["ResponseText"] if res["ResponseText"] else "(선택지 텍스트 없음)"
                dpg.add_button(label=btn_label, callback=self.on_select_sim_response, user_data=res, parent="sim_response_group", width=-1, height=30)
        else:
            next_idx = -1
            for res in node["Responses"]:
                if res["NextDialogueIndex"] != -1:
                    next_idx = res["NextDialogueIndex"]
                    break
            if next_idx != -1:
                dpg.add_button(label="Next >>", callback=lambda: self.go_to_sim_node(next_idx), parent="sim_response_group", width=-1, height=30)
            else:
                dpg.add_button(label="Close / End Dialogue", callback=lambda: dpg.delete_item("sim_window"), parent="sim_response_group", width=-1, height=30)

    def on_select_sim_response(self, sender, app_data, user_data):
        res_data = user_data
        
        if res_data["ResponseType"] == 1:
            res_func = res_data["ResponseCode"] if res_data["ResponseCode"] else "UnknownResponseFunction"
            self.log_to_sim_console(f"선택지 함수 발동!! -> [ {res_func}() ]", color=[150, 255, 150])
        else:
            self.log_to_sim_console(f"Selected response: '{res_data['ResponseText']}'")
            
        next_node_idx = res_data["NextDialogueIndex"]
        self.go_to_sim_node(next_node_idx)