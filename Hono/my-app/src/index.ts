import { Hono } from 'hono'
import { serve } from '@hono/node-server'
import { writeFile, mkdir } from 'fs/promises'
import path from 'path'
import Jimp from 'jimp'
import { createWorker } from 'tesseract.js'


const app = new Hono()

app.post('/upload', async (c) => {
  try {
    const body = await c.req.parseBody()
    const file = body['image'] as File

    if (!file) {
      return c.text('No se recibió ninguna imagen', 400)
    }

    const arrayBuffer = await file.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)

    const image = await Jimp.read(buffer)

    image.crop(1200, 820, 600, 120) 
    await image
      .grayscale()
      .contrast(0.4)
      .writeAsync('temp.jpg')

    const worker = await createWorker('eng')

    await worker.setParameters({
      tessedit_char_whitelist: '0123456789',
    });

    const processedBuffer = await image.getBufferAsync(Jimp.MIME_JPEG)
    const { data: { text } } = await worker.recognize(processedBuffer)

    await worker.terminate()

    const uploadDir = path.join(process.cwd(), 'imagenes')
    await mkdir(uploadDir, { recursive: true })

    const filePath = path.join(uploadDir, file.name)
    await writeFile(filePath, buffer)

    return c.json({
      message: 'Imagen procesada correctamente',
      file: file.name,
      value: text
    })

  } catch (error) {
    console.error(error)
    return c.text('Error al subir o procesar la imagen', 500)
  }
})

serve({
  fetch: app.fetch,
  port: 3001
})

console.log('Servidor corriendo en http://localhost:3001')
