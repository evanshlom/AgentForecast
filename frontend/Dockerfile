FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

EXPOSE 3369

CMD ["npx", "http-server", "-p", "3369", "-c-1"]