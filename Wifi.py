import tkinter as tk
from tkinter import messagebox, ttk
import speedtest  # Asegúrate de que este es el módulo correcto, no tu archivo local speedtest.py
print(speedtest.__file__)
import subprocess
import csv
import socket
import time
import threading
from plyer import notification
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from fpdf import FPDF
import schedule

# ------------------------ VARIABLES GLOBALES ------------------------
download_speeds = []
upload_speeds = []
times = []
fig, ax = plt.subplots()

# ------------------------ FUNCIONES PRINCIPALES ------------------------

def test_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000
        ping = st.results.ping

        download_label.config(text=f"Descarga: {download_speed:.2f} Mbps")
        upload_label.config(text=f"Subida: {upload_speed:.2f} Mbps")
        ping_label.config(text=f"Ping: {ping:.2f} ms")

        if download_speed < 5:
            send_notification("¡Alerta! La velocidad de descarga es menor a 5 Mbps.")

        save_report(download_speed, upload_speed, ping)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo medir la velocidad: {str(e)}")

def scan_networks():
    try:
        if system_var.get() == "Windows":
            networks = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True, text=True)
        elif system_var.get() == "Linux":
            networks = subprocess.check_output("nmcli -f SSID,SIGNAL dev wifi", shell=True, text=True)

        networks_text.delete(1.0, tk.END)
        networks_text.insert(tk.END, networks)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo escanear las redes: {str(e)}")

def get_connected_devices():
    try:
        if system_var.get() == "Windows":
            devices = subprocess.check_output("arp -a", shell=True, text=True)
        elif system_var.get() == "Linux":
            devices = subprocess.check_output("sudo nmap -sn 192.168.1.0/24", shell=True, text=True)

        devices_text.delete(1.0, tk.END)
        devices_text.insert(tk.END, devices)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener los dispositivos: {str(e)}")

