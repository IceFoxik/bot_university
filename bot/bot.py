import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import async_session
from models import Schedule, DaysOfTheWeek, Disciplines, Audiences, Couples, Teachers, Groups, TypesOfActivities
from sqlalchemy import select

API_TOKEN = '8040196337:AAHM-ekXN0XOzj9TGTfPBe_pMWKnUMNiiMI'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Определение состояний для FSM
class AddScheduleState(StatesGroup):
    day_name = State()
    pair_number = State()
    start_time = State()
    end_time = State()
    audience_name = State()
    teacher_name = State()
    group_name = State()
    activity_type = State()

class UpdateScheduleState(StatesGroup):
    schedule_id = State()
    field_name = State()
    new_value = State()

class DeleteScheduleState(StatesGroup):
    schedule_id = State()

class GetScheduleState(StatesGroup):
    group_name = State()

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "Добро пожаловать! Используйте следующие команды:\n"
        "/add_schedule — Добавить расписание\n"
        "/update_schedule — Изменить расписание\n"
        "/delete_schedule — Удалить расписание\n"
        "/get_schedule — Получить расписание"
    )

# Добавление расписания
@dp.message(Command("add_schedule"))
async def add_schedule_start(message: types.Message, state: FSMContext):
    await message.reply("Введите день недели:")
    await state.set_state(AddScheduleState.day_name)

@dp.message(AddScheduleState.day_name)
async def process_day_name(message: types.Message, state: FSMContext):
    await state.update_data(day_name=message.text)
    await message.reply("Введите номер пары:")
    await state.set_state(AddScheduleState.pair_number)

@dp.message(AddScheduleState.pair_number)
async def process_pair_number(message: types.Message, state: FSMContext):
    try:
        pair_number = int(message.text)
        await state.update_data(pair_number=pair_number)
        await message.reply("Введите время начала пары (например, 09:00):")
        await state.set_state(AddScheduleState.start_time)
    except ValueError:
        await message.reply("Неверный формат данных. Введите целое число для номера пары.")

@dp.message(AddScheduleState.start_time)
async def process_start_time(message: types.Message, state: FSMContext):
    await state.update_data(start_time=message.text)
    await message.reply("Введите время окончания пары (например, 10:30):")
    await state.set_state(AddScheduleState.end_time)

@dp.message(AddScheduleState.end_time)
async def process_end_time(message: types.Message, state: FSMContext):
    await state.update_data(end_time=message.text)
    await message.reply("Введите номер аудитории:")
    await state.set_state(AddScheduleState.audience_name)

@dp.message(AddScheduleState.audience_name)
async def process_audience_name(message: types.Message, state: FSMContext):
    await state.update_data(audience_name=message.text)
    await message.reply("Введите имя преподавателя:")
    await state.set_state(AddScheduleState.teacher_name)

@dp.message(AddScheduleState.teacher_name)
async def process_teacher_name(message: types.Message, state: FSMContext):
    await state.update_data(teacher_name=message.text)
    await message.reply("Введите название группы:")
    await state.set_state(AddScheduleState.group_name)

