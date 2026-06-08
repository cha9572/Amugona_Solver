import tkinter as tk
import tkinter.messagebox as messagebox
import random
import datetime
import os

# --- 전역 변수 (데이터를 저장할 리스트) ---
participants = [] # 참가자 명단을 저장할 리스트
menus = []        # 메뉴(또는 벌칙) 후보를 저장할 리스트
HISTORY_FILE = "history.txt" # 기록을 저장할 텍스트 파일 이름

# --- 함수 정의 부분 (클래스 없이 절차지향적으로 작성) ---

def add_participant():
    """
    참가자 추가 버튼을 누르거나 엔터키를 쳤을 때 실행되는 함수입니다.
    입력창에 적힌 이름을 가져와서 리스트와 화면(Listbox)에 추가합니다.
    """
    # 1. 입력창(Entry)에서 텍스트를 가져옵니다. strip()은 양쪽 공백을 제거해줍니다.
    name = entry_participant.get().strip()
    
    # 2. 이름이 비어있지 않은 경우에만 추가합니다.
    if name:
        participants.append(name) # 파이썬 리스트에 이름 추가
        listbox_participants.insert(tk.END, name) # 화면의 리스트박스 맨 끝에 이름 추가
        entry_participant.delete(0, tk.END) # 입력창을 비워줍니다 (다음 입력을 위해)
    else:
        # 이름이 비어있다면 경고 메시지 창을 띄웁니다.
        messagebox.showwarning("입력 오류", "참가자 이름을 입력해주세요!")

def add_menu():
    """
    메뉴 추가 버튼을 누르거나 엔터키를 쳤을 때 실행되는 함수입니다.
    입력창에 적힌 메뉴를 가져와서 리스트와 화면(Listbox)에 추가합니다.
    """
    # 입력창에서 텍스트를 가져와 공백을 제거합니다.
    menu = entry_menu.get().strip()
    
    if menu:
        menus.append(menu) # 파이썬 리스트에 메뉴 추가
        listbox_menus.insert(tk.END, menu) # 화면 리스트박스에 추가
        entry_menu.delete(0, tk.END) # 입력창 비우기
    else:
        messagebox.showwarning("입력 오류", "메뉴(또는 벌칙)를 입력해주세요!")

def finish_animation(ladder_window, final_matches):
    """
    애니메이션이 끝난 후 실행되는 함수입니다.
    사다리 창을 닫고, 최종 매칭 결과를 문자열로 만들어 팝업으로 보여주며 파일에 저장합니다.
    """
    ladder_window.destroy() # 사다리 창 닫기
    
    # 1. 결과 문자열 만들기
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result_text = f"--- [ {now} ] 복불복 결과 ---\n\n"
    
    for p, m in final_matches.items():
        result_text += f"👤 {p}  👉  🍽️ {m}\n"
    result_text += "\n-----------------------------------\n\n"
    
    # 2. 결과를 팝업창으로 보여주기
    messagebox.showinfo("🎉 두구두구 결과 발표 🎉", result_text)
    
    # 3. 결과를 텍스트 파일(history.txt)에 저장하기
    try:
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(result_text)
    except Exception as e:
        messagebox.showerror("저장 오류", f"기록을 저장하는 중 오류가 발생했습니다:\n{e}")

