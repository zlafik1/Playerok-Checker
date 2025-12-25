import sys
import os
import time
import webbrowser
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import json

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
        Printer.print_color(f"✓ {text}", Color.GREEN)
    
    @staticmethod
    def error(text: str):
        Printer.print_color(f"✗ {text}", Color.RED)
    
    @staticmethod
    def warning(text: str):
        Printer.print_color(f"⚠ {text}", Color.YELLOW)
    
    @staticmethod
    def info(text: str):
        Printer.print_color(f"ℹ {text}", Color.CYAN)
    
    @staticmethod
    def header(text: str):
        Printer.print_color(f"\n{text}", Color.BOLD + Color.BLUE)
    
    @staticmethod
    def menu_item(num: int, text: str):
        Printer.print_color(f"  [{num}] {text}", Color.CYAN)

class UIHelper:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_centered(text: str, width: int = 60, color: str = Color.BLUE):
        padding = (width - len(text)) // 2
        Printer.print_color(" " * padding + text + " " * padding, color)
    
    @staticmethod
    def print_separator(char: str = "═", length: int = 60, color: str = Color.BLUE):
        Printer.print_color(char * length, color)
    
    @staticmethod
    def print_box(title: str, content: List[str], border_color: str = Color.BLUE):
        width = 60
        print()
        Printer.print_color("╔" + "═" * (width - 2) + "╗", border_color)
        Printer.print_color("║" + title.center(width - 2) + "║", border_color)
        Printer.print_color("╠" + "═" * (width - 2) + "╣", border_color)
        for line in content:
            Printer.print_color("║ " + line.ljust(width - 3) + "║", border_color)
        Printer.print_color("╚" + "═" * (width - 2) + "╝", border_color)
    
    @staticmethod
    def get_input(prompt: str, default: str = "") -> str:
        Printer.print_color(f"{prompt}: ", Color.YELLOW, end="")
        result = input().strip()
        return result if result else default

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
    def format_balance(balance_obj: Any) -> str:
        try:
            if hasattr(balance_obj, 'available'):
                return f"{balance_obj.available:,.2f} ₽".replace(",", " ")
            elif hasattr(balance_obj, 'total'):
                return f"{balance_obj.total:,.2f} ₽".replace(",", " ")
            elif hasattr(balance_obj, '__str__'):
                balance_str = str(balance_obj)
                try:
                    balance_float = float(balance_str)
                    return f"{balance_float:,.2f} ₽".replace(",", " ")
                except ValueError:
                    return balance_str
            else:
                return str(balance_obj)
        except Exception:
            return "Неизвестно"

