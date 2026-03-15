import asyncio
import websockets
import json
import sounddevice as sd
import numpy as np
import io
from pydub import AudioSegment
import queue
import threading
import sys
import shutil
import logging

# Cấu hình âm thanh
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'

class VoiceClient:
    def __init__(self, uri):
        self.uri = uri
        self.audio_buffer = []
        self.is_recording = False
        self.play_queue = queue.Queue()
        self.loop = None

    def check_dependencies(self):
        if not shutil.which("ffmpeg"):
            print("\nLỖI: Không tìm thấy 'ffmpeg'!")
            return False
        return True

    def audio_callback(self, indata, frames, time, status):
        if self.is_recording:
            self.audio_buffer.append(indata.copy())

    def play_worker(self):
        """Luồng phát âm thanh riêng biệt"""
        while True:
            samples = self.play_queue.get()
            if samples is None: break
            try:
                print(f"\n[SOPHIA ĐANG NÓI...]")
                sd.play(samples, SAMPLE_RATE)
                sd.wait()
            except Exception as e:
                print(f"Lỗi phát loa: {e}")
            finally:
                self.play_queue.task_done()

    async def receive_loop(self, websocket):
        """Tác vụ nhận dữ liệu từ WebSocket liên tục"""
        while True:
            try:
                response = await websocket.recv()
                if isinstance(response, bytes):
                    # Giải mã MP3 ngay khi nhận được
                    try:
                        audio_segment = AudioSegment.from_file(io.BytesIO(response), format="mp3")
                        audio_segment = audio_segment.set_frame_rate(SAMPLE_RATE).set_channels(1)
                        samples = np.frombuffer(audio_segment.raw_data, dtype=np.int16)
                        self.play_queue.put(samples)
                    except Exception as e:
                        print(f"Lỗi giải mã âm thanh: {e}")
                else:
                    data = json.loads(response)
                    if data.get("type") == "error":
                        print(f"\n[SERVER ERROR]: {data.get('message')}")
            except websockets.exceptions.ConnectionClosed:
                print("\nKết nối tới Server đã đóng.")
                break
            except Exception as e:
                print(f"Lỗi nhận: {e}")
                break

    def get_user_input(self):
        """Hàm chạy trong thread riêng để không block event loop"""
        while True:
            print("\n" + "="*40)
            input("Nhấn [Enter] để BẮT ĐẦU nói...")
            self.is_recording = True
            self.audio_buffer = []
            
            input("Đang thu âm... Nhấn [Enter] để GỬI.")
            self.is_recording = False
            
            if self.audio_buffer:
                recording = np.concatenate(self.audio_buffer, axis=0)
                # Gửi yêu cầu qua event loop
                asyncio.run_coroutine_threadsafe(self.send_audio(recording.tobytes()), self.loop)
            else:
                print("Không có âm thanh.")

    async def send_audio(self, data):
        if self.ws and self.ws.open:
            await self.ws.send(data)
            print(">>> Đã gửi âm thanh. Sophia đang suy nghĩ...")

    async def run(self):
        if not self.check_dependencies(): return
        self.loop = asyncio.get_running_loop()

        # Phát loa trong thread riêng
        threading.Thread(target=self.play_worker, daemon=True).start()

        print(f"Kết nối tới: {self.uri}")
        async with websockets.connect(self.uri, max_size=10*1024*1024) as websocket:
            self.ws = websocket
            print("Đã kết nối thành công!")

            # Chạy loop nhận dữ liệu
            recv_task = asyncio.create_task(self.receive_loop(websocket))
            
            # Chạy Input trong thread riêng
            input_thread = threading.Thread(target=self.get_user_input, daemon=True)
            input_thread.start()

            # Mở Micro
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, callback=self.audio_callback):
                await recv_task # Chờ cho đến khi kết nối đóng

if __name__ == "__main__":
    WS_URI = "ws://localhost:8000/ws/audio/laptop_user"
    client = VoiceClient(WS_URI)
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\nKết thúc.")
