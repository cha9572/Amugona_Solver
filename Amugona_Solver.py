import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import ttk
import random
import datetime
import os
import requests  # API 호출을 위해 requests 모듈 추가

# --- 설정 변수 ---
# 카카오 REST API 키를 입력하는 변수입니다. 나중에 키만 복사해서 넣으면 바로 작동합니다.
KAKAO_API_KEY = "1a890234d0d54f9b0f3313c41d537a9f"

# --- 전역 변수 (데이터를 저장할 리스트) ---
menus = []        # 메뉴(또는 벌칙) 후보를 저장할 리스트
HISTORY_FILE = "history.txt" # 기록을 저장할 텍스트 파일 이름

# --- 함수 정의 부분 (클래스 없이 절차지향적으로 작성) ---

def add_menu():
    """
    메뉴 추가 버튼을 누르거나 엔터키를 쳤을 때 실행되는 함수입니다.
    입력창에 적힌 메뉴를 가져와서 리스트와 화면(Listbox)에 추가합니다.
    """
    # 입력창에서 텍스트를 가져와 공백을 제거합니다.
    menu = entry_menu.get().strip()
    
    if menu:
        # 중복 체크: 이미 리스트에 있는 메뉴면 추가하지 않습니다.
        if menu in menus:
            messagebox.showwarning("중복 오류", "이미 추가된 메뉴입니다!")
        else:
            menus.append(menu) # 파이썬 리스트에 메뉴 추가
            listbox_menus.insert(tk.END, menu) # 화면 리스트박스에 추가
            entry_menu.delete(0, tk.END) # 입력창 비우기
    else:
        messagebox.showwarning("입력 오류", "메뉴(또는 벌칙)를 입력해주세요!")

def delete_menu(event=None):
    """
    리스트박스에서 선택된 메뉴를 삭제하는 함수입니다.
    키보드 Delete/BackSpace 키나 '선택 항목 삭제' 버튼을 누르면 실행됩니다.
    """
    selected_indices = listbox_menus.curselection()
    
    if selected_indices:
        # 여러 개가 선택되었을 때 인덱스 밀림을 방지하기 위해 뒤에서부터 삭제합니다.
        for index in reversed(selected_indices):
            del menus[index] # 파이썬 내부 리스트에서 삭제
            listbox_menus.delete(index) # 화면(리스트박스)에서 삭제
    else:
        # 키보드가 아닌 마우스로 삭제 버튼을 클릭했는데 아무것도 선택되지 않았을 때만 경고
        if event is None:
            messagebox.showwarning("삭제 오류", "삭제할 메뉴를 리스트에서 클릭하여 선택해주세요!")

def clear_menu():
    """
    모든 메뉴 선택지를 초기화하는 함수입니다.
    """
    if not menus:
        messagebox.showinfo("안내", "이미 초기화되어 메뉴가 없습니다.")
        return
        
    answer = messagebox.askyesno("전체 초기화", "추가된 모든 메뉴를 전부 지우시겠습니까?")
    if answer:
        menus.clear() # 파이썬 내부 리스트 비우기
        listbox_menus.delete(0, tk.END) # 화면 리스트박스 내용 전체 삭제

