import tkinter as tk
from tkinter import ttk
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
import requests
from bs4 import BeautifulSoup
import threading
import time
import re
import sys


class App:

    def __init__(self, root):

        self.root = root

        # ============================================================
        # SISTEMA DE LOGS
        # ============================================================

        self.logs = []

        # ============================================================
        # DIRECTORIO DE LA APLICACIÓN
        # ============================================================

        if getattr(sys, "frozen", False):

            self.app_dir = Path(
                sys.executable
            ).resolve().parent

        else:

            self.app_dir = Path(
                __file__
            ).resolve().parent

        # ============================================================
        # CARPETA DOWNLOADS
        # ============================================================

        self.downloads_dir = (
            self.app_dir /
            "downloads"
        )

        self.downloads_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # ============================================================
        # SESSION HTTP
        # ============================================================

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 "
                "Safari/537.36"
            )
        })

        # ============================================================
        # LOG INICIAL
        # ============================================================

        self.log("=" * 80)
        self.log(" MEDIAFIRE DOWNLOADER")
        self.log("=" * 80)

        self.log(
            f"[INIT] Directorio aplicación: "
            f"{self.app_dir}"
        )

        self.log(
            f"[INIT] Directorio descargas: "
            f"{self.downloads_dir}"
        )

        self.log("=" * 80)

        # ============================================================
        # VENTANA
        # ============================================================

        self.root.title(
            "MediaFire Downloader"
        )

        self.root.geometry(
            "800x550"
        )

        self.root.resizable(
            False,
            False
        )

        # ============================================================
        # TÍTULO
        # ============================================================

        title = tk.Label(
            root,
            text="MediaFire Downloader",
            font=("Arial", 24, "bold")
        )

        title.pack(
            pady=(35, 30)
        )

        # ============================================================
        # URL
        # ============================================================

        url_label = tk.Label(
            root,
            text="URL de MediaFire:",
            font=("Arial", 12)
        )

        url_label.pack(
            anchor="w",
            padx=50
        )

        self.url_entry = tk.Entry(
            root,
            font=("Arial", 12)
        )

        self.url_entry.pack(
            fill="x",
            padx=50,
            pady=(5, 20)
        )

        # ============================================================
        # BOTONES
        # ============================================================

        buttons_frame = tk.Frame(
            root
        )

        buttons_frame.pack(
            pady=10
        )

        self.download_button = tk.Button(
            buttons_frame,
            text="Descargar",
            font=("Arial", 12, "bold"),
            width=15,
            command=self.start_download
        )

        self.download_button.pack(
            side="left",
            padx=5
        )

        self.logs_button = tk.Button(
            buttons_frame,
            text="Mostrar logs",
            font=("Arial", 12),
            width=15,
            command=self.show_logs
        )

        self.logs_button.pack(
            side="left",
            padx=5
        )

        # ============================================================
        # ESTADO
        # ============================================================

        self.status_label = tk.Label(
            root,
            text="Estado: Esperando...",
            font=("Arial", 11)
        )

        self.status_label.pack(
            pady=20
        )

        # ============================================================
        # PROGRESO
        # ============================================================

        self.progress = ttk.Progressbar(
            root,
            orient="horizontal",
            length=700,
            mode="determinate",
            maximum=100
        )

        self.progress.pack(
            pady=10
        )

        # ============================================================
        # VARIABLES PARA RENOMBRAR
        # ============================================================

        self.rename_window = None
        self.pending_download_url = None
        self.pending_filename = None
        self.pending_extension = None

    # =================================================================
    # LOG
    # =================================================================

    def log(self, message):

        message = str(
            message
        )

        self.logs.append(
            message
        )

        print(
            message,
            flush=True
        )

        if hasattr(
            self,
            "logs_text"
        ):

            try:

                self.logs_text.config(
                    state="normal"
                )

                self.logs_text.insert(
                    "end",
                    message + "\n"
                )

                self.logs_text.see(
                    "end"
                )

                self.logs_text.config(
                    state="disabled"
                )

            except tk.TclError:

                pass

    # =================================================================
    # VENTANA DE LOGS
    # =================================================================

    def show_logs(self):

        if hasattr(
            self,
            "logs_window"
        ):

            try:

                if self.logs_window.winfo_exists():

                    self.logs_window.deiconify()

                    self.logs_window.lift()

                    self.logs_window.focus_force()

                    return

            except tk.TclError:

                pass

        self.logs_window = tk.Toplevel(
            self.root
        )

        self.logs_window.title(
            "Logs - MediaFire Downloader"
        )

        self.logs_window.geometry(
            "900x600"
        )

        self.logs_window.minsize(
            600,
            400
        )

        # =============================================================
        # FRAME
        # =============================================================

        frame = tk.Frame(
            self.logs_window
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # =============================================================
        # TEXT
        # =============================================================

        self.logs_text = tk.Text(
            frame,
            wrap="none",
            font=("Courier New", 10),
            bg="#111111",
            fg="#eeeeee",
            insertbackground="white"
        )

        self.logs_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        # =============================================================
        # SCROLL VERTICAL
        # =============================================================

        vertical_scroll = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.logs_text.yview
        )

        vertical_scroll.pack(
            side="right",
            fill="y"
        )

        self.logs_text.configure(
            yscrollcommand=vertical_scroll.set
        )

        # =============================================================
        # SCROLL HORIZONTAL
        # =============================================================

        horizontal_scroll = ttk.Scrollbar(
            self.logs_window,
            orient="horizontal",
            command=self.logs_text.xview
        )

        horizontal_scroll.pack(
            side="bottom",
            fill="x",
            padx=10
        )

        self.logs_text.configure(
            xscrollcommand=horizontal_scroll.set
        )

        # =============================================================
        # BOTONES
        # =============================================================

        buttons_frame = tk.Frame(
            self.logs_window
        )

        buttons_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 10)
        )

        clear_button = tk.Button(
            buttons_frame,
            text="Limpiar logs",
            command=self.clear_logs
        )

        clear_button.pack(
            side="left"
        )

        close_button = tk.Button(
            buttons_frame,
            text="Cerrar",
            command=self.close_logs
        )

        close_button.pack(
            side="right"
        )

        # =============================================================
        # CARGAR LOGS
        # =============================================================

        self.logs_text.config(
            state="normal"
        )

        for message in self.logs:

            self.logs_text.insert(
                "end",
                message + "\n"
            )

        self.logs_text.see(
            "end"
        )

        self.logs_text.config(
            state="disabled"
        )

        # =============================================================
        # CIERRE
        # =============================================================

        self.logs_window.protocol(
            "WM_DELETE_WINDOW",
            self.close_logs
        )

    # =================================================================
    # CERRAR VENTANA LOGS
    # =================================================================

    def close_logs(self):

        try:

            self.logs_window.destroy()

        except (
            tk.TclError,
            AttributeError
        ):

            pass

        if hasattr(
            self,
            "logs_text"
        ):

            del self.logs_text

        if hasattr(
            self,
            "logs_window"
        ):

            del self.logs_window

    # =================================================================
    # LIMPIAR LOGS
    # =================================================================

    def clear_logs(self):

        self.logs.clear()

        if hasattr(
            self,
            "logs_text"
        ):

            try:

                self.logs_text.config(
                    state="normal"
                )

                self.logs_text.delete(
                    "1.0",
                    "end"
                )

                self.logs_text.config(
                    state="disabled"
                )

            except tk.TclError:

                pass

        self.log(
            "[LOG] Logs limpiados."
        )

    # =================================================================
    # INICIAR DESCARGA
    # =================================================================

    def start_download(self):

        self.log("")
        self.log("=" * 80)
        self.log(
            "[DOWNLOAD] BOTÓN DESCARGAR PRESIONADO"
        )
        self.log("=" * 80)

        url = self.url_entry.get().strip()

        self.log(
            f"[DOWNLOAD] URL recibida: {url}"
        )

        if not url:

            self.log(
                "[ERROR] La URL está vacía."
            )

            self.status_label.config(
                text="Estado: Introduce una URL"
            )

            return

        if "mediafire.com" not in url.lower():

            self.log(
                "[ERROR] La URL no parece ser de MediaFire."
            )

            self.status_label.config(
                text="Estado: URL de MediaFire inválida"
            )

            return

        self.download_button.config(
            state="disabled"
        )

        self.progress["value"] = 0

        self.status_label.config(
            text="Estado: Obteniendo página de MediaFire..."
        )

        thread = threading.Thread(
            target=self.process_download,
            args=(url,),
            daemon=True
        )

        thread.start()

        self.log(
            "[THREAD] Thread iniciado."
        )

    # =================================================================
    # PROCESAR MEDIAFIRE
    # =================================================================

    def process_download(
        self,
        mediafire_url
    ):

        start_time = time.time()

        try:

            self.log("")
            self.log("-" * 80)
            self.log(
                "[PROCESS] PASO 1 - "
                "OBTENIENDO PÁGINA DE MEDIAFIRE"
            )
            self.log("-" * 80)

            self.log(
                f"[HTTP] GET {mediafire_url}"
            )

            response = self.session.get(
                mediafire_url,
                timeout=30,
                allow_redirects=True
            )

            self.log(
                f"[HTTP] Status: "
                f"{response.status_code}"
            )

            self.log(
                f"[HTTP] URL final: "
                f"{response.url}"
            )

            self.log(
                f"[HTTP] Content-Type: "
                f"{response.headers.get('Content-Type')}"
            )

            self.log(
                f"[HTTP] HTML recibido: "
                f"{len(response.content):,} bytes"
            )

            response.raise_for_status()

            html = response.text

            # =========================================================
            # GUARDAR HTML
            # =========================================================

            debug_file = (
                self.app_dir /
                "mediafire_debug.html"
            )

            debug_file.write_text(
                html,
                encoding="utf-8"
            )

            self.log(
                f"[DEBUG] HTML guardado en: "
                f"{debug_file}"
            )

            # =========================================================
            # PARSEAR
            # =========================================================

            self.log("")
            self.log("-" * 80)
            self.log(
                "[PROCESS] PASO 2 - ANALIZANDO HTML"
            )
            self.log("-" * 80)

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            # =========================================================
            # DOWNLOAD BUTTON
            # =========================================================

            self.log(
                "[SEARCH] Buscando #downloadButton..."
            )

            download_button = soup.find(
                "a",
                id="downloadButton"
            )

            download_url = None

            if download_button:

                self.log(
                    "[SEARCH] #downloadButton encontrado."
                )

                download_url = (
                    download_button.get(
                        "href"
                    )
                )

            # =========================================================
            # SELECTORES ALTERNATIVOS
            # =========================================================

            if not download_url:

                self.log(
                    "[SEARCH] Probando selectores alternativos..."
                )

                selectors = [
                    "a#downloadButton",
                    "a.input.popsok",
                    "a.download_link",
                    "a[aria-label='Download file']"
                ]

                for selector in selectors:

                    element = soup.select_one(
                        selector
                    )

                    if element:

                        href = element.get(
                            "href"
                        )

                        if href:

                            self.log(
                                f"[SEARCH] Encontrado con: "
                                f"{selector}"
                            )

                            download_url = href

                            break

            # =========================================================
            # BUSCAR LINKS
            # =========================================================

            if not download_url:

                self.log(
                    "[SEARCH] Buscando enlaces alternativos..."
                )

                for link in soup.find_all(
                    "a",
                    href=True
                ):

                    href = link.get(
                        "href"
                    )

                    text = link.get_text(
                        " ",
                        strip=True
                    )

                    if (
                        "download" in href.lower()
                        or
                        "download" in text.lower()
                    ):

                        self.log(
                            f"[SEARCH] Posible enlace: "
                            f"{href}"
                        )

                        if not download_url:

                            download_url = href

            # =========================================================
            # VALIDAR
            # =========================================================

            if not download_url:

                raise Exception(
                    "No se encontró el enlace directo "
                    "de descarga en MediaFire."
                )

            download_url = urljoin(
                response.url,
                download_url
            )

            self.log("")
            self.log("=" * 80)
            self.log(
                "[DIRECT] URL DIRECTA ENCONTRADA"
            )
            self.log("=" * 80)

            self.log(
                download_url
            )

            self.log("=" * 80)

            elapsed = (
                time.time()
                -
                start_time
            )

            self.log(
                f"[PROCESS] Tiempo extracción: "
                f"{elapsed:.2f}s"
            )

            # =========================================================
            # OBTENER INFORMACIÓN DEL ARCHIVO
            # =========================================================

            self.log("")
            self.log(
                "[FILE] Obteniendo información del archivo..."
            )

            file_response = self.session.get(
                download_url,
                stream=True,
                timeout=60,
                allow_redirects=True
            )

            file_response.raise_for_status()

            filename = self.extract_filename(
                file_response
            )

            file_response.close()

            self.log(
                f"[FILE] Nombre detectado: {filename}"
            )

            # =========================================================
            # SEPARAR NOMBRE Y EXTENSIÓN
            # =========================================================

            original_path = Path(
                filename
            )

            extension = (
                original_path.suffix
            )

            name_without_extension = (
                original_path.stem
            )

            if not extension:
                extension = ""

            self.log(
                f"[FILE] Nombre sin extensión: "
                f"{name_without_extension}"
            )

            self.log(
                f"[FILE] Extensión: "
                f"{extension if extension else '(ninguna)'}"
            )

            # =========================================================
            # MOSTRAR VENTANA DE NOMBRE
            # =========================================================

            self.root.after(
                0,
                self.show_filename_window,
                download_url,
                name_without_extension,
                extension
            )

        except requests.exceptions.Timeout:

            self.handle_error(
                "Timeout conectando con MediaFire."
            )

        except requests.exceptions.HTTPError as error:

            self.handle_error(
                f"Error HTTP: {error}"
            )

        except requests.exceptions.RequestException as error:

            self.handle_error(
                f"Error de conexión: {error}"
            )

        except Exception as error:

            self.handle_error(
                str(error)
            )

    # =================================================================
    # VENTANA PARA ELEGIR NOMBRE
    # =================================================================

    def show_filename_window(
        self,
        download_url,
        original_name,
        extension
    ):

        self.pending_download_url = download_url

        self.pending_filename = original_name

        self.pending_extension = extension

        # =============================================================
        # CREAR VENTANA
        # =============================================================

        self.rename_window = tk.Toplevel(
            self.root
        )

        self.rename_window.title(
            "Nombre del archivo"
        )

        self.rename_window.geometry(
            "500x230"
        )

        self.rename_window.resizable(
            False,
            False
        )

        self.rename_window.transient(
            self.root
        )

        self.rename_window.grab_set()

        # =============================================================
        # TÍTULO
        # =============================================================

        title = tk.Label(
            self.rename_window,
            text="Guardar archivo",
            font=("Arial", 18, "bold")
        )

        title.pack(
            pady=(25, 15)
        )

        # =============================================================
        # INFORMACIÓN
        # =============================================================

        info = tk.Label(
            self.rename_window,
            text=(
                "Escribe el nombre con el que quieres guardar "
                "el archivo:"
            ),
            font=("Arial", 10)
        )

        info.pack(
            pady=(0, 8)
        )

        # =============================================================
        # INPUT
        # =============================================================

        input_frame = tk.Frame(
            self.rename_window
        )

        input_frame.pack(
            padx=30,
            fill="x"
        )

        self.filename_entry = tk.Entry(
            input_frame,
            font=("Arial", 12)
        )

        self.filename_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        # =============================================================
        # EXTENSIÓN
        # =============================================================

        extension_label = tk.Label(
            input_frame,
            text=extension,
            font=("Arial", 12, "bold"),
            fg="#555555"
        )

        extension_label.pack(
            side="left",
            padx=(5, 0)
        )

        # =============================================================
        # NOMBRE ORIGINAL
        # =============================================================

        self.filename_entry.insert(
            0,
            original_name
        )

        self.filename_entry.select_range(
            0,
            "end"
        )

        self.filename_entry.focus_set()

        # =============================================================
        # BOTONES
        # =============================================================

        buttons_frame = tk.Frame(
            self.rename_window
        )

        buttons_frame.pack(
            pady=25
        )

        download_confirm_button = tk.Button(
            buttons_frame,
            text="Descargar",
            font=("Arial", 11, "bold"),
            width=15,
            command=self.confirm_filename
        )

        download_confirm_button.pack(
            side="left",
            padx=5
        )

        cancel_button = tk.Button(
            buttons_frame,
            text="Cancelar",
            font=("Arial", 11),
            width=15,
            command=self.cancel_filename
        )

        cancel_button.pack(
            side="left",
            padx=5
        )

        # =============================================================
        # TECLAS
        # =============================================================

        self.rename_window.bind(
            "<Return>",
            lambda event: self.confirm_filename()
        )

        self.rename_window.bind(
            "<Escape>",
            lambda event: self.cancel_filename()
        )

        self.rename_window.protocol(
            "WM_DELETE_WINDOW",
            self.cancel_filename
        )

        self.status_label.config(
            text="Estado: Elige el nombre del archivo..."
        )

    # =================================================================
    # CONFIRMAR NOMBRE
    # =================================================================

    def confirm_filename(self):

        if not self.rename_window:

            return

        new_name = (
            self.filename_entry
            .get()
            .strip()
        )

        # =============================================================
        # VALIDAR
        # =============================================================

        if not new_name:

            self.filename_entry.focus_set()

            self.status_label.config(
                text="Estado: El nombre no puede estar vacío."
            )

            return

        # =============================================================
        # CARACTERES INVÁLIDOS
        # =============================================================

        invalid_chars = r'<>:"/\|?*'

        if any(
            char in new_name
            for char in invalid_chars
        ):

            self.status_label.config(
                text=(
                    "Estado: El nombre contiene caracteres inválidos."
                )
            )

            return

        # =============================================================
        # EVITAR EXTENSIÓN DUPLICADA
        # =============================================================

        extension = (
            self.pending_extension
        )

        if extension and new_name.lower().endswith(
            extension.lower()
        ):

            new_name = new_name[
                :-len(extension)
            ].rstrip()

        if not new_name:

            self.status_label.config(
                text="Estado: El nombre no puede estar vacío."
            )

            return

        # =============================================================
        # NOMBRE FINAL
        # =============================================================

        final_filename = (
            new_name +
            extension
        )

        output_file = (
            self.downloads_dir /
            final_filename
        )

        self.log("")
        self.log("=" * 80)
        self.log(
            "[RENAME] NOMBRE PERSONALIZADO"
        )
        self.log("=" * 80)

        self.log(
            f"[RENAME] Nombre introducido: "
            f"{new_name}"
        )

        self.log(
            f"[RENAME] Extensión original: "
            f"{extension if extension else '(ninguna)'}"
        )

        self.log(
            f"[RENAME] Nombre final: "
            f"{final_filename}"
        )

        self.log(
            f"[RENAME] Destino: "
            f"{output_file}"
        )

        self.log("=" * 80)

        # =============================================================
        # CERRAR VENTANA
        # =============================================================

        try:

            self.rename_window.grab_release()

            self.rename_window.destroy()

        except tk.TclError:

            pass

        self.rename_window = None

        # =============================================================
        # INICIAR DESCARGA
        # =============================================================

        self.status_label.config(
            text="Estado: Descargando..."
        )

        self.download_file(
            self.pending_download_url,
            final_filename
        )

        self.pending_download_url = None
        self.pending_filename = None
        self.pending_extension = None

    # =================================================================
    # CANCELAR NOMBRE
    # =================================================================

    def cancel_filename(self):

        self.log(
            "[RENAME] Usuario canceló la descarga."
        )

        try:

            self.rename_window.grab_release()

            self.rename_window.destroy()

        except (
            tk.TclError,
            AttributeError
        ):

            pass

        self.rename_window = None

        self.pending_download_url = None
        self.pending_filename = None
        self.pending_extension = None

        self.download_button.config(
            state="normal"
        )

        self.status_label.config(
            text="Estado: Descarga cancelada."
        )

    # =================================================================
    # INICIAR DESCARGA
    # =================================================================

    def download_file(
        self,
        url,
        filename
    ):

        self.log("")
        self.log("=" * 80)
        self.log(
            "[FILE] PASO 3 - INICIANDO DESCARGA"
        )
        self.log("=" * 80)

        self.log(
            f"[FILE] URL: {url}"
        )

        self.log(
            f"[FILE] Nombre elegido: {filename}"
        )

        thread = threading.Thread(
            target=self._download_file_thread,
            args=(url, filename),
            daemon=True
        )

        thread.start()

        self.log(
            "[FILE] Thread de descarga iniciado."
        )

    # =================================================================
    # THREAD DE DESCARGA
    # =================================================================

    def _download_file_thread(
        self,
        url,
        filename
    ):

        try:

            self.log("")
            self.log("-" * 80)
            self.log(
                "[FILE] CONECTANDO AL ARCHIVO"
            )
            self.log("-" * 80)

            response = self.session.get(
                url,
                stream=True,
                timeout=60,
                allow_redirects=True
            )

            self.log(
                f"[FILE] HTTP Status: "
                f"{response.status_code}"
            )

            self.log(
                f"[FILE] URL final: "
                f"{response.url}"
            )

            self.log(
                f"[FILE] Content-Type: "
                f"{response.headers.get('Content-Type')}"
            )

            self.log(
                f"[FILE] Content-Length: "
                f"{response.headers.get('Content-Length')}"
            )

            self.log(
                f"[FILE] Content-Disposition: "
                f"{response.headers.get('Content-Disposition')}"
            )

            response.raise_for_status()

            # =========================================================
            # NOMBRE
            # =========================================================

            self.log(
                f"[FILE] Nombre final: "
                f"{filename}"
            )

            output_file = (
                self.downloads_dir /
                filename
            )

            self.log(
                f"[FILE] Destino: "
                f"{output_file}"
            )

            # =========================================================
            # TAMAÑO
            # =========================================================

            content_length = response.headers.get(
                "Content-Length"
            )

            if content_length:

                total_size = int(
                    content_length
                )

                self.log(
                    f"[FILE] Tamaño: "
                    f"{self.format_bytes(total_size)}"
                )

            else:

                total_size = 0

                self.log(
                    "[FILE] Tamaño desconocido."
                )

            # =========================================================
            # TRANSFERENCIA
            # =========================================================

            self.log("")
            self.log("=" * 80)
            self.log(
                "[FILE] COMENZANDO TRANSFERENCIA"
            )
            self.log("=" * 80)

            downloaded = 0

            start_time = time.time()

            last_ui_update = 0

            with open(
                output_file,
                "wb"
            ) as file:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if not chunk:

                        continue

                    file.write(
                        chunk
                    )

                    downloaded += len(
                        chunk
                    )

                    # =================================================
                    # VELOCIDAD
                    # =================================================

                    elapsed = (
                        time.time()
                        -
                        start_time
                    )

                    if elapsed > 0:

                        speed = (
                            downloaded /
                            elapsed
                        )

                    else:

                        speed = 0

                    # =================================================
                    # PORCENTAJE
                    # =================================================

                    if total_size:

                        percentage = (
                            downloaded /
                            total_size
                        ) * 100

                    else:

                        percentage = 0

                    # =================================================
                    # ETA
                    # =================================================

                    if (
                        total_size
                        and
                        speed > 0
                    ):

                        remaining = (
                            total_size
                            -
                            downloaded
                        )

                        eta = (
                            remaining /
                            speed
                        )

                    else:

                        eta = 0

                    # =================================================
                    # CONSOLA
                    # =================================================

                    if total_size:

                        print(
                            "\r"
                            f"[FILE] "
                            f"{percentage:6.2f}% | "
                            f"{self.format_bytes(downloaded)} / "
                            f"{self.format_bytes(total_size)} | "
                            f"{self.format_bytes(speed)}/s | "
                            f"ETA "
                            f"{self.format_time(eta)}",
                            end="",
                            flush=True
                        )

                    else:

                        print(
                            "\r"
                            f"[FILE] "
                            f"{self.format_bytes(downloaded)} | "
                            f"{self.format_bytes(speed)}/s",
                            end="",
                            flush=True
                        )

                    # =================================================
                    # UI
                    # =================================================

                    now = time.time()

                    if (
                        now -
                        last_ui_update
                        >=
                        0.1
                    ):

                        last_ui_update = now

                        self.root.after(
                            0,
                            self.update_progress,
                            percentage,
                            downloaded,
                            total_size,
                            speed,
                            eta
                        )

            print()

            # =========================================================
            # FINAL
            # =========================================================

            elapsed = (
                time.time()
                -
                start_time
            )

            self.log("")
            self.log("=" * 80)
            self.log(
                "[FILE] DESCARGA TERMINADA"
            )
            self.log("=" * 80)

            self.log(
                f"[FILE] Archivo: "
                f"{output_file}"
            )

            self.log(
                f"[FILE] Tamaño: "
                f"{self.format_bytes(downloaded)}"
            )

            self.log(
                f"[FILE] Tiempo: "
                f"{self.format_time(elapsed)}"
            )

            if elapsed > 0:

                average_speed = (
                    downloaded /
                    elapsed
                )

                self.log(
                    f"[FILE] Velocidad promedio: "
                    f"{self.format_bytes(average_speed)}/s"
                )

            self.log("=" * 80)

            self.root.after(
                0,
                self.download_finished,
                output_file
            )

        except requests.exceptions.Timeout:

            self.handle_error(
                "Timeout durante la descarga."
            )

        except requests.exceptions.RequestException as error:

            self.handle_error(
                f"Error descargando archivo: {error}"
            )

        except Exception as error:

            self.handle_error(
                f"Error durante la descarga: {error}"
            )

    # =================================================================
    # NOMBRE DEL ARCHIVO
    # =================================================================

    def extract_filename(
        self,
        response
    ):

        content_disposition = (
            response.headers.get(
                "Content-Disposition"
            )
        )

        if content_disposition:

            self.log(
                f"[FILE] Content-Disposition: "
                f"{content_disposition}"
            )

            # filename*=UTF-8''archivo.rar

            match = re.search(
                r"filename\*\s*=\s*UTF-8''([^;]+)",
                content_disposition,
                re.IGNORECASE
            )

            if match:

                return unquote(
                    match.group(1).strip('"')
                )

            # filename="archivo.rar"

            match = re.search(
                r'filename\s*=\s*"([^"]+)"',
                content_disposition,
                re.IGNORECASE
            )

            if match:

                return match.group(1)

            # filename=archivo.rar

            match = re.search(
                r"filename\s*=\s*([^;]+)",
                content_disposition,
                re.IGNORECASE
            )

            if match:

                return match.group(1).strip()

        # =============================================================
        # FALLBACK
        # =============================================================

        parsed = urlparse(
            response.url
        )

        filename = Path(
            parsed.path
        ).name

        if filename:

            return filename

        return "archivo_descargado"

    # =================================================================
    # PROGRESO
    # =================================================================

    def update_progress(
        self,
        percentage,
        downloaded,
        total,
        speed=0,
        eta=0
    ):

        if total:

            self.progress["value"] = (
                percentage
            )

            self.status_label.config(
                text=(
                    f"Descargando... "
                    f"{percentage:.1f}% | "
                    f"{self.format_bytes(downloaded)} / "
                    f"{self.format_bytes(total)} | "
                    f"{self.format_bytes(speed)}/s | "
                    f"ETA {self.format_time(eta)}"
                )
            )

        else:

            self.status_label.config(
                text=(
                    f"Descargando... "
                    f"{self.format_bytes(downloaded)} | "
                    f"{self.format_bytes(speed)}/s"
                )
            )

    # =================================================================
    # FINALIZADO
    # =================================================================

    def download_finished(
        self,
        output_file
    ):

        self.progress["value"] = 100

        self.status_label.config(
            text=(
                f"Descarga terminada: "
                f"{output_file.name}"
            )
        )

        self.download_button.config(
            state="normal"
        )

        self.log(
            "[UI] Descarga finalizada correctamente."
        )

    # =================================================================
    # ERROR
    # =================================================================

    def handle_error(
        self,
        error
    ):

        self.log("")
        self.log("=" * 80)
        self.log(
            "[ERROR] PROCESO FINALIZADO CON ERROR"
        )
        self.log("=" * 80)
        self.log(
            f"[ERROR] {error}"
        )
        self.log("=" * 80)

        self.root.after(
            0,
            self.download_error,
            error
        )

    # =================================================================
    # ERROR UI
    # =================================================================

    def download_error(
        self,
        error
    ):

        self.status_label.config(
            text=f"Error: {error}"
        )

        self.download_button.config(
            state="normal"
        )

    # =================================================================
    # BYTES
    # =================================================================

    @staticmethod
    def format_bytes(
        value
    ):

        if value < 1024:

            return f"{value:.0f} B"

        if value < 1024 ** 2:

            return (
                f"{value / 1024:.2f} KB"
            )

        if value < 1024 ** 3:

            return (
                f"{value / (1024 ** 2):.2f} MB"
            )

        return (
            f"{value / (1024 ** 3):.2f} GB"
        )

    # =================================================================
    # TIEMPO
    # =================================================================

    @staticmethod
    def format_time(
        seconds
    ):

        seconds = int(
            max(
                seconds,
                0
            )
        )

        hours = (
            seconds // 3600
        )

        minutes = (
            seconds % 3600
        ) // 60

        seconds = (
            seconds % 60
        )

        if hours:

            return (
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{seconds:02d}"
            )

        return (
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )


# =====================================================================
# MAIN
# =====================================================================

def main():

    print("")
    print("=" * 80)
    print(
        " INICIANDO MEDIAFIRE DOWNLOADER"
    )
    print("=" * 80)

    root = tk.Tk()

    app = App(
        root
    )

    root.mainloop()


if __name__ == "__main__":

    main()
