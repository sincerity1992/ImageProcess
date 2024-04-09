import face_recognition as fr
import os
import cv2
import face_recognition
import numpy as np
from time import sleep

import customtkinter as ctk
from utilities import resolve_relative_path ,is_image, is_video
import metadata
import globals
from typing import Callable, Tuple
from PIL import Image, ImageOps,ImageDraw
import customtkinter

import requests
import json
import base64

  
url = "https://www.ailabapi.com/api/portrait/effects/emotion-editor"



ROOT = None
ROOT_HEIGHT = 700
ROOT_WIDTH = 600

PREVIEW = None
PREVIEW_MAX_HEIGHT = 700
PREVIEW_MAX_WIDTH = 1200

RECENT_DIRECTORY_SOURCE = None
RECENT_DIRECTORY_TARGET = None
RECENT_DIRECTORY_OUTPUT = None

preview_label = None
preview_slider = None
#source_label1
target_label = None
status_label = None
face_landmarks_list = None

smile_mode = 3

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

def render_image_preview(image_path: str, size: Tuple[int, int]) -> ctk.CTkImage:   
    image = Image.open(image_path)
    if size:
        image = ImageOps.fit(image, size, Image.LANCZOS)
    return ctk.CTkImage(image, size=image.size)
    
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Image Processing")
        self.geometry(f"{1100}x{580}")

        
        # configure grid layout (4x4)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure((0,2), weight=1)
        self.grid_rowconfigure(3, weight=0)

        self.source_label = customtkinter.CTkLabel(self, text="", anchor="w")
        self.source_label.grid(row=0, column=0, rowspan=3,   padx=20, pady=(10, 0))

        self.open_button = customtkinter.CTkButton(self, text='Open', command=lambda: self.select_source_path(self.source_label,self.dst_label))
        self.open_button.grid(row=3, column=0, padx=20, pady=10)
        
        
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=1, rowspan=5, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Filter", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.smile_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Small Smile", "Large Smile","Pouting"],fg_color = "White",bg_color="White",button_color="White",text_color="Black",
                                                                       command=self.change_smile_mode_event)
        self.smile_mode_optionemenu.grid(row=1, column=0, padx=20, pady=(10, 10))
        
        
        self.sidebar_smilebutton = customtkinter.CTkButton(self.sidebar_frame, text = "Apply", command=self.sidebar_button_eventSmile)
        self.sidebar_smilebutton.grid(row=2, column=0, padx=20, pady=20)
        
       
     
        self.dst_label = customtkinter.CTkLabel(self, text="", anchor="w")
        self.dst_label.grid(row=0, column=2, rowspan=3,   padx=20, pady=(10, 0))
        
        self.save_button = customtkinter.CTkButton(self, text='Save', command=self.sidebar_button_event)
        self.save_button.grid(row=3, column=2, padx=20, pady=10)
        
        globals.smile_mode = 3
        globals.gimgDst = self.dst_label
        
        
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")
    
    
            
    def sidebar_button_eventSmile(self):
        self.responseimage() # type: ignore
        print("Apply Button click") 
        
    # def sidebar_button_eventUgly(self):
    #     print("sidebar_button click")   
    def responseimage(self:customtkinter.CTk):    
        payload={'service_choice' : str(globals.smile_mode)}
        print(payload)
        files=[('image_target',('file',open(globals.source_path,'rb'),'application/octet-stream'))]
        headers = {'ailabapi-api-key': '7NeYLDfVgoqfyEFQP5r9SiHxN41shwsvpI88nwlZiBdFJ3Jm0XqGjOypnKgkCrMz'}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        
        resp1 = response.text
        # print(resp1)
        data = json.loads(resp1)
        print(data)
        
        result = data['data']
        image_data = result['image']

        image_bytes = base64.b64decode(image_data)
        
        with open('image.jpg', 'wb') as image_file:
            image_file.write(image_bytes)
        
        image1 = Image.open('image.jpg')            
        image1 = ImageOps.fit(image1, (300, 300), Image.LANCZOS)
        
        ctk_image1 = customtkinter.CTkImage(image1,size=image1.size)
        globals.gimgDst.configure(image=ctk_image1)
            
        #print(resp)
            
    def change_smile_mode_event(self, smile_modestr: str):
        if (smile_modestr == "Large Smile"):
            globals.smile_mode = 0
        elif (smile_modestr == "Small Smile"):
             globals.smile_mode = 3
        else:
             globals.smile_mode = 1
        print(str( globals.smile_mode))   
    

    def select_source_path(a: customtkinter.CTk, imgSrc: customtkinter.CTkLabel,imgDst: customtkinter.CTkLabel) -> None:
        global RECENT_DIRECTORY_SOURCE        
        # PREVIEW.withdraw()
        print(type(a))
        print(type(imgSrc))
        source_path = ctk.filedialog.askopenfilename(title='select an source image', initialdir=RECENT_DIRECTORY_SOURCE)
        if is_image(source_path):
            globals.source_path = source_path
            RECENT_DIRECTORY_SOURCE = os.path.dirname(globals.source_path)
            #image = render_image_preview(globals.source_path, (300, 300)) # type: ignore
            
            image = Image.open(source_path)            
            image = ImageOps.fit(image, (300, 300), Image.LANCZOS)
            
            ctk_image = customtkinter.CTkImage(image,size=image.size)
            imgSrc.configure(image=ctk_image)
            
            #imgDst.configure(image=ctk_image)
            
            image = image.convert("RGB")           
            
            image1 = np.asarray(image)
            
            face_landmarks_list = face_recognition.face_landmarks(image1)
            pil_image = Image.fromarray(image1)
            
            for face_landmarks in face_landmarks_list:                
                d = ImageDraw.Draw(pil_image, 'RGBA')
                # Make the eyebrows into a nightmare
                d.polygon(face_landmarks['left_eyebrow'], fill=(68, 54, 39, 128))
                d.polygon(face_landmarks['right_eyebrow'], fill=(68, 54, 39, 128))
                d.line(face_landmarks['left_eyebrow'], fill=(68, 54, 39, 150), width=5)
                d.line(face_landmarks['right_eyebrow'], fill=(68, 54, 39, 150), width=5)

                # Gloss the lips
                d.polygon(face_landmarks['top_lip'], fill=(150, 0, 0, 128))
                d.polygon(face_landmarks['bottom_lip'], fill=(150, 0, 0, 128))
                d.line(face_landmarks['top_lip'], fill=(150, 155, 64), width=8)
                d.line(face_landmarks['bottom_lip'], fill=(150, 0, 0, 64), width=8)

                # Sparkle the eyes
                d.polygon(face_landmarks['left_eye'], fill=(255, 255, 255, 30))
                d.polygon(face_landmarks['right_eye'], fill=(255, 255, 255, 30))

                # Apply some eyeliner
                d.line(face_landmarks['left_eye'] + [face_landmarks['left_eye'][0]], fill=(0, 0, 0, 110), width=6)
                d.line(face_landmarks['right_eye'] + [face_landmarks['right_eye'][0]], fill=(0, 0, 0, 110), width=6)

            #pil_image.show()
        else:
            globals.source_path = None
            imgSrc.configure(image=None)        
            imgDst.configure(image=None)        
   
    
    
