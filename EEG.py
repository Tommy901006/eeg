import serial
import csv
import time
import matplotlib.pyplot as plt
from collections import deque

# 設定串口名稱和波特率
SERIAL_PORT = 'COM15'  # 根據你的電腦串口名稱修改
BAUD_RATE = 500000
OUTPUT_FILE = 'eeg_data.csv'

# 初始化即時繪圖
plt.ion()  # 開啟互動模式
fig, ax = plt.subplots()
x_data = deque(maxlen=1000)  # 儲存時間數據（最多顯示1000筆）
y_data = deque(maxlen=1000)  # 儲存訊號數據（最多顯示1000筆）
line, = ax.plot([], [], '-b', label="EEG Signal")
ax.set_xlim(0, 1000)
ax.set_ylim(-500, 500)  # 根據訊號範圍調整
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Signal")
ax.legend()
plt.title("Real-Time EEG Signal")

# 打開串口
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")

# 打開 CSV 檔案準備寫入
with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Time(ms)', 'Signal'])  # 寫入標題

    print("Recording data... Press Ctrl+C to stop.")
    try:
        start_time = time.time()  # 紀錄開始時間
        while True:
            if ser.in_waiting > 0:  # 如果有可用的數據
                line_data = ser.readline().decode('utf-8').strip()  # 讀取一行數據
                try:
                    # 計算相對時間戳
                    elapsed_time = int((time.time() - start_time) * 1000)  # 毫秒
                    signal = float(line_data)  # 將訊號轉為浮點數

                    # 儲存資料到 CSV
                    writer.writerow([elapsed_time, signal])

                    # 更新即時繪圖
                    x_data.append(elapsed_time)
                    y_data.append(signal)
                    line.set_data(x_data, y_data)
                    ax.set_xlim(max(0, elapsed_time - 1000), elapsed_time)  # 動態更新 X 軸範圍
                    ax.set_ylim(min(y_data) - 10, max(y_data) + 10)  # 動態調整 Y 軸範圍
                    plt.pause(0.01)  # 更新圖表

                    print(f"{elapsed_time},{signal}")  # 即時顯示數據
                except ValueError:
                    pass  # 忽略格式錯誤的數據
    except KeyboardInterrupt:
        print("\nRecording stopped.")
    finally:
        ser.close()
        print(f"Data saved to {OUTPUT_FILE}.")
