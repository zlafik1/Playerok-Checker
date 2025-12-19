import sys
import os
import time
import webbrowser

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_blue(text):
    print(f"\033[34m{text}\033[0m")

def print_cyan(text):
    print(f"\033[36m{text}\033[0m")

def print_green(text):
    print(f"\033[32m{text}\033[0m")

def print_yellow(text):
    print(f"\033[33m{text}\033[0m")

def print_red(text):
    print(f"\033[31m{text}\033[0m")

def open_website():
    webbrowser.open("https://zlafik1.github.io/zlafikbio/")

def show_banner():
    clear_screen()
    
    print_blue("╔══════════════════════════════════════════════════════════╗")
    print_blue("║                                                          ║")
    print_blue("║                     ZLF PLAYEROK CHECKER                 ║")
    print_blue("║                          v1.0                            ║")
    print_blue("║                                                          ║")
    print_blue("╚══════════════════════════════════════════════════════════╝")
    print()
    print_cyan("       playerokapi от: alleexxeeyy")
    print_cyan("       Портфолио: https://zlafik1.github.io/zlafikbio/")
    print()

def format_balance(balance_obj):
    """Форматирование объекта баланса в читаемый вид"""
    try:
        if hasattr(balance_obj, 'available'):
            return f"{balance_obj.available:.2f} ₽"
        elif hasattr(balance_obj, 'total'):
            return f"{balance_obj.total:.2f} ₽"
        elif hasattr(balance_obj, '__str__'):
            balance_str = str(balance_obj)
            try:
                balance_float = float(balance_str)
                return f"{balance_float:.2f} ₽"
            except:
                return balance_str
        else:
            return str(balance_obj)
    except:
        return "Неизвестно"

def check_single_token(Account):
    print()
    print_blue("╔══════════════════════════════════════════════════════════╗")
    print_blue("║                    Проверка токена                       ║")
    print_blue("╚══════════════════════════════════════════════════════════╝")
    print()
    
    print("Введите токен: ", end="")
    token = input()
    
    if not token:
        print_red("Ошибка: токен не может быть пустым")
        return
    
    print()
    print_yellow("Проверяем токен...")
    
    try:
        account = Account(
            token=token,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            requests_timeout=10,
            proxy=None
        )
        
        acc_info = account.get()
        
        clear_screen()
        show_banner()
        
        print_green("╔══════════════════════════════════════════════════════════╗")
        print_green("║                    Токен работает!                      ║")
        print_green("╚══════════════════════════════════════════════════════════╝")
        print()
        
        print_cyan("┌────────────────────────────────────────────────────────────┐")
        print_cyan("│                      Информация                            │")
        print_cyan("├────────────────────────────────────────────────────────────┤")
        
        balance_display = format_balance(acc_info.profile.balance)
        
        info_items = [
            ("Никнейм:", acc_info.profile.username),
            ("Баланс:", balance_display),
            ("Email:", acc_info.profile.email),
            ("Статус:", "Активен" if not getattr(acc_info.profile, 'is_blocked', False) else "Заблокирован")
        ]
        
        for label, value in info_items:
            display_value = str(value)[:45]
            print(f"│ {label:<10} {display_value:<42} │")
        
        print_cyan("└────────────────────────────────────────────────────────────┘")
        
    except Exception as e:
        print_red(f"Ошибка: {str(e)}")

