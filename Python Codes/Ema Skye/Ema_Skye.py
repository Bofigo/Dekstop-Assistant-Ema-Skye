import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
import google.generativeai as genai
import pyttsx3
import threading

API_Key = "Enter Your Google Gemini API key here"
genai.configure(api_key=API_Key)
model = genai.GenerativeModel("gemini-1.5-flash")

engine = pyttsx3.init()

global_photo = None
sound_enabled = False

# dictionary of program names you want to open via assistant. Enter app name and app path.
app_names = {
    "app name": "app path",
}


def make_window_draggable(window, enable_dragging):
    def start_drag(event):
        if enable_dragging:
            window.start_x = event.x
            window.start_y = event.y

    def drag(event):
        if enable_dragging:
            x = window.winfo_x() + event.x - window.start_x
            y = window.winfo_y() + event.y - window.start_y
            window.geometry(f"+{x}+{y}")

    window.bind("<ButtonPress-1>", start_drag)
    window.bind("<B1-Motion>", drag)


def speak(speech):
    engine.say(speech)
    engine.runAndWait()


def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled


def create_box(text):
    global global_photo
    global sound_enabled
    global idle
    global note
    global talk

    win2 = tk.Toplevel()
    win2.geometry("600x170+580+630")
    win2.overrideredirect(True)
    win2.config(highlightbackground="dark slate gray")
    win2.wm_attributes("-transparentcolor", "dark slate gray")

    main_canvas = tk.Canvas(win2, width=600, height=170, bg="dark slate gray", highlightthickness=0)
    main_canvas.pack()

    img = Image.open("talk_box.png").resize((600, 170))
    global_photo = ImageTk.PhotoImage(img)
    main_canvas.create_image(0, 0, anchor="nw", image=global_photo)

    text_canvas = tk.Canvas(main_canvas, width=550, height=90, bg="black", highlightthickness=0)
    text_canvas.place(x=25, y=60)

    text_var = tk.StringVar()
    text_canvas.create_text(
        275, 45,
        text=text_var.get(),
        font=("Arial", 10),
        fill="white",
        width=550,
        anchor="center"
    )

    max_time = 20
    if len(text) > ((max_time * 1000) / 50):
        animate_time = int((max_time * 1000) / len(text))
    else:
        animate_time = 50

    def animate_text(index=0):
        if index < len(text):
            text_canvas.delete("all")
            text_canvas.create_text(
                275, 45,
                text=text[:index+1],
                font=("Arial", 10),
                fill="white",
                width=550,
                anchor="center"
            )
            win2.after(animate_time, animate_text, index+1)
        else:
            global idle
            global talk
            idle = True
            talk = False
            idle_update(0)

    animate_text()
    idle = False
    note = False
    talk = True
    if sound_enabled:
        engine.setProperty("rate", animate_time)
        thread = threading.Thread(target=speak, args=(text,))
        thread.start()
    talk_update(0)

    def _on_mousewheel(event):
        text_canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    text_canvas.bind_all("<MouseWheel>", _on_mousewheel)

def idle_update(ind):
    global idle

    if idle and not talk:
        frame = idle_frames[ind]
        ema.configure(image=frame)
        if ind == 0:
            ind += 1
            win.after(idle_wait*1000, idle_update, ind)
        else:
            ind += 1
            if ind == idle_frameCnt:
                ind = 0
            win.after(150, idle_update, ind)


def note_update(ind):
    global note

    if note:
        frame = note_frames[ind]
        ema.configure(image=frame)
        ind += 1
        if ind == note_frameCnt:
            ind = 0
        win.after(160, note_update, ind)


def talk_update(ind):
    global talk

    if talk:
        frame = talk_frames[ind]
        ema.configure(image=frame)
        ind += 1
        if ind == talk_frameCnt:
            ind = 0
        win.after(120, talk_update, ind)


def on_enter(event):
    global sound_enabled

    user_input = entry.get()
    user_input = user_input.lower()
    entry.delete(0, tk.END)

    if user_input[:1] == "?":
        user_input = user_input[1:]
        ai(user_input)
    elif user_input == "close":
        sys.exit()
    elif user_input in app_names:
        app = app_names[user_input]
        os.startfile(app)
    elif user_input[:5] == "sound":
        if user_input == "sound on":
            sound_enabled = True
        elif user_input == "sound off":
            sound_enabled = False
    elif user_input[:4] == "lock":
        if user_input == "lock on":
            make_window_draggable(win, False)
        elif user_input == "lock off":
            make_window_draggable(win, True)
    elif user_input[:7] == "topmost":
        if user_input == "topmost on":
            win.wm_attributes("-topmost", 1)
        elif user_input == "topmost off":
            win.wm_attributes("-topmost", 0)


def ai(inp):
    user_input = inp

    response = model.generate_content(str(user_input))
    print(response)
    print(response.text)
    create_box(response.text)


def check(event):
    user_input = entry.get()

    global idle
    global note
    global talk

    if user_input:
        if idle:
            idle = False
            note = True
            talk = False
            note_update(0)
    else:
        if note:
            note = False
        if talk:
            idle = False
        elif not idle:
            idle = True
            idle_update(0)


win = tk.Tk()
x_pos = 200
y_pos = 400
win.geometry("500x416+" + str(x_pos) + "+" + str(y_pos))
win.overrideredirect(True)
win.config(highlightbackground="black")
win.wm_attributes("-transparentcolor","black")

canvas = tk.Canvas(win, width=500, height=416, highlightthickness=0, bg="black")
canvas.pack(fill="both", expand=True)

ema = tk.Label(canvas, bd=0, bg="black", anchor="w")
ema.pack()

idle = True
idle_wait = 3
idle_frameCnt = 8
idle_frames = [tk.PhotoImage(file="ema_idle.gif",format = "gif -index %i" %(i)) for i in range(idle_frameCnt)]
# tk.PhotoImage(file="ema_idle.gif",format = "gif -index %i" %(i)) for i in range(idle_frameCnt)

# img = Image.open("ema_idle.gif")
# for i in range(idle_frameCnt):
#    img.seek(i)
#    resized_img = img.resize((250, 416), Image.Resampling.LANCZOS)
#    resized_photo = ImageTk.PhotoImage(resized_img)
#    idle_frames.append(resized_photo)

note = False
note_frameCnt = 38
note_frames = [tk.PhotoImage(file="ema_note.gif", format = "gif -index %i" %(i)) for i in range(note_frameCnt)]
# tk.PhotoImage(file="ema_note.gif", format = "gif -index %i" %(i)) for i in range(note_frameCnt)

# img = Image.open("ema_note.gif")
# for i in range(note_frameCnt):
#    img.seek(i)
#    resized_img = img.resize((250, 416), Image.Resampling.LANCZOS)
#    resized_photo = ImageTk.PhotoImage(resized_img)
#    note_frames.append(resized_photo)

talk = False
talk_frameCnt = 26
talk_frames = []

img = Image.open("ema_talk.gif")
for i in range(talk_frameCnt):
    img.seek(i)
    resized_img = img.resize((250, 416), Image.Resampling.LANCZOS)
    resized_photo = ImageTk.PhotoImage(resized_img)
    talk_frames.append(resized_photo)

entry = tk.Entry(win, font=("Arial", 14), width=10, bg="white", state="normal")

canvas.create_window(380, 100, window=entry, anchor="center")

entry.bind("<Return>", on_enter)
entry.bind("<KeyRelease>", check)

make_window_draggable(win, False)
win.after(0, idle_update, 0)
win.mainloop()
