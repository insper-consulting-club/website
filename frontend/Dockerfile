FROM node:20-slim
 
WORKDIR /app
 
# Instala dependências
COPY package*.json ./
RUN npm install
 
# Copia o código
COPY . .
 
# Inicia o servidor de desenvolvimento
CMD ["npm", "run", "dev", "--", "--host"]