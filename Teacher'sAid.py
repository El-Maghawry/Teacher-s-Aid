from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SwapTransition
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, NoTransition
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
import os
import wave
import simpleaudio as sa
import pyaudio
import time
from datetime import date, datetime
import arabic_reshaper
from bidi.algorithm import get_display
from kivy.clock import Clock
import math

today = date.today()
today = f"{today.strftime('%B %d, %Y')}"

print("••••••••••", os.getcwd())
path = os.getcwd()

try:
    os.mkdir(f"{path}/{today}")
except FileExistsError:
    # the dir already exists
    # put code handing this case here
    pass

os.chdir(f"{path}/{today}")
print("••••••••••", os.getcwd())

# this is where the main screen starts  •••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
today = date.today().strftime('%B %d, %Y')

Window.size = (1450 / 2.5, 1600 / 4.5)

Window.clearcolor = (1, 1, 1, 1)


class Ar_text(TextInput):
    max_chars = NumericProperty(120)  # maximum character allowed
    str = StringProperty()

    def __init__(self, **kwargs):
        super(Ar_text, self).__init__(**kwargs)
        self.text = get_display(arabic_reshaper.reshape("اطبع شيئاً"))

    def insert_text(self, substring, from_undo=False):
        if not from_undo and (len(self.text) + len(substring) > self.max_chars):
            return
        self.str = self.str + substring
        self.text = get_display(arabic_reshaper.reshape(self.str))
        substring = ""
        super(Ar_text, self).insert_text(substring, from_undo)

    def do_backspace(self, from_undo=False, mode='bkspc'):
        self.str = self.str[0:len(self.str) - 1]
        self.text = get_display(arabic_reshaper.reshape(self.str))

class MenuScreen(Screen):  # put it somewhere where it makes sense
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.ids.inputs.halign = 'center'

    def start_recording_schedule(self):
        self.ids.status_recording.text = "Recording ..."
        self.ids.status_recording.color = 'red'
        Clock.schedule_once(self.recording_user_input, 0.05)

    def recording_user_input(self, dt):
        seconds_recording = math.ceil((len(self.ids.inputs.text) + 0.1) / 6) + 1
        print("seconds_recording: ", seconds_recording + 1, len(self.ids.inputs.text))
        self.ids.status_recording.text = "Recording..."

        self.audio = pyaudio.PyAudio()
        stream = self.audio.open(format=pyaudio.paInt16,
                                 channels=1,
                                 rate=44100,
                                 input=True,
                                 frames_per_buffer=1024)

        self.frames = []

        for i in range(0, int(44100 / 1024 * seconds_recording)):
            data = stream.read(1024)  # try exc
            self.frames.append(data)  # try exc

        print("recording has finished...")
        self.ids.status_recording.text = "Recording Finished"
        self.ids.status_recording.color = 'red'

        stream.stop_stream()
        stream.close()
        self.audio.terminate()
        Clock.schedule_once(self.save_recording, 0.1)

    def save_recording(self, dt):
        self.sound_file_name = f"{get_display(self.ids.inputs.text)}.wav"
        sound_file = wave.open(self.sound_file_name, "wb")
        sound_file.setnchannels(1)
        sound_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(44100)
        sound_file.writeframes(b''.join(self.frames))
        sound_file.close()

        wave_obj = sa.WaveObject.from_wave_file(self.sound_file_name)
        play_obj = wave_obj.play()
        play_obj.wait_done()  # Wait until sound has finished playing
        print(len(self.ids.inputs.text))

        wav_files = glob.glob('./*.wav')

        for wav_file in wav_files:
            mp3_file = os.path.splitext(wav_file)[0] + '.mp3'
            sound = pydub.AudioSegment.from_wav(wav_file)
            sound.export(mp3_file, format="mp3")
            os.remove(wav_file)

    def replay(self):
        for i in range(1):
            wave_obj = sa.WaveObject.from_wave_file(self.sound_file_name)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            self.ids.status_recording.text = "Playback Finished"
            self.ids.status_recording.color = 'orange'
            time.sleep(1)

    def remove_input(self):
        self.ids.inputs.text = ''
        self.ids.inputs.str = ''



class MLAProjectsApp(App):
    def build(self, *args):
        Builder.load_string('''
<Ar_text@TextInput>:
    text: ""
    multiline: 0
    size_hint: 1,1
    font_name: 'Arial'
    font_size: '20sp'


<Label>
    halign: 'left'
    color: 0,0,0,1
    font_size: '15sp'
    bold: False

<Button>
    # background_color: (0,0,0,0)
    background_normal: ''
    

<Image>
    center_x: self.parent.center_x
    center_y: self.parent.center_y

<Image_Button@ButtonBehavior+Image>:
    source:

<MenuScreen>:
    name: 'speaker_screen'
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'

        BoxLayout:
            size_hint_y: .1  # 40
            orientation: 'vertical'

            Label:
                #size_hint_x: .8
                text:"Test v"
                halign: 'center'
                color: 0,0,0,1
                font_size: '30sp'
                bold: True

        BoxLayout:
            size_hint_y: .01
            #size_hint_y: None
            canvas.before:
                Color:
                    rgba: 0,0,0,1
                Line:
                    points: [self.x+30,self.y, self.x+self.width-30, self.y ]
                    width: 1
        Button:
            size_hint_y: .05
                
        BoxLayout:
            size_hint_y: .06
            orientation: 'horizontal'
            Button:
                size_hint_x: .05
            Ar_text:
                font_name: 'Arial'
                size_hint_x: .9
                id: inputs
                background_normal: 'btn_normal.png'
                background_down: 'btn_down.png'
                background_color: (0,0,0,0.1)
                halign: 'center'
                text_size: self.size
            Button:
                size_hint_x: .05


        BoxLayout:
            size_hint_y: .05  #
            orientation: 'horizontal'

            Label:
                size_hint_x: .9
                text: '...'
                id: status_recording
                bold: 'True'



        BoxLayout:
            size_hint_y: .2  # 95
            orientation: 'horizontal'
                                                    
            BoxLayout:
                orientation: 'vertical'
                AnchorLayout:
                    anchor_x: 'center'
                    anchor_y: 'center'
                    Button:
                        size_hint: .8, .4
                        text: 'Replay'
                        font_size: '20sp'
                        bold: True
                        background_normal: 'btn_normal.png'
                        background_down: 'btn_down.png'
                        background_color: 'orange'
                        color: 'white'
                        on_release:
                            root.replay()

            BoxLayout:
                orientation: 'vertical'
                AnchorLayout:
                    anchor_x: 'center'
                    anchor_y: 'center'
                    Button:
                        size_hint: .8, .4
                        text: 'Record'
                        font_size: '20sp'
                        bold: True
                        background_normal: 'btn_normal.png'
                        background_down: 'btn_down.png'
                        background_color: 'red'
                        color: 'white'
                        on_release:
                            root.start_recording_schedule()
                            
            BoxLayout:
                orientation: 'vertical'
                AnchorLayout:
                    anchor_x: 'center'
                    anchor_y: 'center'
                    Button:
                        size_hint: .8, .4
                        text: 'New'
                        font_size: '20sp'
                        bold: True
                        background_normal: 'btn_normal.png'
                        background_down: 'btn_down.png'
                        background_color: 'white'
                        color: 'white'
                        on_release:
                            root.remove_input()
        ''')
        sm = ScreenManager()
        self.main = MenuScreen()
        sm.add_widget(self.main)

        return sm


if __name__ == '__main__':
    MLAProjectsApp().run()
