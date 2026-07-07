import os
from PySide6.QtCore import QThread, Signal


class FileAnalyzerThread(QThread):
    result_ready = Signal(str)
    error_occurred = Signal(str)
    progress = Signal(str)

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path

    def run(self):
        ext = os.path.splitext(
            self.file_path
        )[1].lower()

        self.progress.emit(
            f"Analyzing {os.path.basename(self.file_path)}..."
        )

        try:
            if ext in ['.jpg', '.jpeg', '.png',
                       '.bmp', '.gif', '.webp']:
                result = self._analyze_image()
            elif ext == '.pdf':
                result = self._analyze_pdf()
            elif ext in ['.docx', '.doc']:
                result = self._analyze_word()
            elif ext in ['.txt', '.py', '.js',
                         '.html', '.css', '.json',
                         '.xml', '.csv', '.log']:
                result = self._analyze_text()
            elif ext in ['.mp3', '.mp4', '.wav',
                         '.flac', '.m4a']:
                result = self._analyze_media()
            else:
                result = self._analyze_general()

            self.result_ready.emit(result)

        except Exception as e:
            self.error_occurred.emit(
                f"Could not analyze file: {str(e)}"
            )

    # ----------------------------
    # Image Analysis
    # ----------------------------
    def _analyze_image(self):
        try:
            from PIL import Image
            import pytesseract

            # Set tesseract path
            pytesseract.pytesseract\
                .tesseract_cmd = (
                r'C:\Program Files\Tesseract-OCR'
                r'\tesseract.exe'
            )

            img = Image.open(self.file_path)
            name = os.path.basename(self.file_path)
            size = os.path.getsize(
                self.file_path
            )
            size_str = f"{size / 1024:.1f} KB" \
                if size < 1024 * 1024 \
                else f"{size / (1024*1024):.1f} MB"

            # Basic image info
            info = (
                f"🖼 Image Analysis: {name}\n\n"
                f"📐 Dimensions: "
                f"{img.width} x {img.height} px\n"
                f"🎨 Mode: {img.mode}\n"
                f"📦 Size: {size_str}\n"
                f"📁 Format: "
                f"{img.format or 'Unknown'}\n\n"
            )

            # Extract text with OCR
            try:
                text = pytesseract.image_to_string(
                    img, lang='eng'
                ).strip()
                if text and len(text) > 10:
                    if len(text) > 500:
                        text = text[:500] + '...'
                    info += (
                        f"📝 Text found in image:\n"
                        f"{text}"
                    )
                else:
                    info += (
                        "📝 No readable text "
                        "found in this image."
                    )
            except Exception:
                info += (
                    "📝 OCR not available. "
                    "Install Tesseract to "
                    "extract text from images."
                )

            return info

        except ImportError:
            return (
                "Please install Pillow: "
                "pip install Pillow pytesseract"
            )

    # ----------------------------
    # PDF Analysis
    # ----------------------------
    def _analyze_pdf(self):
        try:
            import PyPDF2

            name = os.path.basename(self.file_path)
            size = os.path.getsize(self.file_path)
            size_str = f"{size / 1024:.1f} KB" \
                if size < 1024 * 1024 \
                else f"{size / (1024*1024):.1f} MB"

            with open(
                self.file_path, 'rb'
            ) as f:
                reader = PyPDF2.PdfReader(f)
                pages = len(reader.pages)

                # Extract text from first 3 pages
                text = ""
                for i in range(min(3, pages)):
                    page_text = reader.pages[
                        i
                    ].extract_text()
                    if page_text:
                        text += page_text + "\n"

                # Get metadata
                meta = reader.metadata
                author = getattr(
                    meta, 'author', 'Unknown'
                ) or 'Unknown'
                title = getattr(
                    meta, 'title', 'Unknown'
                ) or name

            info = (
                f"📄 PDF Analysis: {name}\n\n"
                f"📑 Pages: {pages}\n"
                f"📦 Size: {size_str}\n"
                f"✏ Title: {title}\n"
                f"👤 Author: {author}\n\n"
            )

            if text.strip():
                preview = text.strip()[:400]
                info += (
                    f"📝 Content Preview:\n"
                    f"{preview}..."
                    if len(text) > 400
                    else f"📝 Content:\n{preview}"
                )
            else:
                info += (
                    "📝 Could not extract text. "
                    "PDF may be scanned/image-based."
                )

            return info

        except ImportError:
            return (
                "Please install PyPDF2: "
                "pip install PyPDF2"
            )

    # ----------------------------
    # Word Document Analysis
    # ----------------------------
    def _analyze_word(self):
        try:
            from docx import Document

            name = os.path.basename(self.file_path)
            size = os.path.getsize(self.file_path)
            size_str = f"{size / 1024:.1f} KB"

            doc = Document(self.file_path)

            # Count paragraphs and words
            paragraphs = [
                p.text for p in doc.paragraphs
                if p.text.strip()
            ]
            all_text = ' '.join(paragraphs)
            word_count = len(all_text.split())
            char_count = len(all_text)

            # Preview
            preview = all_text[:400] + '...' \
                if len(all_text) > 400 \
                else all_text

            info = (
                f"📝 Word Document: {name}\n\n"
                f"📦 Size: {size_str}\n"
                f"📄 Paragraphs: {len(paragraphs)}\n"
                f"💬 Words: {word_count}\n"
                f"🔤 Characters: {char_count}\n\n"
                f"📋 Content Preview:\n{preview}"
            )

            return info

        except ImportError:
            return (
                "Please install python-docx: "
                "pip install python-docx"
            )

    # ----------------------------
    # Text File Analysis
    # ----------------------------
    def _analyze_text(self):
        name = os.path.basename(self.file_path)
        ext = os.path.splitext(name)[1].lower()
        size = os.path.getsize(self.file_path)
        size_str = f"{size / 1024:.1f} KB"

        try:
            with open(
                self.file_path, 'r',
                encoding='utf-8', errors='ignore'
            ) as f:
                content = f.read()

            lines = content.split('\n')
            words = content.split()
            preview = content[:400] + '...' \
                if len(content) > 400 \
                else content

            file_type = {
                '.py': 'Python Script',
                '.js': 'JavaScript File',
                '.html': 'HTML File',
                '.css': 'CSS Stylesheet',
                '.json': 'JSON Data',
                '.xml': 'XML File',
                '.csv': 'CSV Data',
                '.txt': 'Text File',
                '.log': 'Log File',
            }.get(ext, 'Text File')

            info = (
                f"📄 {file_type}: {name}\n\n"
                f"📦 Size: {size_str}\n"
                f"📏 Lines: {len(lines)}\n"
                f"💬 Words: {len(words)}\n"
                f"🔤 Characters: {len(content)}\n\n"
                f"📋 Preview:\n{preview}"
            )

            return info

        except Exception as e:
            return f"Could not read file: {e}"

    # ----------------------------
    # Media File Analysis
    # ----------------------------
    def _analyze_media(self):
        name = os.path.basename(self.file_path)
        ext = os.path.splitext(name)[1].lower()
        size = os.path.getsize(self.file_path)
        size_str = f"{size / (1024*1024):.1f} MB"

        file_type = {
            '.mp3': '🎵 MP3 Audio',
            '.mp4': '🎬 MP4 Video',
            '.wav': '🎵 WAV Audio',
            '.flac': '🎵 FLAC Audio',
            '.m4a': '🎵 M4A Audio',
        }.get(ext, '🎵 Media File')

        info = (
            f"{file_type}: {name}\n\n"
            f"📦 Size: {size_str}\n"
            f"📁 Format: {ext.upper()[1:]}\n\n"
            f"💡 Tip: Say 'play {name}' to play this file!"
        )

        return info

    # ----------------------------
    # General File Analysis
    # ----------------------------
    def _analyze_general(self):
        name = os.path.basename(self.file_path)
        ext = os.path.splitext(name)[1].lower()
        size = os.path.getsize(self.file_path)

        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024*1024):.1f} MB"

        import datetime
        mod_time = os.path.getmtime(self.file_path)
        mod_date = datetime.datetime.fromtimestamp(
            mod_time
        ).strftime("%B %d, %Y %I:%M %p")

        info = (
            f"📁 File Analysis: {name}\n\n"
            f"📦 Size: {size_str}\n"
            f"🏷 Type: {ext.upper()[1:] if ext else 'Unknown'}\n"
            f"📅 Last Modified: {mod_date}\n"
            f"📂 Location: {os.path.dirname(self.file_path)}"
        )

        return info


class FileAnalyzer:
    def __init__(self):
        self.thread = None
        self.is_analyzing = False

    def analyze(
        self, file_path,
        on_result, on_error,
        on_progress=None
    ):
        if self.is_analyzing:
            return

        if not os.path.exists(file_path):
            on_error("File not found!")
            return

        self.thread = FileAnalyzerThread(file_path)

        if on_progress:
            self.thread.progress.connect(on_progress)

        self.thread.result_ready.connect(
            lambda r: self._done(r, on_result)
        )
        self.thread.error_occurred.connect(
            lambda e: self._done(e, on_error)
        )

        self.thread.start()
        self.is_analyzing = True

    def _done(self, result, callback):
        self.is_analyzing = False
        callback(result)