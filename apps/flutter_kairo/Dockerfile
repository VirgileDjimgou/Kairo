FROM ghcr.io/cirruslabs/flutter:stable AS build

WORKDIR /app
COPY pubspec.yaml pubspec.lock ./
RUN flutter pub get
COPY . .

ARG KAIRO_FLAVOR=staging
ARG KAIRO_API_BASE_URL=https://flutter-staging.example.org/api/v1
RUN flutter build web --release \
    --dart-define=KAIRO_FLAVOR=${KAIRO_FLAVOR} \
    --dart-define=KAIRO_API_BASE_URL=${KAIRO_API_BASE_URL}

FROM nginx:1.27-alpine AS production
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build/web /usr/share/nginx/html
EXPOSE 80
