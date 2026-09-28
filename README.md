<h1 align="center">Зернушка — сборки приложения</h1>

<p align="center">
  <a href="../../releases/latest"><img alt="Последняя версия" src="https://img.shields.io/github/v/release/Zernushka/releases?style=for-the-badge&label=%D0%B2%D0%B5%D1%80%D1%81%D0%B8%D1%8F&color=2E7D32"></a>
  <a href="../../actions/workflows/mirror.yml"><img alt="Зеркало" src="https://img.shields.io/github/actions/workflow/status/Zernushka/releases/mirror.yml?style=for-the-badge&label=%D0%B7%D0%B5%D1%80%D0%BA%D0%B0%D0%BB%D0%BE"></a>
</p>

<p align="center">
Готовые сборки приложения <b>Зернушка</b> для Android, Android TV и Windows.<br>
Это зеркало официальной раздачи — на случай, если основной сайт у вас не открывается.
</p>

## ⬇️ Скачать

<p align="center">
  <a href="../../releases/latest"><img alt="Android" src="https://img.shields.io/badge/Android-%D1%82%D0%B5%D0%BB%D0%B5%D1%84%D0%BE%D0%BD%D1%8B%20%D0%B8%20%D0%BF%D0%BB%D0%B0%D0%BD%D1%88%D0%B5%D1%82%D1%8B-3DDC84?style=for-the-badge&logo=android&logoColor=white"></a>
  <a href="../../releases/latest"><img alt="Android TV" src="https://img.shields.io/badge/Android%20TV-%D1%82%D0%B5%D0%BB%D0%B5%D0%B2%D0%B8%D0%B7%D0%BE%D1%80%D1%8B-1E88E5?style=for-the-badge&logo=android&logoColor=white"></a>
  <a href="../../releases/latest"><img alt="Windows" src="https://img.shields.io/badge/Windows-10%20%2F%2011-0078D4?style=for-the-badge&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTMgNC41IDExIDMuNHY4LjFIM3ptOSAtMS4yTDIxIDJ2OS41aC05ek0zIDEyLjVoOHY4LjFMMyAxOS41em05IDBoOVYyMmwtOS0xLjN6Ii8+PC9zdmc+&logoColor=white"></a>
</p>

Кнопки ведут на страницу последнего релиза — там прямые ссылки на каждый файл.

| файл | для чего |
|:--|:--|
| `zernushka-X.Y.Z-arm64.apk` | **Android** — телефоны и планшеты, подходит почти всем |
| `zernushka-X.Y.Z-armv7.apk` | **Android TV** — телевизоры и приставки, а также старые 32-битные устройства |
| `zernushka-X.Y.Z-x86_64.apk` | **Android x86** — устройства на Intel, эмуляторы |
| `Zernushka-Setup-X.Y.Z.exe` | **Windows 10 / 11** — установщик |

<details><summary>Как установить</summary>

- **Телефон:** скачайте APK, откройте его и разрешите установку из этого источника. Если arm64 не ставится — попробуйте armv7.
- **Android TV:** перекиньте armv7-APK на телевизор (файловый менеджер, «Send Files to TV» или флешка) и откройте.
- **Windows:** запустите `Setup.exe`. SmartScreen может предупредить о неизвестном издателе — «Подробнее» → «Выполнить в любом случае».
- Вход в приложение — по «Коду подключения» из Telegram-бота.

</details>

## 🔐 Откуда файлы и как проверить

- Официальная раздача: [зернушка.рф/dl](https://xn--80ajfnorw4b.xn--p1ai/dl/) · витрина: [zernushka.store](https://zernushka.store)
- Сборки сюда копирует автоматический процесс ([`mirror.yml`](.github/workflows/mirror.yml)): он скачивает файлы с официальной раздачи и публикует их **только если SHA-256 совпал** с официальным списком [`SHA256SUMS`](https://xn--80ajfnorw4b.xn--p1ai/dl/SHA256SUMS). Суммы продублированы в описании каждого релиза.
- Проверить у себя: Windows — `certutil -hashfile файл SHA256`, Linux/macOS — `sha256sum файл`.

## 💬 Связь

<p>
  <a href="https://t.me/Zernushka_bot"><img alt="Бот" src="https://img.shields.io/badge/Telegram-%D0%B1%D0%BE%D1%82%20%D0%B8%20%D0%BF%D0%BE%D0%B4%D0%BF%D0%B8%D1%81%D0%BA%D0%B0-26A5E4?style=for-the-badge&logo=telegram&logoColor=white"></a>
  <a href="https://t.me/Zernushka_support_bot"><img alt="Поддержка" src="https://img.shields.io/badge/Telegram-%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%BA%D0%B0-26A5E4?style=for-the-badge&logo=telegram&logoColor=white"></a>
  <a href="https://xn--80ajfnorw4b.xn--p1ai/"><img alt="Сайт" src="https://img.shields.io/badge/%D0%B7%D0%B5%D1%80%D0%BD%D1%83%D1%88%D0%BA%D0%B0.%D1%80%D1%84-%D1%81%D0%B0%D0%B9%D1%82-2E7D32?style=for-the-badge"></a>
</p>

Исходного кода в этом репозитории нет — только сборки и скрипт зеркалирования.
