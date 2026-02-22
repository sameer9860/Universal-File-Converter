<div align="center">

# ⚡ Universal File Converter

**Convert Any File Format** <br>
Fast, secure, and completely free format conversion tool built with Django.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-6.0.2-green.svg)](https://www.djangoproject.com/)

</div>

---

## 🌟 Overview

Universal File Converter is a powerful, modern, open-source web application designed to handle all your file conversion needs in one seamless interface. It boasts a dynamic, premium "glassmorphism" user interface and executes conversions entirely on the backend utilizing industry-standard open-source conversion engines.

### Key Features

- **✨ Stunning Modern UI**: A responsive, vibrant dark-mode interface with glassmorphism and micro-animations.
- **🛡️ Secure Processing**: Files are processed and then served dynamically without relying on external APIs.
- **📄 Documents**: Convert DOCX, PDF, ODT, HTML, MD, TXT, and more.
- **🖼️ Images**: Convert PNG, JPG, WEBP, SVG, TIFF, BMP, and more.
- **🎵 Audio**: Convert MP3, WAV, FLAC, OGG, AAC, etc.
- **🎬 Video**: Convert MP4, AVI, MKV, WEBM, MOV, etc.
- **📊 Data**: Convert CSV, JSON, XLSX, XML, YAML, etc.
- **📦 Archives**: Convert ZIP, RAR, 7Z, TAR.GZ, etc.

---

## 🚀 Getting Started

### Prerequisites

To run this application, you will need Python 3 installed on your machine.
Because this tool relies on powerful local conversion engines, your system also needs the following underlying dependencies installed (instructions below are for Ubuntu/Debian):

```bash
# General / Documents
sudo apt install libreoffice pandoc

# Images
sudo apt install imagemagick

# Audio / Video
sudo apt install ffmpeg
```

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sameer9860/Universal-File-Converter.git
   cd Universal-File-Converter
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   _(Note: The project leverages Django and various format-specific libraries like `pandas`, `Pillow`, `pydub`, etc.)_

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Start the development server**

   ```bash
   python manage.py runserver
   ```

6. **Open your browser**
   Navigate to `http://127.0.0.1:8000` to start converting!

### Docker Deployment (Recommended)

You can easily deploy the application using Docker and Docker Compose. This ensures all system dependencies (LibreOffice, FFmpeg, etc.) are correctly set up.

1. **Setup environment**: `cp .env.example .env` and update the values.
2. **Launch**: `docker-compose up --build -d`

The app will be available at `http://localhost:8000`.

---

## 💻 Usage

1. Open the application in your browser.
2. Select the category of your file (Document, Image, Audio, etc.) from the **Category Tabs**.
3. The format selectors will automatically update. Choose your **"Convert from"** and **"Convert to"** formats.
4. Drag and drop your file into the designated drop zone, or click to browse and select it.
5. Click the **⚡ Convert Now** button.
6. Once processing is complete, a success card will appear and the converted file will **auto-download** within 5 seconds!

---

## 🤝 Contributing

We love open-source and welcome contributions from the community!

Here is how you can help:

1. **Fork** the repository.
2. **Create a new branch** for your feature or bugfix (`git checkout -b feature/amazing-feature`).
3. **Commit your changes** with descriptive commit messages (`git commit -m "Add amazing feature"`).
4. **Push your branch** to your fork (`git push origin feature/amazing-feature`).
5. **Open a Pull Request** describing your changes.

### Development Guidelines

- **Frontend changes**: Please try to maintain the existing glassmorphic and animated aesthetic found in `dashboard.html`.
- **New Formats**: If adding new conversion formats, ensure they are properly mapped in `CONVERSION_MAP` inside `converter/views.py` and handled correctly in the respective backend handler within `converter/converters/`. Update the `FORMAT_MAP` logic in the frontend `dashboard.html` as well.

---

## 📜 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more information.

---

<div align="center">
  <i>Built with ❤️ for the open-source community.</i>
</div>