def save_report(download_speed, upload_speed, ping):
    with open('speed_report.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([f"{download_speed:.2f}", f"{upload_speed:.2f}", f"{ping:.2f}"])

def send_notification(message):
    try:
        notification.notify(
            title="Alerta de Red",
            message=message,
            timeout=10
        )
    except Exception as e:
        messagebox.showerror("Error de Notificación", f"No se pudo enviar la notificación: {str(e)}")

def update_graph(i):
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000
        upload_speed = st.upload() / 1_000_000

        download_speeds.append(download_speed)
        upload_speeds.append(upload_speed)
        times.append(time.strftime("%H:%M:%S"))

        if len(times) > 10:
            download_speeds.pop(0)
            upload_speeds.pop(0)
            times.pop(0)

        ax.clear()
        ax.plot(times, download_speeds, label="Descarga (Mbps)", color="cyan", marker='o')
        ax.plot(times, upload_speeds, label="Subida (Mbps)", color="magenta", marker='x')
        ax.legend(loc="upper left")
        ax.set_title("Velocidad de Internet en Tiempo Real")
        ax.set_xlabel("Hora")
        ax.set_ylabel("Velocidad (Mbps)")
        ax.tick_params(axis='x', rotation=45)
        fig.tight_layout()
    except:
        pass

def run_schedule():
    schedule.every(10).minutes.do(test_speed)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print(f"Error en programación programada: {e}")

def get_latency_info():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        server = st.results.server
        latency_info = f"Servidor: {server['sponsor']}\nUbicación: {server['name']}, {server['country']}\nLatencia: {server['latency']} ms"
        messagebox.showinfo("Información de Latencia", latency_info)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la latencia: {str(e)}")

# ------------------------ FUNCIONES ADICIONALES ------------------------

def send_email_notification():
    messagebox.showinfo("Correo", "Funcionalidad aún no implementada.")

def release_renew_ip():
    try:
        if system_var.get() == "Windows":
            subprocess.run("ipconfig /release", shell=True)
            subprocess.run("ipconfig /renew", shell=True)
        elif system_var.get() == "Linux":
            subprocess.run("nmcli networking off", shell=True)
            time.sleep(2)
            subprocess.run("nmcli networking on", shell=True)
        messagebox.showinfo("Listo", "IP liberada y renovada exitosamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo liberar y renovar la IP: {str(e)}")

def show_adapter_info():
    try:
        if system_var.get() == "Windows":
            result = subprocess.check_output("ipconfig /all", shell=True, text=True)
        elif system_var.get() == "Linux":
            result = subprocess.check_output("ifconfig", shell=True, text=True)
        messagebox.showinfo("Información del Adaptador de Red", result)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la información del adaptador: {str(e)}")

def run_vulnerability_scan():
    try:
        ip = "192.168.1.1"
        result = subprocess.check_output(f"nmap -sV --script vuln {ip}", shell=True, text=True)
        messagebox.showinfo("Escaneo de Vulnerabilidades", result)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo realizar el escaneo de vulnerabilidades: {str(e)}")

def show_connected_devices_history():
    try:
        history_window = tk.Toplevel(root)
        history_window.title("Historial de Dispositivos Conectados")
        history_window.geometry("500x300")
        history_window.config(bg="black")

        tree = ttk.Treeview(history_window, columns=("dispositivo", "ip", "mac"), show='headings')
        tree.heading("dispositivo", text="Dispositivo")
        tree.heading("ip", text="IP")
        tree.heading("mac", text="MAC")
        tree.pack(fill=tk.BOTH, expand=True)

        devices = [("Dispositivo 1", "192.168.1.2", "00:1A:2B:3C:4D:5E"),
                   ("Dispositivo 2", "192.168.1.3", "00:1A:2B:3C:4D:6F")]
        for device in devices:
            tree.insert("", tk.END, values=device)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el historial: {str(e)}")

def save_pdf_report():
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Reporte de Conexión de Red", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, txt="Este es un reporte de ejemplo sobre el estado de la red", ln=True)
        pdf.output("report.pdf")
        messagebox.showinfo("PDF Guardado", "El reporte se ha guardado como 'report.pdf'.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el reporte en PDF: {str(e)}")

# ------------------------ FUNCIONES AUXILIARES ------------------------

def show_ip_window():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        messagebox.showinfo("Dirección IP", f"IP Local: {ip_address}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo obtener la IP: {str(e)}")

def show_history_window():
    try:
        with open("speed_report.csv", newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)

        history_win = tk.Toplevel(root)
        history_win.title("Historial de Pruebas de Velocidad")
        tree = ttk.Treeview(history_win, columns=("Descarga", "Subida", "Ping"), show="headings")
        for col in ("Descarga", "Subida", "Ping"):
            tree.heading(col, text=col)
        for row in rows:
            tree.insert("", tk.END, values=row)
        tree.pack(expand=True, fill='both')
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el historial: {str(e)}")

def scan_ports_window():
    messagebox.showinfo("Función en Desarrollo", "Escaneo de puertos aún no implementado.")

def restart_adapter_window():
    messagebox.showinfo("Función en Desarrollo", "Reinicio de adaptador aún no implementado.")

# ------------------------ INTERFAZ GRÁFICA ------------------------

root = tk.Tk()
root.title("Monitor de Red Profesional")
root.geometry("700x800")
root.config(bg="black")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

main_frame = tk.Frame(notebook, bg="black")
latency_frame = tk.Frame(notebook, bg="black")
graph_frame = tk.Frame(notebook, bg="black")

notebook.add(main_frame, text="Principal")
notebook.add(latency_frame, text="Latencia ISP")
notebook.add(graph_frame, text="Gráfico en Tiempo Real")

title_label = tk.Label(main_frame, text="Monitor de Red Profesional", font=("Helvetica", 16, "bold"), fg="white", bg="black")
title_label.pack(pady=10)

system_var = tk.StringVar(value="Windows")
tk.Label(main_frame, text="Selecciona el sistema operativo:", fg="white", bg="black").pack()
tk.Radiobutton(main_frame, text="Windows", variable=system_var, value="Windows", fg="white", bg="black", selectcolor="gray").pack()
tk.Radiobutton(main_frame, text="Linux", variable=system_var, value="Linux", fg="white", bg="black", selectcolor="gray").pack()

tk.Button(main_frame, text="Medir Velocidad de Internet", command=test_speed, width=25, bg="gray", fg="white").pack(pady=5)
download_label = tk.Label(main_frame, text="Descarga: -- Mbps", fg="white", bg="black")
download_label.pack()
upload_label = tk.Label(main_frame, text="Subida: -- Mbps", fg="white", bg="black")
upload_label.pack()
ping_label = tk.Label(main_frame, text="Ping: -- ms", fg="white", bg="black")
ping_label.pack(pady=5)

tk.Button(main_frame, text="Escanear Redes Wi-Fi", command=scan_networks, width=25, bg="gray", fg="white").pack(pady=5)
networks_text = tk.Text(main_frame, height=5, width=60, bg="black", fg="white")
networks_text.pack(pady=5)

tk.Button(main_frame, text="Ver Dispositivos Conectados", command=get_connected_devices, width=25, bg="gray", fg="white").pack(pady=5)
devices_text = tk.Text(main_frame, height=5, width=60, bg="black", fg="white")
devices_text.pack(pady=5)

tk.Button(main_frame, text="Ver Dirección IP", command=show_ip_window, width=25, bg="gray", fg="white").pack(pady=5)
tk.Button(main_frame, text="Ver Historial de Pruebas", command=show_history_window, width=25, bg="gray", fg="white").pack(pady=5)
tk.Button(main_frame, text="Escanear Puertos", command=scan_ports_window, width=25, bg="gray", fg="white").pack(pady=5)
tk.Button(main_frame, text="Reiniciar Adaptador de Red", command=restart_adapter_window, width=25, bg="gray", fg="white").pack(pady=5)

tk.Button(latency_frame, text="Obtener Información de Latencia del Proveedor de Internet", command=get_latency_info, bg="gray", fg="white", width=50).pack(pady=30)
tk.Button(latency_frame, text="Notificaciones por Email", command=send_email_notification, bg="gray", fg="white", width=50).pack(pady=5)
tk.Button(latency_frame, text="Liberar y Renovar IP Pública", command=release_renew_ip, bg="gray", fg="white", width=50).pack(pady=5)
tk.Button(latency_frame, text="Información del Adaptador de Red", command=show_adapter_info, bg="gray", fg="white", width=50).pack(pady=5)
tk.Button(latency_frame, text="Escaneo de Vulnerabilidades Básico", command=run_vulnerability_scan, bg="gray", fg="white", width=50).pack(pady=5)
tk.Button(latency_frame, text="Historial de Dispositivos Conectados", command=show_connected_devices_history, bg="gray", fg="white", width=50).pack(pady=5)
tk.Button(latency_frame, text="Guardar Reporte en PDF", command=save_pdf_report, bg="gray", fg="white", width=50).pack(pady=5)

# Insertar gráfico en graph_frame
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Iniciar animación y programación periódica
ani = FuncAnimation(fig, update_graph, interval=30000)
schedule_thread = threading.Thread(target=run_schedule, daemon=True)
schedule_thread.start()

root.mainloop()
