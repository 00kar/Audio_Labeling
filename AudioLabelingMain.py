import os
import sys
import json
import glob

from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog

from pydub import AudioSegment

from AudioLabelingUI import *


class AudioLabelingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_ui()
        self.audio_files = []
        self.current_audio_index = 0
        self.load_audio_files()
        
        # Initialize the QMediaPlayer
        self.media_player = QMediaPlayer()
        self.media_player.stateChanged.connect(self.update_audio_state)
        self.media_player.positionChanged.connect(self.update_audio_position)
        self.media_player.durationChanged.connect(self.update_audio_duration)

    def init_ui(self):
        self.ui.actionOpen.triggered.connect(self.open_folder)
        self.ui.AudioPlayPushButton.clicked.connect(self.play_button_action)
        self.ui.NextAudioPushButton.clicked.connect(self.next_audio)
        self.ui.PreviousAudioPushButton.clicked.connect(self.previous_audio)
        self.ui.HappyPushButton.clicked.connect(lambda: self.set_emotion('hap'))
        self.ui.AngryPushButton.clicked.connect(lambda: self.set_emotion('ang'))
        self.ui.SadPushButton.clicked.connect(lambda: self.set_emotion('sad'))
        self.ui.NeutralPushButton.clicked.connect(lambda: self.set_emotion('neu'))
        self.ui.ResetPushButton.clicked.connect(lambda: self.set_emotion(None))
        self.ui.actionSaveAs.triggered.connect(self.save_results)
        self.ui.StartSelectionButton.clicked.connect(self.start_audio_selection)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        label_file_path = glob.glob(f"{folder_path}/*.json")
        print(folder_path, label_file_path)
        if folder_path:
            self.audio_files = [os.path.join(folder_path, filename) for filename in sorted(os.listdir(folder_path)) if filename.endswith(('.mp4', '.wav'))]
            self.audio_names = [os.path.basename(audio_file) for audio_file in self.audio_files]
            self.results = {}
            if label_file_path:
                print(label_file_path[0])
                with open(label_file_path[0], 'r') as labels_file:
                    uploaded_labels = json.load(labels_file)
                for labeli in uploaded_labels:
                    self.results[labeli['wav']] = {"emotion" : labeli['emo'], "length" : labeli['length']}
            else:
                for file in self.audio_files:
                    self.results[file] = {"emotion" : None, "length" : None}
            self.current_audio_index = 0
            self.update_audio_info()
            self.load_audio_files()

    def load_audio_files(self):
        self.ui.scrollAreaWidgetContents.deleteLater()
        self.ui.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.ui.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 188, 418))
        layout = QtWidgets.QVBoxLayout(self.ui.scrollAreaWidgetContents)

        for i in range(len(self.audio_files)):
            audio_button = QtWidgets.QPushButton(os.path.basename(self.audio_files[i]))
            audio_button.clicked.connect(self.audio_file_chosen)

            emotion = self.results[self.audio_files[i]]['emotion']
            if emotion == 'hap':
                audio_button.setStyleSheet("QPushButton { background-color: rgb(129, 255, 124); }")
            elif emotion == 'ang':
                audio_button.setStyleSheet("QPushButton { background-color: rgb(255, 66, 94); }")
            elif emotion == 'sad':
                audio_button.setStyleSheet("QPushButton { background-color: rgb(248, 255, 159); }")
            elif emotion == 'neu':
                audio_button.setStyleSheet("QPushButton { background-color: rgb(138, 255, 238); }")
            else:
                audio_button.setStyleSheet("")

            layout.addWidget(audio_button)

        self.ui.scrollArea.setWidget(self.ui.scrollAreaWidgetContents)

    def audio_file_chosen(self):
        button_text = self.sender().text()
        self.current_audio_index = self.audio_names.index(button_text)
        self.play_audio(self.audio_files[self.current_audio_index])

    def play_audio(self, audio_file_i):
        self.ui.AudioPlayPushButton.setText("Pause")
        media = QMediaContent(QUrl.fromLocalFile(audio_file_i))
        self.media_player.setMedia(media)
        self.media_player.play()


    def update_audio_info(self):
        if 0 <= self.current_audio_index < len(self.audio_files):
            audio_file = self.audio_files[self.current_audio_index]
            file_name = os.path.basename(audio_file)
            self.ui.AudioTimeLabel.setText("00:00:00")  # Reset the time label
            self.ui.AudioTimeLabel.adjustSize()
            # You can also update other information about the audio file in the UI.            

    def set_emotion(self, emotion):
        self.results[self.audio_files[self.current_audio_index]]["emotion"] = emotion

        current_button = self.ui.scrollAreaWidgetContents.layout().itemAt(self.current_audio_index).widget()
        if emotion == 'hap':
            current_button.setStyleSheet("QPushButton { background-color: rgb(129, 255, 124); }")
        elif emotion == 'ang':
            current_button.setStyleSheet("QPushButton { background-color: rgb(255, 66, 94); }")
        elif emotion == 'sad':
            current_button.setStyleSheet("QPushButton { background-color: rgb(248, 255, 159); }")
        elif emotion == 'neu':
            current_button.setStyleSheet("QPushButton { background-color: rgb(138, 255, 238); }")
        else:
            current_button.setStyleSheet("")


    def play_button_action(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.ui.AudioPlayPushButton.setText("Play")
        elif self.media_player.state() == QMediaPlayer.PausedState:
            self.media_player.play()
            self.ui.AudioPlayPushButton.setText("Pause")
        elif self.media_player.state() == QMediaPlayer.StoppedState:
            self.media_player.setPosition(0)
            self.media_player.play()
            self.ui.AudioPlayPushButton.setText("Pause")


    def update_audio_state(self, state):
        if state == QMediaPlayer.PlayingState:
            # Update the UI when audio is playing.
            pass
        elif state == QMediaPlayer.PausedState:
            # Update the UI when audio is paused.
            pass
        elif state == QMediaPlayer.StoppedState:
            self.ui.AudioPlayPushButton.setText("Play")

    def update_audio_position(self, position):
        # Update the audio position on the slider and time label.
        duration = self.media_player.duration()
        self.results[self.audio_files[self.current_audio_index]]["length"] = duration / 1000
        if duration > 0:
            self.ui.AudioHorizontalSlider.setValue(position)
            self.ui.AudioTimeLabel.setText(self.format_time(position))

    def update_audio_duration(self, duration):
        # Update the slider's maximum value when the duration changes.
        if duration > 0:
            self.ui.AudioHorizontalSlider.setMaximum(duration)

    def format_time(self, position):
        current_seconds = position // 1000

        hours, remainder = divmod(current_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        current_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return current_time


    def next_audio(self):
        if self.current_audio_index != len(self.audio_files)-1:
            self.current_audio_index += 1
        else:
            self.current_audio_index = 0
        self.update_audio_info()
        self.play_audio(self.audio_files[self.current_audio_index])

    def previous_audio(self):
        if self.current_audio_index != 0:
            self.current_audio_index -= 1
        else:
            self.current_audio_index = len(self.audio_files)-1
        self.update_audio_info()
        self.play_audio(self.audio_files[self.current_audio_index])

    def save_results(self):
        results = []

        for file_name, value in self.results.items():
                results.append( {"wav" : file_name, "length": value["length"], "emo" : value["emotion"]} )

        save_path, _ = QFileDialog.getSaveFileName(self, "Save Results As", "", "JSON Files (*.json)")
        if save_path:
            with open(save_path, 'w') as file:
                json.dump(results, file, indent=4)
    def start_audio_selection(self):
        start_time_ms = self.ui.StartTimeInput.value()
        end_time_ms = self.ui.EndTimeInput.value()
        path  = self.audio_files[self.current_audio_index]
        # print(start_time_ms, path)
        self.cut_audio(start_time_ms,end_time_ms, path, path)

    def cut_audio(self, start_time, end_time, audio_path, output_path):
        # Load the audio file
        audio = AudioSegment.from_file(audio_path)

        # Convert start and end times to milliseconds
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)

        # Cut the audio
        cut_audio = audio[start_ms:end_ms]
        output_path = audio_path[:-4] + "_____1.wav"

        # Export the cut audio to the specified output file
        cut_audio.export(output_path, format="wav") 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = AudioLabelingApp()
    main_win.show()
    sys.exit(app.exec_())
