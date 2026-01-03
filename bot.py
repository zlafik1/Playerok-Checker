import sys
import os
import time
import json
import curl_cffi
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum


class Color:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Printer:
    @staticmethod
    def print_color(text: str, color: str, end: str = "\n"):
        print(f"{color}{text}{Color.RESET}", end=end)
    
    @staticmethod
    def success(text: str):
        Printer.print_color(f"[+] {text}", Color.GREEN)
    
    @staticmethod
    def error(text: str):
        Printer.print_color(f"[-] {text}", Color.RED)
    
    @staticmethod
    def warning(text: str):
        Printer.print_color(f"[!] {text}", Color.YELLOW)
    
    @staticmethod
    def info(text: str):
        Printer.print_color(f"[i] {text}", Color.CYAN)


class UIHelper:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_line(char: str = "─", length: int = 60, color: str = Color.BLUE):
        Printer.print_color(char * length, color)
    
    @staticmethod
    def print_double_line(length: int = 60, color: str = Color.MAGENTA):
        Printer.print_color("═" * length, color)
    
    @staticmethod
    def print_header(text: str):
        UIHelper.print_double_line()
        print(f"{Color.BOLD}{Color.MAGENTA}{text.center(60)}{Color.RESET}")
        UIHelper.print_double_line()
    
    @staticmethod
    def get_input(prompt: str, default: str = "") -> str:
        Printer.print_color(f"{prompt}: ", Color.YELLOW, end="")
        result = input().strip()
        return result if result else default
    
    @staticmethod
    def print_box(title: str, content: List[str], border_color: str = Color.CYAN):
        width = 60
        print()
        Printer.print_color("┌" + "─" * (width - 2) + "┐", border_color)
        Printer.print_color(f"│ {title.center(width - 4)} │", border_color)
        Printer.print_color("├" + "─" * (width - 2) + "┤", border_color)
        for line in content:
            if line.strip():
                Printer.print_color(f"│ {line.ljust(width - 4)} │", border_color)
            else:
                Printer.print_color(f"│{' ' * (width - 2)}│", border_color)
        Printer.print_color("└" + "─" * (width - 2) + "┘", border_color)


class PlayerOkAPI:
    PERSISTED_QUERIES = {
        "user": "2e2e3b656d2ba48e0b2cd5eeedf88ef70e4aabb4ac4d9d9e9b8feff343a37d98",
        "deals": "c3b623b5fe0758cf91b2335ebf36ff65f8650a6672a792a3ca7a36d270d396fb",
        "deal": "5652037a966d8da6d41180b0be8226051fe0ed1357d460c6ae348c3138a0fba3",
        "games": "b9f6675fd5923bc5c247388e8e3209c3eede460ed328dbe6a9ec8e6428d3649b",
        "game": "12e701986f07aaaf57327b1133b9a1f3050b851c99b19293adfac40cfed0e41d",
        "game_category": "d81943c23bc558591f70286ad69bb6bf7f6229d04aae39fb0a9701d78a9fd749",
        "game_category_agreements": "3ea4b047196ed9f84aa5eb652299c4bd73f2e99e9fdf4587877658d9ea6330f6",
        "game_category_obtaining_types": "15b0991414821528251930b4c8161c299eb39882fd635dd5adb1a81fb0570aea",
        "game_category_instructions": "5991cead6a8ca46195bc4f7ae3164e7606105dbb82834c910658edeb0a1d1918",
        "game_category_data_fields": "6fdadfb9b05880ce2d307a1412bc4f2e383683061c281e2b65a93f7266ea4a49",
        "chats": "f7e6ee4fbb892abbd196342110e2abb0be309e2bd6671abb2963d0809c511d05",
        "chat": "bb024dc0652fc7c1302a64a117d56d99fb0d726eb4b896ca803dca55f611d933",
        "chat_messages": "e8162a8500865f4bb18dbaacb1c4703823f74c1925a91a5103f41c2021f0557a",
        "items": "206ae9d63e58bc41df9023aae39b9136f358282a808c32ee95f5b8b6669a8c8b",
        "item": "5b2be2b532cea7023f4f584512c4677469858e2210349f7eec78e3b96d563716",
        "item_priority_statuses": "b922220c6f979537e1b99de6af8f5c13727daeff66727f679f07f986ce1c025a",
        "transaction_providers": "31960e5dd929834c1f85bc685db80657ff576373076f016b2578c0a34e6e9f42",
        "transactions": "3b9925106c3fe9308ac632254fd70da347b5701f243ab8690477d5a7ca37c2c8",
        "sbp_bank_members": "ef7902598e855fa15fb5e3112156ac226180f0b009a36606fc80a18f00b80c63",
        "verified_cards": "eb338d8432981307a2b3d322b3310b2447cab3a6acf21aba4b8773b97e72d1aa"
    }