if __name__ == "__main__":
    app = App()
    app.mainloop()


        
# def select_output_path() -> None:
#     global RECENT_DIRECTORY_OUTPUT

#     if is_image(globals.target_path):
#         output_path = ctk.filedialog.asksaveasfilename(title='save image output file', defaultextension='.png', initialfile='output.png', initialdir=RECENT_DIRECTORY_OUTPUT)
#     elif is_video(globals.target_path):
#         output_path = ctk.filedialog.asksaveasfilename(title='save video output file', defaultextension='.mp4', initialfile='output.mp4', initialdir=RECENT_DIRECTORY_OUTPUT)
#     else:
#         output_path = None
#     if output_path:
#         globals.output_path = output_path
#         RECENT_DIRECTORY_OUTPUT = os.path.dirname(globals.output_path)
#         #start()

# def destroy() -> None:
#     #if roop.globals.target_path:
#     #    clean_temp(roop.globals.target_path)
#     quit()

# def create_root() -> ctk.CTk:
#     global source_label, target_label, status_label
#     ctk.deactivate_automatic_dpi_awareness()
#     ctk.set_appearance_mode('system')
#     ctk.set_default_color_theme(resolve_relative_path('ui.json'))

#     root = ctk.CTk()
#     #root = ctk.Tk()
#     root.minsize(ROOT_WIDTH, ROOT_HEIGHT)
#     root.title(f'{metadata.name} {metadata.version}')
#     root.configure()
#     root.protocol('WM_DELETE_WINDOW', lambda: destroy())

