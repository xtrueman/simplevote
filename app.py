#!/usr/bin/env python3

"""SimpleVote - FastAPI сервис для голосования за выступающих
Хранение данных в памяти (в рамках одного процесса)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


app = FastAPI(
    title="SimpleVote API",
    version="1.0.0",
    description="API для голосования за выступающих на мероприятиях",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    root_path="/api"  # Префикс для всех endpoints
)

# Настройка CORS для работы с frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Статусы голосования
class VotingStatus(str, Enum):
    VOTING_NOT_STARTED = "VOTING_NOT_STARTED"
    VOTING = "VOTING"
    VOTING_FINISHED = "VOTING_FINISHED"


# Модели данных
class StatusResponse(BaseModel):
    status: VotingStatus
    personnum: Optional[int] = None
    description: Optional[str] = None


class VoteResult(BaseModel):
    personnum: int
    description: str
    rating: float


# Хранилище данных в памяти (глобальные переменные)
voting_status: VotingStatus = VotingStatus.VOTING_NOT_STARTED
current_person_num: int = 0
current_description: str = ""
# Структура: { personnum: { "description": str, "votes": [ratings] } }
persons: dict = {}


# Вспомогательные функции

def set_current_person(description: str):
    """Установить текущую персону для голосования"""
    global voting_status, current_person_num, current_description, persons
    
    if description == "VOTING_FINISHED":
        voting_status = VotingStatus.VOTING_FINISHED
        current_person_num = 0
        current_description = ""
    elif description == "VOTING_RESTART":
        # Сброс всего голосования к начальному состоянию
        voting_status = VotingStatus.VOTING_NOT_STARTED
        current_person_num = 0
        current_description = ""
        persons.clear()  # Очищаем все результаты
    else:
        voting_status = VotingStatus.VOTING
        current_person_num += 1
        current_description = description
        # Инициализируем хранилище для новой персоны
        if current_person_num not in persons:
            persons[current_person_num] = {
                "description": description,
                "votes": []
            }


def add_vote(personnum: int, rating: int) -> bool:
    """Добавить голос. Возвращает True если успешно, False если ошибка"""
    global voting_status, current_person_num, persons
    
    # Проверка: голосование должно быть активно
    if voting_status != VotingStatus.VOTING:
        return False
    
    # Проверка: нельзя голосовать за будущих участников
    if personnum > current_person_num:
        return False
    
    # Проверка: рейтинг должен быть от 1 до 5
    if rating < 1 or rating > 5:
        return False
    
    # Инициализируем хранилище если его нет (на случай голосования за прошлых)
    if personnum not in persons:
        persons[personnum] = {
            "description": f"Участник №{personnum}",
            "votes": []
        }
    
    # Добавляем голос
    persons[personnum]["votes"].append(rating)
    return True


def get_current_status() -> StatusResponse:
    """Получить текущий статус голосования"""
    if voting_status == VotingStatus.VOTING_NOT_STARTED:
        return StatusResponse(status=VotingStatus.VOTING_NOT_STARTED)
    elif voting_status == VotingStatus.VOTING_FINISHED:
        return StatusResponse(status=VotingStatus.VOTING_FINISHED)
    else:  # VOTING
        return StatusResponse(
            status=VotingStatus.VOTING,
            personnum=current_person_num,
            description=current_description
        )


def get_voting_results() -> List[VoteResult]:
    """Получить результаты голосования, отсортированные по рейтингу"""
    results = []
    
    for personnum, data in persons.items():
        if data["votes"]:  # Только если есть голоса
            # Вычисляем средний рейтинг
            avg_rating = sum(data["votes"]) / len(data["votes"])
            results.append(VoteResult(
                personnum=personnum,
                description=data["description"],
                rating=round(avg_rating, 2)
            ))
    
    # Сортируем по рейтингу (по убыванию)
    results.sort(key=lambda x: x.rating, reverse=True)
    return results


# Endpoints

@app.get(
    "/status",
    response_model=StatusResponse,
    summary="Получить статус голосования",
    description="Возвращает текущий статус голосования и информацию о текущем участнике",
    tags=["Голосование"]
)
async def get_status():
    """
    Получить текущий статус голосования
    
    Возвращает:
    - **VOTING_NOT_STARTED**: голосование ещё не началось
    - **VOTING**: идёт голосование (с номером и описанием текущей персоны)
    - **VOTING_FINISHED**: голосование завершено
    """
    return get_current_status()


@app.post(
    "/vote",
    summary="Отправить голос",
    description="Принимает голос (оценку от 1 до 5) за участника",
    tags=["Голосование"]
)
async def submit_vote(
    personnum: int = Query(..., description="Номер персоны за которую голосуем", gt=0),
    rating: int = Query(..., ge=1, le=5, description="Оценка от 1 до 5")
):
    """
    Отправить голос за персону
    
    Параметры:
    - **personnum**: номер персоны (должен быть <= текущего номера)
    - **rating**: оценка от 1 до 5
    
    Возвращает 200 при успехе, 400 при ошибке
    """
    success = add_vote(personnum, rating)
    
    if not success:
        # Определяем причину ошибки
        if voting_status != VotingStatus.VOTING:
            raise HTTPException(
                status_code=400,
                detail="Голосование не активно"
            )
        elif personnum > current_person_num:
            raise HTTPException(
                status_code=400,
                detail=f"Нельзя голосовать за будущих участников. Текущий номер: {current_person_num}"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Ошибка при сохранении голоса"
            )
    
    return {"success": True, "message": "Голос принят"}


@app.post(
    "/setcurrentperson",
    summary="Установить текущего участника (админ)",
    description="Админская функция для запуска голосования за следующего участника или завершения голосования",
    tags=["Администрирование"]
)
async def set_current_person_endpoint(
    description: str = Query(
        ...,
        description="Имя/описание персоны, VOTING_FINISHED для завершения или VOTING_RESTART для сброса",
        min_length=1
    )
):
    """
    Админская функция: установить текущую персону для голосования
    
    Параметры:
    - **description**: имя/описание персоны
    - Специальное значение **"VOTING_FINISHED"** завершает голосование
    - Специальное значение **"VOTING_RESTART"** сбрасывает всё к начальному состоянию
    """
    set_current_person(description)
    
    if description == "VOTING_FINISHED":
        return {
            "success": True,
            "message": "Голосование завершено",
            "status": "VOTING_FINISHED"
        }
    elif description == "VOTING_RESTART":
        return {
            "success": True,
            "message": "Голосование сброшено к начальному состоянию",
            "status": "VOTING_NOT_STARTED"
        }
    else:
        return {
            "success": True,
            "message": f"Голосование открыто для участника №{current_person_num}",
            "personnum": current_person_num,
            "description": description
        }


@app.get(
    "/getresults",
    response_model=List[VoteResult],
    summary="Получить результаты голосования",
    description="Возвращает список всех участников с их рейтингами, отсортированный по убыванию",
    tags=["Результаты"]
)
async def get_results():
    """
    Получить результаты голосования
    
    Возвращает список всех персон с их рейтингами,
    отсортированный по убыванию рейтинга
    """
    return get_voting_results()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