class PlayerOkChecker:
    def __init__(self):
        self.Account = None
        self.stats = {
            'checked': 0,
            'valid': 0,
            'invalid': 0,
            'start_time': None
        }
    
    def initialize_api(self) -> bool:
        Printer.info("Инициализация playerokapi...")
        try:
            from playerokapi.account import Account
            self.Account = Account
            Printer.success("API успешно инициализировано")
            return True
        except ImportError:
            Printer.error("Модуль playerokapi не найден")
            Printer.info("Установите: pip install playerokapi")
            return False
        except Exception as e:
            Printer.error(f"Ошибка инициализации: {e}")
            return False
    
    def create_account_instance(self, token: str, timeout: int = 10):
        return self.Account(
            token=token,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            requests_timeout=timeout,
            proxy=None
        )
    
    def check_single_token(self):
        UIHelper.clear_screen()
        self.show_banner()
        
        UIHelper.print_box("ПРОВЕРКА ТОКЕНА", [])
        
        token = UIHelper.get_input("Введите токен")
        if not token:
            Printer.error("Токен не может быть пустым")
            time.sleep(1.5)
            return
        
        Printer.info("Проверяем токен...")
        
        try:
            account = self.create_account_instance(token)
            acc_info = account.get()
            
            UIHelper.clear_screen()
            self.show_banner()
            
            Printer.print_color("\n" + "═" * 60, Color.GREEN)
            Printer.print_color("✅ ТОКЕН РАБОЧИЙ".center(60), Color.GREEN)
            Printer.print_color("═" * 60, Color.GREEN)
            
            balance = TokenManager.format_balance(acc_info.profile.balance)
            
            info_lines = [
                f"👤 Никнейм:    {acc_info.profile.username}",
                f"💰 Баланс:      {balance}",
                f"📧 Email:       {acc_info.profile.email}",
                f"🔒 Статус:      {'🟢 Активен' if not getattr(acc_info.profile, 'is_blocked', False) else '🔴 Заблокирован'}",
                f"🆔 ID:          {getattr(acc_info.profile, 'id', 'Неизвестно')}",
                f"📅 Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            ]
            
            for line in info_lines:
                Printer.print_color(line, Color.CYAN)
            
            self.stats['checked'] += 1
            self.stats['valid'] += 1
            
        except Exception as e:
            Printer.error(f"Токен невалидный: {str(e)[:100]}")
            self.stats['checked'] += 1
            self.stats['invalid'] += 1
    
    def check_multiple_tokens(self):
        UIHelper.clear_screen()
        self.show_banner()
        
        UIHelper.print_box("МАССОВАЯ ПРОВЕРКА ТОКЕНОВ", [])
        
        tokens = TokenManager.load_tokens()
        
        if not tokens:
            Printer.error("Файл tokens.txt не найден или пуст")
            time.sleep(1.5)
            return
        
        Printer.info(f"Найдено токенов: {len(tokens)}")
        print()
        
        valid_tokens = []
        invalid_tokens = []
        
        self.stats['start_time'] = time.time()
        
        for i, token in enumerate(tokens, 1):
            progress = f"[{i}/{len(tokens)}]"
            token_preview = token[:15] + "..." if len(token) > 15 else token
            
            print(f"\r{progress} Проверка {token_preview:<20}", end="")
            
            try:
                account = self.create_account_instance(token, timeout=5)
                acc_info = account.get()
                balance = TokenManager.format_balance(acc_info.profile.balance)
                
                valid_tokens.append({
                    'token': token[:10] + "...",
                    'username': acc_info.profile.username,
                    'balance': balance,
                    'email': acc_info.profile.email,
                    'status': 'active'
                })
                
                print(f"\r{progress} {token_preview:<20} ", end="")
                Printer.print_color("🟢 ВАЛИДНЫЙ", Color.GREEN)
                
            except Exception:
                invalid_tokens.append(token[:10] + "...")
                print(f"\r{progress} {token_preview:<20} ", end="")
                Printer.print_color("🔴 НЕВАЛИДНЫЙ", Color.RED)
        
        elapsed_time = time.time() - self.stats['start_time']
        
        Printer.header("\n" + "═" * 60)
        Printer.print_color("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ".center(60), Color.BOLD)
        Printer.header("═" * 60)
        
        Printer.success(f"Проверено токенов: {len(tokens)}")
        Printer.success(f"Валидных: {len(valid_tokens)}")
        Printer.error(f"Невалидных: {len(invalid_tokens)}")
        Printer.info(f"Время выполнения: {elapsed_time:.2f} сек")
        Printer.info(f"Скорость: {len(tokens)/elapsed_time:.1f} токенов/сек" if elapsed_time > 0 else "")
        
        if valid_tokens:
            Printer.header("\n" + "═" * 60)
            Printer.print_color("🎯 ВАЛИДНЫЕ ТОКЕНЫ".center(60), Color.BOLD)
            Printer.header("═" * 60)
            
            for i, token_info in enumerate(valid_tokens[:15], 1):
                print(f"{i:2}. 👤 {token_info['username']:<20} 💰 {token_info['balance']:<15}")
            
            if len(valid_tokens) > 15:
                Printer.info(f"... и еще {len(valid_tokens) - 15} токенов")
            
            save_choice = UIHelper.get_input("\nСохранить валидные токены в файл? (y/n)", "n")
            if save_choice.lower() == 'y':
                TokenManager.save_valid_tokens(valid_tokens)
        
        self.stats['checked'] += len(tokens)
        self.stats['valid'] += len(valid_tokens)
        self.stats['invalid'] += len(invalid_tokens)
    
    def show_help(self):
        UIHelper.clear_screen()
        self.show_banner()
        
        help_content = [
            "🛠️  КАК ПОЛУЧИТЬ ТОКЕН:",
            "1. Зайдите на PlayerOk.com",
            "2. Авторизуйтесь в аккаунте",
            "3. Настройки → API / Токены",
            "4. Создайте новый токен",
            "5. Скопируйте его",
            "",
            "📁 МАССОВАЯ ПРОВЕРКА:",
            "• Создайте файл tokens.txt",
            "• Каждый токен на новой строке",
            "• Можно добавлять комментарии через #",
            "• Сохраните в папке с программой",
            "",
            "📊 СТАТИСТИКА:",
            f"• Проверено: {self.stats['checked']}",
            f"• Валидных: {self.stats['valid']}",
            f"• Невалидных: {self.stats['invalid']}",
            "",
            "👨‍💻 РАЗРАБОТЧИКИ:",
            "• ZLF Team",
            "• playerokapi от: alleexxeeyy",
            "• Портфолио: zlafik1.github.io/zlafikbio/"
        ]
        
        UIHelper.print_box("📘 СПРАВКА", help_content)
    
    def open_portfolio(self):
        Printer.info("Открываю портфолио...")
        try:
            webbrowser.open("https://zlafik1.github.io/zlafikbio/")
            Printer.success("Портфолио открыто в браузере")
        except Exception as e:
            Printer.error(f"Ошибка открытия: {e}")
        time.sleep(1)
    
    def show_banner(self):
        banner = [
            "╔══════════════════════════════════════════════════════════╗",
            "║                                                          ║",
            "║                  🚀 ZLF PLAYEROK CHECKER                 ║",
            "║                     Версия 2.0                           ║",
            "║                                                          ║",
            "╚══════════════════════════════════════════════════════════╝",
            "",
            "       📦 playerokapi от: alleexxeeyy",
            "       🌐 Портфолио: https://zlafik1.github.io/zlafikbio/",
            ""
        ]
        
        for line in banner:
            if "ZLF" in line:
                Printer.print_color(line, Color.BOLD + Color.MAGENTA)
            elif "playerokapi" in line or "Портфолио" in line:
                Printer.print_color(line, Color.CYAN)
            else:
                Printer.print_color(line, Color.BLUE)
    
    def show_menu(self):
        while True:
            UIHelper.clear_screen()
            self.show_banner()
            
            menu_items = [
                "🔍 Проверить один токен",
                "📊 Проверить несколько токенов",
                "📘 Справка",
                "🌐 Открыть портфолио",
                "📈 Показать статистику",
                "🚪 Выход"
            ]
            
            UIHelper.print_box("📋 ГЛАВНОЕ МЕНЮ", [])
            
            for i, item in enumerate(menu_items, 1):
                Printer.menu_item(i, item)
            
            print()
            
            choice = UIHelper.get_input("Выберите действие (1-6)", "1")
            
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
                self.open_portfolio()
                time.sleep(1)
            elif choice == '5':
                self.show_stats()
                UIHelper.get_input("\nНажмите Enter чтобы продолжить", "")
            elif choice == '6':
                Printer.warning("Выход из программы...")
                break
            else:
                Printer.error("Неверный выбор")
                time.sleep(1)
    
    def show_stats(self):
        UIHelper.clear_screen()
        self.show_banner()
        
        stats_content = [
            f"📊 СТАТИСТИКА ПРОВЕРОК:",
            f"",
            f"✅ Проверено токенов: {self.stats['checked']}",
            f"🟢 Валидных:         {self.stats['valid']}",
            f"🔴 Невалидных:       {self.stats['invalid']}",
            f"",
            f"📈 Эффективность:    {self.stats['valid']/self.stats['checked']*100:.1f}%" if self.stats['checked'] > 0 else "📈 Эффективность:    0%",
            f"",
            f"🕐 Последняя проверка: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        UIHelper.print_box("📈 СТАТИСТИКА", stats_content)
    
    def run(self):
        try:
            UIHelper.clear_screen()
            self.show_banner()
            
            Printer.info("Инициализация системы...")
            
            if not self.initialize_api():
                UIHelper.get_input("\nНажмите Enter для выхода", "")
                return
            
            Printer.success("Система готова к работе")
            time.sleep(1)
            
            self.show_menu()
            
        except KeyboardInterrupt:
            Printer.warning("\nПрограмма прервана пользователем")
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