def show_results():
    """
    결과 보기 버튼을 누를 때 실행되는 핵심 함수입니다.
    기존의 단순 무작위 섞기 대신, 사다리타기 애니메이션 캔버스를 띄웁니다.
    """
    # 1. 참가자나 메뉴가 입력되지 않았는지 확인합니다.
    if not participants:
        messagebox.showwarning("경고", "참가자를 최소 1명 이상 입력해주세요!")
        return 
    if not menus:
        messagebox.showwarning("경고", "메뉴를 최소 1개 이상 입력해주세요!")
        return 

    # 2. 참가자 수와 메뉴 수가 다를 경우를 처리합니다.
    temp_menus = list(menus) 
    while len(temp_menus) < len(participants):
        temp_menus.extend(menus)
    temp_menus = temp_menus[:len(participants)]

    # 사다리의 출발 순서와 도착 순서를 미리 섞어줍니다.
    random.shuffle(participants)
    random.shuffle(temp_menus)
    
    # -----------------------------------
    # 3. 새 창을 띄우고 캔버스(사다리 화면) 설정하기
    # -----------------------------------
    ladder_window = tk.Toplevel(window)
    ladder_window.title("사다리타기 진행 중...")
    
    num_p = len(participants)
    # 참가자 수에 비례하여 캔버스 가로 너비를 유동적으로 설정합니다.
    canvas_w = max(500, num_p * 100 + 100) 
    canvas_h = 600
    ladder_window.geometry(f"{canvas_w}x{canvas_h}")
    
    # 그림을 그릴 캔버스 위젯 생성
    canvas = tk.Canvas(ladder_window, width=canvas_w, height=canvas_h, bg="#F8FAFC")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # -----------------------------------
    # 4. 사다리 세로줄 그리기
    # -----------------------------------
    x_positions = [] # 각 세로줄의 X 좌표를 저장할 리스트
    start_x = 50
    spacing = (canvas_w - 100) / max(1, num_p - 1) if num_p > 1 else 0
    if num_p == 1:
        start_x = canvas_w / 2
        
    for i in range(num_p):
        x = start_x + i * spacing
        x_positions.append(x)
        # 세로줄 그리기 (회색)
        canvas.create_line(x, 60, x, canvas_h - 60, fill="#CBD5E1", width=4)
        # 위쪽에 참가자 이름 텍스트 달기
        canvas.create_text(x, 30, text=participants[i], font=("Helvetica", 14, "bold"), fill="#1E293B")
        # 아래쪽에 도착 메뉴 텍스트 달기
        canvas.create_text(x, canvas_h - 30, text=temp_menus[i], font=("Helvetica", 14, "bold"), fill="#1E293B")
        
    # -----------------------------------
    # 5. 사다리 가로줄(발판) 무작위 생성하기
    # -----------------------------------
    rungs = [] # 가로줄 정보를 (Y좌표, 몇번째 줄인지) 형태로 저장
    if num_p > 1:
        for i in range(num_p - 1):
            # 각 세로줄 사이마다 가로줄 2~4개를 무작위 위치에 추가합니다.
            for _ in range(random.randint(2, 4)):
                y = random.randint(100, canvas_h - 100)
                rungs.append((y, i))
                
        # 가로줄이 위에서 아래로 내려오도록 Y좌표 기준으로 정렬합니다.
        rungs.sort() 
        
        # 겹침 방지: 너무 가까운 가로줄은 그려지지 않게 걸러냅니다.
        valid_rungs = []
        last_y = 0
        for y, idx in rungs:
            if y - last_y > 30: # 최소 30픽셀 이상 차이날 때만 그림
                valid_rungs.append((y, idx))
                last_y = y
                # 캔버스에 가로줄 그리기
                x1 = x_positions[idx]
                x2 = x_positions[idx+1]
                canvas.create_line(x1, y, x2, y, fill="#CBD5E1", width=4)
    else:
        valid_rungs = []

    # -----------------------------------
    # 6. 각 참가자별 사다리 타기 경로 미리 계산하기
    # -----------------------------------
    paths = []
    final_matches = {} # {참가자이름: 도착메뉴이름}
    
    for i in range(num_p):
        current_x_idx = i # 현재 위치한 세로줄 인덱스
        current_y = 60    # 출발 Y좌표
        path = [(x_positions[current_x_idx], current_y)] # 꺾이는 지점의 좌표들을 저장
        
        # 가로줄을 만나면 옆으로 이동합니다.
        for y, idx in valid_rungs:
            if idx == current_x_idx:
                # 현재 위치의 오른쪽에 가로줄이 있으면 오른쪽으로 이동
                path.append((x_positions[current_x_idx], y))
                current_x_idx += 1
                path.append((x_positions[current_x_idx], y))
            elif idx == current_x_idx - 1:
                # 현재 위치의 왼쪽에 가로줄이 있으면 왼쪽으로 이동
                path.append((x_positions[current_x_idx], y))
                current_x_idx -= 1
                path.append((x_positions[current_x_idx], y))
                
        # 바닥에 도착
        path.append((x_positions[current_x_idx], canvas_h - 60))
        paths.append(path)
        
        # 도착한 위치(current_x_idx)의 메뉴가 이 참가자의 결과가 됩니다.
        final_matches[participants[i]] = temp_menus[current_x_idx]

    # -----------------------------------
    # 7. 사다리 경로 애니메이션 (선 긋기)
    # -----------------------------------
    colors = ["#EF4444", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6"]
    
    # 애니메이션을 처리하는 재귀(반복) 함수
    def animate_path(person_idx, step_idx):
        # 모든 사람의 애니메이션이 끝났으면 결과 함수 호출
        if person_idx >= num_p:
            # 1초 대기 후 사다리 창을 닫고 결과창 띄우기
            ladder_window.after(1000, lambda: finish_animation(ladder_window, final_matches))
            return
            
        path = paths[person_idx]
        color = colors[person_idx % len(colors)] # 사람마다 다른 색상
        
        # 선분을 하나씩 그립니다.
        if step_idx < len(path) - 1:
            x1, y1 = path[step_idx]
            x2, y2 = path[step_idx+1]
            
            canvas.create_line(x1, y1, x2, y2, fill=color, width=5)
            
            # 100ms(0.1초) 후에 다음 선분을 그립니다.
            ladder_window.after(100, animate_path, person_idx, step_idx + 1)
        else:
            # 한 명의 애니메이션이 끝났으면 400ms 대기 후 다음 사람 시작
            ladder_window.after(400, animate_path, person_idx + 1, 0)
            
    # 첫 번째 참가자(0번 인덱스), 첫 번째 선분(0번 스텝)부터 애니메이션 시작!
    animate_path(0, 0)

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
window.geometry("600x540") # 여유 있게 창 크기 확대
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

# [왼쪽 영역: 참가자 관리 (하얀색 카드 형태)]
frame_left = tk.Frame(frame_main, bg=CARD_COLOR, highlightbackground="#E2E8F0", highlightthickness=1, bd=0)
frame_left.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 10))