def load_restaurants():
    """
    IP 기반 위치 정보를 가져온 후, 해당 위치(내 주변)를 기준으로 
    카카오 로컬 API를 호출하여 주변 '맛집'을 검색하는 함수입니다.
    """
    try:
        # 0. 사용자가 설정한 추가 개수 가져오기
        try:
            req_size = int(spin_count.get())
            req_size = max(1, min(15, req_size)) # API 최대 한도 15개로 제한
        except ValueError:
            req_size = 5 # 숫자가 아닐 경우 기본값
            
        lbl_location.config(text="📍 현재 탐색 위치: 위치 정보 검색 중...")
        window.update() # UI 즉각 반영
        
        # 1. 사용자가 직접 입력한 주소가 있는지 확인합니다.
        user_address = entry_address.get().strip()
        headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
        
        if user_address:
            # 주소를 입력한 경우: 카카오 로컬 API(장소 검색)를 이용해 해당 주소의 좌표(x, y)를 알아냅니다.
            search_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
            addr_params = {"query": user_address, "size": 1} # 가장 정확한 1개만 가져옵니다.
            
            addr_response = requests.get(search_url, headers=headers, params=addr_params)
            if addr_response.status_code == 200:
                addr_data = addr_response.json()
                documents = addr_data.get('documents', [])
                if not documents:
                    messagebox.showerror("위치 오류", "입력하신 주소나 장소를 찾을 수 없습니다.")
                    lbl_location.config(text="📍 탐색 위치: 검색 실패")
                    return
                
                # 첫 번째 결과의 좌표와 장소명을 가져옵니다.
                lat = documents[0].get("y")
                lon = documents[0].get("x")
                address_name = documents[0].get("place_name") or documents[0].get("address_name")
                lbl_location.config(text=f"📍 탐색 위치: {address_name} 주변")
            else:
                messagebox.showerror("API 오류", "주소 검색에 실패했습니다.")
                lbl_location.config(text="📍 탐색 위치: 오류 발생")
                return
        else:
            # 빈칸인 경우: 기존처럼 IP 기반 무료 API를 호출하여 현재 위치를 알아냅니다.
            location_response = requests.get("http://ip-api.com/json/")
            if location_response.status_code == 200:
                location_data = location_response.json()
                lat = location_data.get("lat")
                lon = location_data.get("lon")
                
                # 카카오 좌표->행정동 변환 API 호출
                addr_url = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json"
                addr_params = {"x": lon, "y": lat}
                addr_response = requests.get(addr_url, headers=headers, params=addr_params)
                
                if addr_response.status_code == 200:
                    addr_data = addr_response.json()
                    docs = addr_data.get('documents', [])
                    if docs:
                        address_name = docs[0].get('address_name', '알 수 없는 위치')
                        lbl_location.config(text=f"📍 현재 위치: {address_name}")
                else:
                    lbl_location.config(text="📍 현재 위치: 주소 변환 실패")
            else:
                messagebox.showerror("위치 오류", "현재 위치를 가져오는데 실패했습니다.")
                lbl_location.config(text="📍 현재 위치: 알 수 없음")
                return
            
        # 4. 내 위치 주변 검색에 필요한 파라미터(Parameter) 정보를 설정합니다.
        url = "https://dapi.kakao.com/v2/local/search/keyword.json"
        
        # 사용자가 선택한 카테고리에 따라 검색어를 설정합니다.
        selected_category = combo_category.get()
        if selected_category == "전체":
            search_query = "맛집"
        else:
            search_query = f"{selected_category} 맛집"
            
        params = {
            "query": search_query,
            "y": lat,
            "x": lon,
            "radius": 2000,
            "size": req_size
        }
        
        # 5. requests 모듈을 사용하여 카카오 서버에 HTTP GET 요청을 보냅니다.
        response = requests.get(url, headers=headers, params=params)
        
        # 6. 응답 상태 코드가 200(성공)인지 확인합니다.
        if response.status_code == 200:
            data = response.json()
            places = data.get('documents', [])
            
            if not places:
                messagebox.showinfo("검색 결과", "주변에 검색된 식당이 없습니다.")
                return
                
            # 7. 무작위로 추출하기 위해 파이썬의 random 모듈을 사용하여 결과 리스트의 순서를 섞어줍니다.
            random.shuffle(places)
            
            # 8. 상위 순서대로 사용자가 원하는 만큼의 식당 정보를 추출합니다.
            selected_places = places[:req_size]
            
            # 9. 중복을 방지하여 식당 목록을 리스트와 화면에 추가합니다.
            added_count = 0
            for place in selected_places:
                restaurant_name = place.get('place_name') # 개별 식당 데이터에서 상호명 추출
                if restaurant_name not in menus:
                    menus.append(restaurant_name) # 파이썬의 메뉴 리스트 변수에 상호명 추가
                    listbox_menus.insert(tk.END, restaurant_name) # 화면(GUI)의 리스트박스 맨 끝에 상호명 삽입
                    added_count += 1
                
            if added_count > 0:
                messagebox.showinfo("불러오기 완료", f"내 위치 주변 식당 {added_count}개를 새로 추가했습니다!\n(기존에 있던 중복 식당 제외)")
            else:
                messagebox.showinfo("불러오기 완료", "가져온 식당들이 이미 모두 메뉴에 있습니다.")
        else:
            messagebox.showerror("API 오류", f"API 호출에 실패했습니다.\n상태 코드: {response.status_code}")
    except Exception as e:
        messagebox.showerror("실행 오류", f"식당 정보를 불러오는 중 오류가 발생했습니다:\n{e}\n\n터미널에서 'pip install requests' 명령어를 실행하여 모듈이 설치되어 있는지 확인해주세요.")

