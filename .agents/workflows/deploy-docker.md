---
description: How to deploy the Universal-File-Converter application using Docker
---

1. **Prepare Environment Variables**
   Ensure you have a `.env` file based on `.env.example`.

   ```bash
   cp .env.example .env
   ```

   Open `.env` and set `SECRET_KEY`, `DEBUG=False`, and your `ALLOWED_HOSTS`.

2. **Build and Start the Containers**
   // turbo
   Use Docker Compose to build the image and start the services in the background.

   ```bash
   docker-compose up --build -d
   ```

3. **Verify Deployment**
   Check if the containers are running.

   ```bash
   docker-compose ps
   ```

4. **Access the Application**
   Open your browser and navigate to `http://localhost:8000`.

5. **Stopping the Application**
   To stop the services:
   ```bash
   docker-compose down
   ```
