import base64
import datetime
import os
import paho.mqtt.client as mqtt
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    battery_level = Column(Float, nullable=True)
    image_path = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Image id={self.id}, battery={self.battery_level}, path='{self.image_path}'>"

engine = create_engine(
    "mariadb+mariadbconnector://nichoir_user:vtfencntm@localhost:3306/nichoir",
    echo=False
)

Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine) 

SAVE_FOLDER = "/home/pi/nichoir_images"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload

    if topic == "nichoir/image":
        img_data = base64.b64decode(payload)
        filename = f"{SAVE_FOLDER}/{datetime.datetime.now().isoformat()}.jpg"

        with open(filename, "wb") as f:
            f.write(img_data)

        entry = Image(
            timestamp=datetime.datetime.now(),
            battery_level=None,
            image_path=filename
        )

        session.add(entry)
        session.commit()

        print(f"[OK] Image enregistrée : {filename}")


    elif topic == "nichoir/battery":
        level = float(payload.decode())

        entry = Image(
            timestamp=datetime.datetime.now(),
            battery_level=level,
            image_path=None
        )

        session.add(entry)
        session.commit()

        print(f"[OK] Batterie enregistrée : {level}%")


client = mqtt.Client()
client.on_message = on_message
client.connect("192.168.2.33", 1883, 60)
client.subscribe("nichoir/#")

print("Serveur MQTT en écoute...")
client.loop_forever()