def show_results():
    """
    결과 보기 버튼을 누를 때 실행되는 함수입니다.
    메뉴들 중 하나를 무작위로 선택하는 룰렛 애니메이션을 보여줍니다.
    """
    if not menus:
        messagebox.showwarning("경고", "메뉴를 최소 1개 이상 입력해주세요!")
        return 
        
    # 새로운 창 띄우기
    roulette_window = tk.Toplevel(window)
    roulette_window.title("메뉴 고르는 중...")
    roulette_window.geometry("400x300")
    roulette_window.configure(bg="#F8FAFC")
    
    # 룰렛 텍스트를 보여줄 라벨
    lbl_result = tk.Label(roulette_window, text="과연...", font=("Helvetica", 24, "bold"), bg="#F8FAFC", fg="#1E293B")
    lbl_result.pack(expand=True, fill=tk.BOTH)
    
    # 애니메이션을 위한 함수
    def animate_roulette(count):
        if count > 0:
            # 남은 횟수 동안 무작위 메뉴를 빠르게 보여줍니다.
            random_menu = random.choice(menus)
            lbl_result.config(text=random_menu)
            # 점점 느려지게 만듭니다 (기본 50ms, 남은 횟수가 적어지면 딜레이 증가)
            delay = 50 + (20 - count) * 15 
            roulette_window.after(delay, animate_roulette, count - 1)
        else:
            # 최종 선택된 메뉴
            final_menu = random.choice(menus)
            lbl_result.config(text=f"🎉 {final_menu} 🎉", fg="#EF4444")
            
            # 결과 저장
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result_text = f"--- [ {now} ] 뽑기 결과 ---\n\n"
            result_text += f"👉  선택된 메뉴: {final_menu}\n"
            result_text += "\n-----------------------------------\n\n"
            
            try:
                with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
                    f.write(result_text)
            except Exception as e:
                messagebox.showerror("저장 오류", f"기록을 저장하는 중 오류가 발생했습니다:\n{e}")
                
    # 룰렛 애니메이션 시작 (20번 변경)
    animate_roulette(20)

def show_history():
    """
    기록 보기 버튼을 누르면 실행되는 함수입니다.
    history.txt 파일을 읽어서 그 내용을 팝업창(새로운 창)에 보여줍니다.
    """
    # 1. 파일이 존재하는지 먼저 확인합니다.
    if not os.path.exists(HISTORY_FILE):
        messagebox.showinfo("기록 없음", "아직 저장된 복불복 기록이 없습니다.")
        return

    # 2. 'r' 모드(읽기 모드)로 파일을 엽니다.
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history_content = f.read() # 파일의 모든 내용을 문자열로 읽어옵니다.
            
        # 파일 내용이 비어있는지 확인
        if not history_content.strip():
             messagebox.showinfo("기록 없음", "기록 파일은 있지만 내용이 비어있습니다.")
        else:
            # 3. 기록을 보여주기 위한 새로운 창(Toplevel)을 만듭니다.
            # 기록이 길어질 수 있으므로 일반 messagebox 대신 텍스트 영역을 만듭니다.
            history_window = tk.Toplevel(window)
            history_window.title("지난 복불복 기록")
            history_window.geometry("450x550")
            history_window.configure(bg="#F4F6F9") # 모던한 연회색 배경
            
            # 내용을 담을 하얀색 카드(프레임)
            frame_hist = tk.Frame(history_window, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1, bd=0)
            frame_hist.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
            
            # 스크롤바 생성 및 배치
            scrollbar = tk.Scrollbar(frame_hist)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 텍스트를 보여줄 Text 위젯 (테두리 없이 깔끔하게)
            text_widget = tk.Text(frame_hist, yscrollcommand=scrollbar.set, font=("Helvetica", 12), bg="#FFFFFF", fg="#1E293B", relief="flat")
            text_widget.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)
            
            scrollbar.config(command=text_widget.yview)
            
            # 읽어온 텍스트 파일 내용을 Text 위젯에 넣습니다.
            text_widget.insert(tk.END, history_content)
            
            # 사용자가 내용을 수정하지 못하게 '읽기 전용' 상태로 만듭니다.
            text_widget.config(state=tk.DISABLED)
            
    except Exception as e:
        messagebox.showerror("읽기 오류", f"기록을 읽어오는 중 오류가 발생했습니다:\n{e}")

