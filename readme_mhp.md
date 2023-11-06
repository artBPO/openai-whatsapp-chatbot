# 1 Variables de entorno
Están en mi archivo `my.env`
Estas no están configuradas aun, pero muchas parece que ni las lee
```bash
export CONVERSATION_EXPIRES_MINS=[N MINUTES UNTIL A CONVERSATION IS ERASED FROM MEMORY]
export ALLOWED_PHONE_NUMBERS=[+1234567890,+1987654321] # Default is any number
export START_TEMPLATE=[PATH TO A FILE WITH A TEMPLATE FOR THE START OF A CONVERSATION] #data/start_template.txt
export ASSEMBLYAI_API_KEY=[YOUR ASSEMBLY-AI API KEY] # esto es 
```

Para exponer el puerto local useé ngrok (cuenta asociada a mi github)

Abrimos un CMD y ejecutamos (lo tengo en c:\ngrok) con el puerto que hemos configurado en el archivo `.env`

Tuve probelmas para leer el archivo `.env`, al final uso el `dotenv` de python, uso `load_dotenv()` dandole el nombre del archivo `.env` . Y uso `os.getenv()` para leer las variables de entorno.
Ejemplo:
```python
from dotenv import load_dotenv
import os
load_dotenv('my.env') # esto lee el archivo .env
api_key = os.environ.get('ASSEMBLYAI_API_KEY') # esto lee la variable de entorno

```


# 2 Puerto
El `Flask` habilita un puerto para escuchar lo que le venga al bot. (el puerto se especifica en el archivo `.env`)
Ojo que tuvimos que instalar el flask async:
```bash
C:\Users\milen\AppData\Local\Programs\Python\Python38\python\python.exe -m pip install "Flask[async]"
```

## 2.1 Twilio
Este valor del puerto (del que se ve desde internet, no el local) se debe configurar en Twilio:
- Dentro de un Número de teléfono en el menú de la iz (Developers) vamos a `Messaging\Try it out\Send a WhatsApp Message`. 
Ahí en **Sandbox Settings** tenemos que poner la url, agregando el endpoint `whatsapp/reply` (que es el que hemos configurado en el archivo `app/whatsapp.py`)
- está el de `status`, pero que de momento no lo he necesitado ni probado.

## 2.2 ngrok
Para exponer el puerto local useé ngrok (cuenta asociada a mi github) porque no he conseguido abrir el puerto de mi router. Espero que en la nube o con docker sea más sencillo.

```bash
ngrok http 5000
```
Esto nos dará dos url
- Uno de interfzz web
- Otro de interfaz de API, para darselo a `Twilio`



# 3 Ejecución desde python

Ejecutamos la app desde python
```bash
C:\Users\milen\AppData\Local\Programs\Python\Python38\python.exe -m app.whatsapp
```
Para ver si esta funcionando (me pasó que se puso tonto), vamos desde el navegador al enlace localhost:5000 (127.0.01:5000). En la consola de python debe aparecer una traza.




# 4 Resumen:
- Estoy trabajando con **sandbox** de twilio, habría que pasar a producción, averiguar cómo
- No sé **abrir el puerto**, me apañe con ngrok. Quizás con solución en la nube sea más fácil. 
    - Probar cómo va con docker, quizás lo del puerto se solucione
- Tengo que hacer un refactoring para meter mis estructuras de Replis (prompts), etc
- Probar si recibe **Audio**, si tengo que enchufarle `Whisper`
- No tiene lo de ir escribiendo en **streaming** a medida que llega el resultado