class APIException(Exception):
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class Account:
    def __init__(self, token: str, timeout: int = 10, proxy: str = None):
        self.token = token
        self.timeout = timeout
        self.proxy = proxy
        self.base_url = "https://playerok.com"
        
        self._user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self._curl_session = curl_cffi.Session(
            impersonate="chrome",
            timeout=timeout,
            proxy=proxy
        )
        
        self.id = None
        self.username = None
        self.email = None
        self.balance = 0.0
        self.is_blocked = False
        self.profile = None

    def _request(self, method: str, endpoint: str, data: dict = None, headers: dict = None):
        url = f"{self.base_url}{endpoint}"
        default_headers = {
            "accept": "*/*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/json",
            "cookie": f"token={self.token}",
            "origin": "https://playerok.com",
            "referer": "https://playerok.com/",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": self._user_agent,
            "x-timezone-offset": "-240"
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self._curl_session.get(url, params=data, headers=default_headers)
            else:
                response = self._curl_session.post(url, json=data, headers=default_headers)
            
            if response.status_code != 200:
                raise APIException(f"HTTP {response.status_code}: {response.text}", response.status_code)
            
            return response.json()
            
        except Exception as e:
            raise APIException(f"Ошибка запроса: {str(e)}")

    def get(self):
        headers = {"accept": "*/*"}
        payload = {
            "operationName": "viewer",
            "query": """
            query viewer {
              viewer {
                ...Viewer
                __typename
              }
            }
            fragment Viewer on User {
              id
              username
              email
              role
              hasFrozenBalance
              supportChatId
              systemChatId
              unreadChatsCounter
              isBlocked
              isBlockedFor
              createdAt
              lastItemCreatedAt
              hasConfirmedPhoneNumber
              canPublishItems
              profile {
                id
                avatarURL
                testimonialCounter
                __typename
              }
              __typename
            }
            """,
            "variables": {}
        }
        
        response = self._request("POST", "/graphql", payload, headers)
        
        if "errors" in response:
            error_msg = response["errors"][0]["message"]
            raise APIException(f"Ошибка API: {error_msg}")
        
        data = response.get("data", {}).get("viewer")
        if not data:
            raise APIException("Не удалось получить данные аккаунта")
        
        self.id = data.get("id")
        self.username = data.get("username")
        self.email = data.get("email")
        self.is_blocked = data.get("isBlocked", False)
        self.profile = data.get("profile", {})
        
        user_payload = {
            "operationName": "user",
            "variables": json.dumps({"username": self.username, "hasSupportAccess": False}, ensure_ascii=False),
            "extensions": json.dumps({"persistedQuery": {"version": 1, "sha256Hash": PlayerOkAPI.PERSISTED_QUERIES["user"]}}, ensure_ascii=False)
        }
        
        user_response = self._request("GET", "/graphql", user_payload, headers)
        user_data = user_response.get("data", {}).get("user", {})
        
        if user_data.get("__typename") == "User":
            balance_data = user_data.get("balance", {})
            self.balance = float(balance_data.get("available", 0)) if balance_data else 0.0
        
        return self


class TokenManager:
    @staticmethod
    def load_tokens(filename: str = "tokens.txt") -> List[str]:
        if not os.path.exists(filename):
            return []
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                tokens = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return tokens
        except Exception as e:
            Printer.error(f"Ошибка чтения файла: {e}")
            return []
    
    @staticmethod
    def save_valid_tokens(tokens: List[Dict[str, Any]], filename: str = "valid_tokens.json"):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            Printer.success(f"Валидные токены сохранены в {filename}")
        except Exception as e:
            Printer.error(f"Ошибка сохранения: {e}")
    
    @staticmethod
    def format_balance(balance: float) -> str:
        try:
            return f"{balance:,.2f} ₽".replace(",", " ")
        except Exception:
            return "Неизвестно"


class PlayerOkChecker:
    def __init__(self):
        self.stats = {
            'checked': 0,
            'valid': 0,
            'invalid': 0,
            'start_time': None
        }
    
    def show_banner(self):
        UIHelper.clear_screen()
        print(Color.BOLD + Color.MAGENTA)
        print("╔══════════════════════════════════════════════════════════╗")
        print("║                                                          ║")
        print("║               PLAYEROK TOKEN CHECKER                     ║")
        print("║                   Версия 2.1                             ║")
        print("║                                                          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print(Color.RESET)
        print(Color.CYAN)
        print("         Встроенный API PlayerOk")
        print("         Разработано ZLF Team")
        print("         Портфолио: https://zlafik1.github.io/zlafikbio/")
        print(Color.RESET)
        UIHelper.print_line("─", 60, Color.BLUE)
        print(f"{Color.YELLOW}         Текущее время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}{Color.RESET}")
        UIHelper.print_line("─", 60, Color.BLUE)
        print()
    
    def check_single_token(self):
        self.show_banner()
        UIHelper.print_header("ПРОВЕРКА ОДНОГО ТОКЕНА")
        
        token = UIHelper.get_input("Введите токен")
        if not token:
            Printer.error("Токен не может быть пустым")
            time.sleep(1.5)
            return
        
        Printer.info("Проверяем токен...")
        
        try:
            account = Account(token, timeout=5)
            account.get()
            
            self.show_banner()
            UIHelper.print_header("РЕЗУЛЬТАТ ПРОВЕРКИ")
            
            balance = TokenManager.format_balance(account.balance)
            status = "АКТИВЕН" if not account.is_blocked else "ЗАБЛОКИРОВАН"
            status_color = Color.GREEN if not account.is_blocked else Color.RED
            
            info = [
                f"Никнейм:      {account.username}",
                f"Баланс:       {balance}",
                f"Email:        {account.email or 'Не указан'}",
                f"Статус:       {status_color}{status}{Color.RESET}",
                f"ID:           {account.id or 'Неизвестно'}",
                f"Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            
            UIHelper.print_box("ИНФОРМАЦИЯ О АККАУНТЕ", info)
            
            self.stats['checked'] += 1
            self.stats['valid'] += 1
            
        except APIException as e:
            UIHelper.print_header("РЕЗУЛЬТАТ ПРОВЕРКИ")
            Printer.error(f"Токен невалидный: {str(e)}")
            self.stats['checked'] += 1
            self.stats['invalid'] += 1
        except Exception as e:
            UIHelper.print_header("РЕЗУЛЬТАТ ПРОВЕРКИ")
            Printer.error(f"Ошибка: {str(e)}")
            self.stats['checked'] += 1
            self.stats['invalid'] += 1
    
    def check_multiple_tokens(self):
        self.show_banner()
        UIHelper.print_header("МАССОВАЯ ПРОВЕРКА ТОКЕНОВ")
        
        tokens = TokenManager.load_tokens()
        
        if not tokens:
            Printer.error("Файл tokens.txt не найден или пуст")
            time.sleep(1.5)
            return
        
        Printer.info(f"Найдено токенов: {len(tokens)}")
        UIHelper.print_line("─", 60, Color.CYAN)
        print()
        
        valid_tokens = []
        invalid_tokens = []
        
        self.stats['start_time'] = time.time()
        
        for i, token in enumerate(tokens, 1):
            progress = f"[{i}/{len(tokens)}]"
            token_preview = token[:15] + "..." if len(token) > 15 else token
            
            print(f"\r{progress} Проверка {token_preview:<25}", end="")
            
            try:
                account = Account(token, timeout=5)
                account.get()
                balance = TokenManager.format_balance(account.balance)
                
                valid_tokens.append({
                    'token': token[:10] + "...",
                    'username': account.username,
                    'balance': balance,
                    'email': account.email or 'Не указан',
                    'status': 'АКТИВЕН' if not account.is_blocked else 'ЗАБЛОКИРОВАН'
                })
                
                print(f"\r{progress} {token_preview:<25} ", end="")
                Printer.print_color("ВАЛИДНЫЙ", Color.GREEN)
                
            except Exception:
                invalid_tokens.append(token[:10] + "...")
                print(f"\r{progress} {token_preview:<25} ", end="")
                Printer.print_color("НЕВАЛИДНЫЙ", Color.RED)
        
        elapsed_time = time.time() - self.stats['start_time']
        
        UIHelper.print_header("ИТОГИ ПРОВЕРКИ")
        
        results = [
            f"Проверено токенов: {len(tokens)}",
            f"Валидных:          {len(valid_tokens)}",
            f"Невалидных:        {len(invalid_tokens)}",
            f"Время выполнения:  {elapsed_time:.2f} сек",
            f"Скорость проверки: {len(tokens)/elapsed_time:.1f} токенов/сек" if elapsed_time > 0 else ""
        ]
        
        UIHelper.print_box("СТАТИСТИКА", results)
        
        if valid_tokens:
            UIHelper.print_header("ВАЛИДНЫЕ ТОКЕНЫ")
            
            token_list = []
            for i, token_info in enumerate(valid_tokens[:10], 1):
                username_display = token_info['username'][:18] + "..." if len(token_info['username']) > 18 else token_info['username']
                token_list.append(f"{i:2}. {username_display:<22} {token_info['balance']:<15}")
            
            if len(valid_tokens) > 10:
                token_list.append(f"... и еще {len(valid_tokens) - 10} токенов")
            
            UIHelper.print_box("СПИСОК", token_list)
            
            save_choice = UIHelper.get_input("\nСохранить валидные токены в файл? (y/n)", "n")
            if save_choice.lower() == 'y':
                TokenManager.save_valid_tokens(valid_tokens)
                Printer.success("Токены успешно сохранены!")
        
        self.stats['checked'] += len(tokens)
        self.stats['valid'] += len(valid_tokens)
        self.stats['invalid'] += len(invalid_tokens)
    
    def show_help(self):
        self.show_banner()
        UIHelper.print_header("СПРАВКА И ИНСТРУКЦИИ")
        
        help_content = [
            "КАК ПОЛУЧИТЬ ТОКЕН:",
            "1. Установите расширение Cookie Editor",
            "2. Зайдите на playerok.com и авторизуйтесь",
            "3. Откройте Cookie Editor",
            "4. Найдите сайт playerok.com в списке",
            "5. Найдите куку с названием 'token'",
            "6. Скопируйте значение токена",
            "",
            "МАССОВАЯ ПРОВЕРКА:",
            "Создайте файл tokens.txt",
            "Каждый токен на новой строке",
            "Комментарии начинаются с #",
            "Сохраните в папке с программой",
            "",
            "ПРИМЕР ФАЙЛА tokens.txt:",
            "# Это комментарий",
            "ваш_токен_1_здесь",
            "ваш_токен_2_здесь",
            "# Еще один токен",
            "ваш_токен_3_здесь",
            "",
            "СТАТИСТИКА ПРОГРАММЫ:",
            f"Проверено: {self.stats['checked']}",
            f"Валидных: {self.stats['valid']}",
            f"Невалидных: {self.stats['invalid']}",
            "",
            "РАЗРАБОТЧИКИ:",
            "ZLF Team",
            "Портфолио: zlafik1.github.io/zlafikbio/"
        ]
        
        UIHelper.print_box("ИНСТРУКЦИЯ", help_content)
    
    def show_stats(self):
        self.show_banner()
        UIHelper.print_header("СТАТИСТИКА ПРОВЕРОК")
        
        if self.stats['checked'] > 0:
            efficiency = self.stats['valid'] / self.stats['checked'] * 100
        else:
            efficiency = 0
        
        stats_content = [
            "ОБЩАЯ СТАТИСТИКА:",
            "",
            f"Проверено токенов: {self.stats['checked']}",
            f"Валидных токенов:  {self.stats['valid']}",
            f"Невалидных токенов: {self.stats['invalid']}",
            "",
            f"Процент валидности: {efficiency:.1f}%",
            "",
            "ПОСЛЕДНИЕ ДЕЙСТВИЯ:",
            f"Последняя проверка: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
            "",
            "ПРОГРАММА:",
            "PlayerOk Token Checker v2.3",
            "Разработано ZLF Team"
        ]
        
        UIHelper.print_box("СТАТИСТИЧЕСКИЕ ДАННЫЕ", stats_content)
    
    def show_menu(self):
        while True:
            self.show_banner()
            
            menu_items = [
                "Проверить один токен",
                "Проверить несколько токенов",
                "Справка и инструкции",
                "Показать статистику",
                "Выход из программы"
            ]
            
            print(Color.BOLD + "ГЛАВНОЕ МЕНЮ" + Color.RESET)
            UIHelper.print_double_line()
            
            for i, item in enumerate(menu_items, 1):
                print(f"  {Color.CYAN}[{i}]{Color.RESET} {item}")
            
            UIHelper.print_double_line()
            print()
            
            choice = UIHelper.get_input("Выберите действие (1-5)", "1")
            
            if choice == '1':
                self.check_single_token()
                UIHelper.get_input("\nНажмите Enter чтобы продолжить", "")
            elif choice == '2':
                self.check_multiple_tokens()
                UIHelper.get_input("\nНажмите Enter чтобы продолжить", "")
            elif choice == '3':
                self.show_help()
                UIHelper.get_input("\nНажмите Enter чтобы продолжить", "")
            elif choice == '4':
                self.show_stats()
                UIHelper.get_input("\nНажмите Enter чтобы продолжить", "")
            elif choice == '5':
                Printer.info("Завершение работы программы...")
                UIHelper.print_double_line()
                print(f"{Color.BOLD}Спасибо за использование программы!{Color.RESET}")
                UIHelper.print_double_line()
                break
            else:
                Printer.error("Неверный выбор. Пожалуйста, введите число от 1 до 5")
                time.sleep(1.5)
    
    def run(self):
        try:
            self.show_banner()
            Printer.info("Инициализация системы...")
            
            try:
                import curl_cffi
                Printer.success("Зависимости проверены успешно")
                Printer.success("Система готова к работе")
            except ImportError:
                Printer.error("Ошибка: Модуль curl-cffi не найден!")
                Printer.warning("Для работы программы необходимо установить curl-cffi")
                Printer.info("Установите выполнив команду: pip install curl-cffi")
                UIHelper.print_line("─", 60, Color.RED)
                UIHelper.get_input("\nНажмите Enter для выхода", "")
                return
            
            time.sleep(1.5)
            
            self.show_menu()
            
        except KeyboardInterrupt:
            print("\n")
            Printer.warning("Работа программы прервана пользователем")
            UIHelper.print_line("─", 60, Color.YELLOW)
            time.sleep(1)
        except Exception as e:
            Printer.error(f"Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            UIHelper.get_input("\nНажмите Enter для выхода", "")


def main():
    checker = PlayerOkChecker()
    checker.run()


if __name__ == "__main__":
    main()
