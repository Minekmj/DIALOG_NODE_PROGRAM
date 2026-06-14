import dearpygui.dearpygui as dpg #대충 dearpygui 라이브러리 가져오기

from src.makerMain import DialogueNodeEditor
from src.makerSim import DialogueNodeSim

def StartMain():
    dpg.create_context()

    # 배율 증감 스펙 정의
    zoom_state = {
        "current": 1.0,
        "min": 0.4,
        "max": 2.2,
        "step": 0.15
    }

    # 코드 상단에 폰트 객체 변수 선언
    korean_font = None 

    # 폰트 등록 부분
    with dpg.font_registry():
        with dpg.font(r"C:\Windows\Fonts\malgun.ttf", 16) as f: #<- 폰트 파일 위치
            korean_font = f # 객체를 변수에 저장

    dpg.bind_font(korean_font)

    editor = DialogueNodeEditor()
    sim = DialogueNodeSim()

    def clean_shortcut_handler(sender, app_data):
        if editor._is_restoring: return 

        if dpg.is_key_down(dpg.mvKey_ModCtrl) and app_data == dpg.mvKey_Z:
            editor.undo()
            editor.set_zoom_scale_at_mouse(editor.zoom_scale, 0, 0)
        elif dpg.is_key_down(dpg.mvKey_ModCtrl) and app_data == dpg.mvKey_Y:
            editor.redo()
            editor.set_zoom_scale_at_mouse(editor.zoom_scale, 0, 0)
        elif dpg.is_key_down(dpg.mvKey_ModCtrl) and app_data == dpg.mvKey_C:
            if dpg.get_selected_nodes("node_editor"):
                editor.copy_selected_node()
        elif dpg.is_key_down(dpg.mvKey_ModCtrl) and app_data == dpg.mvKey_V:
            if editor.copied_node_data:
                editor.save_state()
                new_node_id = editor.add_node(int(editor.copied_node_data["index"])+1, True, '/'.join(editor.copied_node_data["text"].split("\n")))
                ui_refs = editor.nodes[new_node_id]
                dpg.set_value(ui_refs["type"], editor.copied_node_data["type"])
                dpg.set_value(ui_refs["text"], editor.copied_node_data["text"])
                dpg.set_value(ui_refs["has_response"], editor.copied_node_data["has_response"])
                dpg.set_value(ui_refs["special_code_text"], editor.copied_node_data["special_code_text"])
                dpg.set_value(ui_refs["special_code_int"], editor.copied_node_data["special_code_int"])
                editor.on_dialogue_type_change(None, editor.copied_node_data["type"], new_node_id)

                for res in editor.copied_node_data["responses"]:
                    editor.add_response(None, None, new_node_id)
                    new_res_ref = ui_refs["responses"][-1]
                    dpg.set_value(new_res_ref["text"], res["text"])
                    dpg.set_value(new_res_ref["type"], res["type"])
                    editor.on_response_type_change(None, res["type"], new_res_ref["code"])
                    dpg.set_value(new_res_ref["code"], res["code"])

                # 캐시 영역에 먼저 1.0배율 기준 원본 좌표 오프셋 부여
                origin_pos = editor.copied_node_data["pos"].copy()
                origin_pos[0] += 80
                origin_pos[1] += 80
                # 보조 위치 캐시(에디터가 이를 사용해 현재 배율로 동기화)
                editor.node_positions[new_node_id] = origin_pos

                # 배치 동기화 호출로 현재 배율에 맞는 화면 좌표로 자동 배치
                editor.synchronize_positions_to_screen()
                editor.update_node_colors()
                editor.set_zoom_scale_at_mouse(editor.zoom_scale)
                editor.update_node_colors()
                
        elif app_data == dpg.mvKey_Delete:
            if dpg.get_selected_nodes("node_editor"):
                editor.delete_selected_node()
            if dpg.get_selected_links("node_editor"):
                editor.delete_selected_links()

    def mouse_wheel_handler(sender, app_data):

        # 포지션 저장
        editor.update_original_positions_from_viewport()

        # 확대 축소 배율 변경
        if app_data > 0:
            next_scale = min(zoom_state["max"], zoom_state["current"] + zoom_state["step"])
        elif app_data < 0:
            next_scale = max(zoom_state["min"], zoom_state["current"] - zoom_state["step"])
            
        if next_scale == zoom_state["current"]:
            return

        # self에 저장된 고정 값을 기준으로 확대/축소 레이아웃 변경 함수 호출
        editor.set_zoom_scale_at_mouse(next_scale)
        editor.update_node_colors()
        
        # 동기화
        zoom_state["current"] = editor.zoom_scale


    with dpg.handler_registry():
        dpg.add_key_release_handler(callback=clean_shortcut_handler)
        dpg.add_mouse_wheel_handler(callback=mouse_wheel_handler)

    # --- 레이아웃 정의 ---
    with dpg.window(label="Control Panel", tag="control_panel_window", width=300, height=800, pos=(0, 0), no_close=True, no_move=True, no_title_bar=True):
        dpg.add_text("NPC Dialogue Editor", color=[255, 200, 0])
        dpg.add_separator()
        dpg.add_button(label="▶ Start Simulation", tag="sim_start_btn", callback=lambda: sim.open_simulation_window(editor), width=-1, height=45)
        dpg.bind_item_theme("sim_start_btn", sim.start_btn_theme)
        dpg.add_spacer(height=10)
        dpg.add_button(label="Add New Node", callback=editor.add_node, width=-1, height=35)
        dpg.add_button(label="Delete Selected Node", callback=editor.delete_selected_node, width=-1, height=30)
        dpg.add_spacer(height=10)
        dpg.add_button(label="Import JSON", callback=editor.import_from_json, width=-1, height=35)
        dpg.add_button(label="Export JSON", callback=editor.export_to_json, width=-1, height=35)
        
        dpg.add_spacer(height=15)
        dpg.add_separator()
        dpg.add_text("Global Function List", color=[100, 200, 255])
        dpg.add_input_text(tag="new_func_input", hint="Enter func name...", width=-1)
        dpg.add_button(label="+ Add Function", callback=editor.add_global_function, width=-1)
        dpg.add_spacer(height=5)
        dpg.add_combo(editor.function_list, tag="global_func_combo", default_value=editor.function_list[0] if editor.function_list else "", width=-1)
        dpg.add_button(label="- Delete Function", callback=editor.delete_global_function, width=-1)
        dpg.add_separator()
        dpg.add_spacer(height=15)
        dpg.add_text("Shortcuts:")
        dpg.add_text("- Ctrl + Z : Undo\n- Ctrl + Y : Redo\n- Ctrl + C : Copy Node\n- Ctrl + V : Paste Node\n- Delete : Delete Selected", color=[200, 200, 200])
        

    with dpg.window(label="Node Workspace", tag="node_workspace_tag", width=1020, height=800, pos=(300, 0), no_close=True, no_move=True, no_title_bar=True):
        with dpg.node_editor(tag="node_editor", callback=editor.link_callback, delink_callback=editor.delink_callback, minimap=True):
            pass
    
    def resize_callback(sender, app_data):
        new_width = app_data[0]
        new_height = app_data[1]

        # 컨트롤 패널의 높이를 뷰포트 높이와 항상 일치시키기
        dpg.set_item_width("control_panel_window", 300)
        dpg.set_item_height("control_panel_window", new_height)

        dpg.set_item_pos("node_workspace_tag", [300,0])

        dpg.set_item_width("node_workspace_tag", new_width - 300)
        dpg.set_item_height("node_workspace_tag", new_height)

    dpg.set_viewport_resize_callback(resize_callback)

    dpg.create_viewport(title='대화 노드 프로그램', width=1280, height=840)
    dpg.setup_dearpygui()
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        editor.process_text_queue()
        editor.monitor_changes()
        dpg.render_dearpygui_frame()

    dpg.destroy_context()