def check_multiple_tokens(Account):
    print()
    print_blue("╔══════════════════════════════════════════════════════════╗")
    print_blue("║                 Массовая проверка токенов                ║")
    print_blue("╚══════════════════════════════════════════════════════════╝")
    print()
    
    if not os.path.exists("tokens.txt"):
        print_red("Файл tokens.txt не найден")
        return
    
    with open("tokens.txt", "r", encoding="utf-8") as f:
        tokens = [line.strip() for line in f if line.strip()]
    
    if not tokens:
        print_red("Файл tokens.txt пуст")
        return
    
    print_cyan(f"Найдено токенов: {len(tokens)}")
    print()
    
    valid_tokens = []
    invalid_tokens = []
    
    for i, token in enumerate(tokens, 1):
        print(f"[{i}/{len(tokens)}] ", end="")
        
        try:
            account = Account(
                token=token,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                requests_timeout=5,
                proxy=None
            )
            acc_info = account.get()
            balance_display = format_balance(acc_info.profile.balance)
            valid_tokens.append(f"{acc_info.profile.username} | {balance_display}")
            print_green("Рабочий")
        except:
            invalid_tokens.append(token[:20])
            print_red("Невалидный")
    
    print()
    if valid_tokens:
        print_green(f"Рабочих токенов: {len(valid_tokens)}")
        for i, token_info in enumerate(valid_tokens[:10], 1):
            print(f"  {i}. {token_info}")
        if len(valid_tokens) > 10:
            print(f"  ... и еще {len(valid_tokens) - 10}")
    else:
        print_green("Рабочих токенов: 0")
    
    print_red(f"Невалидных токенов: {len(invalid_tokens)}")

def show_help():
    print()
    print_blue("╔══════════════════════════════════════════════════════════╗")
    print_blue("║                         Справка                          ║")
    print_blue("╚══════════════════════════════════════════════════════════╝")
    print()
    
    print_cyan("Как получить токен:")
    print("1. Зайдите на PlayerOk.com")
    print("2. Авторизуйтесь в аккаунте")
    print("3. Настройки → API / Токены")
    print("4. Создайте новый токен")
    print("5. Скопируйте его")
    print()
    
    print_cyan("Массовая проверка:")
    print("• Создайте файл tokens.txt")
    print("• Каждый токен на новой строке")
    print("• Сохраните в папке с программой")
    print()
    
    print_cyan("Разработчик:")
    print("• ZLF Team")
    print("• playerokapi от: alleexxeeyy")
    print("• Портфолио: zlafikbio.github.io")

def show_menu(Account):
    while True:
        clear_screen()
        show_banner()
        
        print_blue("╔══════════════════════════════════════════════════════════╗")
        print_blue("║                      Главное меню                        ║")
        print_blue("╚══════════════════════════════════════════════════════════╝")
        print()
        
        print_cyan("1. Проверить один токен")
        print_cyan("2. Проверить несколько токенов")
        print_cyan("3. Справка")
        print_cyan("4. Открыть портфолио")
        print_cyan("5. Выход")
        print()
        
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == '1':
            check_single_token(Account)
            input("\nНажмите Enter чтобы продолжить...")
        elif choice == '2':
            check_multiple_tokens(Account)
            input("\nНажмите Enter чтобы продолжить...")
        elif choice == '3':
            clear_screen()
            show_banner()
            show_help()
            input("\nНажмите Enter чтобы продолжить...")
        elif choice == '4':
            print()
            print_yellow("Открываю портфолио...")
            open_website()
            time.sleep(1)
            print_green("Портфолио открыто")
            input("\nНажмите Enter чтобы продолжить...")
        elif choice == '5':
            print()
            print_yellow("Выход из программы...")
            break
        else:
            print_red("Неверный выбор")
            time.sleep(1)

def main():
    try:
        clear_screen()
        show_banner()
        
        print_yellow("Загрузка playerokapi...")
        
        try:
            from playerokapi.account import Account
        except ImportError:
            print_red("Ошибка: playerokapi не найден")
            print_cyan("Установите: pip install playerokapi")
            input("\nНажмите Enter для выхода...")
            return
        
        print_green("playerokapi загружен")
        time.sleep(1)
        
        show_menu(Account)
        
    except KeyboardInterrupt:
        print()
        print_yellow("Программа прервана")
    except Exception as e:
        print_red(f"Ошибка: {e}")
        input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main()