#     source_label = ctk.CTkLabel(root, text=None)
#     source_label.place(relx=0.1, rely=0.1, relwidth=0.3, relheight=0.25)

#     target_label = ctk.CTkLabel(root, text=None)
#     target_label.place(relx=0.6, rely=0.1, relwidth=0.3, relheight=0.25)

#     source_button = ctk.CTkButton(root, text='Select a face', cursor='hand2', command=lambda: select_source_path())
#     source_button.place(relx=0.1, rely=0.4, relwidth=0.3, relheight=0.1)

#     return root
#     # start_button = ctk.CTkButton(root, text='Start', cursor='hand2', command=lambda: select_output_path())
#     # start_button.place(relx=0.15, rely=0.75, relwidth=0.2, relheight=0.05)

 

# def get_encoded_faces():

#     encoded = {}

#     for dirpath, dnames, fnames in os.walk("./face_repository"):
#         for f in fnames:
#             if f.endswith(".jpg") or f.endswith(".png"):
#                 face = fr.load_image_file("face_repository/" + f)
#                 encoding = fr.face_encodings(face)[0]
#                 encoded[f.split(".")[0]] = encoding

#     return encoded


# def unknown_image_encoded(img):

#     face = fr.load_image_file("face_repository/" + img)
#     encoding = fr.face_encodings(face)[0]

#     return encoding


# def classify_face(img):

    
#     faces = get_encoded_faces()
#     faces_encoded = list(faces.values())
#     known_face_names = list(faces.keys())

#    # img = cv2.imread(im, 1)
 
#     face_locations = face_recognition.face_locations(img)
#     unknown_face_encodings = face_recognition.face_encodings(img, face_locations)

#     face_names = []
#     for face_encoding in unknown_face_encodings:
   
#         matches = face_recognition.compare_faces(faces_encoded, face_encoding)
#         name = "Unknown"

        
#         face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
#         best_match_index = np.argmin(face_distances)
#         if matches[best_match_index]:
#             name = known_face_names[best_match_index]

#         face_names.append(name)

#         for (top, right, bottom, left), name in zip(face_locations, face_names):
            
#             cv2.rectangle(img, (left-20, top-10), (right+20, bottom+15), (300, 0, 0), 2)

       
#             cv2.rectangle(img, (left-20, bottom -10), (right+20, bottom+15), (500, 0, 0), cv2.FILLED)
#             font = cv2.FONT_HERSHEY_DUPLEX
#             cv2.putText(img, name, (left -10, bottom + 10), font, 0.5, (300, 300, 300), 1)


   
#     while True:

#         cv2.imshow('Whom are you looking for?', img)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             return face_names 

# create_root()
# #classify_face("test1.jpg") # You can either try to find people "test2.jpg" or "test1.jpg" in the string.
