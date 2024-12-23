import asyncio
import logging
import csv
from dataclasses import dataclass, field
from os import getenv
from typing import Any

from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.scene import Scene, SceneRegistry, ScenesManager, on
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import KeyboardButton, Message, ReplyKeyboardRemove
from aiogram.utils.formatting import (
    Bold,
    as_key_value,
    as_list,
    as_numbered_list,
    as_section,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()


@dataclass
class Answer:
    """
    Represents an answer to a question.
    """

    text: str
    """The answer text"""
    is_correct: bool = False
    """Indicates if the answer is correct"""

@dataclass
class Question:
    """
    Class representing a quiz with a question and a list of answers.
    """

    text: str
    """The question text"""
    answers: list[Answer]
    """List of answers"""

    correct_answer: str = field(init=False)

    def __post_init__(self):
        self.correct_answer = next(answer.text for answer in self.answers if answer.is_correct)


# Fake data, in real application you should use a database 
# or something else
def questions(filename):
    result = []
    with open(filename, encoding='utf-8') as fp:
        reader = csv.DictReader(fp)
        data = list(reader)
    for row in data:
        indexes = ['1', '2', '3', '4']
        result.append(Question(
            text=row['text'],
            answers=[Answer(
                row[i], is_correct=(i==row['correct'])) for i in indexes]
        ))
    return result

QUESTIONS = questions('quiz-geography.csv')


class QuizScene(Scene, state="quiz"):
    """
    This class represents a scene for a quiz game.

    It inherits from Scene class and is associated with the state "quiz".
    It handles the logic and flow of the quiz game.
    """

    @on.message.enter()
    async def on_enter(self, message: Message, state: FSMContext, step: int | None = 0) -> Any:
        """
        Method triggered when the user enters the quiz scene.

        It displays the current question and answer options to the user.

        :param message:
        :param state:
        :param step: Scene argument, can be passed to the scene using the wizard
        :return:
        """
        # TODO: dynamically load QUESTIONS based on user message `football or geography`
        if not step:
            # This is the first step, so we should greet the user
            await message.answer("Добро пожаловать в Игру!")

        try:
            quiz = QUESTIONS[step]
        except IndexError:
            # This error means that the question's list is over
            return await self.wizard.exit()

        markup = ReplyKeyboardBuilder()
        markup.add(*[KeyboardButton(text=answer.text) for answer in quiz.answers])

        if step > 0:
            markup.button(text="🔙 Back")
        markup.button(text="🚫 Exit")

        await state.update_data(step=step)
        return await message.answer(
            text=QUESTIONS[step].text,
            reply_markup=markup.adjust(2).as_markup(resize_keyboard=True),
        )

    @on.message.exit()
    async def on_exit(self, message: Message, state: FSMContext) -> None:
        """
        Method triggered when the user exits the quiz scene.

        It calculates the user's answers, displays the summary, and clears the stored answers.

        :param message:
        :param state:
        :return:
        """
        data = await state.get_data()
        answers = data.get("answers", {})

        correct = 0
        incorrect = 0
        user_answers = []
        for step, quiz in enumerate(QUESTIONS):
            answer = answers.get(step)
            is_correct = answer == quiz.correct_answer
            if is_correct:
                correct += 1
                icon = "✅"
            else:
                incorrect += 1
                icon = "❌"
            if answer is None:
                answer = "no answer"
            user_answers.append(f"{quiz.text} ({icon} {html.quote(answer)})")

        content = as_list(
            as_section(
                Bold("Ваши ответы:"),
                as_numbered_list(*user_answers),
            ),
            "",
            as_section(
                Bold("Всего:"),
                as_list(
                    as_key_value("Верно", correct),
                    as_key_value("Неверно", incorrect),
                ),
            ),
        )

        await message.answer(**content.as_kwargs(), reply_markup=ReplyKeyboardRemove())
        await state.set_data({})

    @on.message(F.text == "🔙 Back")
    async def back(self, message: Message, state: FSMContext) -> None:
        """
        Method triggered when the user selects the "Back" button.

        It allows the user to go back to the previous question.

        :param message:
        :param state:
        :return:
        """
        data = await state.get_data()
        step = data["step"]

        previous_step = step - 1
        if previous_step < 0:
            # In case when the user tries to go back from the first question,
            # we just exit the quiz
            return await self.wizard.exit()
        return await self.wizard.back(step=previous_step)

    @on.message(F.text == "🚫 Exit")
    async def exit(self, message: Message) -> None:
        """
        Method triggered when the user selects the "Exit" button.

        It exits the quiz.

        :param message:
        :return:
        """
        await self.wizard.exit()


    @on.message(F.text)
    async def answer(self, message: Message, state: FSMContext) -> None:
        """
        Method triggered when the user selects an answer.

        It stores the answer and proceeds to the next question.

        :param message:
        :param state:
        :return:
        """
        data = await state.get_data()
        step = data["step"]
        answers = data.get("answers", {})
        answers[step] = message.text
        await state.update_data(answers=answers)

        await self.wizard.retake(step=step + 1)

    @on.message()
    async def unknown_message(self, message: Message) -> None:
        """
        Method triggered when the user sends a message that is not a command or an answer.

        It asks the user to select an answer.

        :param message: The message received from the user.
        :return: None
        """
        await message.answer("Пожалуйста, выбери ответ.")

@dp.message(CommandStart())
async def starter(message: Message) -> None:
    msg = 'Good morning! I am a quiz bote! Type "/quiz" to start!'
    await message.answer(msg)

quiz_router = Router(name=__name__)
# Add handler that initializes the scene
quiz_router.message.register(QuizScene.as_handler(), Command("quiz"))


@quiz_router.message(Command("start"))
async def command_start(message: Message, scenes: ScenesManager):
    await scenes.close()
    await message.answer(
        "Привет! Я бот викторины. Для старта используй /quiz команду.",
        reply_markup=ReplyKeyboardRemove(),
    )


def create_dispatcher():
    # Event isolation is needed to correctly handle fast user responses
    dispatcher = Dispatcher(
        events_isolation=SimpleEventIsolation(),
    )
    dispatcher.include_router(quiz_router)

    # To use scenes, you should create a SceneRegistry and register your scenes there
    scene_registry = SceneRegistry(dispatcher)
    # ... and then register a scene in the registry
    # by default, Scene will be mounted to the router that passed to the SceneRegistry,
    # but you can specify the router explicitly using the `router` argument
    scene_registry.add(QuizScene)

    return dispatcher


async def main():
    dp = create_dispatcher()
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Alternatively, you can use aiogram-cli:
    # `aiogram run polling quiz_scene:create_dispatcher --log-level info --token BOT_TOKEN`
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())