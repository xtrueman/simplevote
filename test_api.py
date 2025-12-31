#!/usr/bin/env python3
"""
Скрипт для тестирования API SimpleVote
Демонстрирует базовый workflow голосования
"""

import requests
import time

API_URL = "http://localhost:8000"

def test_api():
    print("🧪 Тестирование SimpleVote API\n")
    
    # 1. Проверка начального статуса
    print("1️⃣ Проверяем начальный статус...")
    response = requests.get(f"{API_URL}/status")
    print(f"   Статус: {response.json()}\n")
    
    # 2. Устанавливаем первого участника
    print("2️⃣ Устанавливаем первого участника...")
    response = requests.post(f"{API_URL}/setcurrentperson?description=Иван Иванов")
    print(f"   Ответ: {response.json()}\n")
    
    # 3. Проверяем статус голосования
    print("3️⃣ Проверяем статус голосования...")
    response = requests.get(f"{API_URL}/status")
    status = response.json()
    print(f"   Статус: {status}\n")
    
    # 4. Отправляем несколько голосов
    print("4️⃣ Отправляем голоса...")
    votes = [5, 4, 5, 5, 4]
    for i, rating in enumerate(votes, 1):
        response = requests.post(f"{API_URL}/vote?personnum=1&rating={rating}")
        print(f"   Голос {i}: рейтинг {rating} - {response.json()['message']}")
    print()
    
    # 5. Устанавливаем второго участника
    print("5️⃣ Устанавливаем второго участника...")
    response = requests.post(f"{API_URL}/setcurrentperson?description=Мария Петрова")
    print(f"   Ответ: {response.json()}\n")
    
    # 6. Голосуем за второго участника
    print("6️⃣ Голосуем за второго участника...")
    votes = [3, 4, 3, 4, 5]
    for i, rating in enumerate(votes, 1):
        response = requests.post(f"{API_URL}/vote?personnum=2&rating={rating}")
        print(f"   Голос {i}: рейтинг {rating} - {response.json()['message']}")
    print()
    
    # 7. Устанавливаем третьего участника
    print("7️⃣ Устанавливаем третьего участника...")
    response = requests.post(f"{API_URL}/setcurrentperson?description=Алексей Сидоров")
    print(f"   Ответ: {response.json()}\n")
    
    # 8. Голосуем за третьего участника
    print("8️⃣ Голосуем за третьего участника...")
    votes = [5, 5, 4, 5, 5]
    for i, rating in enumerate(votes, 1):
        response = requests.post(f"{API_URL}/vote?personnum=3&rating={rating}")
        print(f"   Голос {i}: рейтинг {rating} - {response.json()['message']}")
    print()
    
    # 9. Завершаем голосование
    print("9️⃣ Завершаем голосование...")
    response = requests.post(f"{API_URL}/setcurrentperson?description=VOTING_FINISHED")
    print(f"   Ответ: {response.json()}\n")
    
    # 10. Получаем результаты
    print("🏆 Результаты голосования:")
    response = requests.get(f"{API_URL}/getresults")
    results = response.json()
    
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result['description']} (№{result['personnum']}) - ⭐ {result['rating']}")
    print()
    
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка: не удалось подключиться к серверу")
        print("   Убедитесь, что сервер запущен: python app.py")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
