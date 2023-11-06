FROM python:3.8-buster
WORKDIR /usr/src/app

RUN apt-get update 
RUN python3 --version && pip3 --version

# ADD openai-chatbot/ ./openai-chatbot
COPY ./requirements.txt .en[v] ./
RUN pip3 install -r requirements.txt
ADD /chat ./chat
ADD /app ./app

EXPOSE 8000
WORKDIR /usr/src/app
ENTRYPOINT python3 -m app whatsapp

# docker run -it --rm -v $(pwd)/data:/usr/src/app/data -p 5000:5000 --env-file .env --name whatsapp-chatbot whatsapp-chatbot
# en windows es necesario usar %cd% en lugar de $(pwd):
# docker run -it --rm -v %cd%/data:/usr/src/app/data -p 5000:5000 --env-file .env --name whatsapp-chatbot whatsapp-chatbot
# si queremos poner explicitamente el nombre my.env
# docker run -it --rm -v %cd%/data:/usr/src/app/data -p 5000:5000 --env-file my.env --name whatsapp-chatbot whatsapp-chatbot 
# la explicaciónd e cada parte es:
# -it : interactive mode
# --rm : remove container when it exits
# -v : volume, para montar un directorio local en el contenedor
# -p : port, para mapear un puerto local al contenedor
# --env-file : para pasar un archivo de variables de entorno
# --name : para darle un nombre al contenedor
# whatsapp-chatbot : nombre de la imagen
# . : directorio actual (donde está el Dockerfile). el punto se ponen en lugar de la ruta, es decir queda
# docker run -it --rm -v $(pwd)/data:/usr/src/app/data -p 5000:5000 --env-file .env --name whatsapp-chatbot whatsapp-chatbot



# docker build -t whatsapp-chatbot .
# esto es lo que funciona
# docker run -it --rm -v C:\Users\milen\Desktop\git_others\openai-whatsapp-chatbot\data:/usr/src/app/data -p 5000:5000 --env-file my.env --name whatsapp-chatbot whatsapp-chatbot