# --- GUI (그래픽 사용자 인터페이스) 화면 구성 부분 ---

# 1. 메인 창 만들기
window = tk.Tk()
window.title("오늘 뭐 먹지? GUI 복불복 사다리") # 프로그램 창의 제목
window.geometry("600x780") # 화면 하단 UI(초기화 버튼 등)가 잘리지 않도록 세로 길이를 더 늘립니다.
window.configure(bg="#F4F6F9") # 깔끔하고 모던한 연회색 배경

# --- 공통 색상 설정 (디자인 통일성) ---
BG_COLOR = "#F4F6F9"       # 전체 배경 (연회색)
CARD_COLOR = "#FFFFFF"     # 카드 배경 (흰색)
TEXT_COLOR = "#1E293B"     # 기본 글자색 (진한 남회색)
PRIMARY_COLOR = "#4361EE"  # 메인 포인트 색상 (파란색)
DANGER_COLOR = "#F43F5E"   # 서브 포인트 색상 (빨간색/분홍색)
BTN_TEXT_COLOR = "#FFFFFF" # 버튼 글자색 (흰색)

# 2. 프로그램 제목 라벨(Label) 만들기
title_label = tk.Label(window, text="🎲 Amugona Solver 🎲", font=("Helvetica", 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
title_label.pack(pady=(25, 15)) # 위 25, 아래 15 여백

# --- 데이터를 입력하고 보여줄 중간 영역(프레임) 구성 ---
frame_main = tk.Frame(window, bg=BG_COLOR)
frame_main.pack(pady=5, fill=tk.BOTH, expand=True, padx=25)

# [메뉴 관리 (단일 하얀색 카드 형태)]
frame_right = tk.Frame(frame_main, bg=CARD_COLOR, highlightbackground="#E2E8F0", highlightthickness=1, bd=0)
frame_right.pack(expand=True, fill=tk.BOTH)

# 카드 내부 여백을 위한 프레임
right_inner = tk.Frame(frame_right, bg=CARD_COLOR)
right_inner.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

label_menu = tk.Label(right_inner, text="🍽️ 메뉴/벌칙", font=("Helvetica", 14, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
label_menu.pack(pady=(0, 10))

# 입력창과 버튼을 나란히 놓기 위한 프레임
input_frame_m = tk.Frame(right_inner, bg=CARD_COLOR)
input_frame_m.pack(fill=tk.X, pady=(0, 10))

# 메뉴 입력창(Entry)
entry_menu = tk.Entry(input_frame_m, font=("Helvetica", 12), relief="solid", bd=1)
entry_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 8))
entry_menu.bind("<Return>", lambda event: add_menu())

btn_add_menu = tk.Button(input_frame_m, text="추가", command=add_menu, font=("Helvetica", 11, "bold"), bg=DANGER_COLOR, fg=BTN_TEXT_COLOR, relief="flat", cursor="hand2")
btn_add_menu.pack(side=tk.RIGHT, ipady=3, ipadx=8)

# [새로 추가된 부분] API 추가 설정 영역 (개수 설정 및 위치 표시)
api_setting_frame = tk.Frame(right_inner, bg=CARD_COLOR)
api_setting_frame.pack(fill=tk.X, pady=(0, 10))

# 사용자 직접 주소 입력 프레임
addr_frame = tk.Frame(api_setting_frame, bg=CARD_COLOR)
addr_frame.pack(fill=tk.X, pady=(0, 5))

lbl_addr = tk.Label(addr_frame, text="기준 주소 (비우면 현재 위치):", font=("Helvetica", 10), bg=CARD_COLOR, fg=TEXT_COLOR)
lbl_addr.pack(side=tk.LEFT, padx=(0, 5))

entry_address = tk.Entry(addr_frame, font=("Helvetica", 10), relief="solid", bd=1)
entry_address.pack(side=tk.LEFT, fill=tk.X, expand=True)

# 위치 정보 라벨
lbl_location = tk.Label(api_setting_frame, text="📍 탐색 위치: 아직 검색되지 않음", font=("Helvetica", 10), bg=CARD_COLOR, fg="#64748B")
lbl_location.pack(side=tk.TOP, anchor="w", pady=(0, 5))

# 설정 입력란을 담을 프레임 (카테고리 + 개수)
count_frame = tk.Frame(api_setting_frame, bg=CARD_COLOR)
count_frame.pack(side=tk.TOP, fill=tk.X)

# 카테고리 콤보박스 추가
categories = ["전체", "한식", "중식", "일식", "양식", "분식", "카페", "술집"]
combo_category = ttk.Combobox(count_frame, values=categories, state="readonly", width=5, font=("Helvetica", 11))
combo_category.set("전체") # 기본값
combo_category.pack(side=tk.LEFT, padx=(0, 10))

lbl_count = tk.Label(count_frame, text="추가할 개수 (1~15):", font=("Helvetica", 11), bg=CARD_COLOR, fg=TEXT_COLOR)
lbl_count.pack(side=tk.LEFT, padx=(0, 5))

# 개수 조절을 위한 Spinbox 추가
spin_count = tk.Spinbox(count_frame, from_=1, to=15, width=4, font=("Helvetica", 11), relief="solid", bd=1)
spin_count.delete(0, "end")
spin_count.insert(0, 5) # 기본값 5로 설정
spin_count.pack(side=tk.LEFT)

# [수정된 부분] 내 위치 주변 식당 불러오기 버튼 (API 연동)
btn_load_api = tk.Button(right_inner, text="🔍 내 위치 주변 식당 불러오기", command=load_restaurants, font=("Helvetica", 11, "bold"), bg="#F59E0B", fg="white", relief="flat", cursor="hand2")
btn_load_api.pack(fill=tk.X, pady=(0, 10), ipady=3)

# 메뉴 명단을 보여줄 리스트박스(Listbox)
listbox_menus = tk.Listbox(right_inner, font=("Helvetica", 12), selectbackground=DANGER_COLOR, selectforeground="white", relief="solid", bd=1, highlightthickness=0)
listbox_menus.pack(fill=tk.BOTH, expand=True)

# 리스트박스 항목을 선택하고 Delete 또는 BackSpace 키를 누르면 바로 삭제되도록 연결
listbox_menus.bind("<Delete>", delete_menu)
listbox_menus.bind("<BackSpace>", delete_menu)

# 버튼들을 나란히 배치하기 위한 프레임
action_btn_frame = tk.Frame(right_inner, bg=CARD_COLOR)
action_btn_frame.pack(fill=tk.X, pady=(10, 0))

# 리스트박스 아래에 '선택 삭제' 버튼 추가
btn_delete_menu = tk.Button(action_btn_frame, text="❌ 선택 삭제 (Del)", command=delete_menu, font=("Helvetica", 10, "bold"), bg="#E2E8F0", fg=TEXT_COLOR, relief="flat", cursor="hand2")
btn_delete_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=3)

# 전체 초기화 버튼 추가
btn_clear_menu = tk.Button(action_btn_frame, text="🗑️ 전체 초기화", command=clear_menu, font=("Helvetica", 10, "bold"), bg="#CBD5E1", fg=TEXT_COLOR, relief="flat", cursor="hand2")
btn_clear_menu.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0), ipady=3)

# --- 화면 하단의 동작 버튼 (결과 보기, 기록 보기) 영역 ---
frame_bottom = tk.Frame(window, bg=BG_COLOR)
frame_bottom.pack(pady=(15, 25))

# 결과 보기 버튼 (초록색 포인트로 눈에 띄게)
btn_result = tk.Button(frame_bottom, text="🎉 결과 보기 🎉", command=show_results, font=("Helvetica", 15, "bold"), bg="#10B981", fg="white", relief="flat", width=16, height=2, cursor="hand2")
btn_result.pack(side=tk.LEFT, padx=15)

# 기록 보기 버튼 (부드러운 회색)
btn_history = tk.Button(frame_bottom, text="📜 기록 보기", command=show_history, font=("Helvetica", 13, "bold"), bg="#64748B", fg="white", relief="flat", width=12, height=2, cursor="hand2")
btn_history.pack(side=tk.LEFT, padx=15)

# 3. 메인 루프 실행 (GUI 프로그램의 핵심!)
window.mainloop()
