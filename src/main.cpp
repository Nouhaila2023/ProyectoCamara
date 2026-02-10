#include <Arduino.h>
#include "WifiAp.h"
#include "esp_camera.h"

const char *WIFI_SSID = "Riego_243";
const char *WIFI_PASSWORD = "primaram100";

static const uint32_t PHOTO_INTERVAL_MS = 60UL * 60UL * 1000UL;

WifiAp wifi(WIFI_SSID, WIFI_PASSWORD);

static uint32_t lastPhotoMs = 0;
static bool photoRequested = false;

camera_config_t config = {
    .pin_pwdn       = 32,
    .pin_reset      = -1,
    .pin_xclk       = 0,
    .pin_sccb_sda   = 26,
    .pin_sccb_scl   = 27,
    .pin_d7         = 35,
    .pin_d6         = 34,
    .pin_d5         = 39,
    .pin_d4         = 36,
    .pin_d3         = 21,
    .pin_d2         = 19,
    .pin_d1         = 18,
    .pin_d0         = 5,
    .pin_vsync      = 25,
    .pin_href       = 23,
    .pin_pclk       = 22,
    .xclk_freq_hz   = 20000000,
    .ledc_timer     = LEDC_TIMER_0,
    .ledc_channel   = LEDC_CHANNEL_0,
    .pixel_format   = PIXFORMAT_JPEG,
    .frame_size     = FRAMESIZE_SVGA,
    .jpeg_quality   = 12,
    .fb_count       = 1
};

void takePhotoAndCollectData() {
    // Inicializar cámara (solo la primera vez)
    static bool cameraInitialized = false;
    if (!cameraInitialized) {
        esp_err_t err = esp_camera_init(&config);
        if (err != ESP_OK) {
            Serial.printf("Error inicializando cámara: 0x%x\n", err);
            return;
        }
        cameraInitialized = true;
        Serial.println("Cámara inicializada");
    }

    // Capturar imagen
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Error capturando foto");
        return;
    }

    Serial.printf("Foto tomada! Tamaño: %u bytes\n", fb->len);

    Serial.println("Preparado para enviar a la nube...");

    esp_camera_fb_return(fb);

    Serial.println("Foto lista \n");
}

void setup()
{
    Serial.begin(115200);
    delay(1000);
    Serial.println("ESP32 Camera on");

    wifi.connect();

    lastPhotoMs = millis();
}

void loop()
{
    const uint32_t nowMs = millis();

    wifi.loop();

    if (!photoRequested && (nowMs - lastPhotoMs >= PHOTO_INTERVAL_MS))
    {
        Serial.println("Photo interval reached");
        photoRequested = true;

        if (!wifi.isConnected())
        {
            Serial.println("WiFi not connected, retrying...");
            wifi.connect();
        }
    }

    if (photoRequested && wifi.isConnected())
    {
        takePhotoAndCollectData();

        lastPhotoMs = millis();
        photoRequested = false;
    }

    delay(10); // watchdog safe
}