# 카드 내부 여백을 위한 프레임
left_inner = tk.Frame(frame_left, bg=CARD_COLOR)
left_inner.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

label_participant = tk.Label(left_inner, text="🙋 참가자 명단", font=("Helvetica", 14, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR)
label_participant.pack(pady=(0, 10))

# 입력창과 버튼을 나란히 놓기 위한 프레임
input_frame_p = tk.Frame(left_inner, bg=CARD_COLOR)
input_frame_p.pack(fill=tk.X, pady=(0, 10))

# 참가자 입력창(Entry) - 테두리를 solid로 깔끔하게 지정
entry_participant = tk.Entry(input_frame_p, font=("Helvetica", 12), relief="solid", bd=1)
entry_participant.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5, padx=(0, 8))
entry_participant.bind("<Return>", lambda event: add_participant())

btn_add_participant = tk.Button(input_frame_p, text="추가", command=add_participant, font=("Helvetica", 11, "bold"), bg=PRIMARY_COLOR, fg=BTN_TEXT_COLOR, relief="flat", cursor="hand2")
btn_add_participant.pack(side=tk.RIGHT, ipady=3, ipadx=8)

# 참가자 명단을 보여줄 리스트박스(Listbox)
listbox_participants = tk.Listbox(left_inner, font=("Helvetica", 12), selectbackground=PRIMARY_COLOR, selectforeground="white", relief="solid", bd=1, highlightthickness=0)
listbox_participants.pack(fill=tk.BOTH, expand=True)

# [오른쪽 영역: 메뉴 관리 (하얀색 카드 형태)]
frame_right = tk.Frame(frame_main, bg=CARD_COLOR, highlightbackground="#E2E8F0", highlightthickness=1, bd=0)
frame_right.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=(10, 0))

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

# 메뉴 명단을 보여줄 리스트박스(Listbox)
listbox_menus = tk.Listbox(right_inner, font=("Helvetica", 12), selectbackground=DANGER_COLOR, selectforeground="white", relief="solid", bd=1, highlightthickness=0)
listbox_menus.pack(fill=tk.BOTH, expand=True)

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