@dp.message(AddScheduleState.group_name)
async def process_group_name(message: types.Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    await message.reply("Введите тип занятия (например, Лекция или Практика):")
    await state.set_state(AddScheduleState.activity_type)

@dp.message(AddScheduleState.activity_type)
async def process_activity_type(message: types.Message, state: FSMContext):
    await state.update_data(activity_type=message.text)

    # Получаем все собранные данные
    data = await state.get_data()

    async with async_session() as session:
        # Находим или создаем записи в связанных таблицах
        day = await session.execute(select(DaysOfTheWeek).filter_by(day_of_the_week=data['day_name']))
        day = day.scalars().first()
        if not day:
            day = DaysOfTheWeek(day_of_the_week=data['day_name'])
            session.add(day)
            await session.commit()

        teacher = await session.execute(select(Teachers).filter_by(name=data['teacher_name']))
        teacher = teacher.scalars().first()
        if not teacher:
            teacher = Teachers(name=data['teacher_name'])
            session.add(teacher)
            await session.commit()

        audience = await session.execute(select(Audiences).filter_by(audience=data['audience_name']))
        audience = audience.scalars().first()
        if not audience:
            audience = Audiences(audience=data['audience_name'])
            session.add(audience)
            await session.commit()

        group = await session.execute(select(Groups).filter_by(group_name=data['group_name']))
        group = group.scalars().first()
        if not group:
            group = Groups(group_name=data['group_name'])
            session.add(group)
            await session.commit()

        activity = await session.execute(select(TypesOfActivities).filter_by(type=data['activity_type']))
        activity = activity.scalars().first()
        if not activity:
            activity = TypesOfActivities(type=data['activity_type'])
            session.add(activity)
            await session.commit()

        couple = await session.execute(select(Couples).filter_by(
            pair_number=data['pair_number'],
            start_time=data['start_time'],
            end_time=data['end_time']
        ))
        couple = couple.scalars().first()
        if not couple:
            couple = Couples(
                pair_number=data['pair_number'],
                start_time=data['start_time'],
                end_time=data['end_time']
            )
            session.add(couple)
            await session.commit()

        # Создаем запись в расписании
        schedule = Schedule(
            day_of_the_week_id=day.id,
            couples_id=couple.id,
            audience_id=audience.id,
            teacher_id=teacher.id,
            groups_id=group.id,
            type_id=activity.id
        )
        session.add(schedule)
        await session.commit()

    await message.reply("Расписание успешно добавлено!")
    await state.clear()

# Изменение расписания
@dp.message(Command("update_schedule"))
async def update_schedule_start(message: types.Message, state: FSMContext):
    await message.reply("Введите ID записи для изменения:")
    await state.set_state(UpdateScheduleState.schedule_id)

@dp.message(UpdateScheduleState.schedule_id)
async def process_update_schedule_id(message: types.Message, state: FSMContext):
    try:
        schedule_id = int(message.text)
        await state.update_data(schedule_id=schedule_id)
        await message.reply("Введите поле для изменения (например, day_of_the_week, pair_number, teacher и т.д.):")
        await state.set_state(UpdateScheduleState.field_name)
    except ValueError:
        await message.reply("Неверный формат данных. Введите целое число для ID.")

@dp.message(UpdateScheduleState.field_name)
async def process_update_field_name(message: types.Message, state: FSMContext):
    await state.update_data(field_name=message.text)
    await message.reply("Введите новое значение для этого поля:")
    await state.set_state(UpdateScheduleState.new_value)

@dp.message(UpdateScheduleState.new_value)
async def process_update_new_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    schedule_id = data['schedule_id']
    field_name = data['field_name']
    new_value = message.text

    async with async_session() as session:
        # Находим запись в расписании
        schedule = await session.get(Schedule, schedule_id)
        if not schedule:
            await message.reply("Запись с таким ID не найдена.")
            await state.clear()
            return

        # Обновляем данные
        if field_name == "day_of_the_week":
            day = await session.execute(select(DaysOfTheWeek).filter_by(day_of_the_week=new_value))
            day = day.scalars().first()
            if not day:
                day = DaysOfTheWeek(day_of_the_week=new_value)
                session.add(day)
                await session.commit()
            schedule.day_of_the_week_id = day.id
        elif field_name == "pair_number":
            schedule.couples.pair_number = int(new_value)
        elif field_name == "start_time":
            schedule.couples.start_time = new_value
        elif field_name == "end_time":
            schedule.couples.end_time = new_value
        elif field_name == "audience":
            audience = await session.execute(select(Audiences).filter_by(audience=new_value))
            audience = audience.scalars().first()
            if not audience:
                audience = Audiences(audience=new_value)
                session.add(audience)
                await session.commit()
            schedule.audience_id = audience.id
        elif field_name == "teacher":
            teacher = await session.execute(select(Teachers).filter_by(name=new_value))
            teacher = teacher.scalars().first()
            if not teacher:
                teacher = Teachers(name=new_value)
                session.add(teacher)
                await session.commit()
            schedule.teacher_id = teacher.id
        elif field_name == "group":
            group = await session.execute(select(Groups).filter_by(group_name=new_value))
            group = group.scalars().first()
            if not group:
                group = Groups(group_name=new_value)
                session.add(group)
                await session.commit()
            schedule.groups_id = group.id
        elif field_name == "type":
            activity = await session.execute(select(TypesOfActivities).filter_by(type=new_value))
            activity = activity.scalars().first()
            if not activity:
                activity = TypesOfActivities(type=new_value)
                session.add(activity)
                await session.commit()
            schedule.type_id = activity.id

        await session.commit()

    await message.reply("Расписание успешно обновлено!")
    await state.clear()

# Удаление расписания
@dp.message(Command("delete_schedule"))
async def delete_schedule_start(message: types.Message, state: FSMContext):
    await message.reply("Введите ID записи для удаления:")
    await state.set_state(DeleteScheduleState.schedule_id)

@dp.message(DeleteScheduleState.schedule_id)
async def process_delete_schedule(message: types.Message, state: FSMContext):
    try:
        schedule_id = int(message.text)

        async with async_session() as session:
            # Находим запись в расписании
            schedule = await session.get(Schedule, schedule_id)
            if not schedule:
                raise ValueError("Запись с таким ID не найдена.")

            # Удаляем запись
            await session.delete(schedule)
            await session.commit()

        await message.reply(f"Расписание с ID {schedule_id} успешно удалено!")
        await state.clear()

    except ValueError as e:
        await message.reply(str(e))

# Получение расписания
@dp.message(Command("get_schedule"))
async def get_schedule_start(message: types.Message, state: FSMContext):
    await message.reply("Введите название группы:")
    await state.set_state(GetScheduleState.group_name)

@dp.message(GetScheduleState.group_name)
async def process_get_schedule(message: types.Message, state: FSMContext):
    group_name = message.text

    async with async_session() as session:
        # Находим группу
        group = await session.execute(select(Groups).filter_by(group_name=group_name))
        group = group.scalars().first()
        if not group:
            await message.reply("Группа не найдена.")
            await state.clear()
            return

        # Запрашиваем расписание
        result = await session.execute(
            select(Schedule, DaysOfTheWeek, Couples, Teachers, Audiences, TypesOfActivities)
            .join(DaysOfTheWeek, Schedule.day_of_the_week_id == DaysOfTheWeek.id)
            .join(Couples, Schedule.couples_id == Couples.id)
            .join(Teachers, Schedule.teacher_id == Teachers.id)
            .join(Audiences, Schedule.audience_id == Audiences.id)
            .join(TypesOfActivities, Schedule.type_id == TypesOfActivities.id)
            .filter(Schedule.groups_id == group.id)
        )

        schedules = result.all()

    if not schedules:
        await message.reply("Расписание не найдено.")
        await state.clear()
        return

    response = "Расписание:\n"
    for schedule, day, couple, teacher, audience, activity in schedules:
        response += (
            f"День: {day.day_of_the_week}\n"
            f"Пара: {couple.pair_number} ({couple.start_time} - {couple.end_time})\n"
            f"Преподаватель: {teacher.name}\n"
            f"Аудитория: {audience.audience}\n"
            f"Тип занятия: {activity.type}\n"
            f"---\n"
        )

    await message.reply(response)
    await state.clear()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())