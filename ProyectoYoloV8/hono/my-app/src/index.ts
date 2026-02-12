import { serve } from "@hono/node-server";
import { Hono } from "hono";
import fetch from "node-fetch"; // npm install node-fetch
import FormData from "form-data"; // npm install form-data

//Crea una instancia de Hono
const app = new Hono();

//Define una ruta POST llamada /detect
app.post("/detect", async (c) => {
  try {

		/*Obtiene el cuerpo de la petición HTTP (la data que envía ESP32-CAM).
		parseBody() convierte automáticamente JSON o multipart/form-data en un 
		objeto que podemos usar en Node.js */
    const body = await c.req.parseBody();
    const image = body["image"] as File;

		//Valida que sí haya una imagen si no error
    if (!image) return c.json({ error: "No image received" }, 400);

		//Convierte el archivo de imagen a un buffer para enviarlo a la API de YOLO
    const arrayBuffer = await image.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

		//Prepara el FormData para enviar la imagen a la API de YOLO
    const formData = new FormData();
    formData.append("file", buffer, "temp.jpg");

    // Llamar a la API de YOLO
    const response = await fetch("http://localhost:5000/detect", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();
    return c.json(result);
  } catch (err) {
    console.error(err);
    return c.json({ error: "Internal server error" }, 500);
  }
});

// Inicia el servidor Hono en el puerto 3001
serve({ fetch: app.fetch, port: 3001 });
// Informa que el servidor está corriendo
console.log("Servidor Hono corriendo en http://localhost:3001");
