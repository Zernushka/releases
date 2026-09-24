# Зернушка — сборки приложения

Здесь лежат готовые сборки приложения **Зернушка** для Android и Windows.
Это зеркало официальной раздачи — на случай, если основной сайт у вас не открывается.

**Скачать последнюю версию → [Releases](../../releases/latest)**

| файл | для чего |
|---|---|
| `zernushka-X.Y.Z-arm64.apk` | Android — подходит почти всем телефонам |
| `zernushka-X.Y.Z-armv7.apk` | Android 32-бит, в том числе телевизоры (Android TV) |
| `zernushka-X.Y.Z-x86_64.apk` | Android на процессорах Intel, эмуляторы |
| `Zernushka-Setup-X.Y.Z.exe` | Windows 10 / 11 |

## Откуда файлы и как проверить

- Официальная раздача: https://зернушка.рф/dl/ · витрина: https://zernushka.store
- Сборки сюда копирует автоматический процесс (`.github/workflows/mirror.yml`): он скачивает файлы с официальной раздачи и публикует их **только если SHA-256 совпал** с официальным списком `https://зернушка.рф/dl/SHA256SUMS`. Суммы продублированы в описании каждого релиза.
- Проверить у себя: Windows — `certutil -hashfile файл SHA256`, Linux/macOS — `sha256sum файл`.

Подписка, поддержка и вход в аккаунт — в Telegram: [@ZernushkaVPN_Bot](https://t.me/ZernushkaVPN_Bot), поддержка — [@Zernushka_support_bot](https://t.me/Zernushka_support_bot).

Исходного кода в этом репозитории нет — только сборки и скрипт зеркалирования.
