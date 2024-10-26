import tkinter as tk
from tkinter import filedialog, scrolledtext
import psutil
import time
import os
import threading

# Ana Pencereyi Oluştur
root = tk.Tk()
root.title("Uygulama Takip")

# Pencere boyutları
root.geometry("600x500")
root.configure(bg="#2D2D2D")

# Global Değişkenler
app_paths = []  # Uygulama yolları listesi
detective_icon = None
footprint = None
animation_running = False

# Dosya yükleme işlevi
def upload_file():
    app_path = filedialog.askopenfilename(title="Uygulama Seç")
    if app_path:
        app_paths.append(app_path)
        label.config(text=f"Seçilen Uygulama: {os.path.basename(app_path)}")
        append_to_text_widget(f"{os.path.basename(app_path)} eklendi.\n")

# Dedektif ikonu ve ayak izi animasyonu
def animate_detective():
    global detective_icon, footprint, animation_running
    
    if animation_running:
        return

    animation_running = True
    detective_icon = canvas.create_oval(270, 200, 330, 260, fill="white", outline="black")
    footprint = canvas.create_rectangle(290, 260, 310, 280, fill="black")

    # Animasyonu başlat
    move_detective()

def move_detective():
    global detective_icon, footprint
    canvas.move(detective_icon, 0, 5)  # İkonu aşağı kaydır
    canvas.move(footprint, 0, 5)  # Ayak izini aşağı kaydır

    # Animasyon sınırlarını kontrol et
    if canvas.coords(detective_icon)[1] < 400:  # Eğer hala görünümün içinde
        root.after(100, move_detective)  # 100 ms sonra kendini tekrar çağır
    else:
        canvas.delete(detective_icon)  # İkonu sil
        canvas.delete(footprint)  # Ayak izini sil
        animation_running = False  # Animasyon sona erdi

# Uygulamanın CPU ve çalışma süresini kaydet
def track_application(process_name):
    process = None
    start_time = None
    cpu_usages = []

    output_text = f"Takip edilecek uygulama: {process_name}\n"
    append_to_text_widget(output_text)  # Arayüze ekle

    # Uygulama başlatılana kadar bekleyin
    while not process:
        for proc in psutil.process_iter(['name', 'create_time']):
            if proc.info['name'] == process_name:
                process = proc
                start_time = proc.create_time()
                output_text = f"{process_name} uygulaması başlatıldı.\n"
                append_to_text_widget(output_text, "green")  # Arka planı yeşil yap
                break
        time.sleep(1)  # 1 saniye bekleyin ve tekrar kontrol edin

    # Dedektif animasyonunu başlat
    animate_detective()

    # Uygulama çalışmaya başladıktan sonra takip et
    with open("uygulama_takip.txt", "a") as file:
        file.write(f"\nUygulama: {process_name}\n")
        while True:
            try:
                if not process.is_running():
                    output_text = f"{process_name} uygulaması sonlandı.\n"
                    append_to_text_widget(output_text, "red")  # Arka planı kırmızı yap
                    break

                # CPU kullanımını al ve listeye ekle
                cpu_usage = process.cpu_percent(interval=1) / psutil.cpu_count()
                cpu_usages.append(cpu_usage)

            except psutil.NoSuchProcess:
                output_text = f"İşlem sonlandı: {process_name}\n"
                append_to_text_widget(output_text, "red")  # Arka planı kırmızı yap
                break  # İşlem sonlandıysa döngüden çık

        # Uygulama kapandıktan sonra
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Ortalama CPU kullanımını hesapla
        avg_cpu_usage = sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0

        # Çalışma süresi formatı
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed_time_str = f"{int(hours)} saat, {int(minutes)} dakika, {int(seconds)} saniye"

        # Sonuçları dosyaya yaz
        file.write(f"Çalışma Süresi: {elapsed_time_str}, Ortalama CPU Kullanımı: {avg_cpu_usage:.2f}%\n")
        file.write(f"{process_name} uygulaması kapandı.\n")
        output_text = f"Çalışma Süresi: {elapsed_time_str}, Ortalama CPU Kullanımı: {avg_cpu_usage:.2f}%\n"
        append_to_text_widget(output_text)  # Arayüze ekle

# Arayüzde metin ekleme fonksiyonu (arka plan rengiyle birlikte)
def append_to_text_widget(text, bg_color=None):
    output_area.tag_configure("colored", background=bg_color, foreground="white")
    output_area.insert(tk.END, text, ("colored",) if bg_color else ())
    output_area.yview(tk.END)  # Aşağı kaydır

# Takip işlemini ayrı bir iş parçacığında çalıştıran fonksiyon
def start_tracking():
    for app_path in app_paths:
        process_name = os.path.basename(app_path)
        tracking_thread = threading.Thread(target=track_application, args=(process_name,))
        tracking_thread.start()

# Arayüz Elemanları
label = tk.Label(root, text="Uygulama Seçin", font=("Arial", 14), fg="white", bg="#2D2D2D")
label.pack(pady=10)

upload_button = tk.Button(root, text="Uygulama Yükle", command=upload_file, font=("Arial", 12), bg="#007ACC", fg="white", activebackground="#005A99", activeforeground="white")
upload_button.pack(pady=10)

track_button = tk.Button(root, text="Takip Et", command=start_tracking, font=("Arial", 12), bg="#007ACC", fg="white", activebackground="#005A99", activeforeground="white")
track_button.pack(pady=10)

# Çıktı alanı oluştur
output_area = scrolledtext.ScrolledText(root, width=70, height=20, font=("Arial", 10), bg="#1E1E1E", fg="white", insertbackground='white')
output_area.pack(pady=10)

# Canvas ekle
canvas = tk.Canvas(root, width=600, height=400, bg="#2D2D2D", highlightthickness=0)
canvas.pack()

# Uygulamayı başlat
root.mainloop()
