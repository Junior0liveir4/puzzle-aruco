#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "LabSEA-2.4GHz";
const char* password = "@procurando534";
const char* mqtt_server = "10.10.2.211";
const int mqtt_port = 30001;
const char* mqtt_user = "guest";
const char* mqtt_password = "guest";

const char* topic1 = "result";
int menssagem = 0;

const int PIN_FECHADURA = 4;

WiFiClient espClient;
PubSubClient client(espClient);

void callback(char* topic, byte* payload, unsigned int length);

void setup() {
  Serial.begin(115200);
  pinMode(PIN_FECHADURA, OUTPUT);
  digitalWrite(PIN_FECHADURA, HIGH);

  Serial.print("Conectando-se a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado. IP: ");
  Serial.println(WiFi.localIP());

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void callback(char* topic, byte* payload, unsigned int length) {
  // Converte o payload em uma string
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.print("Mensagem recebida no tópico ");
  Serial.print(topic);
  Serial.print(": ");
  Serial.println(message);

  // Se o tópico for o correto, interpreta a mensagem
  if (String(topic) == topic1) {
    if (message == "0") {
      Serial.println("-> Ação: SEQUÊNCIA INCORRETA");
      digitalWrite(PIN_FECHADURA, HIGH); // Mantém/fecha a fechadura

    // Condição de vitória do MODO DEMO
    } else if (message == "1") {
      Serial.println("-> Ação: VITÓRIA MODO DEMO");
      digitalWrite(PIN_FECHADURA, LOW);
      delay(10000);
      digitalWrite(PIN_FECHADURA, HIGH);
      // TODO: Adicione aqui sua lógica para a vitória no modo DEMO

    // --- Condições de vitória dos JOGOS ESPECÍFICOS ---
    } else if (message == "poke-game-win") {
      Serial.println("-> Ação: JOGO POKEMON VENCIDO");
      digitalWrite(PIN_FECHADURA, LOW);
      delay(10000);
      digitalWrite(PIN_FECHADURA, HIGH);
      // TODO: Adicione aqui sua lógica para o jogo POKEPUZZLE GO!

    } else if (message == "angry-game-win") {
      Serial.println("-> Ação: JOGO ANGRY BIRDS VENCIDO");
      digitalWrite(PIN_FECHADURA, LOW);
      delay(10000);
      digitalWrite(PIN_FECHADURA, HIGH);
      // TODO: Adicione aqui sua lógica para o jogo ANGRY ARUCOS

    } else if (message == "gta-game-win") {
      Serial.println("-> Ação: JOGO GTA VENCIDO");
      digitalWrite(PIN_FECHADURA, LOW);
      delay(10000);
      digitalWrite(PIN_FECHADURA, HIGH);
      // TODO: Adicione aqui sua lógica para o jogo GTA: SAN PUZZLE

    } else if (message == "mario-game-win") {
      Serial.println("-> Ação: JOGO MARIO VENCIDO");
      digitalWrite(PIN_FECHADURA, LOW);
      delay(10000);
      digitalWrite(PIN_FECHADURA, HIGH);
      // TODO: Adicione aqui sua lógica para o jogo SUPER MARIO PUZZLE

    } else if (message == "lol-game-win") {
      Serial.println("-> Ação: JOGO LEAGUE OF LEGENDS VENCIDO");
      digitalWrite(PIN_FECHADURA, LOW);
      delay(10000);
      digitalWrite(PIN_FECHADURA, HIGH);
      // TODO: Adicione aqui sua lógica para o jogo LEAGUE OF ARUCOS

    } else {
      Serial.println("-> Ação: MENSAGEM DESCONHECIDA RECEBIDA");
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando se reconectar ao MQTT Broker...");
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("Conectado!");
      // Inscreve-se nos dois tópicos
      client.subscribe(topic1);
      Serial.println("Inscrito nos tópicos:");
      Serial.println(topic1);
    } else {
      Serial.print("Falha, rc=");
      Serial.print(client.state());
      Serial.println(" Tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

void loop() {
  // Reconexão MQTT se necessário
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
